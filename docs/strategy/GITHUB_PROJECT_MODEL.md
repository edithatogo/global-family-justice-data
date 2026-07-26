# GitHub Projects operating model for v1

## Purpose

The roadmap should be managed as evidence-based release work, not a loose list of tasks. A GitHub Project can connect tracks, milestones, jurisdiction work, methods decisions, data corrections, and release gates in one auditable workflow.

## Recommended project fields

| Field | Type | Values / use |
|---|---|---|
| Work item type | Single select | Epic, jurisdiction, source, pipeline, method, data quality, security, product, operation, decision, correction |
| Track | Single select | T1–T12 |
| Stage | Single select | A Foundations, B Pilot, C Alpha, D Beta, E Hardening, F RC, G v1, H Maintenance |
| Target release | Text or iteration | v0.2, v0.3, v0.5, v0.7, v0.8, v0.9-rc, v1.0, v1.0.x |
| Release blocker | Boolean | Whether failure blocks the target release |
| Gate | Single select | Gate 1–12 or none |
| Priority | Single select | P0 critical, P1 high, P2 normal, P3 later |
| Risk | Single select | Low, medium, high, critical |
| Status | Single select | Proposed, ready, in progress, blocked, in review, accepted, deferred, withdrawn |
| Accountable owner | User/team | One owner only |
| Reviewer | User/team | Independent reviewer or group |
| Jurisdiction | Text | Registry ID where applicable |
| Language/region | Text | Coverage and reviewer planning |
| Dependency | Text/link | Blocking issue or decision |
| Evidence | Text/link | PR, data-quality report, review record, or decision |
| Due/review date | Date | Delivery or next-review date |

## Core views

### 1. Executive roadmap

Group by stage, then track. Show target release, blocker, status, owner, and risk.

### 2. v1 release blockers

Filter `Release blocker = true` and target release `v1.0`. Group by Gate. This becomes the operational release-readiness view.

### 3. Jurisdiction census

Filter work item type `jurisdiction`. Show coverage status, languages, reviewer, second review, confidence, and next review due. This view should reconcile with the registry, not replace it.

### 4. Source and acquisition operations

Filter source/pipeline items. Group by source status or expected review date. Highlight failed retrievals, rights-review backlog, and changed sources.

### 5. Methods and schema decisions

Filter method/decision items. Group by status and target release. Accepted decisions must link to a permanent decision record under `docs/decisions/`.

### 6. Data quality and corrections

Show open validation findings, audit discrepancies, correction severity, affected release, owner, and patch target.

### 7. Security, privacy, legal, and operations

Filter T8/T11. Show unrehearsed runbooks, review findings, incidents, restore tests, and release sign-offs. Sensitive incident details remain in restricted systems.

### 8. Regional/language capacity

Group jurisdiction and source work by region/language. Use this to expose reviewer gaps and prevent overconcentration in English-language systems.

## Milestones

Recommended milestones:

- `v0.2 Product contract`;
- `v0.3 Controlled pilot`;
- `v0.5 Integrated alpha`;
- `v0.7 Global public beta`;
- `v0.8 Feature freeze`;
- `v0.9 Release candidate`;
- `v1.0 Stable release`;
- `v1.0.x Maintenance`.

A milestone closes only when its stage gate is accepted. Closing individual issues is not sufficient.

## Issue hierarchy

- **Epic:** a multi-team outcome tied to a track and stage.
- **Work package:** a coherent set of deliverables within an epic.
- **Issue:** a reviewable change or evidence item.
- **Sub-issue/checklist:** a small action that does not merit independent release evidence.

Each epic must state:

- problem and outcome;
- scope and non-scope;
- dependencies;
- acceptance criteria;
- release-gate evidence;
- owner and independent reviewer;
- risks and rollback/defer conditions.

## Definition of ready

An item may enter `ready` only when:

- scope and intended evidence are clear;
- dependencies and responsible owner are identified;
- privacy, rights, and methods implications are screened;
- acceptance criteria are objectively testable;
- the target stage/release is assigned.

## Definition of done

An item is `accepted`, not merely closed, when:

- acceptance criteria pass;
- code/data/docs and tests are merged;
- exact provenance and review evidence are linked;
- methods or security approval is complete where required;
- changelog/migration/decision records are updated;
- generated artifacts are reproducible;
- no unresolved blocker is hidden in a follow-up issue.

## Automation and repository rules

Recommended protections before public beta:

- required pull-request reviews;
- required quality-gate workflow;
- protected default and release branches;
- restricted release/tag permission;
- signed or otherwise attributable release action;
- dependency and secret scanning;
- automatic stale-source and next-review tasks from registry dates;
- automatic project-field assignment from issue templates/labels where feasible;
- no automated closure of data corrections without human verification.

## Reporting cadence

- weekly track review of blockers and dependency changes;
- monthly cross-track risk and coverage review;
- stage-gate review at each milestone;
- release-candidate daily/near-daily blocker triage as needed;
- post-v1 service and quality report on the declared public cadence.

Cadence is a governance choice, not a substitute for evidence. A work item remains incomplete until the linked release criterion passes.
