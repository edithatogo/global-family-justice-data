# Generated programme status

Generated: `2026-07-19T09:11:48+00:00`

Current repository version: **0.3.0**  
Declared current gate: **G1**  
Conductor validation: **PASS** (0 errors, 0 warnings)

## Gate readiness

| Gate | Target | State | Ready | Decision | Controls complete | Principal blockers |
|---|---:|---|---:|---|---:|---|
| G1 — Foundation controls accepted | 0.4.0 | blocked_by_assurance | no | not_evaluated | 2/13 | required work not accepted: WI-G1-01; required work not accepted: WI-G1-02; required work not accepted: WI-G1-03; +20 more |
| G2 — Reproducible pilot proven | 0.5.0 | blocked_by_dependency | no | not_evaluated | 1/13 | dependency gate not accepted: G1; required work not accepted: WI-G2-01; required work not accepted: WI-G2-02; +21 more |
| G3 — Global source census complete | 0.6.0 | blocked_by_dependency | no | not_evaluated | 1/13 | dependency gate not accepted: G2; required work not accepted: WI-G3-01; required work not accepted: WI-G3-02; +21 more |
| G4 — Feature-complete public beta | 0.7.0 | blocked_by_dependency | no | not_evaluated | 1/14 | dependency gate not accepted: G3; required work not accepted: WI-G4-01; required work not accepted: WI-G4-02; +23 more |
| G5 — v1.0 release candidate assured | 0.9.0 | blocked_by_dependency | no | not_evaluated | 1/15 | dependency gate not accepted: G4; required work not accepted: WI-G5-01; required work not accepted: WI-G5-02; +38 more |
| G6 — Stable v1.0 go-live | 1.0.0 | blocked_by_dependency | no | not_evaluated | 1/14 | dependency gate not accepted: G5; required work not accepted: WI-G6-01; required work not accepted: WI-G6-02; +36 more |

## Track maturity

| Track | Implemented work | Accepted work | Blocked | Accepted evidence |
|---|---:|---:|---:|---:|
| T0 — Governance, ethics and independence | 3/11 (27.3%) | 0/11 (0.0%) | 0 | 0/7 |
| T1 — Scope, ontology and methods | 2/3 (66.7%) | 0/3 (0.0%) | 0 | 0/4 |
| T2 — Jurisdiction universe and source census | 1/5 (20.0%) | 0/5 (0.0%) | 0 | 0/5 |
| T3 — Acquisition, preservation and source monitoring | 0/3 (0.0%) | 0/3 (0.0%) | 0 | 0/3 |
| T4 — Data platform and engineering | 3/6 (50.0%) | 0/6 (0.0%) | 0 | 0/7 |
| T5 — Harmonisation, quality and assurance | 0/7 (0.0%) | 0/7 (0.0%) | 0 | 0/7 |
| T6 — Product, documentation and accessibility | 0/7 (0.0%) | 0/7 (0.0%) | 0 | 0/7 |
| T7 — Security, privacy, legal and supply-chain assurance | 2/6 (33.3%) | 0/6 (0.0%) | 0 | 0/9 |
| T8 — Operations, reliability and release management | 0/6 (0.0%) | 0/6 (0.0%) | 0 | 0/6 |
| T9 — International community, localisation and sustainability | 1/4 (25.0%) | 0/4 (0.0%) | 0 | 0/4 |

## Evidence-assured maturity

Self-assessed maturity floor: **L1**  
Evidence-assured maturity floor: **L0**

| Dimension | Assessed | Assured | Target |
|---|---:|---:|---:|
| M01 — Governance and independence | L1 | L0 | L5 |
| M02 — Methods and ontology | L2 | L0 | L5 |
| M03 — Jurisdiction census | L1 | L0 | L5 |
| M04 — Acquisition and preservation | L1 | L0 | L5 |
| M05 — Data engineering | L2 | L0 | L5 |
| M06 — Quality and assurance | L1 | L0 | L5 |
| M07 — Product and accessibility | L1 | L0 | L5 |
| M08 — Security, privacy and legal | L1 | L0 | L5 |
| M09 — Operations and reliability | L1 | L0 | L5 |
| M10 — International sustainability | L1 | L0 | L5 |

## Assurance controls

- Risks: **20**; open critical/high: **19**.
- Defects: **0**; open P0/P1: **0**.
- Approved or pending exceptions recorded: **0**.

## Next dependency-ready actions

- **P0 WI-G1-01** (T0/G1): Host, sponsor, programme charter and independent decision rights are formally accepted. — _in_review_
- **P0 WI-G1-05** (T0/G1): Every critical track has an accountable owner, deputy and escalation route. — _in_review_
- **P0 WI-G1-02** (T1/G1): Scope, unit of analysis, v0.3 ontology and indicator framework are approved for the pilot. — _in_review_
- **P0 WI-G1-08** (T2/G1): Pilot jurisdiction universe and local-verification strategy are approved. — _in_review_
- **P0 WI-G1-04** (T4/G1): Target architecture, contracts, environments and release-authority model are approved. — _in_review_
- **P0 WI-G1-07** (T4/G1): The conductor can validate programme state, calculate gate readiness and render an evidence-linked status report. — _done_
- **P0 WI-G1-03** (T7/G1): Aggregate-only public boundary, ethics principles and prohibited-data rules are accepted. — _in_review_
- **P0 WI-G1-06** (T7/G1): Initial risk, threat, rights and disclosure-control baselines are documented. — _in_review_

> A gate is ready only after evidence, work, maturity, risk, defect and dependency controls pass. It passes only after a recorded governance decision. Document presence and self-assessment do not constitute acceptance.
