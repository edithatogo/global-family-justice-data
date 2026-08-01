# Readiness control board

Status date: 2026-08-01  
Owner: repository owner  
Execution: analyst-agent under fail-closed controls

This board is the operating index for the remaining readiness blockers. The generated census remains authoritative for counts; this document records the evidence needed to change those counts.

## Current gates

| Gate | Authoritative records | Current state | Advancement condition | Fallback |
| --- | --- | --- | --- | --- |
| Coverage | `data/census/institution_map.csv`, `data/census/search_log.csv`, coverage assessments | 23 jurisdictions incomplete | Source-backed institution, multilingual searches, scope, period, taxonomy, missingness, and access evidence reviewed | Keep partial/inaccessible; descriptive-only or exclude |
| Rights | `data/seed/source_register.csv`, source-edition manifests, rights review notes | High-priority rights unresolved or restricted | Exact edition terms support the intended use and are owner-adjudicated | Metadata/citation-only, permission-required, or exclude |
| Enquiries | `data/census/direct_enquiry_register.csv`, controlled receipts, enquiry notes | Responses pending or substantively incomplete | Substantive response or eligible transparent no-response closure is reviewed | Keep unresolved; no automatic follow-up |
| Methods | `data/methods/pilot_adjudication_register.csv`, `data/census/review_ledger.csv` | Fail-closed T1 dispositions recorded | Independent assurance supports any change to a disposition | Retain descriptive-only, quarantine, or exclude |
| Release | census outputs, manifest, validation and test results | Not eligible | All upstream gates complete and current-head checks pass | Repository-only evidence work |

## Pilot work queue

The five-candidate pilot is the only active readiness scope: INT, AUS, USA-MN, BRA, and ZAF. The analyst-agent may complete public-source searches, artifact hashing, coverage assessments, rights documentation, and review-ledger entries without external contact. No candidate may advance solely because a source is official or an enquiry was acknowledged.

For each candidate, the packet must link:

1. institution map and official source URLs;
2. multilingual search receipts, including zero-result and blocked searches;
3. source-edition manifest and checksum where accessible;
4. court, geographic, temporal, and family-law scope;
5. taxonomy and missingness assessment;
6. access and reproducibility limitations;
7. rights classification for the intended use;
8. enquiry state and evidence path;
9. analyst validation and owner adjudication.

## Response and approval controls

The analyst-agent may monitor the controlled mailbox and record responses. It may draft follow-ups, reroutes, permission requests, or alternate-channel instructions, but may not send or submit them. Explicit owner approval is required immediately before every outbound action.

An acknowledgement is routing evidence, not a coverage or rights resolution. A no-response closure is permitted only after the date and delivery-evidence requirements in `docs/methods/evidence-operations-calendar-2026-08-01.md` are met.

## Decision and escalation rules

- Public and reproducible: assess normally.
- Partial or inconsistent: retain descriptive-only and document the limitation.
- 403, CAPTCHA, authentication, phone-only, or postal-only: mark inaccessible and await owner direction; do not infer absence.
- Ambiguous rights: metadata/citation-only or permission-required; do not redistribute.
- Missing denominator, clock, or stable snapshot: quarantine the affected rate or timeliness measure.
- Conflicting official sources: preserve both and quarantine the disputed indicator.

## Gate review cycle

After each evidence change, the orchestrator must run strict validation, census build and verification, manifest verification, focused tests, and (when resources permit) the full test suite. The result and evidence paths must be recorded before any owner decision is presented.

Readiness remains fail-closed at the generated census state until all required gates are complete. No external contact or readiness promotion is implied by this board.
