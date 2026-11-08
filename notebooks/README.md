# Executed Kaggle experiment notebooks (2026-11-08)

These notebooks are the actual uploaded Kaggle training and statistical-analysis run records, **not** the older separate temperature notebooks or the `revision_work/` implementation. Both tracks are preserved for audit; they must not be represented as identical.

| Notebook | Use | Code cells | Total cells |
|---|---|---:|---:|
| [Executed training](original_executed/phase2_training_EXECUTED.ipynb) | Immutable-by-convention saved outputs | 37 | 74 |
| [Executed statistics](original_executed/phase3_statistics_EXECUTED.ipynb) | Saved statistical outputs | 12 | 25 |
| [Editable training](editable/01_phase2_training_EDITABLE.ipynb) | Rerun or edit models, preprocessing and evaluations | 37 | 74 |
| [Editable statistics](editable/02_phase3_statistics_EDITABLE.ipynb) | Rerun or edit statistical checks | 12 | 25 |

Originals were transferred from the uploaded notebook JSON; JSON normalization may change byte-level formatting. Source cells and saved outputs were preserved. The editable copies clear all saved outputs and add portable paths and overwrite guards; they have **not** been executed since editing.

## Required Kaggle inputs

* Phase 2: `CRYOGENIC_KAGGLE_READY.csv`, `ROOM_KAGGLE_READY.csv`, `HIGH_KAGGLE_READY.csv` from the original Block 1 preparation; by default loaded from `/kaggle/input/datasets/shanmukhadattaboda/thermal-conductivity-datasets`. Override with `TC_INPUT_DIR`.
* Phase 3: the **original** `TC_BLOCK2_RESULTS.zip`, not a newly synthesized replacement; override the Kaggle notebook default with `TC_PHASE2_ARCHIVE`.
* The original Phase 3 output ZIP, if available, should be separately archived and checked.

## How to run

1. Open editable Phase 2 on Kaggle, attach the exact original Block 1 CSVs, and verify the dataset identity/checksums. Set `TC_RUN_MODE=full` to compare with the past run; smaller smoke tests are not numerically equivalent.
2. Set `TC_OUTPUT_BASE` only if changing the output location. Default output is `/kaggle/working/TC_BLOCK2_RESULTS`. An existing directory is **not** deleted unless `TC_OVERWRITE_RESULTS=1` is explicitly set. Archive old results first.
3. Keep the actual `TC_BLOCK2_RESULTS.zip` for Phase 3. Open the editable Phase 3 notebook separately and set `TC_PHASE2_ARCHIVE` to that ZIP. Optionally set `TC_PHASE3_OUTPUT_BASE`.
4. Inspect/edit individual cells. When changing preprocessing, feature selection, splits, augmentation or model training, rerun all downstream cells and treat resulting statistics as a **new experiment**.
5. Run `python scripts/validate_kaggle_notebooks.py` from repository root before commits; CI also runs static checks. It does **not** rerun model training.

## Important scientific caveats

Saved outputs indicate 256 records (54 cryogenic + 160 room + 42 high), not the historically cited 259; the discrepancy must be independently reconciled. Source-to-publication row matching and loading units remain unverified. Grouped high-temperature validation is not identifiable when only one provisional publication group exists. Saved outputs cannot establish experimental validation or that all reviewer objections are resolved.

Older `revision_work/` results, original temperature-specific notebooks, and models are intentionally **not deleted or silently rewritten**. See [audit](../docs/KAGGLE_INTEGRATION_AUDIT.md).
