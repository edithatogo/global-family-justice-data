# v1.0 release criteria

## 1. Purpose

This document is the binding definition of done for the first stable release. `ROADMAP.md` explains how the project reaches v1.0; this file defines the evidence required to call the release stable.

A criterion is **mandatory** unless explicitly marked “target”. Release authority may not waive a mandatory criterion informally. Any exception requires a public decision record describing the risk, compensating control, owner and expiry date.

## 2. Release decision model

Five accountable owners sign the release evidence pack:

- **Data owner** — coverage, provenance, rights and release contents;
- **Methods owner** — ontology, indicators, comparability and interpretation;
- **Technical owner** — build, schemas, software and service readiness;
- **Security/privacy owner** — security, disclosure, legal and incident readiness;
- **Executive release owner** — resources, independence and operational sustainability.

An independent release assurer checks the evidence and provides a recommendation. The executive release owner makes the final go/no-go decision but cannot redefine a failed criterion after the fact.

## 3. Mandatory acceptance criteria

### A. Product scope and coverage

| ID | Criterion | Evidence |
|---|---|---|
| A1 | The approved jurisdiction universe is versioned, machine-readable and includes the rule for sovereign, dependent and subnational systems. | Jurisdiction register, scope decision record and version tag |
| A2 | Every in-scope jurisdiction has exactly one current coverage status. | Automated completeness report |
| A3 | Every “no public source found” or “source inaccessible” conclusion has a completed search log and second reviewer. | Review report and sampled search logs |
| A4 | All four v1 products exist: source census, core dataset, outcomes catalogue and context library. | Release inventory |
| A5 | The v1 analytical cohort is explicitly listed; inclusion is based on published quality/comparability rules rather than prestige or convenience. | Cohort manifest and methods note |
| A6 | Known geographic, language, matter-type and outcome gaps are published. | Coverage and limitations report |

### B. Provenance, integrity and reproducibility

| ID | Criterion | Evidence |
|---|---|---|
| B1 | Every released observation has a valid source ID and exact provenance locator. | Automated lineage report |
| B2 | Every released source has publisher, canonical location, retrieval date, rights status and preservation/checksum metadata. | Source validation report |
| B3 | Stable IDs are unique, documented and not reused after retirement. | ID audit |
| B4 | A clean environment can rebuild all derived release artefacts from the approved inputs and produce the expected checksums, except where a documented non-deterministic field is deliberately excluded. | Clean-room build log |
| B5 | All release files pass schema, referential-integrity, type, range, duplication and temporal-consistency checks. | CI and release validation reports |
| B6 | Transformations from bronze to silver to gold are code- or rule-driven, versioned and reviewable. | Pipeline lineage and transformation registry |
| B7 | No released value has been silently overwritten; corrections are represented through versioned releases and changelog entries. | Release-history audit |

### C. Methodological quality and comparability

| ID | Criterion | Evidence |
|---|---|---|
| C1 | Matter taxonomy, indicator dictionary, duration clocks, cohort bases and denominator rules are frozen for v1.0. | Versioned methods bundle |
| C2 | Every gold series has a quality grade, comparability tier, inclusion/exclusion definition and named review record. | Gold promotion report |
| C3 | Every gold series has been independently second-reviewed at source/series level; all observations receive automated checks. | Review ledger |
| C4 | A risk-based independent re-extraction sample achieves at least 99% exact concordance for values and provenance, with 100% concordance on critical classification fields. Any failure triggers root-cause analysis and expanded sampling. | Assurance sample report |
| C5 | Means, medians, percentiles, threshold rates, prospective waits and pending-case ages remain distinct in storage and presentation. | Schema test and product review |
| C6 | Tier 3 and Tier 4 observations are not displayed as directly comparable; Tier 2 transformations are visible. | Comparative-output test |
| C7 | External methodological review has been completed and the project response is public. | Review and response document |

### D. Security, privacy, ethics and legal readiness

| ID | Criterion | Evidence |
|---|---|---|
| D1 | The public release contains no identifiable or linkable person-level case records, sealed material, credentials or secrets. | Automated scans and manual disclosure review |
| D2 | A current threat model and privacy/disclosure impact assessment cover repository, storage, pipelines, website/API and contributor workflows. | Approved assessments |
| D3 | Source rights and redistribution status are recorded; restricted raw materials are excluded from public artefacts. | Rights register and legal review |
| D4 | Critical dependencies and build actions are inventoried; dependency, secret and supply-chain scans have no unresolved critical finding and no unaccepted high-impact finding. | Security scan bundle |
| D5 | Release artefacts have checksums and cryptographic signatures or equivalent provenance attestations. | Signed release manifest |
| D6 | Vulnerability, privacy incident and takedown/reporting channels are published and tested. | Exercise record and `SECURITY.md` |
| D7 | Small-cell, dominance and contextual-harm rules have been applied where disaggregation could expose children or families. | Disclosure-control report |
| D8 | Conflicts of interest, funders and institutional participation are disclosed. | Governance disclosure |

### E. Software, architecture and service readiness

| ID | Criterion | Evidence |
|---|---|---|
| E1 | Release artefacts are the system of record; dashboard and API can be regenerated from them. | Architecture test and deployment record |
| E2 | Public schemas and file contracts are documented and versioned; compatibility tests protect the 1.x contract. | Contract tests and compatibility report |
| E3 | CI runs validation, tests, static checks and release-build verification on protected branches. | Branch protection and CI evidence |
| E4 | Critical validation and transformation logic is covered by automated tests and representative golden fixtures; the G5 coverage and mutation-testing thresholds in `docs/quality/testing-strategy.md` are met without a release-blocking exception. | Test, coverage and mutation report |
| E5 | Production configuration and secrets are separated from source code and use least-privilege access. | Configuration review |
| E6 | Logging and monitoring detect failed builds, stale sources, connector drift and publication failures without recording sensitive content. | Monitoring demonstration |
| E7 | A production-like release rehearsal and rollback/republication exercise has succeeded. | Rehearsal record |

### F. Operations, resilience and support

| ID | Criterion | Evidence |
|---|---|---|
| F1 | Release, correction, incident, source-change, access-review, backup and restore runbooks are approved. | Operations handbook |
| F2 | Immutable release artefacts exist in at least two independently administered locations, one of which is an archival deposit. | Preservation report |
| F3 | Backup restoration has been tested; target recovery is no more than two business days for public access services, with no loss of an immutable release. | Restore-test report |
| F4 | A support rota has a primary and deputy for every critical operational process. | On-call/ownership matrix |
| F5 | Public correction reports are acknowledged within five working days and receive a disposition or progress update within 30 calendar days. | Service policy and test ticket |
| F6 | A 12-month release calendar and maintenance budget are approved. | Operating plan |
| F7 | The v1.0 candidate and most recent prior public release can be reproduced and served; after v1.1, the current and previous minor release remain supported. | Reproducibility exercise |

### G. Documentation, accessibility and international usability

| ID | Criterion | Evidence |
|---|---|---|
| G1 | README, methods, data dictionary, source register, quality statement, limitations and citation guidance are complete. | Documentation inventory |
| G2 | Release data are available in at least one simple open tabular format and one efficient analytical format, without proprietary software. | Release bundle |
| G3 | Original-language source labels are retained and English translations are separated and reviewable. | Data/schema inspection |
| G4 | Core public interfaces and documents pass the host’s adopted AA accessibility assessment. | Accessibility report |
| G5 | Contributor guidance and the high-level methods summary are available in the programme’s selected launch languages, with human translation review. | Localisation report |
| G6 | Every chart/table exposes definitions, period, unit, source and comparability limitations. | Product QA report |

### H. Governance, people and sustainability

| ID | Criterion | Evidence |
|---|---|---|
| H1 | Steering, methods, data operations and lived-experience/child-rights advisory bodies have current terms of reference and published membership or role disclosure. | Governance pack |
| H2 | Decision rights, escalation and release authority are unambiguous. | RACI and charter |
| H3 | Critical methods, build and release processes each have a documented deputy and handover material; no critical process has a bus factor of one. | Continuity assessment |
| H4 | Regional and jurisdiction verification is materially represented in release review, including paid expertise where appropriate. | Participation report |
| H5 | The v1.0 operating model has committed resources for at least 12 months after release. | Approved budget/work plan |
| H6 | A benefits and harms evaluation plan is approved, including monitoring for misleading comparison or policy misuse. | Evaluation plan |

### I. Stability soak

| ID | Criterion | Evidence |
|---|---|---|
| I1 | The frozen release candidate has operated for at least 30 calendar days under production-like monitoring with no open P0/P1 regression or material contract/pipeline instability. | Stability-soak report |

## 4. Target criteria

The following strengthen v1.0 but may be accepted as managed limitations when the mandatory baseline is met:

- gold-layer comparative data from at least 30 jurisdictions spanning all programme regions;
- at least five years of data for the majority of gold series where source continuity permits;
- public query API in addition to downloadable files;
- automated health monitoring for at least 80% of machine-accessible high-priority sources;
- contributor guidance in at least four working languages;
- two independent external methods reviewers from different legal/data traditions;
- a public beta with documented testing by researchers, court administrators, advocates and people with lived experience.

Targets must never be met by weakening the gold rules or inventing data for silent jurisdictions.

## 5. Defect thresholds

- **P0 — release blocking:** privacy breach, corrupt release, material false comparison, unreproducible core build, unlawful disclosure or loss of authoritative artefact. None may be open.
- **P1 — release blocking:** material data error, broken core contract, missing critical jurisdiction status, unmitigated high-impact security issue or failed restore path. None may be open.
- **P2 — normally blocking:** significant documentation, accessibility, coverage or operational defect. May be accepted only through a time-limited, public decision record with an owner.
- **P3 — non-blocking:** minor defect with no material effect on interpretation, integrity or access. Must be logged and prioritised.

## 6. Release evidence pack

The v1.0 tag must point to an evidence pack containing:

1. signed release decision;
2. release inventory and checksums;
3. clean-room build and validation reports;
4. coverage and negative-findings report;
5. gold promotion and independent audit reports;
6. external methods review and response;
7. security, privacy, rights and disclosure assessments;
8. accessibility and localisation reports;
9. backup/restore and release-rehearsal records;
10. known limitations and open P2/P3 issues;
11. operating plan, release calendar and named owners;
12. archival deposit identifier and citation metadata.
