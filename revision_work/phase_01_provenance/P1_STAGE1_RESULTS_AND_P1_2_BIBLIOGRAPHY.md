# P1.1 results committed; P1.2 bibliography verified (2026-11-07)

## P1.1 — Frozen computed results committed to Git

The `results/` directory contains the original P1.1 CI-produced **aggregate** `audit_summary.json`, `dataset_statistics.csv`, and `duplicate_conflict_register.csv`, plus `flagged_record_ids.csv` derived directly from the CI flags. All values were cross-checked against GitHub Actions run **42360296828**, artifact **13569570436**. The **complete 256-row ledger** and detailed row-level CSVs remain in that CI artifact; the producing script in this repo can regenerate them from original XLSX data. The artifact has a 30-day retention period, so download it for long-term archival.

Stage 1: 256 rows; no numerical values changed; zero source-verified DOI/row matches; 3 conflicting-input groups covering 6 Room records; 30 loading unit flags; 4 target-range flags; all 160 Room temperatures missing in original worksheet. A unit/physics flag is not proof that a record is wrong.

## P1.2 — Publication identities, not record provenance

The 11 references [19]–[29] named by the manuscript were searched against original publisher pages or first-party author article PDFs. Each identified publication is recorded in `p1_2_bibliography_verification.csv`, with DOI and evidence URL. Ref [24] lacks a DOI in the manuscript but a conference proceedings DOI **10.1615/IHTC17.460-20** was located using the author paper and secondary indexing; publisher DOI resolution is not yet independently confirmed.

Crucially, **11 bibliographic references identifiable ≠ 256 observation DOIs verified**. No high-temperature or other workbook record has yet been matched to a specific source figure/table. Any article-level matrix identity MUST NOT be automatically copied into the record-level provenance ledger.

### Study material classification from paper metadata (NOT from Excel rows)
- Ref 19: all-glass optical fibers (not epoxy).
- Ref 20: quartz/CaBr2 solution transparent sand (not epoxy).
- Ref 21: Kevlar cord (not epoxy).
- Ref 22: epoxy-based carbon-fiber laminate (anisotropic; not particulate equivalent).
- Ref 23: epoxy + negative thermal expansion nanoparticles.
- Ref 24: macro-porous graphite (not epoxy).
- Ref 25: diamond/graphene reinforced Cu matrix (not epoxy).
- Ref 26: Cu-coated TPU (not epoxy).
- Ref 27: BN/AlN filled UHMWPE (not epoxy).
- Ref 28: BN/MWCNT filled PPS (not epoxy).
- Ref 29: POSS-modified BNNT epoxy, with **wt%**, not necessarily `Vol`.

### BNNT-POSS/epoxy vs. water-nanofluid disagreement

Reference [29] undeniably exists and studies solid epoxy composites. The historical audit labels some high-temperature Excel observations "water" using only k_base thresholds. **Neither result establishes which (if any) of the 42 recorded high-temperature rows came from that paper or from liquid nanofluids.** This is still OPEN pending original data tables/figures and row-level matching.

### P1.2 result and next gate

**Bibliographic identification completed for 11 manuscript references**. **Row-to-paper provenance completed for 0 of 256 observations**. Before closing full P1, acquire source tables / supplements, match measured values, and verify loading-unit conversions for each row (especially High 42). Keep unmatched records in the unresolved partition; no speculative material labels.

## Evidence links

- P1.1 stage-one execution: https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42360296828
- P1.1 full 256-record output: https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42360296828/artifacts/13569570436
- Springer reference 20: https://link.springer.com/article/10.1007/s00231-020-03015-4
- Elsevier reference 22: https://www.sciencedirect.com/science/article/pii/S0017931024003521
- Wiley reference 29: https://advanced.onlinelibrary.wiley.com/doi/10.1002/adfm.201201824
- Begell DOI reference 24, indexed: https://doi.org/10.1615/IHTC17.460-20
