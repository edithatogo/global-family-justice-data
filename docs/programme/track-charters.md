# v1.0 track charters

## How to use this document

Each track has a single accountable lead, a named deputy, defined interfaces and gate evidence. Track leads own outcomes rather than only activities. Cross-track deliverables require one lead to be accountable even when several teams contribute.

## T0 — Governance, ethics and independence

**Mission:** create a legitimate, independent and durable authority for the project.

**Accountable lead:** programme director or governance chair.

**Core deliverables:**

- legal/organisational host and repository/data custodianship;
- programme charter, terms of reference and decision rights;
- conflicts, funding and independence policy;
- lived-experience and child-rights participation model;
- ethics/escalation, corrections, complaints and harms-review pathways;
- release authority and independent assurance arrangements;
- succession and long-term ownership plan.

**v1.0 definition of done:** all bodies operate to current terms of reference; material decisions and conflicts are public; release authority has signed the evidence pack; a 12-month operating plan is funded; no critical role lacks a deputy.

**Leading indicators:** unfilled critical roles, overdue decisions, unresolved conflicts, advisory participation, decision publication lag.

**Key dependencies:** all tracks depend on T0; T0 depends on T9 for representative participation and sustainability.

## T1 — Scope, ontology and methods

**Mission:** provide a stable semantic and analytical contract for the project.

**Accountable lead:** methods director.

**Core deliverables:**

- jurisdiction-universe and subnational inclusion rules;
- matter, proceeding, institution and outcome taxonomies;
- indicator dictionary and duration-clock model;
- denominator, cohort, time-period and missingness rules;
- source quality and comparability framework;
- methods change, versioning and deprecation process;
- jurisdiction profile and outcomes-catalogue methods.

**v1.0 definition of done:** v1 ontology and indicator dictionary are frozen, versioned and externally reviewed; all gold data map to them; compatibility rules for 1.x are published.

**Leading indicators:** unresolved definition questions, unclassified source measures, mapping disagreement rate, late ontology changes.

**Key dependencies:** informs T2, T4, T5 and T6; receives pilot evidence from T2–T5.

## T2 — Jurisdiction universe and source census

**Mission:** establish what every in-scope system reports and what it does not.

**Accountable lead:** global source-census lead.

**Core deliverables:**

- jurisdiction register and institutional maps;
- multilingual source-search protocol and search logs;
- official and supplementary source register;
- negative-findings and inaccessible-source review;
- standard direct-enquiry workflow;
- source coverage atlas and review-cycle status;
- local verification and evidence of unresolved ambiguity.

**v1.0 definition of done:** every jurisdiction has exactly one reviewed current status; all negative findings have second review; federal/devolved systems are represented at the responsible level; known language/coverage gaps are visible.

**Leading indicators:** percentage of universe searched, second-review backlog, jurisdictions without local verification, unanswered enquiries, source aging.

**Key dependencies:** T1 scope, T9 regional network, T3 preservation, T5 review.

## T3 — Acquisition, preservation and source monitoring

**Mission:** obtain source evidence lawfully and keep it verifiable over time.

**Accountable lead:** data acquisition lead.

**Core deliverables:**

- connectors for APIs/files/HTML and controlled procedures for dashboards/PDFs;
- retrieval manifests, query/filter records, checksums and source versions;
- rights/redistribution flags and storage routing;
- immutable source snapshots where lawful;
- public content-addressed B0 custody with native payloads or WARC/WACZ and
  two provider-separated retrieval receipts;
- source-drift, stale-source and broken-link monitoring;
- retry, rate-limit and failure-handling standards;
- acquisition runbooks and connector ownership.

**v1.0 definition of done:** every released source has sufficient evidence to reproduce or verify extraction; every public-safe exact edition is restorable from two public providers without a local cache; high-priority machine-accessible sources are monitored; prohibited material is rejected rather than retained in a hidden local archive; connector failures are observable and owned.

**Leading indicators:** acquisition success, unpreserved sources, stale high-priority sources, connector incident age, manual extraction share.

**Key dependencies:** T2 source register, T7 rights/security, T4 platform, T8 monitoring.

## T4 — Data platform and engineering

**Mission:** make the data pipeline reproducible, testable and supportable.

**Accountable lead:** technical lead.

**Core deliverables:**

- stable identifiers and data contracts;
- B0 preservation, B1 Bronze, Silver, Gold and Platinum storage model with
  quarantine as an orthogonal state;
- transformation pipelines and metadata lineage;
- validation, compatibility and migration tests;
- development/test/release environments;
- release builder, checksums, signatures and software bill of materials;
- portable CSV/Parquet/DuckDB/metadata outputs;
- generation of website/API/dashboard from release artefacts.
- DCAT-AP, Croissant, RO-Crate, PROV-O and OpenLineage-compatible federation
  outputs with content-addressed zero-copy Parquet references.

**v1.0 definition of done:** a clean-room build succeeds from public archives alone; every medallion layer is independently qualified; core contracts are frozen; tests protect critical logic; derived services regenerate from immutable release files; current and prior minor releases remain reproducible.

**Leading indicators:** build success, flaky tests, undocumented manual steps, contract changes, pipeline runtime/failure, technical debt affecting gates.

**Key dependencies:** T1 contracts, T3 acquisition, T5 quality rules, T7 supply-chain controls, T8 release operations.

## T5 — Harmonisation, quality and assurance

**Mission:** prevent data error and false comparison from reaching public products.

**Accountable lead:** quality and methods assurance lead.

**Core deliverables:**

- bronze/silver/gold promotion rules and quarantine process;
- automated validity, range, temporal and referential checks;
- mapping/transformation review workflow;
- dual-review ledger and adjudication process;
- risk-based independent re-extraction sample;
- quality scorecard, release diff and anomaly review;
- independent layer-maturity qualification that cannot use later-layer or
  publication success as evidence for an earlier layer;
- external methodological assurance and response.

**v1.0 definition of done:** all gold series pass dual review; audit thresholds pass; no P0/P1 data defect is open; comparability controls are enforced in files and interfaces; quality evidence is public.

**Leading indicators:** review backlog, correction rate, audit concordance, quarantine volume, anomaly resolution time, gold promotion throughput.

**Key dependencies:** T1 rules, T2/T3 evidence, T4 automation, T6 presentation tests.

## T6 — Product, documentation and accessibility

**Mission:** make the project useful while preserving definitions, uncertainty and context.

**Accountable lead:** product/publication lead.

**Core deliverables:**

- release package and data dictionary;
- source census/availability atlas;
- outcomes evidence catalogue interface;
- jurisdiction profiles and methods handbook;
- constrained comparison explorer and/or API;
- accessibility and usability testing;
- citation, limitations and responsible-use guidance;
- downloadable machine-readable and human-readable outputs.
- public Hugging Face source-archive, catalogue, medallion, evidence and
  Gold/Platinum product roles registered in the dataset estate registry.

**v1.0 definition of done:** all four products are complete; every visual/table exposes source and definition; core interfaces pass adopted accessibility assessment; users can obtain data without proprietary tools; public beta feedback is dispositioned.

**Leading indicators:** documentation completeness, accessibility defects, task success in user testing, unsupported interpretation questions, download/API failures.

**Key dependencies:** T1 methods, T4 release artefacts, T5 comparability, T9 localisation, T8 publication operations.

## T7 — Security, privacy, legal and supply-chain assurance

**Mission:** protect children/families, source rights, credentials, infrastructure and release integrity.

**Accountable lead:** security/privacy/data-governance owner.

**Core deliverables:**

- aggregate/public-data boundary and prohibited-data rules;
- threat model and privacy/disclosure impact assessment;
- licence/rights register and takedown process;
- pre-publication prohibited-data, secret, small-cell and identifying-content
  scans for every source and derived object;
- secret, dependency, artefact and supply-chain scanning;
- access-control and credential-management standards;
- small-cell, dominance and contextual-harm review;
- vulnerability/privacy incident response;
- release signing/provenance attestation.

**v1.0 definition of done:** no prohibited data or unresolved critical finding; rights review complete; response channels tested; release artefacts signed/checksummed; access and incident controls are operational.

**Leading indicators:** unresolved findings, rights-unknown sources, access-review exceptions, scan failures, incident exercise actions.

**Key dependencies:** T0 governance, T3 source handling, T4 build, T5 disclosure checks, T8 incidents.

## T8 — Operations, reliability and release management

**Mission:** turn the project into a repeatable public service.

**Accountable lead:** service/release manager.

**Core deliverables:**

- release calendar, change windows and release checklist;
- correction, incident, source-drift and publication ticket flows;
- monitoring, alert ownership and operational dashboards;
- backups, archival deposits and restore testing;
- provider-separated public custody and anonymous restore testing with no
  durable local-only source of truth;
- append-only correction, withdrawal, tombstone and supersession operations;
- rollback/republish and business-continuity procedures;
- support rota, runbooks and service objectives;
- post-release review and problem management.

**v1.0 definition of done:** release rehearsal and restore test pass; no critical process has a bus factor of one; correction and incident channels meet test objectives; 12-month release calendar and operational budget are approved.

**Leading indicators:** unowned alerts, restore age, correction response time, source incident backlog, failed scheduled jobs, runbook freshness.

**Key dependencies:** T0 resources, T3 monitoring, T4 release tooling, T7 incident controls, T9 continuity.

## T9 — International community, localisation and sustainability

**Mission:** build the local knowledge, legitimacy and resources needed for a durable global product.

**Accountable lead:** international partnerships and sustainability lead.

**Core deliverables:**

- regional/jurisdiction correspondent model and agreements;
- paid local-language/legal verification;
- translation glossary and human review process;
- contributor onboarding, training and recognition;
- inclusive public-beta and lived-experience engagement;
- host/funding/partnership strategy and maintenance budget;
- impact, misuse and benefits evaluation plan;
- succession and regional-capacity plan.
- cross-repository federation registry, interoperability contracts and
  canonical ownership boundaries.

**v1.0 definition of done:** launch languages and key translations are reviewed; regional representation is documented; correspondent and contributor processes function; critical knowledge is not concentrated in one institution; 12-month maintenance resources are committed.

**Leading indicators:** regional coverage gaps, translation review backlog, contributor retention, participation diversity, funding runway and key-person exposure.

**Key dependencies:** T0 governance, T1 terminology, T2 verification, T6 localisation and T8 handover.

## Cross-track integration rituals

- Weekly delivery integration: track leads surface blockers and interface changes.
- Fortnightly methods/data design review: T1, T2, T3, T4 and T5.
- Monthly programme assurance: evidence against gates, risks and maturity.
- Quarterly public methods/governance update during beta and later.
- Formal design freeze and change-control board from v0.7 onward.
- Independent assurance at G2 sample, G5 release candidate and G6 go-live.
