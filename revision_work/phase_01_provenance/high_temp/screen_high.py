#!/usr/bin/env python3
"""P1.3 high-temperature compatibility screen. No inferred material identities."""
import argparse
import csv
import importlib.util
import json
import tempfile
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT_SCRIPT = HERE.parent / "audit_originals.py"
spec = importlib.util.spec_from_file_location("source_neutral_original_audit", AUDIT_SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

def parse_original_high(path):
    headers, data_rows = audit.read_xlsx(path)
    positions = {val: key for key, val in headers.items()}
    required = ["Base TC", "Filler TC", "Vol", "Temp", "Composite TC"]
    missing = set(required) - set(positions)
    if missing:
        raise ValueError("Missing columns: " + str(sorted(missing)))
    if len(data_rows) != 42:
        raise ValueError("Expected 42 original high rows, found " + str(len(data_rows)))
    results = []
    for index, (sheet_row, raw_values, formulas) in enumerate(data_rows):
        if formulas:
            raise ValueError("Excel formulas need separate review at row " + str(sheet_row))
        v = {name: audit.decimal_value(raw_values.get(positions[name], "")) for name in required}
        if any(value is None for value in v.values()):
            raise ValueError("Missing or nonnumeric value at row " + str(sheet_row))
        km = v["Base TC"]
        kf = v["Filler TC"]
        if Decimal("0.60") <= km <= Decimal("0.68"):
            matrix_band = "km_0_60_to_0_68"
        else:
            matrix_band = "km_other"
        if Decimal("28") <= kf <= Decimal("29.25"):
            filler_band = "kf_28_to_29_25"
        elif Decimal("399") <= kf <= Decimal("400"):
            filler_band = "kf_399_to_400"
        elif Decimal("2.93") <= kf <= Decimal("3.10"):
            filler_band = "kf_2_93_to_3_10"
        else:
            filler_band = "kf_other"
        results.append({
            "observation_id": "HIG_%03d" % index,
            "excel_row": sheet_row,
            "original_index": index,
            "base_tc_w_mk": str(km),
            "filler_tc_w_mk": str(kf),
            "loading_raw": str(v["Vol"]),
            "temperature_k": str(v["Temp"]),
            "composite_tc_w_mk": str(v["Composite TC"]),
            "numerical_matrix_band_only": matrix_band,
            "numerical_filler_band_only": filler_band,
            "manuscript_candidate_ref_29_doi": "10.1002/adfm.201201824",
            "ref_29_paper_loading_reported_as": "wt_percent",
            "excel_Vol_loading_basis_verified": "no",
            "row_to_ref_29_value_match": "not_verified",
            "publication_doi_verified_for_row": "",
            "matrix_identity_verified": "",
            "filler_identity_verified": "",
            "measurement_type_verified": "",
            "material_type_verified": "unknown",
            "source_confidence": "U",
            "training_eligibility": "hold_until_source_verified",
        })
    return results

def execute(repo, out):
    repo = Path(repo).resolve()
    out = Path(out).resolve()
    if out == repo or repo in out.parents:
        raise ValueError("Never write output inside original checkout")
    out.mkdir(parents=True, exist_ok=True)
    rows = parse_original_high(repo / "High/High Temp.xlsx")
    with (out / "high_42_source_compatibility.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    km_bands = dict(Counter(r["numerical_matrix_band_only"] for r in rows))
    filler_bands = dict(Counter(r["numerical_filler_band_only"] for r in rows))
    t = [Decimal(r["temperature_k"]) for r in rows]
    summary = {
        "stage": "P1.3 high-temperature source compatibility screening",
        "source_file": "High/High Temp.xlsx",
        "records_examined": len(rows),
        "verified_paper_to_row_matches": 0,
        "verified_material_identities": 0,
        "verified_liquid_records": 0,
        "verified_epoxy_records": 0,
        "unknown_provenance": len(rows),
        "temperature_range_kelvin": [float(min(t)), float(max(t))],
        "distinct_recorded_temperatures": len(set(t)),
        "records_at_298_15_kelvin": sum(x == Decimal("298.15") for x in t),
        "matrix_conductivity_numeric_bands": km_bands,
        "filler_conductivity_numeric_bands": filler_bands,
        "manuscript_candidate_ref_29_doi": "10.1002/adfm.201201824",
        "ref_29_epoxy_material_and_wt_fraction": "Verified at paper level, not row level",
        "notes": [
            "Cannot infer water or epoxy from thermal-conductivity ranges",
            "The publisher reports ref 29 filler loading in wt percent; recorded Excel Vol basis is unverified",
            "No high Excel row is linked to an original paper table or figure",
            "No records have been excluded or corrected"
        ],
    }
    (out / "high_42_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    report = [
        "# P1.3 high temperature source compatibility screen", "",
        "Original rows inspected: 42; source-verified DOI-to-row matches: 0.", "",
        "Temperature span: " + str(min(t)) + " - " + str(max(t)) + " K.",
        "Original rows at 298.15 K: " + str(summary["records_at_298_15_kelvin"]) + ".",
        "Matrix TC numeric bands: " + str(km_bands) + ".",
        "Filler TC numeric bands: " + str(filler_bands) + ".", "",
        "Manuscript ref 29: DOI 10.1002/adfm.201201824. Publisher article describes POSS-BNNT epoxy and wt percent loadings.",
        "This does not establish any Excel row as a measurement from that paper.",
        "The manuscript labels the Excel column Vol; source conversion and units remain unverified.", "",
        "The reviewer's BNNT-POSS dominance claim and the historical code's 25-water-row claim both remain unproved.",
        "No material identities inferred; no training on provisional records; no originals modified.", "",
        "Next: obtain the primary paper figures, supplemental data, and authors' original row-source extraction mapping.",
    ]
    (out / "P1_3_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=".")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    execute(args.repo, args.output)
