# v1.0 programme risk register

This is the initial control register. It should move into the programme’s live risk system with owners, review dates and evidence links.

| ID | Risk | Likelihood | Impact | Principal controls | Trigger / early warning | Accountable track |
|---|---|---:|---:|---|---|---|
| R01 | Global scope is interpreted as complete outcome data rather than complete search coverage | High | High | Product boundary, status taxonomy, published gaps, no imputation | Requests for league tables; blank cells treated as zero | T0/T1/T6 |
| R02 | Incompatible clocks/statistics are compared | High | Critical | Explicit clock/statistic fields, gold gates, UI constraints, methods review | Generic “wait time” field or chart mixes measures | T1/T5/T6 |
| R03 | Federal/devolved responsibility is misrepresented | Medium | High | Subnational units as first-class entities, institutional maps, local review | One national number despite separate court systems | T1/T2 |
| R04 | Non-English or non-digitised sources are missed | High | High | Multilingual searches, paid regional leads, direct enquiry, negative-finding review | Regional coverage imbalance; many “no source” findings by one language team | T2/T9 |
| R05 | Source disappears or dashboard changes | High | High | Retrieval manifests, checksums, preservation, drift alerts, archived releases | Broken link/checksum change/unreproducible filter | T3/T8 |
| R06 | Rights or terms prohibit redistribution | Medium | High | Rights register, manifests instead of files, legal review, takedown process | Unknown licence on core source | T3/T7 |
| R07 | Manual PDF/dashboard extraction produces error | High | High | Dual review, exact locator, structured extraction, independent sample | High discrepancy or correction rate in manual sources | T3/T5 |
| R08 | Translation changes legal/procedural meaning | Medium | High | Original text retained, glossary, local human review, disagreement notes | Mapping disagreement concentrated by language | T1/T9 |
| R09 | Orders are presented as child/family outcomes | Medium | High | Separate evidence domains and catalogue, product labels, methods review | Outcome charts populated only from disposition data | T1/T5/T6 |
| R10 | Small cells/context expose or harm families | Low–Medium | Critical | Aggregate boundary, suppression, contextual-harm review, incident/takedown | Fine geography/demographics or media identification risk | T5/T7 |
| R11 | Credentials or build chain are compromised | Medium | Critical | MFA, least privilege, scans, signed releases, protected branches, key rotation | Secret alert, unexpected artefact hash, dependency compromise | T4/T7/T8 |
| R12 | Pipeline depends on one engineer/researcher | High | High | Deputy roles, runbooks, tests, clean build, handover exercises | Single approver/maintainer; overdue leave blocks release | T0/T4/T8/T9 |
| R13 | Pilot design does not scale globally | Medium | High | Heterogeneous pilot, early regional review, schema change before freeze | Excessive exceptions during global census | T1–T5 |
| R14 | Feature/dashboard work displaces provenance and census | High | High | Critical path, stage gates, must/should/may scope, release blocking criteria | Polished UI with incomplete search/review | T0/T6 |
| R15 | Funders or institutions influence findings | Medium | Critical | Independence charter, conflicts disclosure, external review, no institutional veto | Requests to suppress comparisons/gaps | T0 |
| R16 | Maintenance funding ends at launch | Medium | Critical | 12-month funding gate, costed 1.x plan, host commitment, preservation | No approved post-launch roles at G5 | T0/T9 |
| R17 | Public contracts change repeatedly | Medium | High | 0.x design testing, contract freeze, compatibility tests, deprecation policy | Late field/ID redesign after v0.7 | T1/T4 |
| R18 | Historical source revisions are mistaken for project errors or vice versa | Medium | Medium | Source edition model, correction taxonomy, release diffs | Values change without source revision record | T3/T5/T8 |
| R19 | Comparative product is used as a simplistic ranking | High | High | No composite index, visible tiers/context, responsible-use guidance, misuse monitoring | Media/policy league table strips definitions | T0/T6/T9 |
| R20 | v1.0 is declared with unresolved operational weakness | Medium | Critical | Binding criteria, no-go conditions, independent assurance, restore/release rehearsal | Pressure to launch with P1 or no maintenance owner | T0/T8 |

## Review cadence

- Track owners review monthly.
- Programme assurance escalates red risks at each gate.
- Risk acceptance is time-limited and names an accountable owner.
- P0/P1 data, security, privacy or legal risks cannot be accepted solely to meet a schedule.
