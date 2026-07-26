# Project plan: from international source census to stable v1.0

## 1. Aim

Build a durable international public data product that inventories family-justice reporting, harmonises defensible process and administrative measures, catalogues child and family outcomes evidence, and exposes gaps without overstating comparability.

The project distinguishes five evidence domains:

- **process and performance:** volumes, pending caseload, clearance, hearing waits, case duration, adjournments, legal representation, mediation, and compliance with standards;
- **court and administrative outputs:** modes of disposal, orders, appeals, enforcement, reapplications, and subsequent administrative events;
- **user and access outcomes:** perceived fairness, comprehension, participation, cost, accessibility, legal need, and service experience;
- **child and family outcomes:** safety, stability, reunification, placement, compliance, wellbeing, family functioning, and equity;
- **system inputs and context:** institutions, jurisdiction, staffing, expenditure, legal aid, procedures, reforms, statutory targets, and socioeconomic context.

Routine court statistics, evaluations, surveys, and linked research are represented as different evidence types. The project will not treat faster processing as proof of better child or family outcomes.

## 2. Product boundary

### 2.1 Unit of coverage

The project covers family-justice functions, regardless of the institution’s name. The jurisdiction model begins with sovereign states and adds subnational or devolved systems whenever they control material parts of family justice.

The final jurisdiction universe must explicitly classify:

- national systems;
- states, provinces, territories, cantons, or equivalent autonomous systems;
- supranational and cross-national reporting bodies;
- customary, religious, administrative, or specialist systems where these are material and publicly reportable;
- excluded territories or systems, with reasons.

### 2.2 Core matter types

1. divorce, dissolution, separation, and nullity;
2. private-law parenting, custody, residence, contact, and parental responsibility;
3. public-law child protection, care, dependency, and removal proceedings;
4. civil family-violence and protection-order proceedings;
5. child and spousal maintenance or support;
6. property and financial relief following relationship breakdown;
7. adoption, guardianship, kinship care, and related permanence proceedings;
8. parentage and selected assisted-reproduction matters;
9. international child abduction, access, recognition, and cross-border child protection.

Juvenile criminal justice, probate, criminal family violence, and general civil matters are adjacent domains. They are included only where reporting is inseparable or the project publishes a clearly bounded adjacent product.

### 2.3 Time horizon

- Pilot extraction: most recent five reporting years, where available.
- Preferred historical coverage: 2010 onward when definitions and sources permit.
- Breaks in series are preserved; historical series are not back-cast through legal or methodological changes without explicit evidence.
- Source-census records may include older foundational reporting where it remains relevant.

### 2.4 Definition of global completeness

The project does not promise that every desired outcome has been measured. A defensible completeness claim is:

> Every in-scope jurisdiction has been searched under a documented multilingual protocol; every located in-scope public source has been catalogued; absent, inaccessible, unpublished, and non-comparable measures have been explicitly coded; and every extracted observation or evidence record retains traceable provenance.

Completeness therefore applies first to the **search and source census**, not to the existence of comparable numeric data.

## 3. v1.0 product contract

Version 1.0 is a stable release bundle containing:

1. a global jurisdiction and institutional register;
2. a multilingual source census with status history and negative findings;
3. a versioned matter, stage, and indicator ontology;
4. an outcomes-evidence catalogue;
5. source-native bronze extracts or lawful source manifests;
6. normalised silver observations with source meaning retained;
7. a bounded gold dataset of approved Tier 1 and Tier 2 comparisons;
8. jurisdiction profiles and a global reporting-availability atlas;
9. methods, quality, coverage, limitations, governance, and licensing documentation;
10. reproducible CSV, Parquet, and DuckDB release artifacts;
11. checksums, build metadata, citation information, and archival preservation;
12. operating ownership for monitoring, support, corrections, backups, restoration, and future releases.

The binding release criteria are in `docs/strategy/V1_RELEASE_CRITERIA.md`.

### v1 non-goals

- identifiable case, party, child, or family records in the public repository;
- a single international performance score or country ranking;
- direct comparison of incompatible clocks, cohorts, units, or case types;
- causal inference from descriptive court statistics;
- redistribution of third-party source files without permission;
- real-time coverage of every court system;
- a public API unless the host can operate it under the same stability and support standards as the downloadable release.

## 4. Delivery model

The programme is organised as twelve persistent delivery tracks rather than short-lived work packages. Track charters are in `docs/strategy/DELIVERY_TRACKS.md`.

| Track | Focus | Accountable v1 result |
|---|---|---|
| T1 | Governance and institutional home | Durable authority, independence, decision rights, succession |
| T2 | Scope, ontology, and methods | Frozen v1 semantics and compatibility policy |
| T3 | Global jurisdiction and source census | Complete auditable search coverage |
| T4 | Acquisition, preservation, provenance | Repeatable lawful retrieval and source versioning |
| T5 | Extraction, harmonisation, outcomes evidence | Traceable bronze/silver/gold and evidence catalogue |
| T6 | Scientific and data quality | Quantified reliability and release-blocking QA |
| T7 | Engineering and reproducibility | Tested deterministic release system |
| T8 | Security, privacy, legal, ethics | Harm, rights, and supply-chain controls |
| T9 | Product, documentation, accessibility | Usable public release with definitions at point of use |
| T10 | Languages, partnerships, community | Regionally legitimate multilingual search and review |
| T11 | Operations, releases, support, resilience | Tested maintenance, correction, restore, and rollback |
| T12 | Sustainability and evaluation | Multi-cycle resources, preservation, and impact measures |

Each track must maintain:

- an accountable owner and deputy;
- deliverables and dependencies;
- measurable quarterly outcomes;
- risks and controls;
- evidence mapped to v1 gates;
- a backlog separated into v1-blocking, v1-desirable, and post-v1.

## 5. Stage roadmap

### Stage A — Foundations and product contract, target v0.2

Objectives:

- adopt the charter and v1 release criteria;
- define the jurisdiction universe and federal/subnational rules;
- appoint provisional track owners and release authority;
- settle public/restricted data boundaries;
- decide repository, storage, licensing, and preservation architecture;
- establish risk, decision, conflict, and change logs;
- freeze pilot selection and sampling rationale.

Exit gate:

- governance can answer who owns scope, methods, data, security, release, correction, and preservation;
- the pilot can begin without changing the product boundary.

### Stage B — Controlled heterogeneous pilot, target v0.3

Pilot cohort:

- Australia;
- England and Wales;
- New Zealand;
- Singapore;
- British Columbia, Canada;
- one large and one smaller United States state;
- Spain;
- Brazil;
- India;
- Mexico;
- South Africa.

The final selection may change only with a documented rationale while preserving diversity across region, legal tradition, language, court structure, income setting, and source format.

Pilot tasks:

- map institutions and case pathways;
- complete multilingual search logs;
- ingest at least one API, spreadsheet, HTML table, PDF, and dashboard source;
- catalogue routine reports and outcomes evidence separately;
- retain raw/source manifests and bronze extracts;
- create silver observations and a small gold dataset;
- test manual extraction, translation, double review, and correction;
- publish failed comparisons and ontology changes.

Exit gate:

- a clean environment reproduces the pilot release;
- every pilot gold value has exact provenance and second review;
- pilot source and outcome-evidence gaps are explicit;
- quality checks catch intentionally seeded errors.

### Stage C — Integrated alpha, target v0.4–v0.5

Objectives:

- stabilise IDs and data contracts;
- build acquisition and transformation registries;
- automate structural, referential, temporal, numerical, and lineage validation;
- establish schema migrations and backwards-compatibility tests;
- create regional/language operating procedures;
- generate release packages, profiles, and quality reports from one pipeline;
- run the first independent clean-build and extraction audit.

Exit gate:

- new jurisdictions and sources can be added without changing core architecture;
- manual steps are controlled and recorded;
- failed jobs, stale sources, and unresolved reviews are visible.

### Stage D — Global public beta, target v0.6–v0.7

Objectives:

- create records for the entire defined jurisdiction universe;
- complete documented local-language or relevant official-language searches;
- second-review all negative findings;
- expand extraction to a regionally balanced v1 cohort;
- publish beta source/evidence catalogues, profiles, and atlas;
- collect structured feedback from courts, researchers, advocates, users, and lived-experience advisers;
- publish coverage, data-quality, and comparability metrics.

Exit gate:

- every jurisdiction has a status, search evidence, review date, confidence, and next-review date;
- there is no unexplained regional or language omission;
- beta users can independently reproduce a documented analytical example.

### Stage E — Feature freeze and hardening, target v0.8

Objectives:

- freeze v1 product scope, schemas, ontology, and user features;
- complete test coverage for critical validators and transformations;
- complete source-rights, privacy, disclosure, and security review;
- enable dependency, code, and secret scanning;
- implement source freshness and change detection;
- complete operations, support, correction, backup, restore, rollback, and takedown runbooks;
- complete accessibility, performance, documentation, and disaster-recovery review;
- resolve or remove all severity-1 and severity-2 defects.

Exit gate:

- every mandatory v1 control is implemented and has evidence;
- all remaining work is audit, correction, or release preparation rather than new functionality.

### Stage F — Release candidates and independent assurance, target v0.9.0-rc*

Objectives:

- complete stratified extraction and transformation audit;
- complete independent methods and governance review;
- perform clean-room release build by a non-builder;
- rehearse correction, withdrawal, rollback, incident, and restore processes;
- generate complete release notes, limitations, citation, checksums, and archive package;
- run at least two consecutive release-candidate builds without critical regression.

Exit gate:

- release-readiness matrix passes;
- no unresolved severity-1 or severity-2 defect remains;
- release authority signs the candidate record.

### Stage G — Stable v1.0.0

Release actions:

- tag code, schemas, ontology, and metadata;
- publish data, quality reports, methods, profiles, and atlas as one versioned bundle;
- archive immutable artifacts and issue a persistent identifier;
- publish known gaps and limitations with equal prominence to comparative results;
- activate monitoring, support, and correction processes;
- record next review dates and operational ownership.

### Stage H — v1.0.x maintenance

Permitted work:

- data corrections and source-status updates;
- non-breaking documentation, accessibility, security, and operational fixes;
- refreshed data under unchanged contracts;
- patch releases with transparent correction logs.

New indicators, breaking fields, material ontology changes, or major scope expansion require a minor or major release under the compatibility policy.

## 6. Source discovery and reporting census

### 6.1 Institutional mapping

For each jurisdiction, identify:

- bodies handling each family matter type;
- court levels and appeal pathways;
- justice ministries, statistics offices, legal-aid agencies, child-protection agencies, maintenance agencies, and relevant tribunals;
- federal/devolved responsibilities;
- customary or religious pathways where material;
- publication and accountability obligations.

### 6.2 Search order

1. judiciary and court administration;
2. justice ministry, attorney-general, or equivalent;
3. official statistics office and open-data portal;
4. parliamentary, audit, budget, and performance reporting;
5. child protection, maintenance, legal aid, and family-violence agencies;
6. supranational and regional organisations;
7. academic, civil-society, and professional research;
8. direct enquiry where public sources are absent or ambiguous.

### 6.3 Search controls

Search logs record:

- names and structures used locally;
- languages and search terms;
- domains and catalogues checked;
- dates and reviewers;
- candidate sources and exclusions;
- inaccessible, login-gated, or discontinued sources;
- confidence and next review date.

Automated translation may assist discovery but cannot by itself close a jurisdiction as fully searched.

## 7. Source and evidence acquisition

For every source or evidence item, capture:

- stable ID;
- publisher and official status;
- source/evidence type;
- matter and outcome domains;
- language and geographic scope;
- publication and coverage periods;
- canonical URL and retrieval method;
- query/filter parameters;
- last verified and next review dates;
- source version and checksum when acquired;
- rights/licence and redistribution decision;
- archive or preservation reference;
- status history: active, superseded, changed, unavailable, withdrawn;
- exact provenance for extracted values.

Acquisition code and manual procedures must respect access controls, terms, rate limits, copyright, confidentiality, and security. Public accessibility does not automatically confer redistribution rights.

## 8. Common data model

Every observation should identify:

- schema and record version;
- observation, jurisdiction, institution, source, indicator, and transformation IDs;
- original and harmonised matter type;
- original and harmonised measure;
- procedural start and end events for durations;
- statistic type, unit, numerator, denominator, and denominator definition;
- reporting period and cohort basis;
- inclusion/exclusion rules and breaks in series;
- geography and demographic strata;
- original definition and English translation;
- source version and exact provenance;
- extraction method and transformation lineage;
- reviewer, second-review status, and review date;
- quality grade, comparability tier, release status, and notes.

Missingness states must distinguish at least:

- value not published;
- source not found after completed search;
- source inaccessible;
- not applicable;
- suppressed for confidentiality;
- not yet searched;
- extraction pending;
- mapping rejected as non-comparable.

## 9. v1 core indicators

The first gold release should prioritise measures that are commonly obtainable and interpretable:

1. incoming matters;
2. resolved matters;
3. pending matters;
4. clearance rate;
5. age distribution of pending matters;
6. median filing-to-disposition time;
7. mean filing-to-disposition time, retained separately;
8. selected percentiles where published;
9. proportion completed within a stated standard;
10. ready-to-first-available-hearing wait;
11. filing-to-first-substantive-hearing wait;
12. adjournment or continuance rate;
13. self-representation rate;
14. mediation referral and settlement rates;
15. consent versus contested disposition;
16. appeal, enforcement, or return-to-court rate where definitions permit.

Additional indicators may be catalogued in silver or evidence records without entering gold.

## 10. Outcomes evidence programme

The outcomes stream is a first-class track, not a later narrative appendix. Its v1 purpose is to make the evidence landscape discoverable and accurately characterised.

Evidence classes:

- routine administrative outcome reporting;
- court-user and legal-needs surveys;
- programme or procedural evaluations;
- longitudinal cohorts;
- linked administrative studies;
- qualitative and mixed-methods research;
- systematic reviews and evidence syntheses.

Each record should capture:

- jurisdiction, institution, population, and matter type;
- study setting and period;
- design, comparator, sample, and data source;
- outcome domains and measures;
- publication and source links;
- peer-review/official status;
- limitations and risk-of-bias assessment where applicable;
- whether effect estimates or reusable aggregate data are available;
- exact provenance and reviewer status.

The project will not aggregate effect estimates until compatible outcomes, populations, designs, and risk-of-bias methods are defined.

## 11. Quality and comparability

### Source quality

- **A:** official, machine-readable, documented, and versionable;
- **B:** official tabular publication with adequate definitions;
- **C:** official narrative or interactive source requiring substantial interpretation;
- **D:** credible non-government, academic, or professional source;
- **E:** secondary, unverified, or inadequately documented.

### Comparability

- **Tier 1:** same matter concept, clock, statistic, cohort, unit, and denominator; direct comparison reasonable.
- **Tier 2:** transparent bounded transformation or restricted interpretation required.
- **Tier 3:** descriptive juxtaposition only.
- **Tier 4:** not comparable; retained for discovery and local interpretation.

Grades apply to individual records. A jurisdiction may have excellent filing data and weak timeliness data.

### Mandatory quality controls

- schema and required-field validation;
- ID uniqueness and referential integrity;
- date and period logic;
- unit and allowed-value checks;
- duplicate and overlap detection;
- source-to-publication reconciliation;
- lineage completeness;
- second review for gold;
- stratified independent audit;
- prior-release change analysis;
- documented adjudication of disagreements.

## 12. Technical architecture

The target architecture is described in `ARCHITECTURE.md`.

Core choices:

- public Git monorepo for code, schemas, metadata, documentation, and permitted aggregate release files;
- external object or archival storage for large, licensed, or restricted source artifacts;
- CSV for reviewed human-maintained registries;
- Parquet and DuckDB for analytical release products;
- JSON Schema and explicit data contracts;
- Python acquisition, transformation, validation, and release pipelines;
- static or low-complexity publication architecture unless a supported API is justified;
- continuous integration for tests, validation, linting, schema compatibility, manifests, and release packaging;
- immutable tagged releases with checksums and a persistent archival identifier.

## 13. Security, privacy, law, and ethics

The public project is aggregate-only. Restricted linked-data research, if pursued, requires a separate programme with lawful basis, ethics approval, custodian agreements, secure environments, disclosure controls, and publication review.

Before v1:

- complete source-rights and redistribution decisions;
- implement disclosure and small-cell rules;
- publish vulnerability and takedown processes;
- enable dependency, code, and secret scanning;
- protect release branches and storage;
- review malicious contribution and source-tampering risks;
- test privacy/security incident handling;
- document independence from funders and participating courts.

## 14. Product and publication

The first stable public release should provide:

- global reporting-availability atlas;
- searchable source and outcomes-evidence catalogues;
- downloadable registry and analytical files;
- jurisdiction profiles;
- thematic analysis of timeliness and backlog reporting;
- methods, quality, and limitations handbook;
- worked examples showing valid and invalid comparisons;
- citation and reuse instructions.

The interface should show definitions, data currency, source quality, and comparability warnings next to the value or chart, not only in a remote methods page.

## 15. Governance

### Steering group

Sets strategy, approves annual work, protects independence, and appoints release authority.

### Methods and standards group

Owns scope, ontology, indicator definitions, comparability, suppression, evidence-quality methods, and schema-semantic changes.

### Data operations group

Owns acquisition, extraction, validation, releases, monitoring, corrections, and preservation.

### Security/privacy and ethics function

Owns threat assessment, disclosure controls, incidents, rights/takedown, and the boundary between public and restricted research.

### Jurisdiction and language network

Paid or formally recognised local reviewers verify institutional maps, terminology, and source interpretation. Disagreement is retained in notes or decisions rather than silently resolved.

### Lived-experience and child-rights group

Advises on outcomes, harms, interpretation, product design, and dissemination. Participation is remunerated and designed to avoid disclosure or retraumatisation.

### Independence safeguards

- methods and decision logs are public;
- funders and conflicts are declared;
- courts may correct facts but do not control conclusions;
- release data are reproducible;
- source verification is separated from policy interpretation;
- no jurisdiction is ranked through an opaque composite score.

## 16. Operations and service model

Before v1, the project must have tested procedures for:

- source updates and change detection;
- pipeline failures and anomaly triage;
- data correction, retraction, and withdrawal;
- backup, restore, rollback, and disaster recovery;
- support and severity-based escalation;
- dependency and security maintenance;
- schema migration and backwards compatibility;
- preservation and archive integrity.

At least two people must be able to perform every critical release action. Releases are generated through the documented process in `docs/operations/RELEASE_PROCESS.md`.

## 17. Staffing model

### Controlled pilot

Indicative core capacity:

- project lead: 0.4–0.6 FTE;
- programme/research manager: 1.0 FTE;
- comparative family-law lead: 0.8–1.0 FTE;
- data engineer: 1.0 FTE;
- analysts/researchers: 2.0 FTE;
- statistician/methodologist: 0.4 FTE;
- security/privacy and legal advice: fractional specialist support;
- regional/language reviewers and lived-experience advisers: paid commissioned roles.

Indicative planning envelope: A$600,000–A$1.0 million, depending on host overhead, translation, source complexity, and engineering maturity.

### Stable global v1 programme

A credible 18–24 month route to stable v1 is likely to require:

- 6–10 core FTE across programme, comparative law, data, engineering, quality, product, and operations;
- regional and language leads;
- independent audit and review;
- legal, security, accessibility, preservation, and design support;
- hosted storage, publication, and archival infrastructure;
- post-release maintenance funding.

Indicative planning envelope: A$2.0–A$4.0 million. These are planning ranges, not quotations, and should be tested through a funded discovery phase.

## 18. Principal risks and controls

| Risk | Control |
|---|---|
| “Family court” is defined differently | Model matter, institution, court level, and jurisdiction separately. |
| Wait-time measures are falsely pooled | Require start/end events, statistic, cohort, exclusions, and release-time comparability check. |
| Federal systems are collapsed | Treat autonomous subnational systems as first-class jurisdictions. |
| English and high-income reporting dominates | Paid regional/language leads, explicit coverage metrics, and second review of negative findings. |
| Source pages change or disappear | Manifests, checksums, archives, source-status history, and change detection. |
| Manual PDF/dashboard extraction introduces errors | Controlled templates, double review, audit sampling, and exact locators. |
| Large data volume outpaces review | Gold release limited by quality gates, not collection volume. |
| Court speed is mistaken for family outcomes | Separate evidence streams and prohibit unsupported causal language. |
| Public data create disclosure harm | Aggregate-only release, suppression, privacy review, and takedown process. |
| Source redistribution violates rights | Rights register and manifest-only storage where copying is not permitted. |
| One person becomes indispensable | Named deputies, runbooks, handover tests, and separation of duties. |
| Prototype never becomes maintainable | Feature freeze, release criteria, operational gates, and funded post-release cycles. |
| Jurisdictions seek editorial control | Factual review allowed; independent methods and conclusions protected. |

## 19. v1 success measures

### Coverage

- 100% of in-scope jurisdictions have an auditable coverage status.
- 100% of negative findings have second review.
- Coverage is reported by region, language, legal system, matter type, source type, and outcome domain.

### Quality

- 100% of gold observations have exact provenance, second review, quality grade, and comparability tier.
- Stratified audit reaches at least 99% agreement on copied numeric values and required semantic fields after adjudication.
- Zero unresolved critical or high-severity defect at release.

### Reproducibility

- clean checkout validates and builds all public release artifacts;
- independent clean-room build succeeds;
- artifacts are checksummed, versioned, and archived;
- prior releases remain immutable and available.

### Usability

- users can download and interpret data without proprietary software;
- definitions and warnings appear at the point of use;
- at least two external users reproduce a core analytical example;
- support, correction, and citation routes are clear.

### Operations and sustainability

- correction, restore, rollback, and incident rehearsals pass;
- at least two operators cover each critical function;
- maintenance is resourced for at least two post-release review cycles;
- source freshness, open corrections, and service performance are publicly reported.

## 20. Immediate next actions

1. Approve the v1 product contract and release criteria.
2. Appoint provisional track owners and release authority by role.
3. Define the full jurisdiction universe and completion-status vocabulary.
4. Extend the schemas for source versioning, evidence records, review status, lineage, and release metadata.
5. Run the 12-jurisdiction pilot through a clean end-to-end release build.
6. Establish independent methods, security/privacy, and data-quality review before global scaling.
7. Secure an institutional host and funding that includes post-release operations, not only data collection.
