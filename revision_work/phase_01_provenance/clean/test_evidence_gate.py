"""P1.5 evidence-gate regression checks; original workbooks are never modified."""
import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("p15",HERE/"build_evidence_gated_data.py")
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
REPO=HERE.parents[2]
ASSERTIONS=HERE/"source_assertions.csv"

class EvidenceGatedPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)
        cls.summary=MOD.build(REPO,cls.out,ASSERTIONS)
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def test_all_256_retained_once(self):
        self.assertEqual(self.summary["total_original_rows"],256)
        self.assertEqual(self.summary["per_regime"],{"Cryogenic":54,"Room":160,"High":42})
        with (self.out/"all_256_original_with_status.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),256)
        self.assertEqual(len({r["observation_id"] for r in rows}),256)
    def test_partition_conservation(self):
        self.assertEqual(sum(self.summary["partitions"].values()),256)
        self.assertEqual(self.summary["partitions"]["unknown_provenance"],256)
        for category in MOD.PARTITIONS:
            with (self.out/(category+".csv")).open(newline="") as f:
                actual=list(csv.DictReader(f))
            self.assertEqual(len(actual),self.summary["partitions"][category])
    def test_no_unverified_epoxy_training(self):
        self.assertEqual(self.summary["verified_source_rows"],0)
        self.assertEqual(self.summary["eligible_for_future_training"],0)
    def test_p0_workbook_hashes(self):
        self.assertEqual(self.summary["original_workbook_sha256"],MOD.ORIGINAL_SHA256)
        self.assertFalse(self.summary["original_numerical_data_modified"])
    def test_missing_room_temperature_never_imputed(self):
        self.assertEqual(self.summary["recorded_room_t_missing"],160)
        with (self.out/"all_256_original_with_status.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertTrue(all(r["temperature_k_original"]=="" for r in rows if r["regime"]=="Room"))
    def test_source_reconciliation_guard_rejects_incomplete(self):
        with (self.out/"all_256_original_with_status.csv").open(newline="") as f:
            row=list(csv.DictReader(f))[0]
        bad=dict.fromkeys(MOD.ASSERTION_COLUMNS,"")
        bad["observation_id"]=row["observation_id"]
        with self.assertRaisesRegex(ValueError,"Incomplete documentary assertion"):
            MOD.validate_assertions([bad],{row["observation_id"]:{"regime":"Cryogenic"}})
    def test_conflict_flag_rows_retained(self):
        self.assertEqual(self.summary["unresolved_target_conflict_rows"],6)
        with (self.out/"exclusion_uncertainty_register.csv").open(newline="") as f:
            flagged=[r for r in csv.DictReader(f) if "SAME_INPUTS_DIFFERENT_TARGETS" in r["reason_codes"]]
        self.assertEqual(len(flagged),6)
    def test_output_directory_guard(self):
        with self.assertRaisesRegex(ValueError,"outside frozen checkout"):
            MOD.build(REPO,REPO/"revision_work/phase_01_provenance/clean",ASSERTIONS)
