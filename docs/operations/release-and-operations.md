# Release and operations model

## 1. Operating principle

A stable data product is maintained through routine, observable and rehearsed processes. v1.0 is not released until the project can update, correct, restore and hand over the service without relying on undocumented individual knowledge.

## 2. Service components

| Component | Authority | Operational priority |
|---|---|---|
| Immutable release bundle | Authoritative | Highest; must never be lost or silently changed |
| Source/evidence stores | Authoritative for lineage | High; access may be restricted by rights |
| Repository and CI | Authoritative for code/contracts | High |
| Website/documentation | Derived access channel | Medium-high |
| Dashboard/API/query service | Derived access channel | Medium; downloadable release remains fallback |
| Monitoring/ticketing | Operational control | High during release cycles |

## 3. Release cadence

After v1.0:

- two scheduled data releases per year as the minimum baseline;
- quarterly source-health and coverage-status reviews;
- urgent patch releases for material errors or disclosure/security issues;
- annual methods/ontology review;
- release-candidate freeze before each scheduled major publication;
- no unreviewed production editing.

The first 1.x calendar is approved before G6.

## 4. Release workflow

1. Open release milestone and scope.
2. Freeze source snapshot and analytical cohort.
3. Complete extraction, review and transformation cut-off.
4. Run full validation and release diff.
5. Resolve/quarantine defects and generate candidate artefacts.
6. Run rights, disclosure, security, accessibility and documentation checks.
7. Execute clean-room rebuild and checksum comparison.
8. Obtain data, methods, technical and security sign-off.
9. Publish immutable artefacts and archive deposit.
10. Deploy derived services from the release bundle.
11. Verify downloads, citations, dashboards and status pages.
12. Announce release with known limitations.
13. Conduct post-release review and track actions.

The detailed checklist is `docs/operations/v1-release-checklist.md`.

## 5. Service objectives

These are internal operational objectives for the v1.0 service:

- correction reports acknowledged within five working days;
- correction disposition or progress update within 30 calendar days;
- P0 incident triage begins immediately on detection and publication may be suspended when necessary;
- no loss of an immutable release;
- restore public access services within two business days after a major failure;
- high-priority stale/broken source alerts triaged within five working days;
- current and previous minor release remain reproducible;
- every critical operational process has primary and deputy ownership;
- runbooks reviewed at least annually and after material incidents.

## 6. Incident classification

| Severity | Examples | Required response |
|---|---|---|
| P0 critical | prohibited data disclosure, corrupted authoritative release, material false comparison, lost release, compromised signing credential | Escalate immediately; consider suspension/takedown; preserve evidence; executive/security/methods response; public incident record |
| P1 high | material data error, core build failure, broken public contract, failed restore, high-impact source-rights issue | Release blocking; urgent owner and correction plan |
| P2 significant | important accessibility/documentation/coverage defect, degraded dashboard/API with downloads intact | Time-bound remediation; may require public notice |
| P3 minor | cosmetic or low-impact issue | Normal backlog and scheduled fix |

## 7. Correction workflow

- Intake through public issue/form/email channel.
- Assign severity and affected release/series.
- Acknowledge and preserve reporter evidence.
- Reproduce and assess impact.
- Decide: no change, metadata clarification, patch release, scheduled correction, takedown or incident.
- Re-run lineage, validation, disclosure and derived-output checks.
- Publish a correction note and link it to affected releases.
- Never remove the prior artefact from history unless legal/safety necessity requires restricted access; record the action.

## 8. Source-change operations

Alerts are generated for:

- broken or redirected URLs;
- changed checksums/content structure;
- API schema or authentication changes;
- missing scheduled publication;
- revised historical tables;
- changed definitions or case classifications;
- dashboard filters no longer reproducing results.

A source change is triaged as:

- transport-only change;
- format/parser change;
- data revision;
- definitional/series break;
- access/rights change;
- source retirement.

Definitional changes require methods review before data are appended to an existing series.

## 9. Backup, preservation and recovery

- Git repository mirrored to an independently administered location.
- Release bundles stored in at least two locations plus archival deposit.
- Controlled source storage backed up according to rights and retention rules.
- Configuration and infrastructure definitions versioned.
- Restore test before v1.0 and at least annually.
- Test includes repository, release bundle, derived site and essential metadata.
- Recovery report records actual recovery time, data loss, gaps and actions.

Target: no loss of immutable releases; public access restored within two business days.

## 10. Access and key management

- Named accounts only; no shared production credentials.
- Least privilege and role separation between contributor, reviewer and release publisher.
- Multi-factor authentication for privileged systems.
- Secrets stored outside source and rotated after exposure or role change.
- Access review at least twice yearly and after staff departure.
- Signing and publication credentials have documented recovery and revocation procedures.

## 11. Operational ownership

At minimum, name a primary and deputy for:

- release management;
- source acquisition/connector incidents;
- data-quality triage;
- methods adjudication;
- security/privacy incidents;
- infrastructure/publication;
- archive and preservation;
- public corrections and support;
- communications and jurisdiction liaison.

No v1.0 release occurs with a bus factor of one in a critical process.

## 12. Operational records

Retain:

- release evidence packs;
- build/validation logs;
- access reviews;
- incident and correction records;
- source-change tickets;
- restore and continuity exercises;
- runbook revisions;
- maintenance decisions and deprecations;
- public communications and affected-jurisdiction notifications.
