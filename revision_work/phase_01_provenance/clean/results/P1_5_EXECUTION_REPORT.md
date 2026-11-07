# P1.5 evidence-gated clean-original results — verified execution

**Execution date:** 2026-11-07. **Disposition: P1.5 computational partitioning PASS; scientific source provenance still OPEN.**

## GitHub runs and original data integrity
- Implementation / CLI fix: [2544b581dccb3d23c27b45d59c6700f971243ee8](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/commit/2544b581dccb3d23c27b45d59c6700f971243ee8).
- [P1.5 GitHub Actions run 42362819354](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362819354) = **SUCCESS** (9/9 tests passed).
- [P0 integrity regression run 42362819380](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362819380) = **SUCCESS**.
- [P1 numeric regression run 42362819337](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362819337) = **SUCCESS**.
- Full [P1.5 CI artifact ID 13570064451](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362819354/artifacts/13570064451) contains **all 10 output files**, including **256-row original ledger**, **256-row uncertainty/exclusion register**, and **256-row unit-conversion register**.
- Artifact is retained for **30 days**, so download and archive. This commit pins exact **SHA-256 of all 10 original artifact files** in `P1_5_ARTIFACT_SHA256.json` and tests reproducibility on each revision-work push.

## Actual results
- Original observations: **256** = 54 cryo + 160 room + 42 high.
- All **three original workbook SHA-256** hashes exactly equal P0 baseline.
- Documentary publication/row source matches verified: **0 of 256**.
- Partitions: **256 unknown**, **0 verified epoxy**, **0 other solid**, **0 verified liquid**, **0 verified analytical/simulated**. These are **verification statuses, not scientific conclusions about actual composition**.
- Eligible for future model training as source-verified epoxy: **0**. No training performed.
- Original rows removed or numerically modified: **0**.
- Three same-feature groups / six rows have different targets and await source/process review.
- All 160 room-temperature records have no source temperature. No 300 K/298.15 K substituted.
- No density-based weight-to-volume conversion was invented. All recorded loadings preserved.
- A blank `source_assertions.csv` is intentional until actual DOI + specific table/figure + numerical matches are available.

## Scientific distinction
The underlying files **may contain epoxy materials**, but no record is verified as epoxy with a documentary paper-to-row match. Do not interpret 0 in the verified partition as no epoxy exists. Using the historical guessed labels or the manuscript's bibliography at face value would mislead the reviewer response.

## What is blocked
- P1 cannot be **fully scientifically signed off** until source paper measurements match individual rows and original loading/measurement units are verified.
- The 259 vs 256 manuscript count disagreement remains open.
- The 42 high-temperature BNNT-POSS/epoxy vs nanofluid dispute remains open.
- Study and formulation grouped cross-validation requires verified source IDs and is reserved for P2/P3.

## Evidence to seek from authors / source studies
- Original literature-data extraction workbook linking each Excel row to DOI + figure/table.
- Original supplementary numerical data/figures for the cited references.
- Weight vs volume concentration basis and any source densities used.
- Source experiment-vs-analytical labels, thermal measurement direction and conditions.

**No unauthorized write to main**; code and summary-only evidence committed to `revision-work`. Raw 256-row outputs are held in the CI artifact and regenerate deterministically from frozen workbooks; this commit's checksums validate their exact bytes.
