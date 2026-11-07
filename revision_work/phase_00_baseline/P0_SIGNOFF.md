# P0 — Baseline freeze sign-off (2026-11-07)

**Disposition: COMPLETE for P0 scope, with explicitly documented scientific provenance exception.**

## Git traceability
- Repository: `shanmukhdatta/Epoxy-Thermal-Conductivity-ML-`.
- Original source baseline: `972671a33bba7a9531e92029602b3d2000eabd96`.
- Working branch: `revision-work`; `main` remains pinned to the unmodified baseline.
- P0 implementation commit: `a3e2452e5d021538db814e72852a9ecacb6b0e11`.
- Automatic read-only verification: [GitHub Actions run #42354445961](https://github.com/shanmukhdatta/Epoxy-Thermal-Conductivity-ML-/actions/runs/42354445961) — **SUCCESS**.

## Independently verified in GitHub Actions

| P0 check | Result |
|---|---|
| Original tracked files | **81 / 81** match pinned Git blob hash, file size, and any pre-recorded SHA-256 |
| Full SHA-256 manifest | **81 checksums computed from checkout bytes**; uploaded as CI artifact |
| Original six-workbook verification | **3 originals:** cryogenic 54, room 160, high 42 = **256** data rows |
| Augmented workbooks | **162 + 480 + 126 = 768** rows |
| Existing test suite | **5 / 5 tests passed** |
| Write scope | Only P0 documentation/CI files on `revision-work`; source data and `main` unchanged |

The CI artifact is named `p0-integrity-evidence` (artifact ID `13567266231`) and contains:
`sha256_manifest_full.txt`, `file_integrity_verification.csv`, `verified_workbook_counts.json`, and `P0_CI_VERIFICATION_REPORT.md`. Artifact retention is **30 days**; preserve a local copy for durable secondary archival. SHA-256 of the exact `sha256_manifest_full.txt` CI artifact: `38459edf2a03cb29d0e538d639d3bad5ef1e069c31064ebaf6b4efed4cdb05ea`.

## Scientific exception — NOT RESOLVED

The submitted `MEAS-D-26-20648.pdf`, page 6, says **259** original observations, whereas the six independently counted workbooks contain **256** original and **768** augmented rows. The three-record difference has **no verified record-level origin**. The presence of three `.docx` theoretical comparisons does *not* establish that they were three additional training observations. This discrepancy is registered for P1 source tracing and P11 manuscript correction after author confirmation; no records were silently changed.

## Scope and limitations

- This is **file integrity and baseline preservation**, not independent certification of experimental provenance, leakage-free generalization, measurement uncertainty, or the physical validity of the dataset. Those are later phases.
- The original import commit already included prior `revision_work/` outputs; Git history alone does not provide a pristine pre-audit manuscript snapshot.
- Manuscript and reviewer PDFs are private archived source artifacts; only their filenames and hashes are documented in `private_source_document_manifest.csv`; contents are deliberately not uploaded into this public fork.

**P1 handoff:** confirm study DOI and material identities for all 256 rows, investigate the missing three manuscript observations, and categorize unsupported/non-epoxy sources before any new training.
