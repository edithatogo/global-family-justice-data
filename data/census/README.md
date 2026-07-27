# Operational census inputs

This directory is the controlled landing area for reviewed T2 census records.
The repository ships header-only files so an autonomous run fails closed rather
than treating seed-register notes as empirical evidence.

Populate records only from the approved source-discovery protocol and preserve
the referenced evidence. `gfjd census build` reports missing, unreviewed, stale,
and incomplete records; it never upgrades them.
