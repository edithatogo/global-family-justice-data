# Roadmap to a stable, hardened v1.0

## Purpose

This roadmap changes v1.0 from a simple coverage milestone into a **release contract for a dependable international public data product**. Version 1.0 is not reached merely because a global source list exists. It is reached only when the project is scientifically defensible, reproducible, secure, documented, operationally owned, and maintainable after launch.

The roadmap has three simultaneous goals:

1. **Global discovery:** every in-scope jurisdiction is searched under a documented protocol and assigned an auditable coverage status.
2. **Trusted data:** source metadata, extracted observations, outcome evidence, and comparative datasets meet explicit provenance and quality requirements.
3. **Durable service:** releases can be rebuilt, corrected, archived, supported, and updated without dependence on one person or one machine.

Detailed release criteria are in `docs/strategy/V1_RELEASE_CRITERIA.md`. Track charters are in `docs/strategy/DELIVERY_TRACKS.md`. The executable epic backlog and project-board model are in `docs/strategy/V1_EPICS.md` and `docs/strategy/GITHUB_PROJECT_MODEL.md`.

## Current state

The repository is an early planning and validation scaffold. It contains seed registers, schemas, a preliminary indicator dictionary, methods notes, and lightweight validation. It is **not yet a production dataset or stable v1.0 release**.

## What v1.0 will contain

Version 1.0 will publish a coherent release bundle rather than a collection of unrelated files:

- a global jurisdiction and institutional register;
- a multilingual source census with explicit negative findings;
- a versioned family-justice matter and indicator ontology;
- a catalogue of outcome studies, surveys, evaluations, and administrative reporting;
- source-native bronze tables where lawful and practical;
- normalised silver observations with full lineage;
- a bounded gold dataset containing only approved comparable measures;
- jurisdiction profiles and a global reporting-availability atlas;
- methods, quality, limitations, licensing, and governance documentation;
- machine-readable CSV, Parquet, and DuckDB release files;
- checksums, build metadata, schema versions, and an archival deposit;
- an operational maintenance and correction process.

Version 1.0 will **not** claim that every desired outcome exists, infer child or family wellbeing from court speed alone, publish identifiable records, or create an omnibus country league table.

## Maturity model

| Level | Release family | Meaning | Exit condition |
|---|---|---|---|
| M0 — Concept | v0.1 | Scope, seed schemas, and initial sources exist | Founding assumptions documented |
| M1 — Controlled pilot | v0.2–v0.3 | Repeatable work on a heterogeneous pilot | Pilot data can be rebuilt and audited |
| M2 — Integrated alpha | v0.4–v0.5 | Discovery, extraction, harmonisation, evidence catalogue, and profiles use one data model | End-to-end workflow works across source formats and languages |
| M3 — Public beta | v0.6–v0.7 | Broad global coverage and public test releases | Global census substantially complete; known gaps explicit |
| M4 — Hardened beta | v0.8 | Feature and schema freeze; security, quality, and operations hardening | All mandatory v1 controls implemented |
| M5 — Release candidate | v0.9.0-rc* | Independent review, correction rehearsal, reproducibility test, and release rehearsal | Release criteria pass with no unresolved critical defects |
| M6 — Stable | v1.0.0 | Citable, archived, supported production release | Release authority signs the v1 readiness record |
| M7 — Maintained | v1.0.x | Corrections and non-breaking maintenance | Service levels and annual review cadence met |

## Delivery tracks

Work proceeds through twelve tracks. Each track has its own owner, backlog, evidence, and v1 gate; none is optional.

| Track | Name | v1 outcome |
|---|---|---|
| T1 | Governance and institutional home | Named accountable bodies, decision rights, conflicts policy, succession, and durable host |
| T2 | Scope, ontology, and methods | Frozen v1 scope, matter taxonomy, indicator definitions, comparability rules, and migration policy |
| T3 | Global jurisdiction and source census | Every in-scope jurisdiction searched, reviewed, and assigned a coverage status |
| T4 | Acquisition, preservation, and provenance | Lawful, repeatable retrieval with checksums, archival references, and exact provenance |
| T5 | Extraction, harmonisation, and outcomes evidence | Bronze, silver, gold, and evidence-catalogue pipelines with retained source meaning |
| T6 | Scientific and data quality assurance | Automated tests, reviewer controls, audit sampling, reconciliation, and quality reporting |
| T7 | Engineering, architecture, and reproducibility | Tested builds, versioned schemas, deterministic release artifacts, and supported environments |
| T8 | Security, privacy, legal, and ethics | Aggregate-only public release, rights review, threat model, dependency and secret controls, and incident process |
| T9 | Product, documentation, and accessibility | Downloadable data, profiles, atlas, complete documentation, and accessible public interfaces |
| T10 | Languages, jurisdiction partnerships, and community | Multilingual search and review, regional representation, contributor workflow, and dispute handling |
| T11 | Operations, releases, support, and resilience | Runbooks, monitoring, backups, restore test, corrections, release management, and support ownership |
| T12 | Sustainability and impact evaluation | Resourced maintenance plan, preservation, adoption measures, and post-release evaluation |

## Stage plan and hard gates

### Stage A — Product contract and foundations: v0.2

**Purpose:** remove ambiguity about what will be built, who owns it, and what evidence is required.

Deliverables:

- project charter and explicit v1 product boundary;
- in-scope jurisdiction universe and rules for federal/subnational systems;
- v1 release criteria and risk register;
- track owners and release authority;
- initial architecture, security, licensing, and preservation decisions;
- schema and ontology versioning rules;
- pilot selection and sampling rationale.

**Gate A:** no unresolved question about public data boundaries, release authority, core matter types, or the definition of a completed jurisdiction search.

### Stage B — Controlled heterogeneous pilot: v0.3

**Purpose:** prove the complete workflow, not merely collect examples.

Deliverables:

- at least 12 deliberately heterogeneous pilot jurisdictions;
- institutional maps and documented multilingual search logs;
- at least one API, spreadsheet, HTML table, PDF, and dashboard source handled end to end;
- outcome-evidence catalogue piloted alongside routine court reporting;
- lineage from raw/source manifest to bronze, silver, and gold;
- double review for all pilot gold observations;
- first reproducibility and correction exercises.

**Gate B:** a fresh environment can rebuild the pilot release; every published value can be traced to an exact source location; failed comparisons are retained and explained.

### Stage C — Integrated alpha: v0.4–v0.5

**Purpose:** turn pilot methods into one scalable system.

Deliverables:

- stable identifiers for jurisdictions, institutions, sources, indicators, observations, evidence records, and transformations;
- standard source manifests and retrieval logs;
- data contracts for all release tables;
- transformation registry and schema migrations;
- automated structural, referential, temporal, numerical, and lineage checks;
- regional/language operating model;
- public alpha releases generated through the release pipeline.

**Gate C:** new jurisdictions can be added without changing the core architecture, and routine failures are visible through machine-readable quality reports.

### Stage D — Global public beta: v0.6–v0.7

**Purpose:** complete the international source census and expose the product to real users.

Deliverables:

- records for 100% of the defined jurisdiction universe;
- documented search coverage in local or relevant official languages;
- second review of every “no public source found” conclusion;
- source and outcomes-reporting coverage map;
- a regionally balanced v1 extraction cohort, including all pilot jurisdictions;
- downloadable beta datasets, profiles, and methods handbook;
- external feedback and issue triage process.

**Gate D:** every jurisdiction has a status, evidence trail, last-reviewed date, confidence rating, and next-review date; no geography is silently omitted.

### Stage E — Feature freeze and hardening: v0.8

**Purpose:** stop adding scope and make the release dependable.

Deliverables:

- v1 scope, schemas, ontology, and user-facing features frozen;
- all critical pipelines covered by tests;
- complete source-rights and redistribution review;
- privacy and disclosure review of all outputs;
- threat model, dependency review, and secret scanning enabled;
- source freshness monitoring and broken-link/changed-source queues;
- operations runbooks, correction policy, backup and restore procedures;
- performance, accessibility, and documentation review;
- migration notes for every change since beta.

**Gate E:** zero open critical defects; all mandatory controls in the release-criteria matrix have evidence; any deferred item is explicitly non-v1 and does not undermine the product contract.

### Stage F — Release candidates and independent assurance: v0.9.0-rc1 onward

**Purpose:** demonstrate that v1 can be released and maintained under realistic conditions.

Deliverables:

- clean-room reproducibility test by a person not involved in the build;
- stratified extraction and transformation audit;
- independent methods and governance review;
- jurisdiction-fact-check process that preserves analytical independence;
- simulated source failure, data correction, takedown, and rollback exercises;
- release notes, known limitations, citation, checksums, and archive deposit prepared;
- two consecutive release-candidate builds without a critical regression.

**Gate F:** the release authority approves a signed readiness record; no unresolved severity-1 or severity-2 issue remains; all release artifacts are reproducible and internally consistent.

### Stage G — Stable v1.0.0

**Purpose:** publish a citable and supportable international public data product.

Release actions:

- tag immutable source code and metadata;
- publish release data and documentation together;
- issue checksums and provenance metadata;
- archive the release and assign a persistent identifier;
- publish quality metrics, coverage gaps, and known limitations;
- activate support, correction, and monitoring processes;
- announce the next planned review cycle without promising real-time currency.

### Stage H — v1.0.x maintenance

Only backwards-compatible corrections and operational improvements are permitted in v1.0.x. New indicators, breaking schema changes, or major scope expansion require v1.1 or v2.0 under the compatibility policy.

Maintenance includes:

- source freshness and availability checks;
- scheduled jurisdiction reviews;
- transparent corrections and retractions;
- dependency and security maintenance;
- annual methods and ontology review;
- preservation checks and restore rehearsal;
- public service-level reporting.

## v1.0 release gates at a glance

The detailed matrix is authoritative. At minimum:

### Coverage and content

- 100% of in-scope jurisdictions have an auditable coverage record.
- 100% of negative findings have second review.
- Every high-priority source has official-status, rights, retrieval, last-verified, and next-review metadata.
- The outcomes evidence catalogue distinguishes routine reporting, surveys, evaluations, cohort studies, and linked-data research.

### Data quality

- 100% of gold observations have exact provenance, approved indicator mappings, quality grades, comparability tiers, and second review.
- All gold transformations are reproducible from retained inputs or lawful source manifests.
- A stratified audit reaches at least 99% agreement on copied values and required semantic fields, with all material disagreements resolved before release.
- No known incompatible duration clocks, denominators, units, or cohorts are pooled.

### Engineering and reproducibility

- A clean checkout can validate and build all public release artifacts using documented supported environments.
- Continuous integration covers validation, tests, linting, schema compatibility, packaging, and manifest checks.
- Release files are deterministic where practical and always checksummed.
- No unresolved critical dependency, secret, or code-scanning finding remains.

### Governance, ethics, and law

- Release authority, data steward, security contact, and correction owner are named by role.
- Code, data, and third-party source rights are documented separately.
- Public outputs contain no identifiable family-level records and pass disclosure review.
- Conflicts, methodological decisions, corrections, and disputes have public processes.

### Operations and sustainability

- Monitoring, backups, restore, rollback, correction, takedown, and source-change runbooks have been tested.
- At least two people can operate each critical release process.
- A funded or institutionally committed maintenance plan covers at least the first two post-release review cycles.
- Users have a clear support route, response expectations, and machine-readable changelog.

## Critical path

The critical path is:

1. freeze scope and jurisdiction universe;
2. prove the end-to-end pilot and data model;
3. scale multilingual discovery while hardening provenance;
4. complete global coverage records;
5. freeze features and schemas;
6. complete audit, legal, security, operations, and reproducibility gates;
7. release and maintain.

Data extraction at scale must not outrun ontology, provenance, or reviewer capacity. A smaller gold dataset with complete lineage is preferable to a larger but unverifiable one.

## Post-v1 direction

Likely v1.1 work includes additional jurisdictions in the fully extracted cohort, non-breaking indicators, improved automation, and translated public documentation. A v2.0 programme may add governed person-level linkage partnerships, common user-experience instruments, prospective outcome studies, and breaking ontology improvements.
