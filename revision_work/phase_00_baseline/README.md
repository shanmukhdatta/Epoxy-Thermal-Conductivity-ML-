# P0 — Freeze original research and establish the baseline

**Branch:** `revision-work` (research revision work only; do not merge to `main` as part of P0).  
**Baseline commit:** `972671a33bba7a9531e92029602b3d2000eabd96` (initial imported research, containing earlier revision work).  
**Source:** shanmukhdatta/Epoxy-Thermal-Conductivity-ML- (fork of `Pradeep-gif-hub/Research_Paper_TC`).  
**Scope:** Inventory, immutable baseline checks, and documentation—not model retraining or dataset rewriting.

## Primary files frozen at baseline

- Three original Excel workbooks and three 3× augmented Excel workbooks
- Twelve training notebooks and one data-augmentation notebook
- Three theoretical comparison DOCX files
- Existing `revision_work/` audit scripts, generated models, data exports, reports and plots
- **81 total tracked blobs** in original commit, explicitly enumerated in `file_inventory.csv`.

The PDF manuscript `MEAS-D-26-20648.pdf`, the reviewer PDF and the separate revision-planning document have been retained as **private source materials**. They are **not** included in the public repository. Do not publish those files without checking distribution rights.

## What is established vs. what remains disputed

- Existing clean CSVs contain 54 cryogenic, 160 room-temperature and 42 high-temperature rows = 256.
- Submitted manuscript (PDF page 6) states 259 original points.
- Three additional observations cannot yet be mapped to source rows. Prior audit's 3-DOCX hypothesis is not confirmed.
- Augmentation notebook code references 3% while saved augmented files are labeled 1%; investigate in P2.
- Some source identities in earlier audit are inferred and require P1 verification.
- The original Git commit already includes prior revision artifacts; it is **not proof of a pristine pre-audit submission state**.

## Automated verification

Push to `revision-work` to run read-only GitHub Actions:
`.github/workflows/revision-work-tests.yml`.

`verify_checkout.py` checks the 81 original tracked files against frozen Git blob hashes and available original-byte SHA-256 values, calculates SHA-256 for every original file, counts all six Excel workbooks independently, and checks the three derived CSV counts. It writes its evidence **outside the checkout**, and GitHub Actions uploads these artifacts. The existing unit test suite runs separately. Workflow permissions: `contents: read`.

Local equivalent:

```bash
python revision_work/phase_00_baseline/verify_checkout.py --repo . --output ../p0_verification
python -m unittest discover -s revision_work/tests -p 'test_*.py' -v
```

**Acceptance criteria:** 81/81 original files match, all six workbook counts verified, existing tests pass, original data unchanged, discrepancy explicitly registered. Even when complete, the *cause* of the 259–256 disagreement remains open pending author-side/source evidence.
