# Operational census inputs

This directory is the controlled landing area for reviewed T2 census records.
The repository ships header-only files so an autonomous run fails closed rather
than treating seed-register notes as empirical evidence.

Populate records only from the approved source-discovery protocol and preserve
the referenced evidence. `gfjd census build` reports missing, unreviewed, stale,
and incomplete records; it never upgrades them.

`institution_map.csv` is the operational institutional-map register. The
`review_ledger.csv` file records first review, second review, adjudication, and
independent-assurance dispositions for the pilot. Both are schema-validated and
may remain empty while the evidence packet is being prepared.
