# P1.3 high temperature source compatibility: literature evidence and caveats

**P1.3 STATUS: SCREENING, NOT SOURCE RESOLUTION.**

## Source of reviewer statement
Submitted manuscript reference [29] is Huang et al., 2013, DOI 10.1002/adfm.201201824. Reviewer states the high-temperature Excel dataset is dominated by BNNT-POSS/epoxy.

## Evidence independently verified
- Wiley publisher article: https://advanced.onlinelibrary.wiley.com/doi/10.1002/adfm.201201824
- The publication indeed studies POSS-modified BNNT/epoxy.
- The abstract reports examples with 20 and 30 wt% BNNT loading and a 1360% conductivity enhancement at 30 wt%.
- Supplemental PDF is linked in Wiley, but the current download request returned HTTP 403. Claims about detailed supplemental measurement conditions **cannot be newly validated from that inaccessible file in this run**.
- The Excel column name is Vol; paper reports wt%. There is **no verified conversion** for any record.
- The 42 original high-temperature Excel observations span 308-423 K; paper abstract provides no 42-row matching table.

## Competing and unverified hypotheses
- Reviewer: high dataset mostly BNNT-POSS/epoxy.
- Legacy provenance script: 25/42 water-based nanofluids inferred from matrix conductivity.
- Independent source-neutral audit: 25/42 are in the numerical matrix conductivity band 0.60-0.68 W/(m K). This is only a numeric pattern, **not a fluid or matrix identity**.

Both provenance claims are currently unverified at the row level. Similar nanofluid literature (e.g. https://pmc.ncbi.nlm.nih.gov/articles/PMC5459072/) is contextual evidence only, not proof of the origins of individual Excel entries.

## Data protection
- No original rows changed.
- No material identity guesses assigned.
- No DOIs assigned to rows without matching values in a publication.
- No units converted without source evidence.
- No models retrained.

## Required source-matching evidence to complete P1.3
- Paper data table/figure identifying each temperature, formulation, filler, matrix and conductivity.
- Original author extraction/compilation sheet (especially helpful to resolve 259 vs 256).
- Source basis for filler loading: volume percent, weight percent, or fractional form.
- Any independent nanofluid study matching the actual numerical series.
- Traceable record-by-record evidence with DOI, source location, and match precision.

## Deliverable and verification
Source-neutral program: phase_01_provenance/high_temp/screen_high.py.
CI workflow: .github/workflows/p1-high-temperature-source-audit.yml (revision-work only; read-only permissions).
CI artifact: high_42_source_compatibility.csv, high_42_summary.json and P1_3_REPORT.md.
