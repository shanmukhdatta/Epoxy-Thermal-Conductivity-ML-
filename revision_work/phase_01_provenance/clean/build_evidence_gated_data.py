#!/usr/bin/env python3
"""P1.5: reconcile original records and build evidence-gated clean partitions.

No original-data corrections or inferred material labels. All sources must be
matched independently to a particular original row before any partition change.
This script does not independently verify literature or replace scientific review.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE=Path(__file__).resolve().parent
P1=HERE.parent
SOURCE=P1/"audit_originals.py"
SPEC=importlib.util.spec_from_file_location("p1_original",SOURCE)
AUDIT=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

ORIGINAL_SHA256={
    "Cryogenic/Cryogenic Temp.xlsx":"51f5e924c948854a0cf1474617769b2597a7f54f29e5a4a5937b3760bfb6bd4b",
    "Room/Room Temp.xlsx":"1bdee4c5ec93acd88300f6d2925b74793b5a6197efebcc230c16c42aeef8da7c",
    "High/High Temp.xlsx":"f246cfc1226aa006be68872e1b7b7ad47a3f87844bd9a43b49ca452a6405e66e"
}
ASSERTION_COLUMNS=(
    "observation_id","source_doi","source_url","source_table_or_figure",
    "source_row_identifier","source_match_method","matrix_identity","filler_identity",
    "material_class","measurement_type","loading_basis","source_temperature_kelvin",
    "source_base_tc_w_mk","source_filler_tc_w_mk","source_loading_raw",
    "source_composite_tc_w_mk","digitization_tolerance_absolute",
    "confidence","verified_by","verification_date","evidence_notes"
)
OUTPUT_COLUMNS=(
    "observation_id","regime","workbook_path","excel_row","original_index",
    "base_tc_w_mk_original","filler_tc_w_mk_original","loading_raw",
    "loading_basis_verified","temperature_k_original","temperature_k_source_verified",
    "composite_tc_w_mk_original","matrix_identity","filler_identity",
    "source_doi","source_url","source_table_or_figure","source_row_identifier",
    "measurement_type","material_class","source_confidence","eligibility_status",
    "numeric_flags","source_verification_notes"
)
PARTITIONS=(
    "verified_epoxy_experimental",
    "other_solid",
    "liquid_systems",
    "analytical_or_simulated",
    "unknown_provenance"
)

def write_csv(path,columns,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def read_assertions(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ())!=ASSERTION_COLUMNS:
            raise ValueError("Evidence assertions CSV has wrong columns")
        return list(reader)

def decimal(text):
    try:
        value=Decimal(str(text))
        return value if value.is_finite() else None
    except (InvalidOperation,ValueError,TypeError):
        return None

def validate_assertions(assertions, original_by_id):
    verified={}
    for a in assertions:
        uid=a["observation_id"].strip()
        if uid not in original_by_id or uid in verified:
            raise ValueError("Unknown or duplicated evidence assertion ID: "+uid)
        mandatory=[
            "source_doi","source_url","source_table_or_figure","source_row_identifier",
            "source_match_method","matrix_identity","filler_identity","material_class",
            "measurement_type","loading_basis","source_base_tc_w_mk",
            "source_filler_tc_w_mk","source_loading_raw","source_composite_tc_w_mk",
            "confidence","verified_by","verification_date"
        ]
        if any(not a.get(k,"").strip() for k in mandatory):
            raise ValueError("Incomplete documentary assertion for "+uid)
        if not re.match(r"^10\.\d{4,9}/\S+$",a["source_doi"]):
            raise ValueError("DOI invalid: "+uid)
        if not a["source_url"].startswith("https://"):
            raise ValueError("Source link must be https: "+uid)
        if a["source_match_method"] not in ("exact_table","digitized_figure"):
            raise ValueError("Source match method unrecognized: "+uid)
        if a["confidence"] not in ("A","B"):
            raise ValueError("Only paper-matched high/strong confidence permitted: "+uid)
        if (a["source_match_method"]=="exact_table") != (a["confidence"]=="A"):
            raise ValueError("A requires exact table; B requires documented digitization: "+uid)
        if a["material_class"] not in ("epoxy_solid","other_solid","liquid"):
            raise ValueError("Material class must have original source evidence: "+uid)
        if a["measurement_type"] not in ("experimental","analytical","simulated"):
            raise ValueError("Measurement source type must be explicit: "+uid)
        if a["loading_basis"] not in ("vol_percent","vol_fraction","wt_percent","wt_fraction"):
            raise ValueError("Loading basis must be evidenced: "+uid)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}",a["verification_date"]):
            raise ValueError("Verification date must be YYYY-MM-DD: "+uid)
        record=original_by_id[uid]
        if record["regime"]=="Room" and not a.get("source_temperature_kelvin","").strip():
            raise ValueError("Room temperature missing from source, do not invent 300K: "+uid)
        tol=decimal(a["digitization_tolerance_absolute"]) if a["digitization_tolerance_absolute"] else Decimal("0")
        if tol is None or tol<0 or (a["confidence"]=="A" and tol!=0):
            raise ValueError("Digitization tolerance must be documented and nonnegative: "+uid)
        if a["confidence"]=="B" and tol==0:
            raise ValueError("Digitized figure requires nonzero uncertainty: "+uid)
        pairs=[
            ("source_base_tc_w_mk","base_tc_w_mk_raw"),
            ("source_filler_tc_w_mk","filler_tc_w_mk_raw"),
            ("source_loading_raw","filler_loading_raw"),
            ("source_composite_tc_w_mk","composite_tc_w_mk_raw")
        ]
        if record["regime"]!="Room":
            pairs.append(("source_temperature_kelvin","temperature_k_raw"))
        for source_col,original_col in pairs:
            source_value=decimal(a[source_col])
            original_value=decimal(record[original_col])
            if source_value is None or original_value is None or abs(source_value-original_value)>tol:
                raise ValueError("Source vs Excel numeric mismatch for %s (%s)"%(uid,source_col))
        if a["source_temperature_kelvin"]:
            t=decimal(a["source_temperature_kelvin"])
            if t is None or t<=0:
                raise ValueError("Invalid documentary temperature for "+uid)
        verified[uid]=a
    return verified

def build(repo,out,assertions_path):
    repo=Path(repo).resolve()
    out=Path(out).resolve()
    if out==repo or repo in out.parents:
        raise ValueError("Outputs must be outside frozen checkout")
    actual={rel:hashlib.sha256((repo/rel).read_bytes()).hexdigest()
            for rel in ORIGINAL_SHA256}
    if actual!=ORIGINAL_SHA256:
        raise ValueError("Original Excel bytes differ from P0 SHA-256 baseline")
    with tempfile.TemporaryDirectory() as t:
        prior=AUDIT.build(repo,Path(t))
        with (Path(t)/"record_provenance_ledger.csv").open(newline="",encoding="utf-8") as f:
            originals=list(csv.DictReader(f))
        with (Path(t)/"duplicate_conflict_register.csv").open(newline="",encoding="utf-8") as f:
            duplicates=list(csv.DictReader(f))
    if len(originals)!=256 or Counter(r["regime"] for r in originals)!=Counter({"Cryogenic":54,"Room":160,"High":42}):
        raise ValueError("Original baseline row reconciliation failed")
    id_map={r["observation_id"]:r for r in originals}
    if len(id_map)!=256:
        raise ValueError("Original observation IDs not unique")
    assertions=read_assertions(assertions_path)
    claims=validate_assertions(assertions,id_map)
    conflict_ids=set()
    for g in duplicates:
        if g["group_type"]=="same_recorded_inputs" and g["conflicting_target_flag"]=="yes":
            conflict_ids.update(g["observation_ids"].split(";"))
    partition={name:[] for name in PARTITIONS}
    complete=[]
    uncertainty=[]
    unit_register=[]
    for r in originals:
        uid=r["observation_id"]
        a=claims.get(uid)
        flags=list(filter(None,r["flags"].split(";")))
        if uid in conflict_ids:
            flags.append("CONFLICTING_RECORDED_TARGET_REQUIRES_SOURCE_REVIEW")
        if a:
            if a["measurement_type"]!="experimental":
                category="analytical_or_simulated"
            elif a["material_class"]=="epoxy_solid":
                category="verified_epoxy_experimental"
            elif a["material_class"]=="other_solid":
                category="other_solid"
            else:
                category="liquid_systems"
        else:
            category="unknown_provenance"
        # A known source is not sufficient to train: source loading basis and
        # duplicate/conflict adjudication matter for later leakage-safe modeling.
        can_train=(category=="verified_epoxy_experimental"
                   and a["loading_basis"] in ("vol_percent","vol_fraction")
                   and uid not in conflict_ids
                   and "SOURCE_EXCEL_FORMULA_CHECK" not in flags)
        eligibility=("eligible_for_later_grouped_validation" if can_train
                     else ("hold_source_unverified" if not a else "hold_p1_or_p2_checks"))
        row={
            "observation_id":uid,"regime":r["regime"],"workbook_path":r["workbook_path"],
            "excel_row":r["excel_row"],"original_index":r["original_index"],
            "base_tc_w_mk_original":r["base_tc_w_mk_raw"],
            "filler_tc_w_mk_original":r["filler_tc_w_mk_raw"],
            "loading_raw":r["filler_loading_raw"],
            "loading_basis_verified":a["loading_basis"] if a else "",
            "temperature_k_original":r["temperature_k_raw"],
            "temperature_k_source_verified":a["source_temperature_kelvin"] if a else "",
            "composite_tc_w_mk_original":r["composite_tc_w_mk_raw"],
            "matrix_identity":a["matrix_identity"] if a else "",
            "filler_identity":a["filler_identity"] if a else "",
            "source_doi":a["source_doi"] if a else "",
            "source_url":a["source_url"] if a else "",
            "source_table_or_figure":a["source_table_or_figure"] if a else "",
            "source_row_identifier":a["source_row_identifier"] if a else "",
            "measurement_type":a["measurement_type"] if a else "unknown",
            "material_class":category,
            "source_confidence":a["confidence"] if a else "U",
            "eligibility_status":eligibility,
            "numeric_flags":";".join(sorted(set(flags))),
            "source_verification_notes":a["evidence_notes"] if a else "No original-source-to-row documentary evidence"
        }
        complete.append(row)
        partition[category].append(row)
        reasons=[]
        if not a:
            reasons.append("MISSING_ROW_LEVEL_PUBLICATION_PROOF")
            reasons.append("MATRIX_FILLER_IDENTITIES_UNVERIFIED")
            reasons.append("LOADING_BASIS_UNVERIFIED")
            reasons.append("MEASUREMENT_TYPE_UNVERIFIED")
        if not r["temperature_k_raw"]:
            reasons.append("TEMPERATURE_ABSENT_IN_ORIGINAL")
        if uid in conflict_ids:
            reasons.append("SAME_INPUTS_DIFFERENT_TARGETS")
        if a and a["loading_basis"] in ("wt_percent","wt_fraction"):
            reasons.append("WEIGHT_TO_VOLUME_CONVERSION_NOT_PERFORMED")
        if category!="verified_epoxy_experimental":
            reasons.append("NOT_ELIGIBLE_FOR_EPOXY_EXPERIMENTAL_TRAINING")
        uncertainty.append({
            "observation_id":uid,"material_class":category,
            "disposition":"hold_not_deleted" if eligibility!="eligible_for_later_grouped_validation" else "verify_grouping_before_training",
            "reason_codes":";".join(reasons),
            "quality_flags":row["numeric_flags"],
            "needed_evidence":"DOI, table/figure, material names, loading basis, experimental type and raw values"
        })
        unit_register.append({
            "observation_id":uid,"loading_recorded":r["filler_loading_raw"],
            "loading_basis_verified":row["loading_basis_verified"],
            "conversion_status":"no_conversion_or_unit_edit",
            "normalized_volume_fraction":"",
            "evidence_status":"source_verified" if a else "unverified"
        })
    if sum(map(len,partition.values()))!=256 or set(r["observation_id"] for r in complete)!=set(id_map):
        raise ValueError("Partition reconciliation failed")
    out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"all_256_original_with_status.csv",OUTPUT_COLUMNS,complete)
    for category,part in partition.items():
        write_csv(out/(category+".csv"),OUTPUT_COLUMNS,part)
    write_csv(out/"exclusion_uncertainty_register.csv",
              ["observation_id","material_class","disposition","reason_codes","quality_flags","needed_evidence"],uncertainty)
    write_csv(out/"unit_conversion_register.csv",
              ["observation_id","loading_recorded","loading_basis_verified","conversion_status",
               "normalized_volume_fraction","evidence_status"],unit_register)
    summary={
      "phase":"P1.5",
      "total_original_rows":len(complete),
      "per_regime":dict(Counter(r["regime"] for r in complete)),
      "original_workbook_sha256":actual,
      "verified_source_rows":len(claims),
      "paper_to_row_unverified":len(complete)-len(claims),
      "partitions":{k:len(v) for k,v in partition.items()},
      "eligible_for_future_training":sum(r["eligibility_status"]=="eligible_for_later_grouped_validation" for r in complete),
      "unresolved_target_conflict_rows":len(conflict_ids),
      "recorded_room_t_missing":sum(r["regime"]=="Room" and r["temperature_k_original"]=="" for r in complete),
      "original_numerical_data_modified":False,
      "deleted_original_rows":0,
      "note":"No row-level publication verification exists in provided evidence assertions. Blank verified dataset is scientifically intentional."
    }
    (out/"P1_5_RECONCILIATION.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"P1_5_STATUS.md").write_text(
       "# P1.5 — Evidence-gated clean-original partition\n\n"
       "Original data preserved: **256/256**, P0 SHA-256 matches all three Excel originals.\n\n"
       "Partition counts: "+json.dumps(summary["partitions"])+".\n\n"
       "Source-verified paper-to-row matches: **%d**. Eligible for later modeling: **%d**.\n\n"%(len(claims),summary["eligible_for_future_training"])
       +"All **160** room-temperature source temperatures absent; no 300 K assumption imported as a physical measurement.\n"
       "The **3 groups / 6 records** with conflicting recorded targets remain held for documentary review.\n\n"
       "**Caution:** zero rows in verified_epoxy_experimental is an evidence deficit, NOT proof that the dataset has no epoxy.\n"
       "Full Phase 1 scientific completion requires original paper figure/table and record matches, material identification, loading-unit and measurement-type verification. "
       "Do not train on unknown_provenance.csv as verified epoxy.\n\n"
       "Manuscript corrections to consider: 259 claimed versus 256 actual rows; high-temperature [29] and BNNT-POSS versus nanofluid disagreement; room temperature assumed fixed; "
       "filler wt% versus vol%; theoretical predictions versus experimental ground truth; source-system heterogeneity and grouped validation.\n",
       encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    p.add_argument("--output",required=True)
    p.add_argument("--assertions",required=True)
    args=p.parse_args()
    build(args.repo,args.output,args.assertions)
