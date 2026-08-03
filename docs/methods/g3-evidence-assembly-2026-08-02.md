# G3 source, coverage, rights and enquiry evidence assembly — 2026-08-02

## Current evidence run

The G3 census build and verification completed successfully:

```bash
PYTHONPATH=src uv run python -m gfjd census build --output build/census-g3
PYTHONPATH=src uv run python -m gfjd census verify --output build/census-g3
```

The generated readiness pack contains 23 jurisdictions, 0 ready jurisdictions
and 91 explicit remediation gaps. It is the authoritative current queue; no
jurisdiction was promoted by this run.

## Evidence assembled

- `data/census/search_log.csv`: 233 recorded search rows, including languages,
  access outcomes and evidence paths.
- `data/census/institution_map.csv`: 23 source-backed institutional anchors.
- `data/census/coverage_assessment.csv`: 23 bounded assessments, all retaining
  `partial` coverage and `not_assessed` negative-finding state.
- `data/census/review_ledger.csv`: first reviews, owner pilot dispositions,
  response reviews and search-receipt audit entries.
- `data/raw/archive_inventory.csv`: edition-level SHA-256 and rights routing.
- `data/census/direct_enquiry_register.csv`: 23 enquiry records with sent,
  answered or planned state and evidence paths.

## Fail-closed findings

The Sweden response and workbook are recorded as substantive source evidence,
but reuse terms and several matter mappings remain unresolved. England and
Wales has an edition-bound open-licence archive, but coverage, taxonomy and
independent review remain incomplete. Australia, Brazil and South Africa local
artifacts remain metadata-only because exact-edition redistribution rights are
not resolved. Several enquiries are still awaiting response windows or require
owner-approved authenticated/phone/postal routes; no follow-up was sent.

Agent validation confirms record and receipt consistency only. It does not
substitute for local/regional verification, a second human or accountable
rights authority. Consequently G3 remains evidence-incomplete and no source
or jurisdiction is release-ready.
