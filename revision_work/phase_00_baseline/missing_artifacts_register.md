# Evidence gaps / qualifications for P0 sign-off

1. **259 versus 256:** Three alleged manuscript points lack traceable row-level source evidence. This remains OPEN.
2. **Pre-audit pristine snapshot:** The earliest imported Git commit already includes `revision_work/`. We cannot distinguish earlier versions purely from this Git history.
3. **Manuscript/review PDFs:** Available privately but not committed to a public repository; distribution rights to be checked before publication.
4. **Source DOI and material labels:** Earlier audit contains inferred classifications. They are not independently validated by P0; proceed in P1.
5. **Full checksums:** `file_inventory.csv` starts with ten SHA-256s obtained from original raw bytes; remaining hashes and all 81 blob comparisons are performed by the GitHub Actions verifier. The CI artifact is the authoritative run-specific result.
6. **Physical experiment details:** Resin grades, cured specimens, calibration and measurement uncertainty are unresolved and scheduled for P8–P9.

## Boundary of P0

No edits to original XLSX, original IPYNB, theoretical DOCX, previous revision reports, models or data exports. P0 writes only new `revision_work/phase_00_baseline/` reports/scripts and a branch-scoped workflow.
