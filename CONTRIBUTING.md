# Contributing

## Contributions welcomed

- new or updated official sources;
- corrections to source metadata or released observations;
- jurisdiction profiles and institutional maps;
- original-language definitions and reviewed translations;
- acquisition, validation and release code;
- proposed indicator crosswalks and methods evidence;
- documented negative findings and inaccessible-source evidence;
- accessibility, documentation and reproducibility improvements.

## Evidence standard

Every factual data contribution must include a source ID and exact provenance:

- PDF: page, table/figure and row/column where possible;
- spreadsheet: sheet and cell/range;
- HTML: table/section and retrieval date;
- dashboard/API: filters/query parameters, endpoint/view and retrieval date;
- narrative report: precise section/page and original wording.

Preserve original labels and definitions. Add English translation and harmonised mapping as separate fields.

## Workflow

1. Open the appropriate issue or correction record.
2. Add/amend the relevant register or extraction.
3. Include source edition, rights status, retrieval metadata and exact locator.
4. Run local validation and tests.
5. Request review from a different contributor.
6. Resolve or record mapping/translation disagreement.
7. Gold-layer promotion requires an authorised second reviewer and all quality gates.
8. Released values are corrected through a new version, never by silently replacing history.

Run:

```bash
make check
```

## Change expectations

- Small, reviewable pull requests are preferred.
- Method/schema changes include an impact note and migration implications.
- Breaking public-contract changes are allowed during 0.x but must be documented.
- From 1.0 onward, follow `docs/standards/versioning-and-deprecation.md`.
- New connectors include fixtures, failure handling and ownership/runbook notes.
- New indicators include definition, unit, clock/cohort/denominator rules and intended use.

## Prohibited contributions

Do not commit:

- identifiable or linkable case records;
- sealed or protected material;
- credentials, tokens, cookies or private keys;
- unlawfully redistributed documents;
- data that could expose children or families;
- values without exact provenance;
- mappings that erase original legal/source wording.

Sensitive security or privacy issues must follow `SECURITY.md`, not a public issue.
