# Critical/high risk mitigation control packet — 2026-08-04

This packet records the repository-owned mitigation pass for all 20 programme
risks. It is not an accountable risk acceptance, legal opinion, independent
assurance report or release decision.

## Mitigation disposition

| Risk | Repository-owned action completed | Residual boundary |
|---|---|---|
| R01 | Coverage/status taxonomy, gap publication and no-imputation product controls | Owner/product acceptance pending |
| R02 | Clock, denominator, statistic and comparability contracts; quarantine/release-diff checks | Real-data methods assurance pending |
| R03 | Subnational entities, institutional maps and local-verification queues | Local reviewer evidence pending |
| R04 | Multilingual search logs, negative-finding queues and direct-enquiry register | Human/local review and source evidence pending |
| R05 | Retrieval manifests, checksums, preservation metadata and drift-monitoring rehearsal | Live scheduler/incident ownership pending |
| R06 | Rights queue, metadata-only fallback and redistribution fail-closed policy | Source-specific rights decisions pending |
| R07 | Structured extraction, locators, dual-review and re-extraction controls | Real-source independent review pending |
| R08 | Original-text retention, glossary and disagreement fields | Human/local language review pending |
| R09 | Separate evidence domains, catalogue labels and responsible-use constraints | Methods/product acceptance pending |
| R10 | Aggregate boundary, suppression, disclosure and takedown controls | Current harm/privacy review pending |
| R11 | Pinned workflows, locked dependencies, security scans, SBOM/provenance and signed-commit pathway | Hosted credential/key assurance pending |
| R12 | Runbooks, agent-panel context, clean builds, handover and deputy fields | Named deputy/support consent pending |
| R13 | Heterogeneous pilot contracts, exception tracking and schema-change controls | Real global evidence pending |
| R14 | Stage gates, critical path and release-blocking criteria | Owner enforcement at gates pending |
| R15 | Independence/conflict fields, no-veto policy and disclosure controls | Accountable governance/adjudication pending |
| R16 | Costed operating-plan and preservation fields with G5/G6 no-go controls | Committed funding/host pending |
| R17 | Contract freeze, compatibility tests and deprecation controls | Accountable methods acceptance pending |
| R18 | Source-edition model, correction taxonomy and release-diff records | Real revision adjudication pending |
| R19 | No composite ranking, visible context/tier labels and misuse-monitoring plan | Human/product review pending |
| R20 | Binding release criteria, no-go conditions, restore rehearsal and service handover fields | Final authority, custody and operating commitment pending |

## Result

All risks have an explicit repository-owned mitigation or fail-closed control.
No risk is marked accepted or closed by this packet. The conductor must continue
to block gates while any critical/high residual risk lacks accountable
adjudication, required evidence or specialist authority.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' security
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```
