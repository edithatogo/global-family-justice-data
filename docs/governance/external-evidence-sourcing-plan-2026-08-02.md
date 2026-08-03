# External evidence sourcing and redundancy plan — 2026-08-02

This plan turns each pending gate into an auditable acquisition workflow. It
does not send messages, appoint reviewers, grant rights, or close a gate.
Every evidence item is bound to the frozen candidate commit, manifest digest,
source/receipt digest, date, language and reviewer role.

## Dependency-ordered work packages

| Package | Primary route | Redundant route | Required receipt | Stop/contingency |
|---|---|---|---|---|
| G1/T0 governance | Owner decision packet and decision log | Reconciled agent-panel synthesis plus signed export | immutable decision reference, packet/manifest digests, conditions | no owner record: remain `pending_authority`; panel advice is not acceptance |
| G2/T1 methods | Pilot extraction and methods adjudication | Independent agent re-extraction and discrepancy ledger | frozen methods digest, panel reports, adjudication record | disagreement: `adjudication_required`; quarantine disputed measures |
| G3/T2 local coverage | Public institutional source and local reviewer ledger | Regional/second reviewer; archived official copy | URL, edition/date, language, access receipt, reviewer identity and conclusion | inaccessible/unreviewed: retain unresolved; no absence inference |
| G3/T2 multilingual | Source-language search and translation notes | Independent second-language search/review | search-log row, query/result, language, timestamp, access issue, second-review ledger | missing second review: `evidence_missing` |
| G3/T3 rights | Exact-edition publisher/official terms | Written permission or rights-register cross-check | edition hash, terms URL/text, permission/decision, preservation and redistribution scope | uncertainty: metadata/citation-only or exclude |
| G3/T2 enquiries | Existing mailbox response and controlled receipt | Public-source confirmation; owner-approved follow-up packet | delivery receipt, response or dated closure | no send approval: draft only; no-response closure follows policy date |
| G4/T4–T7 assurance | Role-separated panel reports | Named specialist review per domain | conflict/abstention record, findings, severity, remediation and verdict | missing specialist: `pending_authority`; critical/high: block |
| G5/T8 operations | Private live-like rehearsal | Independent custody/restore and host evidence | host/custody/support/signing receipts, restore hashes and RPO/RTO | no independent custody/signing: unsigned private candidate |
| G5/T9 resources | Owner-approved operating plan | Funder/staff commitment or reduced-scope plan | named roles, coverage, budget, term, expiry and acceptance | no commitment: no live service or G6 |

## Acquisition and redundancy protocol

1. Orchestrator freezes the packet and writes `packet_digest`, `manifest_digest`
   and `source_epoch` before collection.
2. Primary and redundant routes are attempted independently where lawful and
   practical; identical claims are not counted twice without provenance.
3. Capture immutable bytes or a stable public citation, SHA-256, MIME/type,
   edition/version, language, access status and retrieval timestamp.
4. Record failures (403, timeout, robots, unavailable, language gap) as
   first-class search-log evidence; never convert access failure into absence.
5. Route every item to the appropriate role-separated agent panel for options,
   recommendation, rationale, contingencies, conflicts and abstentions.
6. Require owner or named authority adjudication for rights, governance,
   methods, safeguarding, operations and release decisions.
7. Rebuild downstream artefacts after accepted evidence changes and invalidate
   reports whose packet digest no longer matches.

## Evidence record minimum

Each receipt must contain: `evidence_id`, gate/track, claim, route (`primary`
or `redundant`), source URI or controlled-record identifier, edition/version,
language, retrieved/observed date, access result, SHA-256 or explicit
`not_applicable`, reviewer role, panel report reference, authority decision
reference (if applicable), limitations, and next review date.

## Status and closure rules

- Two routes failing does not create a pass; set `evidence_missing` and retain
  the narrowest safe scope.
- Conflicting routes require `adjudication_required` and preserve both records.
- A no-response is only closable after the documented waiting period and owner
  policy; outbound follow-up always requires exact-recipient approval.
- Rights, consent, custody, signing, staffing and funding cannot be supplied by
  agent inference or local tests.
- Only a digest-bound accountable decision may promote a gate; archive remains
  prohibited while any mandatory dependency is pending.

## Outputs and ownership

The orchestrator updates `external-evidence-blocker-register.csv`,
`search_log.csv`, rights/enquiry ledgers and gate decision packets. Panels
produce advisory reports; the owner supplies accountable decisions. This plan
is itself repository-owned preparation and does not represent external
evidence.
