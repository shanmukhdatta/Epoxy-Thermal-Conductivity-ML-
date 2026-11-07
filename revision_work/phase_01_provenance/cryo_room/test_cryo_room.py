"""P1.4 tests against original source workbooks, with no material guesses."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("p1_4",HERE/"screen_cryo_room.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
REPO=HERE.parents[2]

class CryoRoomP1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.shas=MODULE.parse_source(REPO)
    def test_exact_record_count(self):
        self.assertEqual(len(self.rows),214)
        self.assertEqual(sum(x["regime"]=="Cryogenic" for x in self.rows),54)
        self.assertEqual(sum(x["regime"]=="Room" for x in self.rows),160)
        self.assertEqual(len({x["observation_id"] for x in self.rows}),214)
    def test_no_unverified_material_labels(self):
        self.assertTrue(all(x["material_category"]=="unknown_provenance" for x in self.rows))
        self.assertTrue(all(x["source_confidence"]=="U" for x in self.rows))
        self.assertTrue(all(x["study_doi_verified_for_row"]=="" for x in self.rows))
    def test_room_temperature_not_silently_imputed(self):
        room=[r for r in self.rows if r["regime"]=="Room"]
        self.assertEqual(len(room),160)
        self.assertTrue(all(r["temperature_k_raw"]=="" for r in room))
    def test_original_sha256_is_recorded(self):
        self.assertEqual(len(self.shas),2)
        self.assertTrue(all(len(v)==64 for v in self.shas.values()))
        self.assertTrue(all(r["workbook_sha256"]==self.shas[r["workbook"]] for r in self.rows))
    def test_conflicting_recorded_targets_review_not_excluded(self):
        d=MODULE.duplicate_groups(self.rows)
        self.assertEqual(len(d),3)
        self.assertEqual(sum(g["target_conflict"]=="yes" for g in d),3)
        self.assertEqual(sum(g["records"] for g in d),6)
    def test_generates_source_neutral_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            stats=MODULE.run(REPO,temp)
            self.assertEqual(stats["total_rows"],214)
            self.assertEqual(stats["row_paper_doi_matches_verified"],0)
            self.assertTrue((Path(temp)/"cryo_room_214_source_neutral_ledger.csv").exists())
            with (Path(temp)/"cryo_room_214_source_neutral_ledger.csv").open(newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f))),214)
