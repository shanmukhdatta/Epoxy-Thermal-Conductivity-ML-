import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("p1_signoff",HERE/"build_signoff.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
REPO=HERE.parents[2]

class P16AuditGateTests(unittest.TestCase):
    def test_all_40_review_comments_accounted(self):
        reviewers,changes=MODULE.assert_reviewer_coverage()
        self.assertEqual(len(reviewers),40)
        self.assertEqual(len(changes),14)
        self.assertEqual(len({r["issue_id"] for r in reviewers}),40)
    def test_true_condition_is_scientific_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=MODULE.build(REPO,tmp)
            self.assertEqual(s["numeric_pipeline_status"],"PASS")
            self.assertEqual(s["scientific_provenance_signoff"],"BLOCKED")
            self.assertFalse(s["ready_to_train_verified_epoxy_model"])
            self.assertEqual(s["source_verified_records"],0)
            self.assertEqual(s["unverified_records"],256)
            self.assertEqual(s["manuscript_claimed_original_records"],259)
            self.assertEqual(s["frozen_original_records"],256)
            self.assertTrue((Path(tmp)/"P1_6_GATE_REGISTER.csv").exists())
    def test_computational_gate_detects_wrong_counts(self):
        p11=json.loads((HERE.parent/"results/audit_summary.json").read_text())
        p13=json.loads((HERE.parent/"high_temp/results/high_42_summary.json").read_text())
        p14=json.loads((HERE.parent/"cryo_room/results/p1_4_summary.json").read_text())
        p15=json.loads((HERE.parent/"clean/results/P1_5_RECONCILIATION.json").read_text())
        modified=dict(p15,per_regime={"Cryogenic":54,"Room":159,"High":42})
        with self.assertRaises(ValueError):
            MODULE.assess(modified,p11,p13,p14,[{"observation_id":"fake"}],{})
    def test_all_blocked_flags_are_explicit(self):
        with tempfile.TemporaryDirectory() as tmp:
            MODULE.build(REPO,tmp)
            with (Path(tmp)/"P1_6_GATE_REGISTER.csv").open(newline="") as f:
                gates=list(csv.DictReader(f))
            self.assertGreaterEqual(sum(g["state"]=="BLOCKED" for g in gates),4)
            self.assertEqual(next(g for g in gates if g["gate"]=="original_data_sha256")["state"],"PASS")
            self.assertEqual(next(g for g in gates if g["gate"]=="paper_to_row_source_verification")["state"],"BLOCKED")
