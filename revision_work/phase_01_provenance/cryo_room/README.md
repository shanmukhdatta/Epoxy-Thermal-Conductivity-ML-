# P1.4 Cryogenic and room-temperature source trace

## Scope

Run the new audit on the untouched **54 cryogenic** and **160 room** original XLSX rows. No use of legacy material labels or synthetic/augmented data. Status **preliminary source-neutral audit; paper-to-row source matching remains open**.

```bash
python -m unittest discover -s revision_work/phase_01_provenance/cryo_room -p 'test_*.py' -v
python revision_work/phase_01_provenance/cryo_room/screen_cryo_room.py --repo . --output ../P1_4_evidence
```

GitHub Actions runs read-only on revision-work. Output is a CI artifact and later committed as an auditable result.

## Original workbook decisions
- Room 160 observations have **no temperature column**. The manuscript's 300 K assumption is documented but **not imputed** as a measured value.
- Source volume loading stored unchanged: weight versus volume basis **not proven**.
- Report 3 same-input different-target groups, but do **not remove** rows; source processing and measurement direction must be considered.
- Publication references [19]–[23] and [24]–[28] apply to cryogenic and room sections at **bibliography level only**, not individual Excel records.
- Verified matrix/filler identity, DOI, source figure/table, measurement direction and experiment-vs-analysis remain blank/unknown for every untraced record.

## Published bibliography evidence with major scientific issues

The first-party publication abstracts and metadata confirm that:
- Ref [19] studies all-glass optical fibers and is not an epoxy composite source.
- Ref [20] concerns quartz/CaBr2 transparent sand and cites model applicability at 5–45°C; this does **not overlap** the cryogenic file's 2–120 K range.
- Ref [21] measures a Kevlar cord at 0.1–2.5 K (paper reports a formula in W/(cm K)); tiny overlap with 2–120 K cryogenic data.
- Ref [22] uses carbon fiber/epoxy laminates and records anisotropic thermal conductivity: in-plane vs out-of-plane are materially important.
- Ref [23] studies epoxy with negative-expansion particles, measured within 77–300 K.
- Ref [24] is macro-porous graphite, not epoxy; manuscript lists it among room references despite high-temp title.
- Ref [25] is a copper-matrix composite, not epoxy.
- Ref [26] is Cu-coated thermoplastic polyurethane, not epoxy.
- Ref [27] is UHMWPE filled with BN/AlN, not epoxy; wt% loadings mentioned.
- Ref [28] is PPS thermoplastic filled with BN/MWCNT, not epoxy.

Study-level classification does **not** authorize assigning any of those identities to records in Excel. Reference metadata and evidence links are kept in `paper_level_evidence.csv`. Original paper tables, supplements and author's extraction notebook must be consulted for record-to-source assignment.

## Full P1 remaining scope
- Source-matched identification for 54+160 original rows.
- Resolve high-temperature 42 source conflict and 259 vs 256 count discrepancy.
- Preserve all unverified rows in a quarantine dataset, not as verified epoxy.
- Determine reproducible clean-original partition and necessary manuscript corrections after source evidence is available.

No training in P1. No changes to main or original XLSX files.
