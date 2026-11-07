#!/usr/bin/env python3
"""P1 source-neutral audit. Never infers identities from conductivity ranges."""
import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

PATHS = [
    ("Cryogenic", "CRY", "Cryogenic/Cryogenic Temp.xlsx", 54),
    ("Room", "ROO", "Room/Room Temp.xlsx", 160),
    ("High", "HIG", "High/High Temp.xlsx", 42),
]
FEATURES = ("Base TC", "Filler TC", "Vol", "Temp")
COLUMNS = ("Base TC", "Filler TC", "Vol", "Temp", "Composite TC")
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
ROOT = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

def read_xlsx(path):
    """Return columns and nonempty rows from a single-sheet original XLSX."""
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(n.itertext()) for n in root.findall("x:si", NS)]
        sheets = sorted(s for s in z.namelist()
                        if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", s))
        if len(sheets) != 1:
            raise ValueError(f"{path}: expected exactly one worksheet, found {len(sheets)}")
        root = ET.fromstring(z.read(sheets[0]))
        lines = []
        for el in root.findall(".//x:sheetData/x:row", NS):
            vals, formulas = {}, []
            for cell in el.findall("x:c", NS):
                pos = cell.attrib.get("r", "")
                colmatch = re.match(r"[A-Z]+", pos)
                if not colmatch:
                    continue
                col = 0
                for ch in colmatch.group():
                    col = col * 26 + ord(ch) - 64
                rawnode = cell.find("x:v", NS)
                formula = cell.find("x:f", NS)
                if formula is not None:
                    formulas.append(pos)
                typ = cell.attrib.get("t")
                if typ == "inlineStr":
                    inline = cell.find("x:is", NS)
                    value = "".join(inline.itertext()) if inline is not None else ""
                elif rawnode is None:
                    value = ""
                elif typ == "s":
                    value = shared[int(rawnode.text)]
                else:
                    value = rawnode.text or ""
                vals[col] = value.strip()
            if any(v != "" for v in vals.values()) or formulas:
                lines.append((int(el.attrib.get("r", len(lines) + 1)), vals, formulas))
        if not lines:
            raise ValueError(f"{path}: no populated worksheet rows")
        header = {col: str(v).strip() for col, v in lines[0][1].items()}
        if len(set(header.values())) != len(header):
            raise ValueError(f"{path}: duplicate column headers")
        return header, lines[1:]

def decimal_value(value):
    if value is None or value == "":
        return None
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError):
        return None

def csv_write(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def stats(values):
    if not values:
        return {"count": 0, "min": None, "max": None, "mean": None, "median": None}
    n = list(map(float, values))
    return {"count": len(n), "min": min(n), "max": max(n),
            "mean": statistics.mean(n), "median": statistics.median(n)}

def build(repo, out):
    records, issues, flags, summaries = [], [], defaultdict(list), {}
    for regime, prefix, name, expected in PATHS:
        header, entries = read_xlsx(repo / name)
        header_inverse = {v: k for k, v in header.items()}
        required = [x for x in COLUMNS if x != "Temp" or regime != "Room"]
        missing_headers = set(required) - set(header_inverse)
        if missing_headers:
            raise ValueError(f"Missing original columns in {name}: {sorted(missing_headers)}")
        if len(entries) != expected:
            issues.append(f"{name}: observed {len(entries)}, P0 baseline {expected}")
        for i, (excel_row, vals, formulas) in enumerate(entries):
            raw = {k: vals.get(header_inverse.get(k, -1), "") for k in COLUMNS}
            numeric = {k: decimal_value(raw[k]) for k in COLUMNS}
            uid = f"{prefix}_{i:03d}"
            local_flags = []
            for key in ("Base TC", "Filler TC", "Composite TC"):
                if numeric[key] is None:
                    local_flags.append("MISSING_OR_NONNUMERIC_" + key.replace(" ", "_").upper())
                elif numeric[key] <= 0:
                    local_flags.append("NONPOSITIVE_" + key.replace(" ", "_").upper())
            vol = numeric["Vol"]
            if vol is None:
                local_flags.append("MISSING_OR_NONNUMERIC_LOADING")
            elif vol < 0:
                local_flags.append("NEGATIVE_LOADING")
            elif vol > 100:
                local_flags.append("LOADING_GT_100_CHECK_BASIS")
            if regime == "Room":
                local_flags.append("TEMPERATURE_NOT_RECORDED_IN_WORKBOOK")
            elif numeric["Temp"] is None or numeric["Temp"] <= 0:
                local_flags.append("MISSING_INVALID_TEMPERATURE")
            if formulas:
                local_flags.append("EXCEL_FORMULA_PRESENT_CHECK_CACHED_VALUE")
            if vol is not None and 0 <= vol <= 1:
                local_flags.append("LOADING_SCALE_OR_UNIT_REQUIRES_SOURCE_VERIFICATION")
            if all(numeric[k] is not None for k in ("Base TC", "Filler TC", "Composite TC")):
                km, kf, kc = [numeric[k] for k in ("Base TC", "Filler TC", "Composite TC")]
                if kc < min(km, kf) or kc > max(km, kf):
                    local_flags.append("TARGET_OUTSIDE_CONSTITUENT_RANGE_REVIEW_ONLY")
            record = {
                "observation_id": uid, "regime": regime, "workbook_path": name,
                "excel_row": excel_row, "original_index": i,
                "base_tc_w_mk_raw": raw["Base TC"], "filler_tc_w_mk_raw": raw["Filler TC"],
                "filler_loading_raw": raw["Vol"], "temperature_k_raw": raw["Temp"],
                "composite_tc_w_mk_raw": raw["Composite TC"],
                "base_tc_w_mk": str(numeric["Base TC"]) if numeric["Base TC"] is not None else "",
                "filler_tc_w_mk": str(numeric["Filler TC"]) if numeric["Filler TC"] is not None else "",
                "loading_value_unconverted": str(vol) if vol is not None else "",
                "temperature_k_observed": str(numeric["Temp"]) if numeric["Temp"] is not None else "",
                "composite_tc_w_mk": str(numeric["Composite TC"]) if numeric["Composite TC"] is not None else "",
                "matrix_identity_verified": "", "filler_identity_verified": "",
                "publication_doi_verified": "", "source_figure_or_table": "",
                "measurement_type_verified": "", "loading_basis_verified": "",
                "material_category": "unknown_provenance", "source_confidence": "U",
                "training_eligibility": "hold_unverified",
                "flags": ";".join(local_flags),
            }
            for code in local_flags:
                flags[code].append(uid)
            records.append(record)
        summaries[regime] = len(entries)

    # No pre-existing guessed label or DOI is accepted as verified source evidence.
    by_input = defaultdict(list)
    by_full = defaultdict(list)
    for r in records:
        # Decimal normalizes 1 and 1.0. Missing room temperature stays truly missing.
        input_key = (r["regime"],) + tuple(
            decimal_value(r[k]) for k in ("base_tc_w_mk", "filler_tc_w_mk",
                                         "loading_value_unconverted", "temperature_k_observed"))
        target_key = decimal_value(r["composite_tc_w_mk"])
        by_input[input_key].append(r)
        by_full[input_key + (target_key,)].append(r)

    duplicate_register = []
    for kind, mapping in (("same_recorded_inputs", by_input),
                          ("same_inputs_and_target", by_full)):
        for key, members in mapping.items():
            if len(members) < 2:
                continue
            targets = sorted({r["composite_tc_w_mk"] for r in members})
            duplicate_register.append({
                "group_type": kind, "observation_ids": ";".join(x["observation_id"] for x in members),
                "number_records": len(members),
                "number_distinct_targets": len(targets),
                "conflicting_target_flag": "yes" if kind == "same_recorded_inputs" and len(targets) > 1 else "no",
                "review_disposition": "manual_review_no_rows_removed",
            })
            if kind == "same_recorded_inputs" and len(targets) > 1:
                for r in members:
                    flags["CONFLICTING_RECORDED_TARGET"].append(r["observation_id"])

    ledger_cols = list(records[0])
    csv_write(out / "record_provenance_ledger.csv", ledger_cols, records)
    csv_write(out / "clean_original_unverified.csv", ledger_cols, records)
    csv_write(out / "verified_epoxy.csv", ledger_cols, [])
    csv_write(out / "other_solid.csv", ledger_cols, [])
    csv_write(out / "liquid_systems.csv", ledger_cols, [])
    csv_write(out / "analytical_records.csv", ledger_cols, [])
    csv_write(out / "unresolved_records.csv", ledger_cols, records)
    csv_write(out / "duplicate_conflict_register.csv",
              ["group_type", "observation_ids", "number_records", "number_distinct_targets",
               "conflicting_target_flag", "review_disposition"], duplicate_register)
    csv_write(out / "exclusion_uncertainty_register.csv",
              ["observation_id", "status", "reason", "flags"],
              [{"observation_id": r["observation_id"], "status": "hold_not_excluded",
                "reason": "No row-matched primary publication evidence",
                "flags": r["flags"]} for r in records])
    csv_write(out / "numeric_quality_audit.csv",
              ["observation_id", "regime", "excel_row", "flags"],
              [{"observation_id": r["observation_id"], "regime": r["regime"],
                "excel_row": r["excel_row"],
                "flags": ";".join(sorted(set(r["flags"].split(";") + [
                    flag for flag, ids in flags.items() if r["observation_id"] in ids
                ]) - {""}))} for r in records])

    statistics_rows = []
    for regime, _, _, _ in PATHS:
        sub = [r for r in records if r["regime"] == regime]
        for field in ("base_tc_w_mk", "filler_tc_w_mk",
                      "loading_value_unconverted", "temperature_k_observed", "composite_tc_w_mk"):
            vals = [decimal_value(r[field]) for r in sub]
            calc = stats([v for v in vals if v is not None])
            statistics_rows.append({
                "regime": regime, "field": field, "total_rows": len(sub),
                "missing_or_nonnumeric": len(sub) - calc["count"], **calc
            })
    csv_write(out / "dataset_statistics.csv",
              ["regime", "field", "total_rows", "count", "missing_or_nonnumeric",
               "min", "max", "mean", "median"], statistics_rows)
    high = [r for r in records if r["regime"] == "High"]
    csv_write(out / "high_temperature_source_review.csv", ledger_cols, high)
    allids = [r["observation_id"] for r in records]
    basic = {
        "counts": summaries, "total_original": len(records),
        "source_doi_verified": 0, "source_confidence_unverified": len(records),
        "eligible_epoxy_records": 0, "uncertainty_hold_records": len(records),
        "flag_counts": {k: len(set(v)) for k, v in sorted(flags.items())},
        "same_input_groups": sum(len(v) > 1 for v in by_input.values()),
        "exact_duplicate_groups": sum(len(v) > 1 for v in by_full.values()),
        "conflicting_target_groups": sum(len(v) > 1 and len({x["composite_tc_w_mk"] for x in v}) > 1
                                         for v in by_input.values()),
        "high_temp_count": len(high),
        "original_data_untouched": True, "warnings": issues,
    }
    (out / "audit_summary.json").write_text(json.dumps(basic, indent=2) + "\n")
    (out / "P1_NUMERIC_AUDIT_REPORT.md").write_text(
        "# P1.1 Numerical audit — source-neutral results\n\n"
        f"Frozen original rows: **{len(records)}**; by regime: {summaries}.\n\n"
        f"Exact-feature duplicate groups: **{basic['same_input_groups']}**. "
        f"Exact complete-record duplicate groups: **{basic['exact_duplicate_groups']}**. "
        f"Recorded-input target-conflict groups: **{basic['conflicting_target_groups']}**.\n\n"
        f"Flags by type: {basic['flag_counts']}.\n\n"
        "**Source-verified rows: 0 of 256.** This is an honest evidence gap, not a declaration "
        "that original research has no valid sources. Existing labels from the old audit are "
        "deliberately not copied into the verified material fields.\n\n"
        "All original 256 rows are preserved in the unresolved ledger. The five domain-specific "
        "exports remain empty until paper-to-row source matching. No rows have been excluded, "
        "deduplicated, corrected or relabeled.\n\n"
        "Room-temperature source file does not record row-level temperature; no nominal 300 K "
        "value was silently inserted. The loading column 'Vol' must be source-verified for "
        "volume vs weight percent or fractional scale.\n\n"
        "High-temperature BNNT-POSS/epoxy versus nanofluid classification remains unresolved. "
        "Numeric similarities are never used as source proof.\n\n"
        f"Errors: {issues or 'none'}.\n")
    if issues or len(records) != 256 or len(allids) != len(set(allids)):
        raise SystemExit(f"P1 audit structural failure: {issues}")
    return basic

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    target = opts.output.resolve()
    if opts.repo.resolve() in target.parents:
        parser.error("Output must be outside source checkout: never overwrite the original data")
    target.mkdir(parents=True, exist_ok=True)
    print(json.dumps(build(opts.repo.resolve(), target), indent=2))
