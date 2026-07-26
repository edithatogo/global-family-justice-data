# Contributing

## Contributions welcomed

- new or superseded official sources;
- corrections to source, jurisdiction, evidence, or observation metadata;
- jurisdiction profiles and institutional maps;
- original-language definitions and reviewed translations;
- acquisition, transformation, validation, or publication code;
- indicator, outcome-domain, and comparability proposals;
- documented negative findings and inaccessible-source evidence;
- accessibility, documentation, and reproducibility improvements.

## Evidence standard

Every factual data contribution must include a source ID and exact provenance:

- PDF: page, table, figure, or paragraph;
- spreadsheet: file version, sheet, and cell/range;
- HTML: page section/table and retrieval date;
- dashboard: filters, date, and exported view or query details;
- API: endpoint, parameters, date, and response/source version;
- manual correspondence: sender role, date, status, and publication permission.

Original wording must be retained. English translation and harmonised terms belong in separate fields.

## Workflow

1. Open the appropriate source, correction, or methods issue.
2. Add or amend the relevant register or pipeline.
3. Record source rights, retrieval, and provenance.
4. Add or update tests for changed logic.
5. Run `make manifest-update`, then `make check`.
6. Update documentation, migration notes, and changelog when user-visible.
7. Request independent second review for gold-layer data and material methods changes.
8. Obtain methods approval for semantic or comparability changes.

## Review rules

- At least one independent reviewer is required for ordinary changes.
- Gold data require a reviewer who did not perform the extraction/transformation.
- Breaking schema or ontology changes require methods review and migration documentation.
- Security/privacy-sensitive changes require the designated specialist review.
- Large generated files must be produced by the release pipeline, not hand-edited.

## Prohibited contributions

Do not commit:

- identifiable case, party, child, or family records;
- sealed, protected, or unlawfully obtained material;
- login credentials, tokens, API keys, or private endpoints;
- source files whose redistribution is not permitted;
- malicious code or content designed to re-identify people;
- generated gold data edited without lineage;
- unsupported country rankings or causal claims.

Potential security or privacy issues must follow `SECURITY.md` and must not be opened publicly.

## Contributor conduct

Contributors must engage respectfully across legal systems, languages, professions, and lived experiences. Critique evidence and methods, not people or jurisdictions. Do not disclose personal family-court experiences without explicit, informed choice and appropriate safeguards.
