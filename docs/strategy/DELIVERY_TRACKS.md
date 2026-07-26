# Delivery track charters

## How tracks are managed

Each track must have one accountable owner, at least one deputy, measurable quarterly outcomes, dependencies, risks, and evidence for the v1 release gate. Track completion is based on accepted evidence, not percentage-complete estimates.

## T1 — Governance and institutional home

**Objective:** make the project independent, accountable, and durable.

v1 deliverables:

- charter, terms of reference, and decision rights;
- steering, methods, data-operations, ethics/lived-experience, security, and release roles;
- conflicts and funding register;
- institutional host, repository ownership, domain, preservation, and succession arrangements;
- policy for court/jurisdiction factual review without editorial veto;
- public decision and dispute log.

Key dependency: must precede feature freeze and all final legal/release decisions.

## T2 — Scope, ontology, and methods

**Objective:** define exactly what is counted, compared, and excluded.

v1 deliverables:

- jurisdiction universe and subnational inclusion rules;
- matter taxonomy, institution taxonomy, procedural-stage vocabulary, indicator dictionary, and outcome domains;
- source-quality and comparability frameworks;
- rules for duration clocks, counts, rates, cohorts, suppression, and breaks in series;
- versioning, deprecation, and migration policy;
- methods handbook and worked comparison examples.

Key dependency: T3–T6 cannot scale safely until v1 candidate semantics are stable.

## T3 — Global jurisdiction and source census

**Objective:** produce an auditable map of what every in-scope system publishes.

v1 deliverables:

- jurisdiction and responsible-institution records;
- multilingual search logs;
- official source register and source-status history;
- negative findings and inaccessible-source records;
- direct-enquiry register where public information is insufficient;
- data-availability atlas and coverage metrics.

Key control: every negative finding receives independent second review.

## T4 — Acquisition, preservation, and provenance

**Objective:** make source retrieval lawful, repeatable, and resilient to change.

v1 deliverables:

- source manifests, retrieval recipes, checksums, and source-version records;
- connectors for stable APIs/files and controlled procedures for PDFs/dashboards;
- object-storage and archival policy;
- source-change and broken-link detection;
- rights/redistribution decision for every acquired artifact;
- exact page/table/cell/query/filter provenance.

Key control: source files are not committed merely because they are publicly viewable.

## T5 — Extraction, harmonisation, and outcomes evidence

**Objective:** transform source reporting into useful data without erasing meaning.

v1 deliverables:

- bronze, silver, and gold pipelines;
- manual extraction protocol and review forms;
- case-type, measure, stage, unit, and institution crosswalks;
- transformation registry;
- outcome-evidence catalogue covering administrative reports, surveys, evaluations, cohorts, qualitative work, and linked studies;
- release tables and jurisdiction profiles.

Key control: gold contains only approved Tier 1 or Tier 2 comparisons; other evidence remains discoverable but clearly separated.

## T6 — Scientific and data quality assurance

**Objective:** detect errors, quantify reliability, and prevent misleading comparison.

v1 deliverables:

- validation rule catalogue;
- automated structural, referential, temporal, numerical, lineage, and semantic checks;
- double-review policy and reviewer training;
- stratified audit design and adjudication process;
- cross-source reconciliation and anomaly review;
- public quality dashboard/report;
- defect severity and release-blocking rules.

Key control: quality grades apply to observations and evidence records, not broad reputational judgments about countries.

## T7 — Engineering, architecture, and reproducibility

**Objective:** operate the repository as a tested data product.

v1 deliverables:

- documented architecture and supported environments;
- schema registry and migrations;
- continuous integration, tests, linting, type checking, packaging, and manifest verification;
- deterministic or well-characterised release builds;
- release metadata, checksums, and software/data bill of materials;
- independent clean-room build;
- performance and scale tests for release datasets.

Key control: manual edits to generated gold outputs are prohibited.

## T8 — Security, privacy, legal, and ethics

**Objective:** prevent harm, rights violations, and compromise of the project.

v1 deliverables:

- threat model and security policy;
- dependency, code, and secret scanning;
- aggregate-only public-data rule and disclosure controls;
- source-rights register and licences;
- vulnerability, incident, takedown, and legal-challenge processes;
- ethics boundary for restricted linked-data studies;
- training for maintainers and reviewers.

Key control: no public release of person-level court, child, or family records.

## T9 — Product, documentation, and accessibility

**Objective:** make the project usable without sacrificing nuance.

v1 deliverables:

- stable downloads and release catalogue;
- public data-availability atlas;
- searchable source and evidence catalogues;
- jurisdiction profiles;
- methods, dictionary, citation, licensing, limitations, and examples;
- accessible visualisations with downloadable underlying data;
- user research and usability fixes.

Key control: user interfaces must expose definitions and comparison warnings at the point of use.

## T10 — Languages, jurisdiction partnerships, and community

**Objective:** avoid English-language and high-income-country bias while building trusted review relationships.

v1 deliverables:

- regional and language coverage plan;
- paid local correspondents and translation review;
- contributor onboarding, code of conduct, and review pathway;
- factual verification process for jurisdictions;
- public issue templates for sources, corrections, translations, and methods proposals;
- disagreement and minority-view documentation.

Key control: automated translation alone cannot close a jurisdiction as “searched complete”.

## T11 — Operations, releases, support, and resilience

**Objective:** make releases and corrections routine rather than heroic.

v1 deliverables:

- release calendar and authority;
- operational runbook and service targets;
- source freshness and pipeline monitoring;
- backups, restore, rollback, and disaster-recovery tests;
- correction, retraction, and takedown workflow;
- support channels and escalation;
- post-release review and metrics.

Key control: at least two people must be able to perform every critical release action.

## T12 — Sustainability and impact evaluation

**Objective:** keep the product alive and assess whether it improves evidence and reporting.

v1 deliverables:

- multi-cycle maintenance budget and staffing model;
- institutional preservation and succession plan;
- funder-diversification and independence safeguards;
- measures of geographic coverage, data freshness, reuse, citations, corrections, and policy/research uptake;
- v1 evaluation and prioritised v1.1/v2 backlog.

Key control: success is not measured only by website traffic or number of rows.
