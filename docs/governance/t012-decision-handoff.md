# T0/T1/T2 decision handoff

This handoff separates repository implementation from decisions and evidence
that cannot be created by an autonomous analyst. The repository owner has
recorded in-principle approvals in `programme/decision_log.csv`; the evidence,
authority verification, independent technical review, and formal gate
acceptance remain pending.

| ID | Track | Decision or evidence needed | Repository preparation | Required decision-maker or evidence owner | Status |
|---|---|---|---|---|---|
| D-T0-01 | T0 | Accept the programme charter, sponsor, host, and decision rights | Governance pack and unsigned release/declaration templates | Programme executive / host | approved in principle; formal acceptance pending |
| D-T0-02 | T0 | Accept aggregate-only boundary, ethics, security, rights, and disclosure rules | Versioned policies, validators, and fail-closed governance pack | Security and data-governance owner | approved in principle; formal acceptance pending |
| D-T0-03 | T0 | Confirm accountable owners, deputies, and escalation routes | RACI and track registry are checksum-bound | Named accountable owners and deputies | approved in principle; appointments pending |
| D-T1-01 | T1 | Accept the v0.3 scope, ontology, indicators, and contract manifest | Technical analyst review passed; manifest binds schemas and method documents | Methods lead / independent reviewer | approved in principle; programme acceptance pending |
| D-T1-02 | T1 | Complete pilot adjudication of clock, denominator, missingness, and ontology questions | Adjudication schemas, queues, and regression tests | Methods lead with pilot evidence | pending |
| D-T1-03 | T1 | Freeze the pilot methods after adjudication | Change-control and contract-lock machinery | Accountable methods authority | pending |
| D-T2-01 | T2 | Approve the pilot jurisdiction universe and local-verification strategy | Operational census inputs, schemas, readiness matrix, and gap report | Global census lead / accountable approver | approved in principle; evidence and formal acceptance pending |
| D-T2-02 | T2 | Supply reviewed institutional maps, multilingual search logs, and coverage assessments for the pilot | `data/census/` contracts and fail-closed census verifier | Global census lead and reviewers | approved in principle; records pending |
| D-T2-03 | T2 | Record and review priority direct enquiries or transparent closures | Direct-enquiry register, evidence-path field, and status validation | Global census lead / enquiry reviewer | approved in principle; records and review pending |
| D-T2-04 | T2 | Freeze the global universe and coverage cycle | Exact-one-current-assessment check and checksum-bound reports | G3 accountable governance authority | approved in principle; freeze evidence and formal acceptance pending |

## Decision packet contents

For each decision, the approver should review the current generated governance
pack, the relevant evidence register entry, the exact source commit, and the
machine-readable validation output. A green local check demonstrates only that
the repository control works; it does not establish the underlying approval,
source search, coverage conclusion, or institutional fact.

## Current technical baseline

The current census baseline contains draft operational jurisdiction, assessment,
search-log, institution-map, and enquiry records. It reports the remaining
review, coverage, and enquiry gaps as unresolved. Draft records are evidence
receipts only; they do not establish source completeness, rights clearance, or
formal gate acceptance until reviewed under the declared protocols.

The owner has authorized the bounded-pilot and single-owner/agent operating
model in `docs/methods/pilot-scope-decision-2026-08-01.md` and
`docs/governance/single-owner-agent-operating-model.md`. This authorizes
repository-owned implementation; it does not waive evidence, rights,
independence, or external-assurance requirements.
