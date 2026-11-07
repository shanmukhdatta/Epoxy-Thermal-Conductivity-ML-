"""P1.6 committed outputs must match a new run byte-for-byte."""
import tempfile
import unittest
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
SRC=HERE/"build_signoff.py"
SPEC=importlib.util.spec_from_file_location("p1_6_source",SRC)
P16=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P16)
REPO=HERE.parents[2]
FILES=("P1_6_SIGNOFF_STATUS.json","P1_6_GATE_REGISTER.csv","P1_6_FINAL_REPORT.md")

class CommittedP16Results(unittest.TestCase):
    def test_outputs_match_fresh_source_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            P16.build(REPO,tmp)
            for name in FILES:
                self.assertEqual((Path(tmp)/name).read_bytes(),
                                 (HERE/"results"/name).read_bytes(),
                                 "Generated output mismatch: "+name)
