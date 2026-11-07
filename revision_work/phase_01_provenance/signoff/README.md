# P1.6 — Final dataset-audit signoff gate

**Separate software test completion from scientific approval.**

This stage recomputes all 256 original records using the P1.5 evidence-gated builder, verifies unchanged source hashes, reconciles source-neutral P1.1/P1.3/P1.4 summaries and validates that all 40 numbered comments from the actual three reviewer reports are tracked.

Source evidence is missing: all 256 observations remain unverified, verified epoxy training partition is empty and high-temperature / manuscript count conflicts remain open. The workflow should **PASS** when it detects this truthfully, but the generated `scientific_provenance_signoff` must say **BLOCKED**. GitHub Actions green is not research signoff.

Usage:
```bash
python -m unittest discover -s revision_work/phase_01_provenance/signoff -p 'test_*.py' -v
python revision_work/phase_01_provenance/signoff/build_signoff.py --repo . --output ../p1_6_results
```

All outputs go outside checkout; `main` and original Excel files are immutable. Reviewer issue matrix is a **routing register**, not a claim to have satisfied each reviewer. Manuscript change register holds proposed edits, not author-approved revisions.

Scientific P1 gate can be approved only after DOI/table/figure-to-row proof, units and measurement types, high-temp conflict reconciliation, manuscript 259/256 correction, and rerun of the evidence-gated partitions.

Reviewer sources: `MEAS-D-26-20648-reviews.pdf` (reviewer 1 issues 1-17, reviewer 2 issues 1-17, reviewer 3 issues 1-6). Manuscript: `MEAS-D-26-20648.pdf`, Section 3 claims 259 originals, 302-427 K high range and 300 K nominal room temperature.
