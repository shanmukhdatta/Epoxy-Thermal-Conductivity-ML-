#!/usr/bin/env python3
"""P1.6 auditable sign-off gate: evidence-based result; never force scientific PASS.

Recomputes P1.5 directly from original frozen workbooks and source assertions.
PASS for reproducible numeric audit != approval to train or publish the manuscript.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import tempfile
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
P1=HERE.parent
P15_PATH=P1/"clean/build_evidence_gated_data.py"
SPEC=importlib.util.spec_from_file_location("p1_5_clean",P15_PATH)
P15=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P15)

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def assert_reviewer_coverage():
    reviewers=read_csv(HERE/"reviewer_issue_register.csv")
    count=Counter(row["reviewer"] for row in reviewers)
    if count!=Counter({"R1":17,"R2":17,"R3":6}):
        raise ValueError("Reviewer matrix incomplete: "+str(count))
    if len(set(x["issue_id"] for x in reviewers))!=40:
        raise ValueError("Reviewer issue identifiers are duplicated")
    if any(not x["required_response"] for x in reviewers):
        raise ValueError("Reviewer issue lacks response")
    corrections=read_csv(HERE/"manuscript_correction_register.csv")
    if len(corrections)<12:
        raise ValueError("Manuscript corrections register incomplete")
    return reviewers,corrections

def assess(p15,p11,p13,p14,ledger,partitions):
    if p15["total_original_rows"] !=256 or p11["total_original"]!=256:
        raise ValueError("Frozen dataset count mismatch")
    if p15["per_regime"]!=p11["counts"]:
        raise ValueError("Regime counts disagree")
    if p15["per_regime"]!={"Cryogenic":54,"Room":160,"High":42}:
        raise ValueError("Unexpected source row partition")
    if p13["records_examined"]!=42 or p14["total_rows"]!=214:
        raise ValueError("Original source audits incomplete")
    if len(ledger)!=256 or len({r["observation_id"] for r in ledger})!=256:
        raise ValueError("P1.5 full ledger missing/duplicating rows")
    partition_ids=[]
    for category,entries in partitions.items():
        if len(entries)!=p15["partitions"][category]:
            raise ValueError("Category count mismatch: "+category)
        if any(r["material_class"]!=category for r in entries):
            raise ValueError("Category label mismatch in "+category)
        partition_ids.extend(x["observation_id"] for x in entries)
    if sorted(partition_ids)!=sorted(r["observation_id"] for r in ledger):
        raise ValueError("Category partitions do not reconcile to original ledger")
    for row in ledger:
        if row["source_confidence"]=="U" and (row["source_doi"] or row["matrix_identity"] or row["filler_identity"]):
            raise ValueError("Unverified row has asserted material/source identity")
    if p15["verified_source_rows"]+p15["paper_to_row_unverified"]!=256:
        raise ValueError("Source provenance counts not conserved")
    if p15["original_numerical_data_modified"] or p15["deleted_original_rows"]!=0:
        raise ValueError("Original data edited or records deleted")
    if p15["partitions"]["unknown_provenance"] != p15["paper_to_row_unverified"]:
        raise ValueError("Unknown provenance count inconsistent with missing source claims")
    if p15["eligible_for_future_training"]!=sum(
       r["eligibility_status"]=="eligible_for_later_grouped_validation" for r in ledger):
        raise ValueError("Model eligibility count inconsistent")
    if p11["flag_counts"]["CONFLICTING_RECORDED_TARGET"]!=6 or p15["unresolved_target_conflict_rows"]!=6:
        raise ValueError("Unexpected conflicting-input issue counts")
    if p15["recorded_room_t_missing"]!=160 or p14["room_missing_temperature_records"]!=160:
        raise ValueError("Original Room source temperature issue not preserved")
    if p13["unknown_provenance"]>0 and p13["verified_paper_to_row_matches"]>0:
        if p13["unknown_provenance"]+p13["verified_paper_to_row_matches"]!=42:
            raise ValueError("High source match coverage inconsistent")

    gates=[
      {"gate":"original_data_sha256","state":"PASS","evidence":"Frozen original xlsx hashes validated by P1.5"},
      {"gate":"record_count_and_partition_conservation","state":"PASS","evidence":"256 originals, unique IDs, complete partition coverage"},
      {"gate":"source_ledger_reproducibility","state":"PASS","evidence":"P1.5 independently re-executed, equal to committed summary"},
      {"gate":"numeric_quality_screen","state":"PASS_WITH_REVIEW_FLAGS","evidence":"3 conflicting-target groups, 30 loading flags, 4 physical-range review flags"},
      {"gate":"paper_to_row_source_verification","state":"BLOCKED" if p15["paper_to_row_unverified"] else "PASS","evidence":str(p15["paper_to_row_unverified"])+" rows have unknown paper-to-row provenance"},
      {"gate":"epoxy_training_population","state":"BLOCKED" if p15["eligible_for_future_training"]==0 else "PASS","evidence":str(p15["eligible_for_future_training"])+" source-verified and loading-compatible epoxy records eligible"},
      {"gate":"high_temp_material_source_conflict","state":"BLOCKED" if p13["unknown_provenance"] else "PASS","evidence":str(p13["unknown_provenance"])+" high-temperature rows unverified"},
      {"gate":"room_temperature_source_metadata","state":"BLOCKED" if p15["recorded_room_t_missing"] else "PASS","evidence":str(p15["recorded_room_t_missing"])+" room source rows do not record T"},
      {"gate":"manuscript_original_count_259_vs_256","state":"BLOCKED","evidence":"Manuscript states 259 originals; frozen workbooks prove 256; explanation/correction not approved"},
      {"gate":"filler_loading_basis_and_measurement_type","state":"BLOCKED" if p15["paper_to_row_unverified"] else "REQUIRES_MANUAL_CHECK","evidence":"No validated loading units or experimental/analytical origin for unresolved records"},
    ]
    blocked=[g["gate"] for g in gates if g["state"] in ("BLOCKED","REQUIRES_MANUAL_CHECK")]
    return gates, {
      "phase":"P1.6",
      "numeric_pipeline_status":"PASS",
      "scientific_provenance_signoff":"BLOCKED" if blocked else "PASS",
      "ready_to_train_verified_epoxy_model":False if blocked else p15["eligible_for_future_training"]>0,
      "ready_to_submit_revised_manuscript":False,
      "total_original_records":256,
      "source_verified_records":p15["verified_source_rows"],
      "unverified_records":p15["paper_to_row_unverified"],
      "verified_epoxy_eligible_records":p15["eligible_for_future_training"],
      "partition_counts":p15["partitions"],
      "original_data_modified":False,
      "unresolved_input_target_conflict_rows":p15["unresolved_target_conflict_rows"],
      "missing_room_source_temperatures":p15["recorded_room_t_missing"],
      "manuscript_claimed_original_records":259,
      "frozen_original_records":256,
      "blocked_gate_names":blocked,
      "interpretation":"CI PASS validates the audit and correctly detects incomplete source provenance; it is NOT scientific P1 signoff."
    }

def build(repo,out):
    repo=Path(repo).resolve()
    out=Path(out).resolve()
    if repo==out or repo in out.parents:
        raise ValueError("Output must be outside source checkout")
    reviewers,changes=assert_reviewer_coverage()
    p11=json.loads((P1/"results/audit_summary.json").read_text())
    p13=json.loads((P1/"high_temp/results/high_42_summary.json").read_text())
    p14=json.loads((P1/"cryo_room/results/p1_4_summary.json").read_text())
    original15=json.loads((P1/"clean/results/P1_5_RECONCILIATION.json").read_text())
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        new15=P15.build(repo,root,P1/"clean/source_assertions.csv")
        if original15!=new15:
            raise ValueError("Committed P1.5 reconciliation differs from newly derived results")
        ledger=read_csv(root/"all_256_original_with_status.csv")
        parts={name:read_csv(root/(name+".csv")) for name in P15.PARTITIONS}
        gates,summary=assess(new15,p11,p13,p14,ledger,parts)
    summary["reviewer_issues_total"]=len(reviewers)
    summary["reviewer_issue_distribution"]=dict(Counter(r["reviewer"] for r in reviewers))
    summary["reviewer_p1_blocked_items"]=sum(r["p1_status"]=="BLOCKED_P1_PROVENANCE" for r in reviewers)
    summary["manuscript_changes_proposed_not_applied"]=len(changes)
    out.mkdir(parents=True,exist_ok=True)
    (out/"P1_6_SIGNOFF_STATUS.json").write_text(json.dumps(summary,indent=2)+"\n")
    with (out/"P1_6_GATE_REGISTER.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["gate","state","evidence"])
        w.writeheader()
        w.writerows(gates)
    with (out/"P1_6_REVIEWER_ISSUE_MATRIX.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(reviewers[0]))
        w.writeheader()
        w.writerows(reviewers)
    with (out/"P1_6_MANUSCRIPT_CORRECTIONS.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(changes[0]))
        w.writeheader()
        w.writerows(changes)
    (out/"P1_6_FINAL_REPORT.md").write_text(
        "# Phase P1.6 — Evidence-based final gate\n\n"
        "**Numerical audit and CI verification: PASS. Scientific Phase 1 provenance signoff: BLOCKED.**\n\n"
        f"Original observations: {summary['total_original_records']}; source-verified: {summary['source_verified_records']}; "
        f"unknown provenance: {summary['unverified_records']}; eligible verified epoxy: "
        f"{summary['verified_epoxy_eligible_records']}.\n\n"
        "**Do not treat a green GitHub Actions check as publication or source-provenance approval.**\n\n"
        "## Verified computational results\n"
        "- 256 original records preserved across 54 cryogenic, 160 room and 42 high source workbooks.\n"
        "- Three original workbooks SHA-256-checked; numeric/source-neutral P1.1–P1.5 results reconciled.\n"
        "- No rows modified, removed, silently classified or falsely assigned publication DOIs.\n"
        "- Three repeated recorded-input groups (6 rows) have different targets; 30 unit scale flags.\n"
        "- Room source lacks T for 160 records; high study match still unresolved for 42.\n\n"
        "## Manuscript evidence not yet reconciled\n"
        "- Manuscript says **259** original points versus **256** frozen Excel observations.\n"
        "- Claimed continuous temperatures are unsupported by disjoint observed regimes.\n"
        "- Huang et al. BNNT-POSS/epoxy versus historical nanofluid guesses: no verified row assignment.\n"
        "- Original loading units, experimental versus analytical provenance, figure/table page are missing.\n"
        "- Primary epoxy-only training population is still empty because verification has not been completed.\n\n"
        "## Reviewers\n"
        f"All **{len(reviewers)}** numbered comments from three reviewer reports are indexed "
        "and mapped to Phase 1 evidence or future experiments/model revisions. "
        "Mapping a comment does not mean it is addressed scientifically.\n\n"
        "## Conditions for future scientific P1 signoff\n"
        "1. Recover or reconstruct original literature-to-row extraction records with verifiable study DOI, paper figure/table and material identity.\n"
        "2. Verify loading basis, T, measured-versus-theoretical origin, and replicate/direction information.\n"
        "3. Resolve 259-versus-256 by original missing records or evidence-backed manuscript correction.\n"
        "4. Adjudicate high 42 BNNT/epoxy versus liquid-system conflict using sources, not conductivity thresholds.\n"
        "5. Regenerate partitions and unit/exclusion registers with source evidence; run tests and review gate again.\n\n"
        "**Disposition: STOP / NO scientific signoff, no P2 training using unknown-provenance data.**\n"
    )
    print(json.dumps(summary,indent=2))
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",default=".")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    build(args.repo,args.output)
