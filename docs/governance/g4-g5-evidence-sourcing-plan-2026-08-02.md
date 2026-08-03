# G4–G5 evidence sourcing and redundancy plan — 2026-08-02

This plan defines how the repository will source, cross-check, and preserve
evidence for G4 (bounded beta) and G5 (private release candidate). It does not
create rights, consent, independent assurance, custody, funding, or release
authority. Every receipt is bound to the frozen candidate digest and remains
`pending` until an accountable authority accepts it.

## Acquisition protocol

1. Freeze the candidate commit, contract lock, product manifest and SBOM.
2. Create a receipt for every requested item with source, method, language,
   retrieval date, access result, SHA-256, reviewer role and status.
3. Use the primary route first, then the listed independent fallback only when
   the primary route is unavailable or conflicted. Never silently substitute.
4. Have role-separated agent panels compare receipts and record options,
   recommendation, rationale, contingencies, conflicts and abstentions.
5. Re-run acquisition after any packet or digest mutation. Superseded receipts
   remain preserved but cannot satisfy the new packet.

## Redundant sourcing matrix

| Evidence | Primary route | Redundant route | Minimum receipt | Stop/contingency |
|---|---|---|---|---|
| Core schema and lineage | Frozen repository artifacts and build receipt | Independent clean checkout rebuild | commit, lock/manifest digests, row counts, lineage report | Mismatch → quarantine and rebuild |
| Outcomes/context products | Reproducible product builder | Independent agent re-extraction from frozen inputs | input/output digests, transformation log, discrepancy report | Discrepancy → adjudication; no beta claim |
| Quality/comparability | Automated validation plus methods panel | Independent re-extraction and metric recomputation | test receipt, method version, denominator/missingness decisions | Failed check → block affected measure |
| Threat/privacy/rights | Threat model and rights queue | Second role-separated panel review of exact editions | finding IDs, source terms, access mode, severity, disposition | Uncertain rights/privacy → metadata-only or exclude |
| Accessibility/localisation | Automated HTML/contract checks | Human review packet or independent accessibility panel | language, assistive-tech/manual findings, remediations | No human review → private beta/RC only |
| Operations rehearsal | Local backup/restore and incident drill | Separate clean environment or independent operator receipt | RPO/RTO, archive hash, restore log, operator role | Failed restore/no operator → unsigned private candidate |
| Safeguarding/consent | Approved synthetic dry-run packet | Named safeguarding authority and consent audit (if participation) | protocol digest, consent/withdrawal/incident records | Missing authority → no participants; synthetic only |
| Supply chain/SBOM | Generated SPDX and lock verification | Independent SBOM parse and dependency review | SBOM digest, tool/version, findings and exceptions | Malformed/critical finding → quarantine |
| Clean G5 rebuild | Rebuild from frozen commit in isolated workspace | Independent clean checkout rebuild | artifact digests, environment, command log | Non-reproducible → reset G5 to evidence_missing |
| Provenance/signing | Named signing authority and key-custody receipt | Independent archive custodian verification | signature, key reference (never secret), custody/retention receipt | No authority/key custody → unsigned candidate |
| 12-month operations plan | Owner-approved staffing/funding packet | Independent budget/coverage reconciliation | named roles, coverage, budget, expiry and escalation | Partial commitment → scope reduction; no G5 acceptance |

## Panel and owner workflow

- The orchestrator assigns each row to at least two role-separated agent
  reviewers where a redundant route exists.
- Panels may recommend `pass`, `conditional`, `fail-closed`, or
  `adjudication_required`; they cannot promote a gate.
- The owner reviews the digest-bound synthesis and records the actual G4/G5
  decision, conditions, exclusions and residual risk.
- A receipt is acceptable only when its source and role are identifiable,
  evidence is hash-bound, and unresolved conflicts are explicitly recorded.

## Failure and redundancy rules

- Primary unavailable: use the declared fallback and record the access issue;
  never backfill an unobserved result.
- Primary and fallback disagree: preserve both, escalate to adjudication, and
  block the affected gate.
- No route produces evidence: record `evidence_missing` and retain the scope
  as private/non-participatory.
- External contact would be required: prepare the exact recipient, message,
  disclosure and follow-up packet; do not send without explicit approval.
- Any digest mutation: invalidate dependent receipts and repeat acquisition.
- Critical/high finding: quarantine the affected product or measure until an
  accountable exception or remediation is recorded.

## Conductor status mapping

`in_review` requires complete receipts and all required panel reports;
`accepted` requires the owner's digest-bound decision and every mandatory
authority/evidence criterion; otherwise use `pending_authority`,
`evidence_missing`, `adjudication_required`, `waived_for_scope`, or `excluded`.
G4 acceptance is a prerequisite for G5; neither is archive-eligible without
G6 authority, signing, independent custody and restore evidence.
