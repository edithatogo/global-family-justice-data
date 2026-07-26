# v1 epic backlog

This is the initial release-level backlog. Each epic should become a GitHub parent issue using the track-epic template and be decomposed into reviewable work packages. The stage gate, not issue count, determines progress.

## Stage A — Foundations and product contract

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E01 Institutional host and charter | T1 | Host, ownership, independence, decision rights, succession | Approved charter and role register |
| V1-E02 v1 product boundary | T2 | Jurisdiction universe, matter scope, evidence types, non-goals | Scope decision and compatibility baseline |
| V1-E03 Public/restricted data boundary | T8 | Aggregate-only public rule and restricted-research separation | Privacy/ethics boundary approval |
| V1-E04 Target architecture and preservation | T7/T11 | Repository, storage, archives, build, backup, and restore design | Architecture decision and tested prototype |
| V1-E05 Regional and language operating model | T10 | Reviewer network, translation process, and coverage safeguards | Capacity map and contracting/onboarding plan |
| V1-E06 Sustainability baseline | T12 | Costed programme and two-cycle maintenance commitment | Approved funding and staffing model |

## Stage B — Controlled pilot

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E07 Pilot institutional maps and search logs | T3 | Complete mapped search across heterogeneous pilot | Reviewed profiles and logs |
| V1-E08 Multi-format source acquisition | T4 | API, spreadsheet, HTML, PDF, and dashboard handled lawfully | Source manifests and reproducible retrievals |
| V1-E09 Outcomes evidence pilot | T5 | Routine reporting separated from surveys/evaluations/cohorts | Reviewed evidence catalogue records |
| V1-E10 End-to-end bronze/silver/gold pilot | T5/T7 | Rebuildable release lineage across pilot | Clean build and lineage report |
| V1-E11 Pilot data-quality and correction rehearsal | T6/T11 | Error detection, double review, adjudication, patch process | Audit and correction exercise records |
| V1-E12 Pilot public product and user test | T9 | Usable downloads, profile, methods, and example analysis | External user reproduction record |

## Stage C — Integrated alpha

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E13 Stable identifiers and registries | T2/T7 | Jurisdiction, institution, source, indicator, evidence, transformation, release IDs | Contract tests and migration policy |
| V1-E14 Acquisition and transformation registry | T4/T5 | Versioned recipes, code paths, parameters, and lineage | Registry completeness report |
| V1-E15 Automated quality framework | T6 | Structural, referential, temporal, numerical, semantic, lineage checks | Test suite and quality outputs |
| V1-E16 Schema compatibility and release packaging | T7 | Repeatable versioned artifacts with checksums and metadata | Alpha release built in CI |
| V1-E17 Source freshness and change detection | T4/T11 | Detect stale, changed, broken, and superseded sources | Monitoring report and triage runbook |
| V1-E18 Methods handbook alpha | T2/T9 | Full definitions, worked valid/invalid comparisons, and caveats | External methods review |

## Stage D — Global public beta

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E19 Complete jurisdiction universe | T3 | Every in-scope national/subnational system represented | Registry coverage report |
| V1-E20 Multilingual global source census | T3/T10 | Search evidence and status for every jurisdiction | Search-log audit and regional gap report |
| V1-E21 Negative-finding second review | T3/T6 | No-source/inaccessible conclusions independently checked | 100% review metric |
| V1-E22 Regionally balanced extraction cohort | T5/T10 | Core reporting extracted beyond the pilot without regional bias | Cohort rationale and coverage dashboard |
| V1-E23 Global outcomes-evidence catalogue beta | T5 | Searchable evidence and gap map across evidence classes | Catalogue quality report |
| V1-E24 Public atlas, profiles, and beta downloads | T9 | Accessible source/evidence discovery and data downloads | Usability/accessibility findings resolved |
| V1-E25 Public feedback and dispute workflow | T1/T10/T11 | Corrections, factual review, methods proposals, disagreement handling | Issue metrics and accepted process |

## Stage E — Feature freeze and hardening

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E26 v1 schema and ontology freeze | T2/T7 | Stable contracts, deprecation, and migration documentation | Freeze decision and compatibility suite |
| V1-E27 Full rights and redistribution review | T8 | Every v1 source/artifact has a documented public-use decision | Rights register with no blocking unknowns |
| V1-E28 Privacy, disclosure, and ethics assurance | T8 | Public outputs pass disclosure and harm review | Signed review and suppression tests |
| V1-E29 Security and supply-chain hardening | T7/T8 | Protected releases, scanning, dependency controls, threat model | Security review with no critical findings |
| V1-E30 Operational resilience | T11 | Monitoring, backup, restore, rollback, correction, withdrawal, incident runbooks | Rehearsal evidence |
| V1-E31 Documentation and accessibility completion | T9 | Complete methods, data contracts, examples, citation, accessible interface | Documentation and accessibility audit |
| V1-E32 Key-person and handover hardening | T1/T11/T12 | Two operators for each critical path and complete handover | Independent operational demonstrations |

## Stage F — Release candidates

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E33 Stratified independent data audit | T6 | Quantified extraction and semantic agreement across formats/languages | Audit threshold met and findings closed |
| V1-E34 Independent methods and governance assurance | T1/T2 | External challenge of scope, comparison, independence, and harms | Review report and response |
| V1-E35 Clean-room reproducibility | T7 | Non-builder reproduces candidate from documented environment | Build record and matching checksums |
| V1-E36 Failure and correction exercises | T8/T11 | Privacy/security incident, source failure, correction, rollback, restore rehearsed | Exercise reports and fixes |
| V1-E37 Release evidence pack | T7/T9/T11 | Notes, limitations, quality, coverage, citation, checksums, archive package | Complete readiness record |
| V1-E38 Consecutive stable candidates | T6/T7/T11 | Two candidate builds without critical regression | RC comparison and go/no-go recommendation |

## Stage G — v1.0 release and Stage H maintenance

| Epic | Track | Outcome | Primary gate evidence |
|---|---|---|---|
| V1-E39 Stable v1 publication | All | One immutable, citable release bundle | Signed release decision and public verification |
| V1-E40 Archive and preservation verification | T11/T12 | Persistent deposit and recoverable source/release metadata | Archive and restore checks |
| V1-E41 Support and correction service activation | T11 | Published channels, severity process, and patch workflow | Operational acceptance test |
| V1-E42 v1 quality and coverage baseline | T6/T12 | Public baseline for freshness, completeness, defects, use, and gaps | Service/quality report |
| V1-E43 First maintenance cycle | T3–T11 | Source refresh, corrections, dependency/security maintenance | v1.0.x release or no-change report |
| V1-E44 v1 evaluation and v1.1 decision | T12 | Evidence-based next-release scope and resourcing | Evaluation, decision record, and roadmap update |

## Release-blocker rule

An epic may be deferred only when the release authority records that:

- the v1 product contract remains intact;
- no mandatory release criterion depends on it;
- the resulting limitation is public and not misleading;
- an owner and target release are assigned.

Epics covering privacy, rights, release reproducibility, gold lineage, critical defects, operational ownership, or institutional release authority cannot be waived from v1.
