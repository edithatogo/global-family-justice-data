# Pilot scope decision packet

**Decision date:** 2026-08-01  
**Decision authority:** repository owner  
**Decision:** proceed with a bounded pilot; do not make a global coverage claim

## Pilot cohort

The initial pilot candidates are `INT`, `AUS`, `USA-MN`, `BRA`, and `ZAF`.
These candidates have source-backed institution mappings and owner-adjudication
records, but remain conditional until edition-level coverage, rights treatment,
and source/matter mapping are complete.

Australia now has a controlled, checksummed 2024-25 FCFCOA annual-report
edition recorded in `data/seed/source_edition_template.csv`. It remains
metadata-only because the PDF's reuse terms have not been cleared.

The remaining jurisdictions stay in the approved global universe and continue
through the census cycle. They are excluded from pilot outputs until their
coverage and review gates pass.

## Release boundary

- No jurisdiction is promoted to ready by this decision.
- No observation is promoted to gold solely because an official landing page was
  found.
- Source-native counts remain descriptive until methods and mapping review pass.
- Rights-unknown material remains controlled and metadata-only.
- No outbound enquiry is authorised by this packet.

## Exit criteria

For each pilot candidate, agents must retain a reviewed institution map,
multilingual search log, current coverage assessment, source-edition receipt,
rights disposition, and owner adjudication. T1 adjudication must then resolve
clock, denominator, missingness, and ontology questions using real pilot
material before the v0.3 methods package is frozen.

If a criterion cannot be resolved, the affected series or jurisdiction is
quarantined rather than being treated as comparable.
