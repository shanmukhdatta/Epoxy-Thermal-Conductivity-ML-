#!/usr/bin/env python3
"""Static integrity check for uploaded and editable Kaggle notebooks.

Does not execute scientific computations, install packages or reproduce numerical claims.
"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("phase2_training_EXECUTED.ipynb", "01_phase2_training_EDITABLE.ipynb", 74, 37),
    ("phase3_statistics_EXECUTED.ipynb", "02_phase3_statistics_EDITABLE.ipynb", 25, 12),
]

def main():
    for original, editable, total, code_count in PAIRS:
        a = json.loads((ROOT / "notebooks/original_executed" / original).read_text(encoding="utf-8"))
        b = json.loads((ROOT / "notebooks/editable" / editable).read_text(encoding="utf-8"))
        assert a["nbformat"] == b["nbformat"] == 4
        assert len(a["cells"]) == len(b["cells"]) == total
        assert [x["cell_type"] for x in a["cells"]] == [x["cell_type"] for x in b["cells"]]
        ac = [c for c in a["cells"] if c["cell_type"] == "code"]
        bc = [c for c in b["cells"] if c["cell_type"] == "code"]
        assert len(ac) == len(bc) == code_count
        for x, y in zip(a["cells"], b["cells"]):
            if x["cell_type"] == "markdown":
                assert x["source"] == y["source"]
            else:
                assert y.get("execution_count") is None and y.get("outputs") == []
                assert x.get("execution_count") is not None
                assert not any(z.get("output_type") == "error" for z in x.get("outputs", []))
                ast.parse("".join(y["source"]))
        print(f"PASS {original}: {total} cells, {code_count} executed code cells preserved")
    print("STATIC CHECK PASS (NOT runtime or scientific reproduction)")

if __name__ == "__main__":
    main()
