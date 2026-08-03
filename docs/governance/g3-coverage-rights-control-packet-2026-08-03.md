# G3 coverage, rights and enquiry control packet — 2026-08-03

## Current census result

The deterministic census build was run against the current jurisdiction and
source registers. It produced:

- 23 jurisdiction rows;
- 0 ready jurisdictions;
- 91 explicit remediation gaps;
- coverage matrix, gaps, search-review and remediation queues;
- verified output under `build/g3-census-current/`.

This is a transparent coverage state, not a claim that the global census is
complete.

## Bound controls

- `data/census/search_log.csv` retains search, language, date and access states.
- `docs/methods/census-second-review-audit-2026-08-02.md` defines second-review
  routing for negative and inaccessible findings.
- `docs/methods/direct-enquiries/closure-audit-2026-08-02.md` records answered
  and no-response closure rules.
- `docs/methods/exact-edition-rights-screening-2026-08-03.md` and the source
  rights queue preserve metadata-only/quarantine outcomes.
- `docs/methods/t3-preservation-monitoring-control-evidence-2026-08-03.md`
  records manifest and offline monitoring controls.

## Remaining G3 evidence boundaries

The packet does not create local/regional reviewer identities, multilingual
human verification, direct-enquiry responses, exact-edition permissions,
independent custody or G3 authority acceptance. Unsupported jurisdictions and
sources remain explicitly incomplete, inaccessible, metadata-only or
quarantined.
