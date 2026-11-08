# Repository-wide scientific and reproducibility audit — 2026-11-08

**Scope:** GitHub `main` at commit `d63a5361326226ecf98ffce9057f449334e1dcac`, covering historical notebooks, `revision_work/`, two uploaded executed Kaggle notebooks, editable copies, outputs, documentation and CI.

**Method:** Repository-tree inventory, source-code and saved-result inspection, document/data consistency checks, and review of latest GitHub Actions status. **Not performed:** independent end-to-end rerun, verification against original publications or original Kaggle Block 1 input hashes, or independent replication of training artifacts. This is not a scientific signoff.

## Finding register

| ID | Severity | Finding | Evidence | Required action |
| --- | --- | --- | --- | --- |
| A01 | Critical | Publication/source IDs and even material labels are **not independently established** in `revision_work`. `02_data_provenance.py` guesses matrix and filler identities from numerical conductivity intervals and marks rows `Experimental (Extracted from secondary source)`; `Potential_Source_Ref` is simply `Literature compilation`. Matching a numerical filler conductivity to SS304/Al2O3 does not establish its material identity. | `revision_work/src/02_data_provenance.py` | Keep labels provisional; obtain paper/DOI/table/row evidence and validate each mapping before asserting material-specific claims. |
| A02 | Critical | Independent *experimental* validation has not been demonstrated. Current benchmark values in `05_external_validation.py` are hardcoded Maxwell theoretical values (18 entries), not automatically extracted laboratory measurements. | `revision_work/src/05_external_validation.py`, `revision_work/reports/experimental_validation_report.md` | Report as theoretical comparisons and independently check benchmark transcription and formula. Supply actual laboratory records to make experimental claims. |
| A03 | High | Dataset-family validity: the saved provenance table contains 25 high-temperature and 10 room-temperature nanofluid rows, so an all-composites characterization would be misleading. | `revision_work/data/provenance_audit.csv` | Use verified solid-only sensitivity analyses and disclose material mix. |
| A04 | High | **Document arithmetic error** in the provenance report: the material-type count table lists 218 solid + 35 nanofluid = 253, whereas the data contains 256. Three remaining **Room/Composite** records are present but omitted in the report table; 147 solid + 10 nanofluid + 3 composite = 160 room records. | `revision_work/data/provenance_audit.csv`, `revision_work/reports/data_provenance_report.md` | Correct report to show the three unclassified `Composite` rows and avoid calling them validated solids. |
| A05 | High | The historical clean-data metrics and new Kaggle results represent **different** train/test/grouping procedures. `revision_work` uses random 80/20 holdouts and inferred filler identity in grouped CV; the Kaggle training notebook uses provisional publication groups, nested evaluation, and exploratory elevated-temperature analysis. | `revision_work/src/03_model_training.py`, `notebooks/original_executed/` | Never combine or relabel results. Build a table of dataset hashes, splits, model settings, source of each number and final status. |
| A06 | High | `revision_work/README.md` asserts combined Extra Trees R² 0.7587, MAE 0.138; `revision_work/results/metrics.csv` records R² 0.7539866, MAE 0.1391589. The generalisation report itself shows 0.7540 in one table and 0.7587 in its prose. This is a **result attribution / report mismatch**, not proof of wrong modeling. | `revision_work/README.md`, `revision_work/results/metrics.csv`, `revision_work/reports/generalisation_report.md` | Distinguish results from separate pipelines and identify exact output provenance, do not silently choose a preferred number. |
| A07 | High | The revised Kaggle Phase 2 needs three exact source CSVs (`CRYOGENIC_KAGGLE_READY.csv`, `ROOM_KAGGLE_READY.csv`, `HIGH_KAGGLE_READY.csv`); Phase 3 requires the actual `TC_BLOCK2_RESULTS.zip`. Those files are not present in the committed repository. | `notebooks/README.md`; notebook source code | Archive exact source and result artifacts, recording SHA-256; rerun and compare all output hashes, scores and folds. |
| A08 | Medium | GitHub Actions at audited HEAD only runs **static notebook checks**. Prior `revision_work` workflows shown as successful refer to older commits. The static checker does not compare unchanged original code cell contents with editable source, verify input hashes, or execute model/statistical calculations. | `.github/workflows/kaggle-notebooks-static.yml`, `scripts/validate_kaggle_notebooks.py`, Actions run history | Add dataset-independent unit/integration tests and a signed off reproducibility workflow when input data is available. |
| A09 | Medium | Historical synthetic augmentation infers parent IDs using `row_index % n_original` without independently checking that source augmented rows are in exact repeated-parent order. In `01_leakage_safe_pipeline.py`, leakage percentages are conditional on that assumption. | `revision_work/src/01_leakage_safe_pipeline.py` | Verify parent-to-child row correspondence numerically; fail on reordered or unmatched observations. |
| A10 | Medium | No root `README.md` exists at audited HEAD. Entry points are scattered between `revision_work/README.md` and `notebooks/README.md`. | GitHub repository tree | Add an entrypoint explaining historical / Kaggle distinction, setup, dataset requirements, execution graph, and evidence levels. |
| A11 | Medium | Room temperature is assumed to be 298.15 K in the historical provenance pipeline rather than recorded per source; GroupKFold groups inferred `Filler_Identity`, not verified paper-level source IDs. | `revision_work/src/02_data_provenance.py`, `revision_work/src/03_model_training.py` | Treat temperatures and groups as provisional assumptions; verify from primary sources. |
| A12 | Low | Phase 3 editable notebook’s introductory prose describes `INPUT_ZIP=None` auto-discovery, whereas its actual configuration sets a specific default archive path through `TC_PHASE2_ARCHIVE`. | `notebooks/editable/02_phase3_statistics_EDITABLE.ipynb` | Align the notebook instructions with its configured discovery/default behavior. |

## Confirmed positives

* All 256 rows exist in the historical provenance CSV: 54 cryogenic, 42 high and 160 room.
* Two actual executed Kaggle notebooks, with saved outputs, and two clean editable copies are present under `notebooks/`.
* Existing source notebooks, reports, models, and figures were preserved during Kaggle integration.
* GitHub Actions `Kaggle notebook structural audit` completed successfully for `d63a5361326226ecf98ffce9057f449334e1dcac`. **This validates syntax/structure, not scientific reproducibility.**

## Signoff gates

1. Acquire all three original Kaggle-ready source CSVs and the saved Phase 2/3 archives; verify hashes.
2. Verify primary-source row provenance, material and loading definitions, and whether 256 vs historically stated 259 can be reconciled.
3. Independently rerun full Phase 2 and Phase 3 using fixed environment versions; compare numeric outputs and confidence intervals.
4. Run at least source-group, material-group, solid-only, and random-holdout sensitivity checks with rigorous split separation.
5. Correct report discrepancies (A04/A06) with traceable data rather than selecting favorable values.
6. Only then classify reviewer evidence as supported/partial/blocked. Real laboratory validation and uncertainty data remain independent gates.

**Overall audit confidence:** high (0.95) for the listed code, arithmetic, file-inventory and CI observations; lower for original material identities, physical provenance and unrerun Kaggle numerical claims.
