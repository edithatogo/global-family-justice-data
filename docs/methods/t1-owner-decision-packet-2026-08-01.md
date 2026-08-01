# T1 owner decision packet

**Status:** prepared; no adjudication or methods freeze has been asserted  
**Decision authority:** repository owner  
**Independent review:** required after owner decisions

## Purpose

This packet turns the five-candidate pilot evidence into a bounded methods
decision queue. It is not itself a methods approval. The queue is recorded in
`data/methods/pilot_adjudication_register.csv` and retains source-edition,
access, and rights limitations.

## Recommended default decisions

1. Retain source-native categories and counts as descriptive-only until a matter
   mapping is independently reviewed.
2. Quarantine any clearance, duration, rate, or timeliness measure whose clock,
   denominator, cohort, or snapshot date is not explicit.
3. Exclude Minnesota edition-level measures until a reproducible dashboard export
   or accessible report is available; the observed 403 is an access boundary,
   not evidence of absence.
4. Do not pool jurisdictions merely because labels appear similar. Require an
   exact semantic signature and an approved comparability tier.
5. Preserve static-report versus dynamic-dashboard distinctions as separate
   series identities.

## Owner decisions required

For each `ADJQ-*` row, the owner should select one of: retain, transform, split,
downgrade to descriptive-only, quarantine, or exclude. The decision must cite
the source edition, original definition, denominator/clock treatment, impacted
series, and release consequence.

After owner decisions, an independent analyst-agent review may verify the
record's checksum, schema, and internal consistency. That technical review does
not substitute for an external methods reviewer or formal G2 acceptance.

## Freeze boundary

The v0.3 methods package must not be frozen as accepted until the owner
decisions, real pilot evidence, independent review, and change-control digest
are all recorded. Unresolved questions remain quarantined.
