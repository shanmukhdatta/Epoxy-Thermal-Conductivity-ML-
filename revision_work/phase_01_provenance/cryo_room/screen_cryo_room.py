#!/usr/bin/env python3
"""P1.4 source-neutral review of the 54 cryogenic and 160 room original rows.

Only the original workbooks are treated as record-level evidence. A citation
in the manuscript is a *candidate publication*, NOT a verified source of a row.
No numeric thermal conductivity ranges are used to guess matrix or filler.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import statistics
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
NUMERIC_SCRIPT = HERE.parent / "audit_originals.py"
spec = importlib.util.spec_from_file_location("original_source_neutral", NUMERIC_SCRIPT)
numeric = importlib.util.module_from_spec(spec)
spec.loader.exec_module(numeric)

SOURCES = [
    ("Cryogenic", "CRY", "Cryogenic/Cryogenic Temp.xlsx", 54, "19-23"),
    ("Room", "ROO", "Room/Room Temp.xlsx", 160, "24-28")
]
FIELDS = ["Base TC", "Filler TC", "Vol", "Temp", "Composite TC"]
NUMERICAL_FIELDS = ["Base TC", "Filler TC", "Vol", "Composite TC"]

def parse_source(repo):
    records = []
    fingerprints = {}
    for regime, prefix, rel, expected, citation_range in SOURCES:
        path = repo / rel
        fingerprints[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        header, data = numeric.read_xlsx(path)
        columns = {v: k for k, v in header.items()}
        required = set(NUMERICAL_FIELDS) | ({"Temp"} if regime == "Cryogenic" else set())
        if not required.issubset(columns):
            raise ValueError("Missing required header in " + rel + ": " + str(required - set(columns)))
        if len(data) != expected:
            raise ValueError("P0 original count changed in " + rel + " " + str(len(data)))
        if regime == "Room" and "Temp" in columns:
            raise ValueError("Room workbook unexpectedly has Temp column; source format changed")
        for i, (excel_row, cells, formula_cells) in enumerate(data):
            originals = {f: cells.get(columns[f], "") if f in columns else "" for f in FIELDS}
            converted = {f: numeric.decimal_value(v) for f, v in originals.items()}
            flags = []
            for f in ("Base TC", "Filler TC", "Composite TC"):
                if converted[f] is None:
                    flags.append("MISSING_OR_NONNUMERIC_"+f.replace(" ","_").upper())
                elif converted[f] <= 0:
                    flags.append("NONPOSITIVE_"+f.replace(" ","_").upper())
            vol = converted["Vol"]
            if vol is None:
                flags.append("MISSING_OR_NONNUMERIC_LOADING")
            elif vol < 0 or vol > 100:
                flags.append("LOADING_OUT_OF_0_TO_100_REVIEW")
            elif vol <= 1:
                flags.append("LOADING_BASIS_AND_SCALE_UNVERIFIED")
            if regime == "Room":
                flags.append("ROW_TEMPERATURE_MISSING_FROM_ORIGINAL")
            elif converted["Temp"] is None or converted["Temp"] <= 0:
                flags.append("MISSING_OR_INVALID_TEMPERATURE")
            if formula_cells:
                flags.append("SOURCE_EXCEL_FORMULA_CHECK")
            record = {
                "observation_id":f"{prefix}_{i:03d}",
                "regime":regime,
                "workbook":rel,
                "workbook_sha256":fingerprints[rel],
                "excel_row":str(excel_row),
                "original_index":str(i),
                "base_tc_w_mk_raw":originals["Base TC"],
                "filler_tc_w_mk_raw":originals["Filler TC"],
                "loading_raw_unit_unverified":originals["Vol"],
                "temperature_k_raw":originals["Temp"],
                "composite_tc_w_mk_raw":originals["Composite TC"],
                "manuscript_regime_citation_range_not_row_match":citation_range,
                "study_doi_verified_for_row":"",
                "source_table_or_figure_verified":"",
                "material_matrix_verified":"",
                "material_filler_verified":"",
                "loading_basis_verified":"",
                "measurement_type_verified":"",
                "measurement_direction_verified":"",
                "actual_source_temperature_verified":"",
                "material_category":"unknown_provenance",
                "source_confidence":"U",
                "training_eligibility":"hold_unverified",
                "numeric_quality_flags":";".join(flags),
                "source_review_note":"No article-to-row evidence; cited papers are bibliography candidates only"
            }
            records.append(record)
    if len(records) != 214:
        raise ValueError("Expected 214 original Cryogenic/Room records")
    ids = [r["observation_id"] for r in records]
    if len(set(ids)) != 214:
        raise ValueError("Duplicate observation IDs")
    return records, fingerprints

def duplicate_groups(rows):
    by_input = defaultdict(list)
    for row in rows:
        keys = ("base_tc_w_mk_raw", "filler_tc_w_mk_raw","loading_raw_unit_unverified", "temperature_k_raw")
        k = tuple(numeric.decimal_value(row[c]) for c in keys)
        by_input[(row["regime"], k)].append(row)
    groups = []
    for (_, _), members in by_input.items():
        if len(members) <= 1:
            continue
        targets = {numeric.decimal_value(r["composite_tc_w_mk_raw"]) for r in members}
        groups.append({
            "observation_ids":";".join(m["observation_id"] for m in members),
            "records":len(members),
            "different_target_values":len(targets),
            "target_conflict":"yes" if len(targets)>1 else "no",
            "disposition":"review_source_measurement_conditions"
        })
    return groups

def csv_dump(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader()
        w.writerows(rows)

def run(repo, output):
    repo, out=Path(repo).resolve(),Path(output).resolve()
    if out == repo or repo in out.parents:
        raise ValueError("Output must not be inside the original checkout")
    rows, checksums = parse_source(repo)
    out.mkdir(parents=True,exist_ok=True)
    headers=list(rows[0])
    csv_dump(out/"cryo_room_214_source_neutral_ledger.csv",rows,headers)
    csv_dump(out/"cryo_54_unresolved.csv",[r for r in rows if r["regime"]=="Cryogenic"],headers)
    csv_dump(out/"room_160_unresolved.csv",[r for r in rows if r["regime"]=="Room"],headers)
    groups=duplicate_groups(rows)
    csv_dump(out/"same_inputs_conflict_review.csv",groups,
             ["observation_ids","records","different_target_values","target_conflict","disposition"])
    flag_counts=Counter(f for row in rows for f in row["numeric_quality_flags"].split(";") if f)
    temperatures=[numeric.decimal_value(r["temperature_k_raw"]) for r in rows if r["regime"]=="Cryogenic"]
    summary={
        "stage":"P1.4 original record source-neutral audit",
        "original_cryogenic_rows":54,
        "original_room_rows":160,
        "total_rows":214,
        "row_paper_doi_matches_verified":0,
        "row_material_identities_verified":0,
        "unverified_rows":214,
        "all_original_rows_preserved":True,
        "cryogenic_temperature_min_k":float(min(temperatures)),
        "cryogenic_temperature_max_k":float(max(temperatures)),
        "cryogenic_distinct_temperatures_k":sorted(float(t) for t in set(temperatures)),
        "room_temperature_source_column":"ABSENT",
        "room_missing_temperature_records":160,
        "flag_counts":dict(sorted(flag_counts.items())),
        "same_recorded_inputs_groups":len(groups),
        "different_target_groups":sum(g["target_conflict"]=="yes" for g in groups),
        "original_workbook_sha256":checksums,
        "manuscript_regime_paper_references":{"Cryogenic":"19-23","Room":"24-28"},
        "source_match_warning":"Manuscript bibliography is not a record-to-paper mapping. No source identities inferred."
    }
    (out/"p1_4_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    (out/"P1_4_REPORT.md").write_text(
        "# P1.4 — Original cryogenic and room-temperature audit results\n\n"
        f"Original **214/214 rows** inspected (54 Cryogenic; 160 Room); **0/214 row-paper matches verified**.\n"
        f"Cryogenic T range **{summary['cryogenic_temperature_min_k']}–{summary['cryogenic_temperature_max_k']} K**.\n"
        "All 160 room-temperature rows lack explicit temperatures in the source workbook. "
        "No 298.15 K/300 K temperatures were silently added.\n"
        f"Same-input groups: **{len(groups)}**; conflicting target groups: "
        f"**{summary['different_target_groups']}**.\n"
        f"Quality review flags: **{summary['flag_counts']}**.\n\n"
        "All material names, DOI-to-row matches, measurement methods and source-confidence "
        "levels remain unknown. Bibliographic studies are reviewed separately; no row has "
        "been automatically assigned to any cited paper.\n\n"
        "No data values edited, no rows deleted, no unit conversion, no model training.\n\n"
        "Verification of rows against original paper tables, figures, experimental conditions "
        "and (ideally) the authors' literature extraction sheet remains required.\n",
        encoding="utf-8")
    print(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--repo",default=".")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    run(args.repo,args.output)
