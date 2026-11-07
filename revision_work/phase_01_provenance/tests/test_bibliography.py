"""Read-only quality assurance for committed P1.1 results and P1.2 bibliography."""
import csv
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
class BibliographyTests(unittest.TestCase):
    def test_p1_1_summary_counts_and_unverified(self):
        s=json.loads((BASE/"results/audit_summary.json").read_text())
        self.assertEqual(s["counts"], {"Cryogenic":54,"Room":160,"High":42})
        self.assertEqual(s["total_original"],256)
        self.assertEqual(s["source_doi_verified"],0)
        self.assertEqual(s["eligible_epoxy_records"],0)
        self.assertEqual(s["exact_duplicate_groups"],0)
        self.assertEqual(s["conflicting_target_groups"],3)
        self.assertEqual(s["flag_counts"]["CONFLICTING_RECORDED_TARGET"],6)

    def test_bibliography_citations_distinct_and_not_mislabeled_as_matched(self):
        with (BASE/"p1_2_bibliography_verification.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),11)
        self.assertEqual({int(r["manuscript_ref"]) for r in rows},set(range(19,30)))
        self.assertEqual(len({r["candidate_doi"].lower() for r in rows}),11)
        for r in rows:
            self.assertTrue(r["candidate_doi"].startswith("10."))
            self.assertTrue(r["evidence_url"].startswith("https://"))
            self.assertEqual(r["excel_row_source_matching_status"],"NO_EXCEL_ROW_MATCH_VERIFIED")
            self.assertEqual(r["worksheet_record_count_confirmed"],"0")
        r29=next(r for r in rows if r["manuscript_ref"]=="29")
        self.assertIn("POSS",r29["publisher_declared_material"])
        self.assertIn("wt percent",r29["data_relevance_notes"])
        r24=next(r for r in rows if r["manuscript_ref"]=="24")
        self.assertEqual(r24["candidate_doi"].lower(),"10.1615/ihtc17.460-20")

    def test_duplicate_register_preserves_manual_review(self):
        with (BASE/"results/duplicate_conflict_register.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),3)
        self.assertTrue(all(r["conflicting_target_flag"]=="yes" for r in rows))
        self.assertTrue(all(r["review_disposition"]=="manual_review_no_rows_removed" for r in rows))
