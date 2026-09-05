# Recorded completed work

Generated from [the canonical register](../../../programme/work_items.csv). No record, dependency or historical evidence is removed.

30 of 81 work items. [Other view](active-work.md).

Recorded acceptance is not renewed assurance, gate passage or track archival. Items in review stay active even when implementation tests pass.

| Track | Recorded accepted | Total | Whole-track archive eligible |
|---|---:|---:|---|
| T0 | 3 | 11 | no |
| T1 | 2 | 3 | no |
| T2 | 5 | 8 | no |
| T3 | 3 | 5 | no |
| T4 | 6 | 10 | no |
| T5 | 6 | 14 | no |
| T6 | 0 | 9 | no |
| T7 | 4 | 8 | no |
| T8 | 1 | 8 | no |
| T9 | 0 | 5 | no |

| Work item | Track/gate | Status | Title | Evidence IDs | Dependencies |
|---|---|---|---|---|---|
| WI-G1-01 | T0/G1 | accepted | Host, sponsor, programme charter and owner-held decision rights are formally accepted. | E-GOV-CHARTER |  |
| WI-G1-02 | T1/G1 | accepted | Scope, unit of analysis, v0.3 ontology and indicator framework are approved for the pilot. | E-METHODS-SCOPE; E-INDICATOR-FRAMEWORK |  |
| WI-G1-03 | T7/G1 | accepted | Aggregate-only public boundary, ethics principles and prohibited-data rules are accepted. | E-ETHICS-BOUNDARY; E-SECURITY-POLICY |  |
| WI-G1-04 | T4/G1 | accepted | Target architecture, contracts, environments and release-authority model are approved. | E-ARCH-V1 |  |
| WI-G1-05 | T0/G1 | accepted | Every critical track has an accountable owner, an explicit deputy exception and escalation route. | E-RACI; E-TRACK-CHARTERS |  |
| WI-G1-06 | T7/G1 | accepted | Initial risk, threat, rights and disclosure-control baselines are documented. | E-RISK-REGISTER; E-THREAT-BASELINE; E-RIGHTS-BASELINE |  |
| WI-G1-07 | T4/G1 | accepted | The conductor can validate programme state, calculate gate readiness and render an evidence-linked status report. | E-CONDUCTOR-BASELINE |  |
| WI-G1-08 | T2/G1 | accepted | Pilot jurisdiction universe and source-language authoritative-triangulation strategy are approved. | E-PILOT-UNIVERSE |  |
| WI-G1-CLOSE | T0/G1 | accepted | Assemble and approve the G1 gate evidence pack |  | WI-G1-01 (accepted); WI-G1-02 (accepted); WI-G1-03 (accepted); WI-G1-04 (accepted); WI-G1-05 (accepted); WI-G1-06 (accepted); WI-G1-07 (accepted); WI-G1-08 (accepted) |
| WI-G2-01 | T2/G2 | accepted | The approved bounded pilot cohort has institutional maps, search logs and reviewed coverage states. | E-PILOT-CENSUS | WI-G1-CLOSE (accepted) |
| WI-G2-02 | T3/G2 | accepted | Representative API, spreadsheet, HTML/dashboard and PDF/manual acquisition paths have reproducible manifests. | E-PILOT-ACQUISITION | WI-G1-CLOSE (accepted) |
| WI-G2-03 | T4/G2 | accepted | A representative bronze-to-silver-to-gold pipeline builds deterministically from frozen pilot inputs. | E-PILOT-PIPELINE; E-CLEAN-BUILD | WI-G1-CLOSE (accepted) |
| WI-G2-05 | T1/G2 | accepted | Pilot evidence has been used to resolve material ontology, clock, denominator and missingness questions. | E-PILOT-METHODS-ADJUDICATION | WI-G1-CLOSE (accepted) |
| WI-G2-06 | T7/G2 | accepted | Pilot source rights, privacy, security and disclosure assessments have no unresolved critical finding. | E-PILOT-RIGHTS-SECURITY | WI-G1-CLOSE (accepted) |
| WI-G2-08 | T8/G2 | accepted | The pilot release process, correction path and restoration of its artefacts have been rehearsed. | E-PILOT-OPERATIONS-REHEARSAL | WI-G1-CLOSE (accepted) |
| WI-G2-09 | T2/G2 | accepted | Prepare a materially distinct non-search blind-holdout method option set for future owner authorization. | E-G2-METHODS-DISTINCT-PROPOSAL-20260818; E-G2-METHODS-DISTINCT-ADVISORY-REVIEW-20260819; E-G2-METHODS-DISTINCT-OPS-EXPOSURE-REVIEW-20260819; E-G2-METHODS-DISTINCT-GOV-REVIEW-20260819 | WI-G2-07 (in_review) |
| WI-G2-10 | T2/G2 | accepted | Prepare a reusable single-decision G2 evidence-campaign protocol without external activity. | E-G2-EVIDENCE-CAMPAIGN-PROTOCOL-20260820 | WI-G2-09 (accepted) |
| WI-G2-11 | T2/G2 | accepted | Validate offline non-exposed candidate metadata before a future G2 campaign. | E-G2-OFFLINE-CANDIDATE-INTAKE-20260820 | WI-G2-10 (accepted) |
| WI-G2-12 | T5/G2 | accepted | Convert terminal concordance differences into a source-independent atomic field contract and executable tests. | E-G2-ATOMIC-FIELD-CONTRACT-20260826 | WI-G2-07 (in_review) |
| WI-G2-13 | T5/G2 | accepted | Operate a prospective official structured publication-index monitor with explicit publisher timestamps. | E-G2-FUTURE-OFFICIAL-FEED-PREPARATION-20260829; E-G2-FUTURE-OFFICIAL-FEED-OBSERVATION-20260829 | WI-G2-12 (accepted) |
| WI-G2-14 | T5/G2 | accepted | Operate an exact-product Statistics Canada family-law metadata monitor. | E-G2-STATCAN-METADATA-PREPARATION-20260829; E-G2-STATCAN-METADATA-OBSERVATION-20260829 | WI-G2-13 (accepted) |
| WI-G2-15 | T5/G2 | accepted | Operate an exact New Zealand justice-statistics index monitor. | E-G2-NZ-JUSTICE-INDEX-PREPARATION-20260829; E-G2-NZ-JUSTICE-INDEX-OBSERVATION-20260829 | WI-G2-14 (accepted) |
| WI-G2-16 | T5/G2 | accepted | Operate an exact UK family-court release-calendar monitor. | E-G2-UK-FAMILY-CALENDAR-PREPARATION-20260829; E-G2-UK-FAMILY-CALENDAR-OBSERVATION-20260829 | WI-G2-15 (accepted) |
| WI-G2-17 | T5/G2 | accepted | Consolidate a changed three-root lastmod tuple and operate a distinct cumulative-exposure successor. | E-G2-THREE-ROOT-LASTMOD-CONSOLIDATION-20260830 | WI-G2-16 (accepted) |
| WI-G3-MED-00 | T4/G3 | accepted | Adopt the maximal public preservation-first medallion and federation architecture. | E-PUBLIC-MEDALLION-POLICY-20260826 | WI-G1-CLOSE (accepted) |
| WI-G3-MED-01 | T3/G3 | accepted | Create the public B0 exact-edition archive and migrate every public-safe source object from local-only custody. | E-PUBLIC-B0-PRESERVATION | WI-G3-MED-00 (accepted) |
| WI-G3-MED-02 | T3/G3 | accepted | Operate append-only public source monitoring, replay and supersession. | E-PUBLIC-PRESERVATION-MONITORING | WI-G3-MED-01 (accepted) |
| WI-G3-MED-03 | T7/G3 | accepted | Enforce the public archive safety boundary across source and derived objects. | E-PUBLIC-ARCHIVE-SAFETY | WI-G3-MED-00 (accepted) |
| WI-G4-MED-01 | T4/G4 | accepted | Implement executable B0, B1 Bronze, Silver, Gold, Platinum and orthogonal quarantine contracts. | E-MEDALLION-LAYER-CONTRACTS | WI-G3-MED-01 (accepted); WI-G3-MED-03 (accepted) |
| WI-G4-MED-06 | T4/G4 | accepted | Implement shared cross-repository medallion schema compatibility. | E-SHARED-MEDALLION-SCHEMA-COMPAT-20260903 | WI-G4-MED-01 (accepted) |
