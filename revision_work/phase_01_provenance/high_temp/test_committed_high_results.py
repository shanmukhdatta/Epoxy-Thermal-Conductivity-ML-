"""Regression checks: committed P1.3 CSV exactly matches original workbook screen."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("p1_3_screen",HERE/"screen_high.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
REPO=HERE.parents[2]

class CommittedSourceAuditTests(unittest.TestCase):
    def test_results_same_as_original(self):
        with (HERE/"results/high_42_source_compatibility.csv").open(newline="",encoding="utf-8") as f:
            stored=list(csv.DictReader(f))
        source=MODULE.parse_original_high(REPO/"High/High Temp.xlsx")
        self.assertEqual(len(stored),42)
        self.assertEqual(len(source),42)
        for persisted,fresh in zip(stored,source):
            self.assertEqual(persisted["observation_id"],fresh["observation_id"])
            for key in ("base_tc_w_mk","filler_tc_w_mk","loading_raw","temperature_k","composite_tc_w_mk",
                        "source_confidence","publication_doi_verified_for_row","material_type_verified"):
                self.assertEqual(persisted[key],str(fresh[key]))
    def test_no_verified_material_or_doi_claims(self):
        with (HERE/"results/high_42_source_compatibility.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertTrue(all(x["source_confidence"]=="U" for x in rows))
        self.assertTrue(all(not x["publication_doi_verified_for_row"] for x in rows))
        self.assertTrue(all(x["material_type_verified"]=="unknown" for x in rows))
