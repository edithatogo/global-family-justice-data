# Contributing

## Contributions welcomed

- new official sources;
- corrections to source metadata;
- jurisdiction profiles and institutional maps;
- translations of original definitions;
- ingestion or validation code;
- proposed indicator crosswalks;
- documented evidence about data gaps.

## Evidence standard

Every factual data contribution must include a source ID and exact provenance. For PDFs, give page and table. For spreadsheets, give sheet and cell/range. For dashboards and APIs, give filters or query parameters and retrieval date.

## Workflow

1. Open an issue using the new-source template.
2. Add or amend the relevant register row.
3. Preserve the original wording and add an English translation in a separate field.
4. Assign provisional quality and comparability grades.
5. Request a second review for any gold-layer observation.
6. Run `PYTHONPATH=src python -m gfjd.validate` before submitting.

## Prohibited contributions

Do not commit identifiable case records, sealed material, login credentials, API secrets, unlawfully redistributed documents or data whose publication could expose children or families.
