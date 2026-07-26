# Roles, decision rights and RACI

## 1. Accountable roles

| Role | Core accountability |
|---|---|
| Executive release owner | Final go/no-go, resources, independence and institutional accountability |
| Programme/product director | Integrated delivery, scope, budget, risks and benefits |
| Methods owner | Ontology, indicator definitions, comparability and interpretation |
| Data owner | Source census, provenance, rights metadata and release contents |
| Technical owner | Architecture, code, contracts, build and platform reliability |
| Quality/assurance owner | Review system, audits, defect classification and release evidence |
| Security/privacy owner | Threat, privacy, disclosure, access, incident and supply-chain controls |
| Service/release manager | Release calendar, monitoring, support, correction and continuity operations |
| International/localisation lead | Correspondents, translation QA, participation and sustainability |
| Lived-experience/child-rights chair | Harms, outcome priorities, communication and participation quality |
| Independent release assurer | Challenges evidence and recommends go/no-go; does not own delivery |

Every accountable role has a named deputy before G5.

## 2. Decision classes

| Decision | Accountable authority |
|---|---|
| Strategic scope, host, budget and release | Steering group / executive release owner |
| Matter taxonomy, indicator, clock and comparability | Methods and standards group |
| Source inclusion and rights/storage treatment | Data owner with security/legal advice |
| Architecture and public data contracts | Technical owner with methods/data approval |
| Gold promotion and quality exception | Quality owner under approved methods |
| Security/privacy exception or incident action | Security/privacy owner, escalated by severity |
| Public correction/takedown | Data/methods/security owners according to issue |
| Release scheduling and operational change | Service/release manager within approved plan |
| Breaking 1.x change | Executive, methods and technical joint decision under emergency rule |

## 3. RACI for v1 stage gates

Legend: **A** accountable, **R** responsible, **C** consulted, **I** informed.

| Gate activity | Executive | Programme | Methods | Data | Technical | Quality | Security | Service | International | Independent assurer |
|---|---|---|---|---|---|---|---|---|---|---|
| Approve v1 product boundary | A | R | C | C | C | C | C | C | C | I |
| Approve jurisdiction universe/methods | I | C | A/R | R | C | C | C | I | C | I |
| Complete global source census | I | C | C | A | C | R | C | I | R | I |
| Freeze v1 schemas/contracts | I | C | C | C | A/R | C | C | C | I | I |
| Promote data to gold | I | I | C | R | C | A | C | I | C | I |
| Approve security/privacy readiness | I | C | C | C | R | C | A | R | I | I |
| Complete restore/release rehearsal | I | I | I | C | R | C | C | A | I | I |
| External methods/release assurance | I | C | C | C | C | C | C | C | C | A/R |
| Recommend v1 release | I | R | R | R | R | R | R | R | C | C |
| Final v1 go/no-go | A | R | C | C | C | C | C | C | I | C |

## 4. Decision records

Material decisions include:

- context and problem;
- options considered;
- evidence and affected users;
- decision and rationale;
- dissent or unresolved uncertainty;
- owners and implementation date;
- compatibility/security/ethical impact;
- review or expiry date.

Decisions affecting public interpretation, scope, quality or release are published unless confidentiality is necessary; the existence and category of a confidential decision should still be disclosed.

## 5. Quorum and conflicts

- Methods decisions require the methods chair plus at least two members, including one with relevant jurisdictional or subject expertise.
- Release decisions require all five accountable sign-offs defined in `V1_0_RELEASE_CRITERIA.md`.
- A conflicted member declares the conflict and does not determine the relevant decision.
- Funders and data providers may correct factual errors but cannot suppress defensible findings.
- Lived-experience contributors are remunerated and supported; participation is not symbolic.
