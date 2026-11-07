# P1 — Dataset Quality, Provenance and Compatibility (planned work and stage gates)

P0 pinned baseline: `972671a33bba7a9531e92029602b3d2000eabd96`. Use `revision-work` only; **never modify original XLSX files or main**.

## Stage 1: Numeric audit (implemented here)

- Inspect **all 256 ORIGINAL Excel rows** with stable IDs, raw numbers and physical Excel row coordinates.
- Check missing/invalid/nonpositive conductivity, temperature, loading-scale ambiguity and potential physical inconsistencies.
- Find exact feature/formulation duplicates, exact full-record duplicates, and conflicting recorded targets.
- Preserve **all** observations in `clean_original_unverified.csv` and `record_provenance_ledger.csv`.
- Do **not** fill room temperature with 298.15 K or 300 K: original workbook has no row-level T.
- Do **not** infer material identity from conductivity thresholds; all verified labels remain blank until documentary proof.
- Upload full evidence to a GitHub Actions artifact. Tests do not write/commit.

## Stage 2: Source bibliography, candidate DOIs, source acquisition

- Start from manuscript refs [19]–[29], validate metadata against publisher records.
- Obtain original paper full text, supplemental tables and figure/table pages. Record paywall/coverage limitations.
- For each of 256 rows, demand a defensible value match: conductivity, temperature, loading unit, material identity, and table/figure.
- Source confidence: A (exact source table), B (figure digitized with uncertainty), C (candidate only), U (unverified).
- Never copy the old `02_data_provenance.py` material labels into truth columns.

## Stage 3: High temperature first

- Reviewer claims [29] BNNT-POSS/epoxy dominates; historical audit guessed 25/42 water nanofluids.
- Compare all 42 records against [29] DOI `10.1002/adfm.201201824` and other documents.
- Publication abstract describes **wt%** BNNT; spreadsheet column is named `Vol`. Do not assume equivalence.
- Outcome must be row-level evidence, not an unsupported resolution of contradictory claims.

## Stage 4: Cryogenic + Room paper-to-row tracing

- Cryogenic: 54 rows; verify [19]–[23], epoxy vs glass/quartz/Kevlar/CFRP.
- Room: 160 rows; verify [24]–[28], graphitic/metal/TPU/other materials; source actual T and measurement direction.
- Identify studies missing DOI or supplementary rows. Record unknown instead of inventing.

## Stage 5: Material partitioning and evidence-led correction

- Five categories: verified epoxy, other solid, liquid, analytical, unresolved.
- Preserve originals and write a **change-log** for any unit conversion/source-proven correction.
- Unverified rows stay held, not deleted, and are never promoted into the verified epoxy training set.
- Do not train models during P1; corrected validation and retraining occur later.

## Stage 6: Review, CI and manuscript change register

- Review sample-to-paper matches, verify counts sum back to 256, evaluate duplicates and conflicts.
- Run source-neutral automated tests on GitHub Actions and compute exact source coverage/confidence.
- Create a list of necessary manuscript fixes; maintain 259 versus 256 as unresolved unless proof is found.
- P1 may be called source-verified only when there is documentary row-level support or a clearly scoped, justified exclusion.

## CI governance

`.github/workflows/p1-provenance-audit.yml` triggers only for P1 path changes on `revision-work`, has `contents: read` and uploads results; it **never pushes any changes**.
