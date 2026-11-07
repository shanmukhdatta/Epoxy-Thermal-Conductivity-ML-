"""Ensure the Git-committed P1.5 result manifest reproduces byte-for-byte on original Excel."""
import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("p15_guard",HERE/"build_evidence_gated_data.py")
MODULE=importlib.util.module_from_spec(S)
S.loader.exec_module(MODULE)
REPO=HERE.parents[2]
RESULTS=HERE/"results"

class PublishedP15EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.temp.name)
        cls.generated=MODULE.build(REPO,cls.out,HERE/"source_assertions.csv")
        cls.persisted=json.loads((RESULTS/"P1_5_RECONCILIATION.json").read_text())
        cls.manifest=json.loads((RESULTS/"P1_5_ARTIFACT_SHA256.json").read_text())
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def test_summary_unchanged(self):
        self.assertEqual(self.generated,self.persisted)
    def test_exact_sha256_for_all_10_output_files(self):
        self.assertEqual(len(self.manifest["files"]),10)
        for f in self.manifest["files"]:
            b=(self.out/f["name"]).read_bytes()
            self.assertEqual(len(b),f["bytes"],f["name"])
            self.assertEqual(hashlib.sha256(b).hexdigest(),f["sha256"],f["name"])
    def test_256_row_uncertainty_and_eligibility(self):
        for name,expected in (("all_256_original_with_status.csv",256),
                              ("exclusion_uncertainty_register.csv",256),
                              ("unit_conversion_register.csv",256),
                              ("unknown_provenance.csv",256),
                              ("verified_epoxy_experimental.csv",0)):
            with (self.out/name).open(newline="",encoding="utf-8") as file:
                self.assertEqual(len(list(csv.DictReader(file))),expected)
