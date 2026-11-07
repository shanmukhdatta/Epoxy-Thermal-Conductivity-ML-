# P1.1 — Executed source-neutral numeric audit (2026-11-07)

**Status:** P1.1 numeric audit **PASSED**; P1 as a whole is **NOT COMPLETE** because none of the 256 original records have an independently verified paper-to-row source assignment.

## Verifiable execution

- Source branch: `revision-work`; `main` not modified.
- Implementation commit: [c529bea611e59bc33064ad6703b4245f4ac67578](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/commit/c529bea611e59bc33064ad6703b4245f4ac67578)
- [P1.1 CI run 42360296828](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42360296828): **SUCCESS**, three newly added unit tests passed.
- [P0 regression CI run 42360296890](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42360296890): **SUCCESS**.
- Raw evidence: [download P1 CI artifact](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42360296828/artifacts/13569570436) (GitHub artifact is retained for 30 days).
- Code: `revision_work/phase_01_provenance/audit_originals.py`.
- Original Excel workbooks preserved unchanged.

## Computed directly from three ORIGINAL XLSX files

| Regime | Source rows | Matrix TC range | Filler TC range | Composite TC range | Recorded T range |
|---|---:|---:|---:|---:|---:|
| Cryogenic | 54 | 0.01–0.38 | 0.1–23900 | 0.05–1.0 | 2–120 K |
| Room | 160 | 0.05–0.92 | 0.165–4320 | 0.107–2.0 | **Not present in original workbook** |
| High | 42 | 0.20–0.68 | 2.93–400 | 0.65–1.9 | 308–423 K |
| **Total** | **256** | | | | |

Thermal conductivity values in W/(m·K) per manuscript dataset schema. Loading values retained **as recorded**, without assuming percent versus fraction/weight basis.

## Evidence requiring review

1. **3 conflicting-target feature groups / 6 rows** in the original Room dataset:
   - `ROO_048` and `ROO_101`: same numeric inputs (k_m=0.2, k_f=3000, Vol≈0.58), conflicting target k_c=0.38 vs 0.85.
   - `ROO_060` and `ROO_125`: same numeric inputs (k_m=0.2, k_f=3000, Vol≈1.16), conflicting k_c=0.45 vs 1.27.
   - `ROO_087` and `ROO_090`: same numeric inputs (k_m=0.6, k_f=401, Vol=1), conflicting k_c=0.69 vs 0.71.
   Different experimental conditions could explain them; **not automatically errors**. Source study identity, direction, replicate status and dispersion should be checked.
2. **0 exact complete-record duplicates** detected within the corresponding temperature regimes.
3. **30 rows** have loading values ≤1, where unit/scale interpretation needs special review (20 Room, 10 High).
4. **4 rows** have recorded composite k outside the numerical range of the two listed constituents, warranting source review (CRY_015, ROO_000, ROO_001, ROO_002). This is a *screening flag*, not a basis for automatic exclusion.
5. **160 Room rows have no recorded temperature**. Do not silently fill 298.15 or 300 K in the source ledger.
6. **0 of 256 rows are DOI/source verified.** This is an honest stage-1 status. No rows have been assigned confirmed matrix identity, filler identity, measurement type or verified epoxy eligibility.
7. **42 high-temperature rows** remain unclassified. The legacy audit's "water" labels and the reviewer's "BNNT-POSS epoxy" assumption are both unverified at row level.
8. No original numerical values were overwritten, deduplicated, excluded, converted or "corrected".

## Next execution stages

- **P1.2**: Acquire/verify manuscript references [19]–[29] and their source data; establish DOI/source table or figure per row.
- **P1.3**: Prioritize the 42 high-temperature rows. Confirm or refute BNNT-POSS/epoxy versus water-nanofluid claims **from source-matched data**. Ref [29] publisher abstract describes **weight-percent** filler, while Excel calls the field `Vol`. Check loading basis before trusting it.
- **P1.4**: Verify 54 cryogenic + 160 room rows.
- **P1.5**: Adjudicate duplicates, conflicting outputs, units and compatibility; generate *evidence-supported* clean partitions.
- **P1.6**: Publish detailed P1 report, reviewer/manuscript corrections register, and test full partition reconciliation.

Do not declare P1 scientifically complete while provenance remains unverified.
