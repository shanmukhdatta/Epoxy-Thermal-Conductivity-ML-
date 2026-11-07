# P1.5 — Evidence-gated clean-original data (execution instructions)

**Goal:** Build a reproducible 256-record partition **without guessing material identities** or changing the original experimental Excel files.

`build_evidence_gated_data.py` reruns P1.1 extraction on the three frozen source workbooks and verifies exact P0 SHA-256 hashes. It merges every source-unverified record with the (currently empty) reviewer-approved `source_assertions.csv`. Results are mutually exclusive `verified_epoxy_experimental`, `other_solid`, `liquid_systems`, `analytical_or_simulated`, `unknown_provenance` plus all-original, uncertainty and unit registers.

## Critical evidence rules
- A manuscript bibliography citation or numeric TC range is **not** a verified row-to-paper match.
- `source_assertions.csv` is intentionally **empty** until a person reviews the source paper, table/figure and actual row values.
- Assertions require DOI, HTTPS source, figure/table, source ID, actual material identities, measurement type, filler-loading basis, source numbers, reviewer, date and match method.
- Grade A requires exact published table numeric values; grade B requires documented figure digitization tolerance. Automated validation **does not itself certify** the scientific authenticity of a paper; a responsible researcher must verify it.
- Room temperature remains **blank in the original record**, even if a source-matched value later becomes available.
- **No wt% to vol% conversion** without densities, source evidence and a documented method.
- All original 256 rows stay included even if ineligible. The three conflicting-input target groups remain review flags.
- `verified_epoxy_experimental.csv` **will be empty** until source matching succeeds. No new ML training in P1.
- `main` never modified, CI has read-only content permissions.

## Run in GitHub Actions
```bash
python -m unittest discover -s revision_work/phase_01_provenance/clean -p 'test_*.py' -v
python revision_work/phase_01_provenance/clean/build_evidence_gated_data.py --repo . --assertions revision_work/phase_01_provenance/clean/source_assertions.csv --output /tmp/p1_clean_outputs
```

## P1.5 scientific limitations
This phase provides **computationally verified clean partition mechanics**, but cannot deliver source-verified epoxy observations while original paper-to-row evidence is missing. Never claim that "0 verified epoxy" means the source data has no epoxy or discard measurements based on paper-level references.

## Next: P1.6
Create a final data-integrity and reviewer action summary **with provisional scientific status**, and obtain the authors' original publication-extraction spreadsheet and primary figures/tables to complete the provenance source proof. The 259-versus-256 discrepancy and high-temp source disagreement remain open.
