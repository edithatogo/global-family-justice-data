# Project plan: Global Family Justice Data Project

## 1. Executive intent

Build and operate the first reproducible international source census and harmonised data platform for family-justice reporting, process, outputs, administrative outcomes, user experience and child/family outcomes.

The programme is designed to reach a **stable, hardened and maintainable v1.0**, not simply to publish an early global spreadsheet. The delivery model therefore treats methods, data operations, software, security, governance, international verification and financial sustainability as co-equal workstreams.

The v1.0 release will be credible only when an external user can:

- determine what was searched in every in-scope jurisdiction;
- distinguish “not published” from “not searched” and from zero activity;
- trace each released observation to exact source evidence;
- understand the measure, matter type, clock, denominator and limitations;
- reproduce derived release artefacts in a clean environment;
- retrieve a prior release after a correction or source change;
- report an error or vulnerability through a functioning process;
- rely on stable identifiers and contracts throughout the 1.x line.

## 2. Product definition

### 2.1 Four linked public products

| Product | Question answered | v1.0 output |
|---|---|---|
| Global source census | What does each jurisdiction publicly report? | Jurisdiction universe, search logs, source register, coverage status and availability atlas |
| Harmonised core dataset | Which process/performance observations can be compared responsibly? | Bronze/silver/gold release data, dictionary, quality grades and comparability tiers |
| Outcomes evidence catalogue | What evidence exists about subsequent administrative, user, child and family outcomes? | Structured study/dataset catalogue and evidence-gap map |
| Jurisdiction context library | How does each system work and what affects interpretation? | Versioned profiles, institutional maps, procedural clocks, standards, reforms and series breaks |

### 2.2 Authoritative artefacts

The immutable release bundle is the system of record. It contains open tabular files, efficient analytical files, schemas, methods, profiles, validation reports, checksums, citation metadata and change history.

The dashboard, website and API are generated from that bundle. This allows the project to remain usable if a presentation service fails or is replaced.

### 2.3 What v1.0 does not claim

v1.0 will not claim that:

- every desired outcome is measured in every jurisdiction;
- a court order is equivalent to a child or family outcome;
- faster disposition necessarily means better justice;
- silence in a source means zero cases;
- all family matters are heard in an institution called a family court;
- a single composite ranking can fairly summarise international performance;
- descriptive reporting establishes causality.

## 3. Definition of global completeness

A defensible global claim is:

> Every jurisdiction in the approved universe has been searched under a documented multilingual protocol; every located public source has been catalogued; absent, inaccessible and unpublished measures have been explicitly coded and second-reviewed; and every extracted observation retains traceable provenance.

The universe begins with sovereign jurisdictions and expands to subnational systems where responsibility for family justice is materially devolved. Dependent territories and transnational/specialised systems are represented under an explicit inclusion rule rather than handled ad hoc.

Every jurisdiction receives one current coverage status:

- not started;
- search in progress;
- official source found;
- non-government source only;
- no public family-specific source found;
- source inaccessible or rights-restricted;
- direct contact pending;
- verified complete for the current review cycle.

A negative finding requires a preserved search log and second reviewer. It is not a blank cell.

## 4. Scope

### 4.1 Core matter types

1. divorce, dissolution and nullity;
2. private-law parenting, custody, residence, contact and parental responsibility;
3. public-law child protection, care and dependency;
4. civil family-violence and protection-order proceedings;
5. child and spousal maintenance/support;
6. property and financial relief following relationship breakdown;
7. adoption, guardianship and kinship care;
8. parentage and selected assisted-reproduction matters;
9. international child abduction, access and cross-border child protection.

Juvenile criminal justice, probate and general criminal family-violence proceedings remain adjacent domains. They may be catalogued when reporting systems combine them, but they are not automatically pooled with core family-justice measures.

### 4.2 Evidence domains

The data model keeps five domains separate:

- **process and performance** — filings, pending caseload, clearance, waits, duration, adjournments and compliance with standards;
- **court outputs** — manner of disposal, orders and formal decisions;
- **administrative outcomes** — appeals, reversals, enforcement, non-compliance, reapplication and return to court;
- **child/family and user outcomes** — safety, stability, wellbeing, family functioning, perceived fairness and experience;
- **inputs and context** — staffing, expenditure, legal aid, court structure, procedure, reforms and statutory targets.

### 4.3 Time horizon

- Attempt at least the most recent five reporting years in the pilot and core dataset.
- Prefer 2010 onward where source continuity and definitions support it.
- Record series breaks and reform periods; do not back-cast across incompatible definitions.
- Release source-search status with a clear review-cycle date.

## 5. v1.0 capability baseline

The binding release criteria are in `V1_0_RELEASE_CRITERIA.md`. In summary, v1.0 requires:

- complete reviewed coverage status across the approved jurisdiction universe;
- stable v1 identifiers, schemas, ontology and public file contracts;
- exact provenance and preservation metadata for every released observation;
- dual review of all gold series plus independent audit sampling;
- a reproducible clean-room build and immutable signed/checksummed artefacts;
- explicit rights, security, privacy, disclosure and ethical controls;
- public methods, limitations, corrections and vulnerability channels;
- tested release, restore, rollback and continuity processes;
- accessible public products and reviewed translations;
- named role holders and deputies;
- a 12-month funded operating and release plan after launch.

## 6. Programme structure

The work is organised into ten tracks. No track can be deferred to a final “hardening phase”; controls are built progressively from the v0.3 engineering baseline.

### T0 — Governance, ethics and independence

Establish the legal/organisational host, charter, decision rights, conflict management, advisory structures, release authority and accountability for harms and corrections.

### T1 — Scope, ontology and methods

Own the jurisdiction universe, matter taxonomy, indicator dictionary, procedural clocks, denominators, comparability rules, definitions of missingness and methods change control.

### T2 — Jurisdiction universe and source census

Map institutions, execute multilingual searches, maintain coverage status, document negative findings and coordinate direct enquiries and local verification.

### T3 — Acquisition, preservation and source monitoring

Build lawful acquisition pathways for APIs, files, HTML, dashboards and PDFs; preserve evidence; track checksums, rights and source drift.

### T4 — Data platform and engineering

Maintain schemas, identifiers, pipelines, environments, tests, release builds, efficient file formats and reproducible derived services.

### T5 — Harmonisation, quality and assurance

Promote data through bronze, silver and gold; control classification and transformation; run dual review, audit sampling, quality scoring and external assurance.

### T6 — Product, documentation and accessibility

Develop downloadable releases, profiles, atlas, dashboard/query layer, methods, definitions, limitations, user guidance and accessible interfaces.

### T7 — Security, privacy, legal and supply-chain assurance

Enforce the aggregate-data boundary, manage source rights, scan code and artefacts, protect credentials, assess threats and disclosure risk, and operate incident/takedown processes.

### T8 — Operations, reliability and release management

Run release calendars, monitoring, ticketing, source-health checks, correction service, backups, restore exercises, runbooks and service ownership.

### T9 — International community, localisation and sustainability

Build a representative correspondent network, translation QA, contributor training, regional participation, succession plans, funding and impact evaluation.

Detailed charters, deliverables, dependencies and indicators are in `docs/programme/track-charters.md`.

## 7. Integrated delivery plan

### Stage 0 — Mobilise and control the design (months 0–2; v0.4 / G1)

Objectives:

- appoint accountable owners and deputies;
- agree the host, charter, governance and independence protections;
- approve the v1 product boundary, jurisdiction universe and non-goals;
- adopt architecture, security baseline, data-governance boundary and risk approach;
- define stable identifier strategy and draft v1 data contracts;
- agree pilot jurisdictions, review standards and release criteria.

Deliverables:

- signed programme charter;
- RACI and decision log structure;
- v1 scope and methods baseline;
- architecture decision records;
- costed 24-month plan;
- initial threat model, privacy/disclosure assessment and rights workflow;
- stage-gate evidence templates.

Gate G1: all foundation controls approved and every critical track has an owner and deputy.

### Stage 1 — Prove the design in a heterogeneous pilot (months 2–6; v0.5 / G2)

Pilot systems should deliberately test:

- federal and unitary structures;
- common-law, civil-law and mixed systems;
- specialist and general courts;
- national and subnational reporting;
- English and non-English source discovery;
- APIs, spreadsheets, HTML, interactive dashboards and PDFs;
- retrospective duration, prospective listing wait and pending-age measures;
- strong and sparse reporting environments.

Proposed pilot:

- Australia;
- England and Wales;
- New Zealand;
- Singapore;
- British Columbia;
- one large and one smaller United States state;
- Spain;
- Brazil;
- India;
- Mexico;
- South Africa.

Pilot outputs:

- institutional maps and source logs for every pilot system;
- at least five years attempted for priority sources;
- representative bronze-to-gold pipelines;
- first jurisdiction profiles and outcomes-catalogue entries;
- dual review of all pilot gold series;
- independent re-extraction sample;
- pilot comparability and failure report;
- revised schemas and ontology after controlled design review.

Gate G2: end-to-end reproducibility demonstrated and no critical design issue left unresolved.

### Stage 2 — Complete the global source census (months 5–12; v0.6 / G3)

Tasks:

- establish every jurisdiction/subnational record;
- map responsible institutions before searching for “family court” data;
- conduct local-language searches across courts, ministries, statistical agencies, parliaments, audit offices, legal aid and child/family agencies;
- catalogue international/regional sources and research evidence;
- second-review negative findings;
- conduct standardised direct enquiries for absent or ambiguous sources;
- publish a beta source register and data-availability atlas.

Gate G3: every in-scope jurisdiction has a current status and review evidence.

### Stage 3 — Scale acquisition, harmonisation and public beta (months 8–16; v0.7 / G4)

Tasks:

- productionise connectors and controlled manual extraction;
- add checksums, rights metadata, source versioning and drift alerts;
- implement stable IDs, data contracts and migration tests;
- transform source-native tables to normalised long form;
- freeze the v1 core indicator set and proposed analytical cohort;
- complete outcomes evidence catalogue and context-profile templates;
- launch downloadable beta data, profiles and constrained comparison views;
- conduct structured usability, accessibility and interpretation testing.

Gate G4: all v1 products exist in production-like form and the comparative cohort is ready to freeze.

### Stage 4 — Harden and assure the release candidate (months 15–21; v0.9 / G5)

Tasks:

- freeze features, schemas and ontology for v1;
- eliminate manual, undocumented production steps;
- complete gold review and independent audit sample;
- run clean-room build, migration, rollback and republish rehearsals;
- complete rights, disclosure, security, dependency and threat reviews;
- test backups, restoration, source-loss scenarios and continuity handover;
- obtain external methods review and publish responses;
- close P0/P1 defects and disposition P2 issues;
- complete documentation, localisation, citation and limitations materials;
- operate a stability soak under production-like monitoring.

Gate G5: release candidate meets all criteria except final publication and operational handover.

### Stage 5 — Publish and institutionalise v1.0 (months 21–24; G6)

Tasks:

- complete final release evidence pack and go/no-go decision;
- generate immutable release files, checksums, signatures and citation metadata;
- deposit the release in an archival repository;
- publish methods, source register, coverage report, data, profiles and limitations;
- activate correction, incident and support workflows;
- begin the approved 1.x release calendar;
- conduct a post-launch review and prioritise non-breaking v1.1 improvements.

Gate G6: all mandatory v1 criteria pass and a funded operating team accepts service ownership.

## 8. Common data model

Every observation should identify:

- jurisdiction and responsible subnational unit;
- institution and court level;
- original and harmonised matter type;
- original measure and harmonised indicator;
- start and end events for duration measures;
- statistic type: count, mean, median, percentile, rate or proportion;
- unit, numerator and denominator definition;
- reporting period and cohort basis;
- inclusion/exclusion rules and procedural status;
- demographic/geographic strata and disclosure status;
- source ID and exact provenance locator;
- retrieval, extraction, transformation and review records;
- source quality, data-quality result and comparability tier;
- ontology, schema and pipeline version;
- notes, limitations and series-break flags.

Stable identifiers must be opaque enough not to encode changeable semantics. Retired IDs are never reused.

## 9. Minimum v1 core indicator families

The comparative release initially prioritises indicators that are commonly reported and interpretable when definitions align:

1. incoming matters;
2. resolved matters;
3. pending matters;
4. clearance rate;
5. pending-age distribution;
6. median filing-to-disposition duration;
7. mean filing-to-disposition duration, retained separately;
8. percentile duration where available;
9. proportion completed within a defined standard;
10. ready-to-first-available-hearing wait;
11. filing-to-first-substantive-hearing duration;
12. adjournment/continuance rate;
13. self-representation rate;
14. mediation referral and resolution rates;
15. consent versus contested disposition;
16. appeal, enforcement or return-to-court measures where definitions are adequate.

The outcomes catalogue has broader scope, but outcome measures do not enter the gold comparative dataset until their population, follow-up window, instrument and attribution limits are clear.

## 10. Quality and comparability

### 10.1 Source quality

- **A:** official, machine-readable, documented and stable;
- **B:** official tabular publication with adequate definitions;
- **C:** official narrative/dashboard requiring substantial interpretation;
- **D:** credible research or non-government source;
- **E:** secondary, unverified or insufficiently documented.

### 10.2 Comparability

- **Tier 1:** direct comparison is reasonable;
- **Tier 2:** transparent transformation or restriction is required;
- **Tier 3:** descriptive juxtaposition only;
- **Tier 4:** not comparable; retained for local analysis/source mapping.

Grades apply to individual series/observations rather than to countries.

### 10.3 Promotion model

- **Raw evidence:** preserved source and retrieval metadata.
- **Bronze:** source-native extraction; no semantic harmonisation.
- **Silver:** normalised structure with original definitions retained.
- **Gold:** approved use for a specified analytical purpose after review and validation.
- **Quarantine:** failed, ambiguous or rights-restricted material retained outside release outputs.

Every gold series receives source/series-level dual review. Every observation receives automated validation. A separate assurance sample is independently re-extracted before v1.0.

See `docs/quality/v1-data-quality-plan.md`.

## 11. Technical architecture

The public monorepo holds:

- code, schemas, ontologies and documentation;
- redistributable aggregate release data;
- source manifests, checksums and rights status;
- tests, workflows and release configuration.

Large or restricted source files are stored in controlled object/preservation storage. Git stores manifests and checksums rather than unlawfully redistributing material.

Data products are released in:

- CSV or equivalent open tabular format;
- Parquet for efficient analytical use;
- DuckDB or another portable query artefact where appropriate;
- JSON/JSONL metadata for machine use;
- static HTML/documentation generated from the same release.

Architecture details are in `docs/architecture/v1-architecture.md`.

## 12. Security, privacy, ethics and legal controls

The public project is aggregate-only. Any person-level linkage research is a separate programme with its own lawful basis, secure environment, approvals and disclosure controls.

v1 controls include:

- threat modelling and privacy/disclosure impact assessment;
- rights and redistribution register for every source family;
- secret, dependency and release-artifact scanning;
- least-privilege credentials and separated environments;
- signed/checksummed release artefacts;
- small-cell and contextual-harm review;
- vulnerability, privacy incident and takedown channels;
- conflict/funding disclosure and independence protections;
- no publication of sealed, protected or unlawfully acquired records.

## 13. Operating model

The project should run as a release service rather than an episodic research exercise.

### Planned cadence after v1.0

- quarterly source-health and coverage-status review;
- at least two scheduled data releases each year;
- patch releases for material corrections;
- annual methods and ontology review;
- annual jurisdiction-profile refresh, prioritised by source change;
- biennial international analytical report or equivalent thematic publication.

### Service objectives

- correction reports acknowledged within five working days;
- correction disposition or progress update within 30 calendar days;
- no loss of immutable releases;
- restoration of public access services within two business days after a major failure;
- primary and deputy ownership for every critical process;
- current and previous minor releases remain reproducible.

See `docs/operations/release-and-operations.md`.

## 14. Governance and decision rights

### Steering group

Approves strategy, budget, annual work plan, material scope and release authority. Protects independence from funders and participating institutions.

### Methods and standards group

Owns ontology, indicator definitions, comparability, quality rules, suppression policy and methods revisions.

### Data operations and technical group

Owns acquisition, pipelines, validation, releases, security operations, preservation and correction implementation.

### Jurisdiction correspondent network

Verifies institutional maps, local terminology, translations and source interpretation. Disagreement is recorded rather than silently erased.

### Lived-experience and child-rights advisory group

Shapes outcome priorities, communication, harms analysis and interpretation. Participation is paid and supported safely.

### Independent assurance

Reviews the release evidence pack and challenges methodological, operational and security claims before v1.0.

Decision rights and RACI are in `docs/governance/roles-and-raci.md`.

## 15. Staffing and resourcing

A mature 24-month v1.0 programme should be planned at approximately 8–12 core FTE, supplemented by paid regional/jurisdiction reviewers, translation, legal advice, accessibility testing and external assurance.

Indicative core roles:

- programme/product director: 1.0 FTE;
- programme operations/release manager: 1.0 FTE;
- comparative family-law/methods leads: 1.5–2.0 FTE;
- regional source-census leads/analysts: 2.0–4.0 FTE;
- data engineers: 1.5–2.0 FTE;
- quality/assurance lead: 0.8–1.0 FTE;
- platform/product/UX: 0.5–1.0 FTE;
- security/privacy/data-governance support: 0.3–0.6 FTE;
- community/localisation lead: 0.5–1.0 FTE.

A planning envelope of roughly **A$3–6 million over 24 months** is more consistent with a stable international v1.0 than the cost of a lean pilot. The range depends heavily on institutional overhead, translation, manual PDF/dashboard extraction, in-kind court/statistics support and the scale of the public product. It is a planning estimate, not a quotation.

The v1.0 gate also requires committed maintenance resources for at least 12 months after launch.

## 16. Principal risks and controls

| Risk | Control |
|---|---|
| “Family court” structures are incomparable | Model matter type, institution, court level and jurisdiction separately |
| Mean, median and prospective waits are conflated | Store statistic and start/end clock explicitly; block incompatible comparison |
| Federal systems are collapsed into a national figure | Treat responsible subnational systems as first-class jurisdiction units |
| Coverage claims hide unsearched systems | Require a reviewed status and search log for every jurisdiction |
| Source dashboards or URLs disappear | Checksums, preservation, source-health monitoring and archived release evidence |
| Copyright/terms prevent redistribution | Rights register; public manifests; controlled storage where lawful |
| Translation changes legal meaning | Retain original text and require human local-language review for gold use |
| Orders are mislabelled as outcomes | Separate process, output, administrative and person-outcome domains |
| Rankings create misleading incentives | No composite ranking; visible comparability tiers and context notes |
| Sparse reporting disadvantages some regions | Paid regional network, multilingual protocol and explicit missingness |
| Small cells or sensitive data expose families | Aggregate boundary, suppression, disclosure and contextual-harm review |
| Pipelines depend on one engineer | Deputies, runbooks, tests, clean builds and continuity exercises |
| Source changes silently alter trends | Schema/drift monitoring, series-break flags and release diff review |
| Funding or institutional influence weakens independence | Public funding/conflict disclosure and independent methods/release assurance |
| v1.0 is declared before operations are ready | Mandatory release criteria, no-go conditions and executive sign-off |

The maintained risk register is in `docs/programme/risk-register.md`.

## 17. First 100 days

### Days 1–30: establish control

- confirm host, sponsor, programme director and interim track leads;
- approve charter, v1 product boundary and non-goals;
- appoint methods, technical/security and lived-experience advisory structures;
- freeze the pilot list and draft jurisdiction-universe rule;
- approve repository ownership, licensing approach and aggregate-data boundary;
- create decision, risk, issue and change logs;
- cost the 24-month work plan and secure mobilisation resources.

### Days 31–60: freeze foundational design

- approve stable-ID conventions and draft v1 data contracts;
- approve matter taxonomy, core indicator families and duration-clock model;
- complete architecture, threat model and rights workflow;
- establish source-search, translation, extraction and review training;
- create production-like development/test environments;
- complete institutional maps and searches for the first six pilot systems;
- implement baseline CI, validation, provenance and release-manifest checks.

### Days 61–100: prove the first vertical slices

- complete searches for all pilot systems;
- ingest at least one API, one tabular source and one PDF/dashboard source end to end;
- produce source-native, normalised and gold examples with exact lineage;
- run dual review and independent re-extraction on the sample;
- publish an internal pilot quality and design report;
- resolve schema/ontology changes through formal decision records;
- rehearse a versioned pre-release and correction;
- approve the detailed global census allocation and regional engagement plan.

## 18. Success measures for v1.0

The release is successful when:

- 100% of the approved jurisdiction universe has a reviewed coverage status;
- every released observation is traceable and reproducible;
- no critical privacy, legal, security or data-integrity issue is open;
- gold data have passed dual review and independent audit thresholds;
- incompatible measures are not presented as equivalent;
- public artefacts are accessible without proprietary software;
- prior releases remain retrievable and corrections are transparent;
- operations, support, recovery and succession have been rehearsed;
- regional and lived-experience contributors materially influence interpretation;
- the project has a funded, named and monitored 1.x operating model.

## 19. Post-v1.0 direction

The 1.x line should favour non-breaking expansion and quality improvement:

- additional historical depth and jurisdictions in the gold cohort;
- richer outcome evidence and selected secure linked-data partnerships;
- additional languages and regional reports;
- more automated acquisition and source-change monitoring;
- improved user tools constrained by comparability rules;
- evaluation of how the data are used, misused and translated into policy.

A v2.0 should be reserved for genuinely breaking changes, such as a new conceptual model, public contract or person-level research architecture. It should not be used simply because another annual release has occurred.
