# GitHub / Kaggle integration audit — 2026-11-08

## Confirmed repository structure before change

The `main` branch contained `Cryogenic/`, `Room/`, `High/` model notebooks, `336 Data Augmentation.ipynb`, and `revision_work/` (code, data, saved models, reports, tests, results). It had no top-level `notebooks/` directory.

## Actions

* Added both uploaded executed notebooks under `notebooks/original_executed/`, including the saved outputs.
* Added independent editable notebooks under `notebooks/editable/` with cleared outputs and path/overwrite adjustments.
* Added notebook-level instructions and static CI verification.
* Preserved every existing training notebook, source file, model, figure, report, and dataset; no results were silently overwritten.

## Verification scope

Static notebook structure and JSON syntax can be verified using `scripts/validate_kaggle_notebooks.py`. This does **not** establish identical runtime dependencies, successful Kaggle rerun or identical numerical results. The uploaded dataset CSVs and actual generated Phase 2 and Phase 3 archives were not supplied in this turn. The Kaggle source data must be identified and independently validated before claims are finalized.

## Reviewer evidence issues not fixed by code

Saved Kaggle outputs indicate 256 source rows (54 cryogenic, 160 room, 42 high), versus an older manuscript count of 259. Verified physical provenance of each paper-to-row mapping is absent; loading units are not documented; one high-temperature group is insufficient for held-out publication-group validation. Keep these items open until new evidence is obtained, rather than fabricate values.

## Relationship to the historical code

The prior `revision_work/` code and trained artifacts are retained **as historical comparisons**, not relabeled as reproducing these two executed Kaggle notebooks. A numerical reconciliation still requires original Kaggle datasets, archive ZIPs, and environment versions.
