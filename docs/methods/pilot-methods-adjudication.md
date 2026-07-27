# Pilot methods adjudication

This procedure records how real pilot evidence is used to resolve material
questions about ontology, clocks, denominators and missingness. It is a
repository procedure, not pilot evidence and not a methods approval.

## Inputs

For each disputed measure, retain the source edition, preservation checksum,
extraction and second-review records, the original-language definition, and the
observation semantic signature. Generate a comparability audit from the exact
pilot input set:

```bash
gfjd comparability build --input 'data/gold/pilot/**/*.csv' --output build/comparability
gfjd comparability verify --output build/comparability
```

The audit's `comparability-issues.csv` is a review queue. In particular,
`TIMELINESS_CLOCK_UNSPECIFIED`, `DECLARED_TIER_CONFLICT` and
`SERIES_FRAGMENTED_BY_DEFINITION` require a documented methods disposition
before any pooling or public comparison. An exact-signature candidate is never
approval to pool, rank, or infer equivalence.

## Required disposition record

Use the review ledger with `review_type=adjudication`. Its evidence path must
refer to immutable, access-controlled source and review material; do not put
confidential source material in public repository history. Record:

- the question and the affected observation or series IDs;
- the original definition and, where needed, an attributed translation;
- the clock start/end, statistic, count unit, denominator, cohort and missingness
  treatment considered;
- the decision: retain, transform, split, downgrade to descriptive-only,
  quarantine, or exclude;
- the impact on comparability tier, release eligibility and any series break;
- the accountable methods reviewer and an independent reviewer; and
- the immutable evidence reference and exact audit input/output hashes.

No automated command can create an adjudication, accept an evidence record or
advance G2. A real methods lead and independent reviewer must make those
decisions against the preserved pilot material.

## Completion boundary

`WI-G2-05` may move from repository implementation to accepted only when a
genuine, checksum-bound pilot adjudication set has been independently reviewed
and the applicable gate controls are satisfied. Templates, synthetic fixtures,
and a green comparability audit remain implementation support only.
