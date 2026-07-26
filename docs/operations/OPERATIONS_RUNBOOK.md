# Operations runbook outline

This document is a v1 template. Named contacts, systems, commands, storage locations, and escalation routes must be completed before release candidate.

## Routine operations

- scheduled source-freshness checks;
- acquisition job review;
- validation and anomaly queue triage;
- broken-link and superseded-source handling;
- contributor and correction issue triage;
- dependency and security update review;
- backup verification;
- jurisdiction review scheduling.

## Required dashboards or reports

- source freshness and retrieval success;
- unresolved validation errors and warnings;
- lineage completeness;
- gold observations awaiting second review;
- coverage by region, language, matter type, and outcome domain;
- open corrections and incidents by severity;
- backup age and last successful restore test;
- current public release and archive checksums.

## Failure playbooks

### Source unavailable or changed

1. preserve the last known metadata and checksum;
2. mark source status without deleting history;
3. attempt canonical and archive routes;
4. assess whether extraction logic or published values are affected;
5. open a review task and, if material, pause dependent outputs;
6. document the resolution and next review date.

### Pipeline or validation failure

1. stop publication of affected artifacts;
2. capture logs, inputs, and environment metadata;
3. classify severity and identify last known good release;
4. correct code, source mapping, or data under review;
5. add a regression test;
6. rebuild from clean checkout and compare with prior artifacts.

### Material data correction

Follow `docs/operations/RELEASE_PROCESS.md` and `docs/templates/data-correction-report.md`.

### Potential privacy or security incident

Follow `SECURITY.md`; do not disclose sensitive detail in a public issue.

### Rollback or withdrawal

1. release authority identifies affected artifacts;
2. public download is marked withdrawn or replaced by a notice, not silently deleted;
3. prior valid release remains available where safe;
4. users are notified according to severity;
5. corrected release proceeds through normal gates.

## Backup and restore

The v1 deployment must define:

- systems and data covered;
- backup frequency and retention;
- encryption and access controls;
- geographic/provider separation where appropriate;
- restore objectives;
- quarterly sample restore and pre-release full restore test;
- evidence retained from each test.

## Operational handover

Before v1, at least two operators must independently demonstrate:

- clean build and release candidate generation;
- source update and review;
- correction and patch release;
- backup restore;
- incident escalation and rollback.
