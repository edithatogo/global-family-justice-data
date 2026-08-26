# Roadmap to a stable v1.0

## 1. Release intent

Version 1.0 is not merely the first time the project publishes a global table. It is the first release that can be treated as a **stable, governed and supportable international public-data product**.

A v1.0 release must be:

- methodologically defensible;
- reproducible from preserved source evidence;
- operationally maintainable under the documented sole-owner model, with reproducible agent-supported continuity and an unavailable-owner pause;
- secure and privacy-preserving by design;
- explicit about coverage, missingness and comparability;
- backwards-compatible throughout the 1.x line;
- reviewed by role-separated analyst-agent panels and accepted by the sole accountable owner before publication;
- accompanied by a funded maintenance and correction process.

The authoritative v1.0 product is a set of immutable, versioned release artefacts. The website, dashboard and API are derived access channels rather than the sole copy of the data.

## 2. What v1.0 contains

The stable v1.0 product has four linked components:

1. **Global source census** — every approved jurisdiction has a documented coverage status and search record.
2. **Harmonised core dataset** — comparable process and performance observations for eligible jurisdictions and indicators.
3. **Outcomes evidence catalogue** — a structured register of administrative-outcome, user-experience, child and family outcome studies and datasets.
4. **Context library** — versioned jurisdiction profiles explaining institutions, matter types, procedural clocks, reforms and breaks in series.

The source census is global. The comparative dataset is deliberately narrower: only observations that pass the gold-layer rules are included. v1.0 does not imply that every jurisdiction publishes every outcome or that all measures can be ranked.

## 3. Programme tracks

| Track | Purpose | v1.0 end-state |
|---|---|---|
| T0. Governance, ethics and independence | Establish authority, accountability and safeguards | Named accountable bodies, published decisions, conflicts register, ethics and corrections processes, funded operating model |
| T1. Scope, ontology and methods | Define what is being measured and how | Stable v1 matter taxonomy, indicator dictionary, clocks, comparability rules and documented change control |
| T2. Jurisdiction universe and source census | Search every in-scope system consistently | 100% of the approved universe has a reviewed coverage status, search log and institutional map |
| T3. Acquisition, preservation and source monitoring | Obtain and preserve source evidence | Public content-addressed B0 custody, two provider-separated replicas, anonymous restore, immutable snapshots and drift monitoring without local-only authority |
| T4. Data platform and engineering | Transform source-native material into federated release data | Executable B0/B1 Bronze/Silver/Gold/Platinum contracts, stable IDs, field lineage, deterministic replay and portable formats |
| T5. Harmonisation, quality and assurance | Control errors and prevent false comparison | Independent layer qualification, role-separated agent review, audit sampling, orthogonal quarantine and owner-adjudicated Gold promotion |
| T6. Product, documentation and accessibility | Make the evidence usable without hiding uncertainty | Public role-separated Hugging Face datasets, downloadable Gold/Platinum products, accessible explorer, documentation and clear limitations |
| T7. Security, privacy, legal and supply-chain assurance | Protect people, credentials, sources and infrastructure | Prohibited-data, secret, disclosure, archive-safety and supply-chain checks for every public source and derived object |
| T8. Operations, reliability and release management | Make public custody and releases routine rather than heroic | Provider-separated public custody, anonymous restore, correction, tombstone, supersession, monitoring and unavailable-owner pause |
| T9. International community, localisation and sustainability | Build durable jurisdiction knowledge, legitimacy and federation | Source-language review, interoperable dataset-estate registration, canonical ownership boundaries and a resourced 1.x maintenance plan |

Detailed track charters are in `docs/programme/track-charters.md`. Machine-readable definitions are authoritative in `config/tracks.toml`; delivery state is held in `programme/work_items.csv`.

## 4. Integrated release sequence

The schedule is expressed from programme mobilisation. A well-resourced programme should plan for approximately 24 months to a mature v1.0 rather than relabelling an early pilot as stable.

| Release / gate | Indicative period | Purpose | Exit condition |
|---|---:|---|---|
| **v0.1 — concept scaffold** | Existing baseline | Initial schemas, seed registers and methods concept | Repository can represent the proposed work |
| **v0.3 — engineering/conductor baseline** | Current | Establish executable contracts, conductor, acquisition, promotion, validation and deterministic release tooling | Toolchain works and honestly reports missing assurance; no gate is implied to have passed |
| **v0.4 — controlled foundation / G1** | Months 0–2 | Establish programme authority and accept foundation controls | Charter, ownership, jurisdiction-universe rule, v1 scope, risk register, architecture and release criteria are accepted by the sole accountable owner after role-separated agent-panel advice |
| **v0.5 — reproducible pilot alpha / G2** | Months 2–6 | Prove complete lineage in heterogeneous pilot systems | Approved bounded pilot profiles; representative source-format paths; clean rebuild; blinded role-separated agent re-extraction; no unresolved critical design defect |
| **v0.6 — global census beta / G3** | Months 5–12 | Complete the global discovery and coverage layer | Every in-scope jurisdiction has a reviewed status; negative findings are second-reviewed; source register and atlas are publishable |
| **v0.7 — feature-complete public beta / G4** | Months 8–16 | Make the end-to-end product feature-complete | Core pipelines, outcomes catalogue, downloads, profiles and public beta access work in a production-like environment |
| **v0.9 — release candidate / G5** | Months 15–21 | Freeze scope and harden quality, security and operations | Feature freeze; migration rehearsal; role-separated agent-panel assurance advice and owner adjudication; restore test; no open P0/P1 defects; v1 evidence pack complete |
| **v1.0 — stable release / G6** | Months 21–24 | Publish and transition into routine service | Every mandatory criterion in `V1_0_RELEASE_CRITERIA.md` passes and release authority signs the go-live record |
| **v1.1+ — supported maintenance** | After v1.0 | Scheduled updates and non-breaking improvements | Published release calendar, patch support and annual methods review operate to service objectives |

Versions are capability markers, not calendar promises. The v0.3 tooling baseline intentionally precedes G1. A programme release does not advance because time has elapsed or code exists; it advances only when the conductor shows that required evidence and controls are accepted and the authorised gate decision is recorded.

## 5. Stage gates

### G0 — mobilisation authorised

Required evidence:

- confirmed host or interim legal custodian;
- executive sponsor and programme lead;
- initial funding and procurement authority;
- agreement that the public repository contains aggregate data only;
- approval to begin the pilot.

### G1 — controlled foundation

Required evidence:

- signed charter and decision-rights model;
- approved v1 product boundary and non-goals;
- approved jurisdiction-universe rule and subnational treatment;
- architecture, security baseline, data-governance plan and risk register;
- stable identifiers and draft v1 data contracts;
- the sole accountable owner for every critical track, the explicit no-deputy exception and the unavailable-owner pause.

### G2 — reproducible pilot alpha

Required evidence:

- 12 heterogeneous jurisdictions mapped;
- at least five reporting years attempted under a documented protocol;
- API, spreadsheet/HTML and PDF/dashboard acquisition patterns tested;
- bronze-to-gold lineage demonstrated for representative indicators;
- dual review completed for all pilot gold series;
- blinded role-separated agent re-extraction sample meets the quality threshold and is owner-adjudicated;
- design changes from the pilot are resolved or explicitly deferred.

### G3 — global census beta

Required evidence:

- 100% of the approved jurisdiction universe has a coverage record;
- every “no public source found” conclusion has a second-review search log;
- federal and devolved systems are represented at the responsible level;
- language and regional coverage gaps are visible and owned;
- source register, search protocol and coverage atlas pass public-beta review.

### G4 — feature complete

Required evidence:

- all v1 data products exist in production-like form;
- stable API/file contracts and migration scripts are tested;
- outcomes evidence catalogue and context profiles are integrated;
- accessibility and localisation reviews are complete for launch materials;
- operational monitoring, source drift detection and correction workflow are running;
- the v1 comparative cohort is frozen for release-candidate assurance.

### G5 — release candidate

Required evidence:

- feature, schema and ontology freeze;
- clean-room build reproduces release artefacts and checksums;
- full licence, privacy and disclosure review;
- threat model and dependency/supply-chain review updated;
- backup restoration and continuity exercise completed;
- role-separated agent-panel methodological review, owner adjudication and limitations response completed;
- all P0 and P1 issues closed; P2 issues have accepted dispositions;
- user documentation, limitations, citations and correction channels are complete.

### G6 — v1.0 release authority

Required evidence:

- all mandatory v1 criteria pass;
- release candidate has completed at least 30 calendar days of production-like stability soak with no P0/P1 regression or material data-contract/pipeline instability;
- role-separated agent-panel release assurance advice is complete and the owner has adjudicated every finding;
- the sole accountable owner signs the digest-bound go-live record;
- 12-month operating plan, release calendar and maintenance funding are approved;
- immutable artefacts, signatures, checksums and archival deposit are created.

## 6. Critical path

The critical path is:

1. jurisdiction-universe and matter-scope decisions;
2. ontology and stable identifier design;
3. heterogeneous pilot and design correction;
4. global source census;
5. production acquisition and provenance controls;
6. harmonisation and gold promotion;
7. public beta and comparative-cohort freeze;
8. role-separated agent-panel assurance advice, owner adjudication, operational rehearsal and release candidate;
9. v1.0 publication and service handover.

Dashboard polish, optional analytics and secondary indicator families must not displace this path.

## 7. v1.0 release scope control

### Must ship

- global coverage-status register;
- source register with exact provenance and rights metadata;
- stable jurisdiction, matter, source, indicator and observation identifiers;
- core process/performance dataset in open tabular and analytical formats;
- outcomes evidence catalogue;
- jurisdiction profiles and methods handbook;
- reproducible build, validation report and data-quality statement;
- immutable release bundle, checksums, citation file and archive record;
- public correction, security and governance channels.

### Should ship

- public data-availability atlas;
- documented API or query layer;
- multilingual contributor and methodology summaries;
- source-change alerts and connector health dashboard;
- comparison explorer constrained by comparability tier.

### May follow in 1.x

- additional matter types and historical backfill;
- richer demographic stratification after disclosure review;
- automated translation assistance with source-language agent review and authoritative-reference triangulation;
- more advanced visual analytics;
- selected linked-data study metadata.

### Explicitly outside v1.0

- a composite international league table;
- causal claims from descriptive court statistics;
- identifiable or linkable person-level court records in the public repository;
- forced imputation of unpublished outcomes;
- pretending that a missing source is equivalent to zero activity;
- a breaking replacement of local definitions by an English harmonised label.

## 8. Stable 1.x support policy

After v1.0:

- stable IDs and public schemas are backwards-compatible throughout 1.x;
- corrections to released values use patch releases and never silently overwrite history;
- additive indicators or fields use minor releases;
- removals or semantic changes require deprecation and normally wait for v2.0;
- release artefacts remain available permanently;
- at least the current and immediately previous minor release receive correction support;
- a role-separated methods-agent panel reviews ontologies annually and the owner records every decision;
- the project issues at least two scheduled data releases per year, with urgent patch releases when material errors require them.

## 9. No-go conditions for v1.0

Release is blocked if any of the following remains true:

- the jurisdiction universe or inclusion rule is materially unresolved;
- a gold observation cannot be traced to preserved source evidence;
- critical calculations cannot be reproduced in a clean environment;
- personal, sealed or unlawfully redistributed data are present;
- a critical or high-impact security issue is unresolved without formal acceptance;
- release licences or source rights are unclear for core artefacts;
- the comparative product presents incompatible clocks, denominators or matter types as equivalent;
- there is no named operational owner or funded maintenance plan;
- the backup/restore path has not been tested;
- agent-panel assurance advice identifies a material issue that has neither been fixed nor transparently adjudicated by the owner.

## 10. Programme health indicators

The owner should review a compact scorecard each month, informed by role-separated agent-panel analysis:

- jurisdiction coverage and second-review completion;
- source acquisition and preservation success;
- gold-series throughput and review backlog;
- automated validation pass rate;
- role-separated blinded re-extraction concordance;
- connector/source-drift incidents and time to resolution;
- unresolved P0–P2 defects;
- translation/local-review coverage;
- contributor and regional-representation metrics;
- budget, staffing, key-person dependencies and maintenance runway.

A green schedule with weak evidence quality is not a successful programme.
