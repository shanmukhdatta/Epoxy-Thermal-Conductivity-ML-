"""P1.3 read-only original-data tests. These never guess material identities."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("high_source_screen", HERE / "screen_high.py")
SCREEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCREEN)
REPO = HERE.parents[2]

class HighSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = SCREEN.parse_original_high(REPO / "High/High Temp.xlsx")
    def test_exact_original_row_count(self):
        self.assertEqual(len(self.rows), 42)
        self.assertEqual(len(set(row["observation_id"] for row in self.rows)),42)
    def test_provenance_not_inferred(self):
        for row in self.rows:
            self.assertEqual(row["source_confidence"], "U")
            self.assertEqual(row["material_type_verified"], "unknown")
            self.assertEqual(row["publication_doi_verified_for_row"], "")
            self.assertEqual(row["row_to_ref_29_value_match"], "not_verified")
    def test_numeric_only_band(self):
        self.assertEqual(sum(r["numerical_matrix_band_only"] == "km_0_60_to_0_68" for r in self.rows), 25)
    def test_temperature_range(self):
        temps=[float(r["temperature_k"]) for r in self.rows]
        self.assertEqual(min(temps),308.0)
        self.assertEqual(max(temps),423.0)
        self.assertTrue(all(t > 298.15 for t in temps))
    def test_outputs_are_generated_without_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=SCREEN.execute(REPO,tmp)
            self.assertEqual(result["records_examined"],42)
            self.assertTrue((Path(tmp)/"high_42_source_compatibility.csv").is_file())
            self.assertTrue((Path(tmp)/"high_42_summary.json").is_file())
