# Generated programme status

Generated: `2026-08-27T08:36:24+00:00`

Current repository version: **0.6.0-alpha.2**
Declared current gate: **G2**
Conductor validation: **PASS** (0 errors, 0 warnings)

## Gate readiness

| Gate | Target | State | Ready | Decision | Controls complete | Principal blockers |
|---|---:|---|---:|---|---:|---|
| G1 — Foundation controls accepted | 0.4.0 | passed | yes | accepted | 13/13 | — |
| G2 — Reproducible pilot proven | 0.5.0 | blocked_by_maturity | no | not_evaluated | 9/13 | required work not accepted: WI-G2-04; required work not accepted: WI-G2-07; evidence-assured maturity floor L1 is below required L2; +2 more |
| G3 — Global source census complete | 0.6.0 | blocked_by_dependency | no | not_evaluated | 2/13 | dependency gate not accepted: G2; required work not accepted: WI-G3-01; required work not accepted: WI-G3-02; +15 more |
| G4 — Feature-complete public beta | 0.7.0 | blocked_by_dependency | no | not_evaluated | 2/14 | dependency gate not accepted: G3; required work not accepted: WI-G4-01; required work not accepted: WI-G4-02; +21 more |
| G5 — v1.0 release candidate assured | 0.9.0 | blocked_by_dependency | no | not_evaluated | 1/15 | dependency gate not accepted: G4; required work not accepted: WI-G5-01; required work not accepted: WI-G5-02; +41 more |
| G6 — Stable v1.0 go-live | 1.0.0 | blocked_by_dependency | no | not_evaluated | 1/14 | dependency gate not accepted: G5; required work not accepted: WI-G6-01; required work not accepted: WI-G6-02; +37 more |

## Track maturity

| Track | Implemented work | Accepted work | Blocked | Accepted evidence |
|---|---:|---:|---:|---:|
| T0 — Governance, ethics and independence | 11/11 (100.0%) | 3/11 (27.3%) | 0 | 5/21 |
| T1 — Scope, ontology and methods | 3/3 (100.0%) | 2/3 (66.7%) | 0 | 3/5 |
| T2 — Jurisdiction universe and source census | 8/8 (100.0%) | 5/8 (62.5%) | 0 | 8/18 |
| T3 — Acquisition, preservation and source monitoring | 5/5 (100.0%) | 3/5 (60.0%) | 0 | 3/5 |
| T4 — Data platform and engineering | 8/9 (88.9%) | 5/9 (55.6%) | 0 | 6/10 |
| T5 — Harmonisation, quality and assurance | 8/9 (88.9%) | 1/9 (11.1%) | 0 | 8/32 |
| T6 — Product, documentation and accessibility | 7/9 (77.8%) | 0/9 (0.0%) | 0 | 0/9 |
| T7 — Security, privacy, legal and supply-chain assurance | 7/8 (87.5%) | 4/8 (50.0%) | 0 | 7/12 |
| T8 — Operations, reliability and release management | 6/8 (75.0%) | 1/8 (12.5%) | 0 | 1/8 |
| T9 — International community, localisation and sustainability | 4/5 (80.0%) | 0/5 (0.0%) | 0 | 0/6 |

## Evidence-assured maturity

Self-assessed maturity floor: **L1**  
Evidence-assured maturity floor: **L1**

| Dimension | Assessed | Assured | Target |
|---|---:|---:|---:|
| M01 — Governance and independence | L1 | L1 | L5 |
| M02 — Methods and ontology | L2 | L2 | L5 |
| M03 — Jurisdiction census | L1 | L1 | L5 |
| M04 — Acquisition and preservation | L1 | L1 | L5 |
| M05 — Data engineering | L1 | L1 | L5 |
| M06 — Quality and assurance | L1 | L1 | L5 |
| M07 — Product and accessibility | L1 | L1 | L5 |
| M08 — Security, privacy and legal | L1 | L1 | L5 |
| M09 — Operations and reliability | L1 | L1 | L5 |
| M10 — International sustainability | L1 | L1 | L5 |

## Assurance controls

- Risks: **20**; open critical/high: **19**.
- Defects: **1**; open P0/P1: **0**.
- Approved or pending exceptions recorded: **0**.

## Next dependency-ready actions

- **P0 WI-G4-MED-02** (T4/G4): Implement public field lineage, bitemporal snapshot identity and deterministic partition replay. — _planned_
- **P1 WI-G2-04** (T5/G2): Pilot extractions and mappings have documented dual review, adjudication and quarantine outcomes. — _in_review_
- **P1 WI-G2-07** (T5/G2): Blinded role-separated agent re-extraction of the pilot sample passes the approved concordance threshold and is owner-adjudicated. — _in_review_
- **P1 WI-G4-MED-04** (T6/G4): Publish and verify the role-separated GFJD Hugging Face medallion estate. — _planned_

> A gate is ready only after evidence, work, maturity, risk, defect and dependency controls pass. It passes only after a recorded governance decision. Document presence and self-assessment do not constitute acceptance.
