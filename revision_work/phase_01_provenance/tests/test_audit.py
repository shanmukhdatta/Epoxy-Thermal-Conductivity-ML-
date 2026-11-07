import csv
import tempfile
import unittest
import zipfile
from pathlib import Path
import importlib.util

CODE = Path(__file__).resolve().parents[1] / "audit_originals.py"
spec = importlib.util.spec_from_file_location("audit_originals", CODE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class AuditP1UnitTests(unittest.TestCase):
    def test_decimal_parser(self):
        self.assertEqual(str(audit.decimal_value("1.00")), "1.00")
        self.assertIsNone(audit.decimal_value("not-a-number"))
        self.assertIsNone(audit.decimal_value("NaN"))

    def test_xlsx_worksheet_reader(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"mini.xlsx"
            xml='''<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>
              <row r="1"><c r="A1" t="inlineStr"><is><t>Base TC</t></is></c>
                <c r="B1" t="inlineStr"><is><t>Composite TC</t></is></c></row>
              <row r="2"><c r="A2"><v>0.2</v></c><c r="B2"><v>0.8</v></c></row>
            </sheetData></worksheet>'''
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("xl/worksheets/sheet1.xml",xml)
            header,rows=audit.read_xlsx(p)
            self.assertEqual(header[1],"Base TC")
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0][1][2],"0.8")
            self.assertEqual(rows[0][0],2)

    def test_physical_limit_is_flag_only(self):
        self.assertTrue(audit.decimal_value("0") is not None)
        self.assertEqual(audit.decimal_value("1"),audit.decimal_value("1.0"))
