# P0 row-count reconciliation — evidence register

## Evidence

| Source | Cryogenic | Room | High | Total |
|---|---:|---:|---:|---:|
| Existing original-workbook audit (not yet independently rerun in new fork) | 54 | 160 | 42 | **256** |
| Independently counted derived `revision_work/data/*_clean_original.csv` | 54 | 160 | 42 | **256** |
| Existing augmented-workbook audit | 162 | 480 | 126 | **768** |
| Submitted manuscript, PDF page 6 | — | — | — | **259** original points |

**Numerical difference: three records.** The available original file inventory contains three `.docx` theoretical comparison documents (`4.2K.docx`, `300K.docx`, `323K.docx`). The prior audit proposed that these might explain 256 + 3 = 259, but **no verified row-level evidence confirms it**. Do not silently add benchmark calculations to measured data, or silently change the manuscript count.

An automated second audit will independently inspect the actual six XLSX files in GitHub Actions, with detailed outputs in `p0-integrity-evidence`.

## Other baseline discrepancies to address in later phases

- Manuscript's elevated-temperature boundary (302–427 K) versus earlier audited dataset (308–423 K): P1/P7.
- Augmentation code uses `noise_level=0.03`, whereas saved augmented files say `1Percent_Noise`: P2.
- Room dataset lacks explicit temperature feature: temperature assignment is an assumption requiring documentation.
- Row count is not the number of independently fabricated specimens; assess data source/experiment provenance in P1 and P8.

## P0 resolution

The count discrepancy is **recorded as unresolved**, not scientifically resolved. This satisfies the P0 requirement to document it accurately; it does **not** close the P1 provenance investigation.
