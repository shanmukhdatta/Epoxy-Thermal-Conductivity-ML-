"""Verify that committed aggregate results match an independent original-workbook rerun."""
import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("p1_4_original",HERE/"screen_cryo_room.py")
MODULE=importlib.util.module_from_spec(S)
S.loader.exec_module(MODULE)
REPO=HERE.parents[2]
RES=HERE/"results"

class CommittedP14ResultsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.persist=json.loads((RES/"p1_4_summary.json").read_text())
        cls.manifest=json.loads((RES/"p1_4_artifact_sha256_manifest.json").read_text())
    def test_commit_matches_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            run=MODULE.run(REPO,d)
            self.assertEqual(run,self.persist)
    def test_original_sources_unchanged(self):
        self.assertEqual(len(self.persist["original_workbook_sha256"]),2)
        for rel,digest in self.persist["original_workbook_sha256"].items():
            self.assertEqual(hashlib.sha256((REPO/rel).read_bytes()).hexdigest(),digest)
    def test_full_output_manifest_matches_generated_files(self):
        with tempfile.TemporaryDirectory() as d:
            MODULE.run(REPO,d)
            for item in self.manifest["files"]:
                path=Path(d)/item["name"]
                self.assertEqual(path.stat().st_size,item["size_bytes"])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),item["sha256"])
                with path.open(newline="",encoding="utf-8") as f:
                    self.assertEqual(len(list(csv.DictReader(f))),item["rows"])
    def test_conflict_groups_are_kept_unresolved(self):
        with (RES/"same_inputs_conflict_review.csv").open(newline="",encoding="utf-8") as f:
            groups=list(csv.DictReader(f))
        self.assertEqual(len(groups),3)
        self.assertTrue(all(x["target_conflict"]=="yes" for x in groups))
        self.assertTrue(all(x["disposition"]=="review_source_measurement_conditions" for x in groups))
