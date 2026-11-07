# High-temperature material/source conflict — OPEN

**What is known**
- Original file `High/High Temp.xlsx` has 42 data rows (P0 verified).
- Manuscript explicitly cites its ref [29], DOI `10.1002/adfm.201201824`, as the high-temperature source; reviewer says BNNT-POSS/epoxy predominates.
- Publisher abstract for [29] independently confirms POSS-treated BNNT in **epoxy**, with **20–30 wt%** loading examples. https://doi.org/10.1002/adfm.201201824
- Legacy audit code guesses "water" when numerical matrix conductivity falls in its chosen range; it does not source-match the record.
- Original Excel header `Vol` cannot establish wt% versus vol%; no conversion has been verified.

**What is not known**
- Which (if any) of the 42 original rows match Figure/Table/data from ref [29].
- Whether any rows are proven water-based nanofluids.
- Whether `Vol` represents source wt%, vol% or another transformed value for each record.
- Whether all 42 thermal-conductivity targets are laboratory observations.

**Required evidence before decisions**
- Access original paper + supplement/data tables.
- Verify sample IDs, exact loading basis and units, T and measured composite k.
- Record DOI, table/figure location and matching evidence for each row.
- Classify only after corroborated source match; otherwise keep "unknown_provenance".

**Decision status:** Neither the reviewer's domination claim nor old audit's "25 liquid" classification is accepted as row-level verified fact.
