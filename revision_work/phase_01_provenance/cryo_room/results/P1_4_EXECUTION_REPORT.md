# P1.4 — executed and evidence-reviewed (2026-11-07)

**Status:** Numeric audit and study-level bibliography review **COMPLETE** for cryogenic/room sources; **row-to-publication verification still OPEN**. Do **not** label P1 source provenance as complete.

## GitHub Actions evidence
- Code commit [867a1b906698e6fd24a491f594dae797d9eb23bf](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/commit/867a1b906698e6fd24a491f594dae797d9eb23bf)
- [P1.4 GitHub Actions run 42362093453](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362093453): **SUCCESS**; 6/6 new tests passed.
- [Full 214-row audit artifact](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42362093453/artifacts/13569344275) holds 6 generated files; GitHub retains CI artifacts only for 30 days.
- Commit-friendly aggregate results in `results/p1_4_summary.json` and `results/same_inputs_conflict_review.csv`, with exact source CSV SHA-256 manifest for reproducibility.
- P0 and existing P1 regression tests run separately and must remain green.

## Exact numeric results directly from original Excel workbooks
- Cryogenic: **54** rows; T = **2 to 120 K**; 13 distinct source T values.
- Room: **160** rows; there is **no T column** in the original workbook.
- All **214** original rows preserved; all **214** unverified per-row paper DOI/material identities; **zero verified experimental source matches**.
- Room: **20 loading entries at or below numeric 1** warrant percent/fraction basis review; not errors.
- Room: **3 repeated numeric feature groups**, each with differing targets, 6 original records. Preserve until source conditions/measurement direction are checked.
- Original workbook SHA-256: cryo `51f5e924c948854a0cf1474617769b2597a7f54f29e5a4a5937b3760bfb6bd4b`, room `1bdee4c5ec93acd88300f6d2925b74793b5a6197efebcc230c16c42aeef8da7c`.

## Manuscript study-level source incompatibilities — not records
The first-party/publisher source summaries in `paper_level_evidence.csv` show:
- [19] all-glass fibers, NOT epoxy.
- [20] quartz/CaBr2 transparent soil, NOT epoxy; its tested and modeled **5–45°C** scope is outside this cryogenic file's 2–120 K.
- [21] Kevlar cord, NOT epoxy; studied 0.1–2.5 K, only a narrow overlap with cryogenic regime; check **W/cm/K versus W/m/K**.
- [22] actual epoxy-containing T800 carbon-fiber laminate; **longitudinal vs transverse** conductivity is relevant, not represented by the 4 numeric features.
- [23] negative-expansion nanoparticles in epoxy at 77–300 K, candidate epoxy-compatible study.
- [24] macro-porous graphite, NOT epoxy; title high-temperature while listed in room bibliography.
- [25] diamond/graphene reinforced **copper-matrix** composites, NOT epoxy.
- [26] Cu-coated **TPU**, NOT epoxy.
- [27] BN+AlN filled **UHMWPE**, NOT epoxy; source uses wt% in examples.
- [28] BN+MWCNT filled **PPS**, NOT epoxy.

**No specific Excel observation has been assigned any of these DOI or material labels**. Individual raw-source references might differ from manuscript citations and must be matched using original papers, supplementary figures/tables and author extraction records.

## Next steps: P1.5 evidence-led reconciliation
- Obtain primary papers/supplements and original dataset extraction ledger (if held by authors).
- Match raw row values, source temperature, loading basis and measurement type to each source figure/table.
- Place only **documented** epoxy experimental observations in verified_epoxy; keep other systems and unknowns separate.
- Record explicit unit conversions with density/measurement conditions and preserve original data.
- Investigate manuscript 259 claimed original vs actual 256 original.
- Re-run CI and create reviewer-specific change register; **no retraining until reliable partitions exist**.
