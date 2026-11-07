#!/usr/bin/env python3
"""P0: read-only verification of the frozen 81-file research baseline.

Uses Python standard library. No data cleaning, model training, or input changes.
Outputs are written OUTSIDE the repository and uploaded as a CI artifact.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

BASE = "972671a33bba7a9531e92029602b3d2000eabd96"
SHEET_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
WORKBOOKS = {
    "Cryogenic/Cryogenic Temp.xlsx": 54,
    "Room/Room Temp.xlsx": 160,
    "High/High Temp.xlsx": 42,
    "Cryogenic/Cryogenic_Temp_3x_Augmented_1Percent_Noise.xlsx": 162,
    "Room/Room_Temp_3x_Augmented_1Percent_Noise.xlsx": 480,
    "High/High_Temp_3x_Augmented_1Percent_Noise.xlsx": 126,
}
CLEAN_CSVS = {
    "revision_work/data/cryogenic_clean_original.csv": 54,
    "revision_work/data/room_clean_original.csv": 160,
    "revision_work/data/high_clean_original.csv": 42,
}

def git_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def inspect_workbook(path):
    sheets = []
    with zipfile.ZipFile(path) as archive:
        members = archive.namelist()
        paths = sorted(
            [s for s in members if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", s)],
            key=lambda s: int(re.search(r"sheet(\d+)", s).group(1)))
        for sheet in paths:
            root = ET.fromstring(archive.read(sheet))
            active_rows = []
            hidden_rows = []
            first_cell_count = None
            for row in root.findall(".//m:sheetData/m:row", SHEET_NS):
                cells = [
                    c for c in row.findall("m:c", SHEET_NS)
                    if c.find("m:v", SHEET_NS) is not None
                    or c.find("m:is", SHEET_NS) is not None
                    or c.find("m:f", SHEET_NS) is not None
                ]
                if cells:
                    rid = int(row.get("r", str(len(active_rows) + 1)))
                    active_rows.append(rid)
                    if first_cell_count is None:
                        first_cell_count = len(cells)
                    if row.get("hidden", "0") == "1":
                        hidden_rows.append(rid)
            sheets.append({
                "part": sheet,
                "nonempty_rows": len(active_rows),
                "data_rows_excluding_first_nonempty_header": max(0, len(active_rows) - 1),
                "header_cell_count": first_cell_count or 0,
                "hidden_populated_row_indices": hidden_rows,
                "gaps_between_populated_row_indices": [
                    [a, b] for a, b in zip(active_rows, active_rows[1:]) if b - a > 1
                ],
            })
    return sheets

def csv_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return max(0, sum(any(cell.strip() for cell in row) for row in csv.reader(f)) - 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.resolve()
    output = args.output.resolve()
    if output == repo or repo in output.parents:
        ap.error("Output directory must be outside the repository")
    output.mkdir(parents=True, exist_ok=True)
    index_path = Path(__file__).resolve().parent / "file_inventory.csv"
    with index_path.open(newline="", encoding="utf-8") as f:
        inventory = list(csv.DictReader(f))
    issues = []
    if len(inventory) != 81 or len(set(row["repository_path"] for row in inventory)) != 81:
        issues.append("Inventory should contain 81 distinct original Git paths")
    if any(row["baseline_commit"] != BASE for row in inventory):
        issues.append("Baseline commit differs in inventory")
    verify = []
    manifest = []
    for row in inventory:
        path = row["repository_path"]
        full = repo / path
        record = {
            "repository_path": path, "status": "missing",
            "expected_size": row["size_bytes"],
            "expected_git_blob_sha1": row["git_blob_sha1"],
            "expected_sha256_if_preverified": row["sha256"],
            "actual_size": "", "actual_git_blob_sha1": "", "actual_sha256": ""
        }
        if full.is_file():
            data = full.read_bytes()
            record["actual_size"] = len(data)
            record["actual_git_blob_sha1"] = git_sha1(data)
            record["actual_sha256"] = hashlib.sha256(data).hexdigest()
            record["status"] = "verified" if (
                len(data) == int(row["size_bytes"])
                and record["actual_git_blob_sha1"] == row["git_blob_sha1"]
                and (not row["sha256"] or record["actual_sha256"] == row["sha256"])
            ) else "mismatch"
            manifest.append(record["actual_sha256"] + "  " + path)
        verify.append(record)
    with (output / "file_integrity_verification.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(verify[0]))
        w.writeheader()
        w.writerows(verify)
    (output / "sha256_manifest_full.txt").write_text(
        "\n".join(sorted(manifest)) + "\n", encoding="utf-8")
    summary = dict(Counter(row["status"] for row in verify))
    if summary != {"verified": 81}:
        issues.append("Integrity failed: expected all 81 original files to match")

    source_rows = {}
    for path, expected in CLEAN_CSVS.items():
        actual = csv_rows(repo / path)
        source_rows[path] = {"expected": expected, "actual": actual, "matches": expected == actual}
        if actual != expected:
            issues.append("Derived CSV count mismatch: " + path)

    sheets_result = {}
    for path, expected in WORKBOOKS.items():
        try:
            sheets = inspect_workbook(repo / path)
            actual = sheets[0]["data_rows_excluding_first_nonempty_header"] if len(sheets) == 1 else None
            ok = len(sheets) == 1 and actual == expected
            sheets_result[path] = {
                "expected": expected, "actual": actual, "matches": ok, "sheets": sheets
            }
            if not ok:
                issues.append("Workbook worksheet count mismatch: " + path)
        except Exception as exc:
            sheets_result[path] = {"error": str(exc)}
            issues.append("Workbook not readable: " + path)

    result = {
        "baseline_commit": BASE,
        "file_count": len(inventory),
        "integrity_summary": summary,
        "original_rows_aggregate_expected": 256,
        "original_rows_aggregate_found": sum(
            sheets_result[p].get("actual") or 0 for p in WORKBOOKS if "Augmented" not in p
        ),
        "augmented_rows_aggregate_expected": 768,
        "augmented_rows_aggregate_found": sum(
            sheets_result[p].get("actual") or 0 for p in WORKBOOKS if "Augmented" in p
        ),
        "manuscript_original_claim": 259,
        "difference_not_scientifically_reconciled": 3,
        "clean_csv_counts": source_rows,
        "workbook_counts": sheets_result,
        "issues": issues,
    }
    (output / "verified_workbook_counts.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# P0 automated baseline verification", "",
        "Pinned source commit: `" + BASE + "`.",
        "Git object and SHA-256 check for original files: " + str(summary) + ".",
        "Directly counted original workbook rows: " + str(result["original_rows_aggregate_found"]) + ".",
        "Directly counted augmented workbook rows: " + str(result["augmented_rows_aggregate_found"]) + ".",
        "Manuscript says 259 original observations; if this run verifies 256, 3 remain scientifically unresolved.",
        "Source labels, independent specimens, and the true reason for the discrepancy are not established by row-count checks.",
        "",
        "## Issues", "",
    ] + (["- " + x for x in issues] if issues else ["- No computational integrity or counting failures."])
    (output / "P0_CI_VERIFICATION_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "file_integrity": summary,
        "original_workbook_rows": result["original_rows_aggregate_found"],
        "augmented_workbook_rows": result["augmented_rows_aggregate_found"],
        "issues": issues,
    }, indent=2))
    return 0 if not issues else 1

if __name__ == "__main__":
    sys.exit(main())
