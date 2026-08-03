# G6 evidence-sourcing and redundancy plan — 2026-08-02

This plan defines how the remaining G6 evidence will be sourced, checked and
replaced when a primary route fails. It is a sourcing plan, not evidence of
authority, funding, custody or release. No external contact is sent by this
plan; outbound requests require a separately approved recipient/message packet.

## Evidence lanes and redundant routes

| Lane | Primary source | Redundant source | Minimum receipt | Stop/contingency |
|---|---|---|---|---|
| Release authority | Owner-signed digest-bound decision | Delegated authority decision | signer, scope, timestamp, packet/manifest/product digests, conditions | Missing signer keeps G6 `blocked_by_authority`; no conversational inference |
| Findings/assurance | Role-separated panel reports | Independent replay of checks and adversarial panel | report digest, verdict, severity, evidence refs, conflicts/abstentions | Critical/high or disagreement → `adjudication_required`; quarantine affected scope |
| Custody | Two independently administered locations | Encrypted local rehearsal plus second operator receipt | location/operator class, archive and manifest SHA-256, timestamps, restore result | One location or unsigned copy only → private candidate; no archive claim |
| Restore | Witnessed restore from each custody location | Fresh rebuild from source packet and independent checksum comparison | restored file count, digest comparison, RPO/RTO, witness role | Failed restore → quarantine, repair and repeat both routes |
| Service/support | Named service manager, deputy, monitoring, ticketing and incident route | Static handoff and scheduled agent rehearsal | owner names/roles, SLA, escalation, rehearsal receipt | No live support → static/private artifact; no G6 service claim |
| Signing/provenance | Signing authority and key-custody receipt | Offline attestation with key-revocation procedure | signed manifest, key identity (redacted), custody and revocation records | No valid signature → unsigned RC; never publish as final |
| Staffing/funding | Approved 12-month budget and named coverage | Time-boxed pilot budget with explicit expiry | funder/approval, currency, period, FTE/hours, succession, restrictions | Partial/expired funding → reduce scope or maintenance freeze; no continuity claim |
| Publication/takedown | Rights-cleared product pack and owner release scope | Metadata/citation-only preview with takedown register | product digests, rights decisions, accessibility result, rollback/takedown owner | Rights or accessibility gap → exclude/metadata-only; no publication |

## Acquisition sequence

1. Freeze the exact release candidate, manifest, contract lock, SBOM and product
   digests. Generate a sourcing receipt identifying the packet.
2. Run all agent panels independently. The orchestrator records options,
   recommendations, rationale, contingencies, evidence references, conflicts,
   abstentions and verdicts without treating them as authority.
3. Request or collect each primary receipt only through an explicitly approved
   route. Record recipient, scope, date and access result; do not send from this
   plan.
4. Collect the redundant receipt in parallel where feasible. Compare digests,
   scope and dates; conflicting receipts require adjudication.
5. Run custody and restore rehearsals from both locations, then compare to a
   fresh clean rebuild. Record RPO ≤24 hours, service RTO ≤4 hours and archive
   restore RTO ≤24 hours when those targets are in scope.
6. Assemble the evidence index and owner decision packet. Any mutation of the
   frozen packet invalidates all receipts and restarts the sequence.
7. Promote G6 only when every mandatory receipt, authority, rights decision,
   staffing/funding commitment and signed release decision is present. Otherwise
   retain `evidence_missing`, `pending_authority` or `blocked_by_assurance`.

## Redundancy and failure rules

- A redundant route corroborates a claim; it does not replace a missing authority.
- Agent-panel agreement is advisory and cannot establish legal rights, consent,
  custody, signing, funding or publication authority.
- A source that is inaccessible, stale, unsigned or scope-mismatched is recorded
  as an access issue, not silently substituted.
- A primary/backup disagreement preserves both receipts and sets
  `adjudication_required`.
- If a required route remains unavailable after the documented closure window,
  use the narrower fallback (private, unsigned, metadata-only, synthetic or
  excluded) and record a transparent closure; do not mark G6 accepted.
- Any critical/high finding, failed restore, key incident, rights uncertainty,
  support gap or funding expiry blocks publication and archive eligibility.

## Required receipt fields

Every receipt must contain: `evidence_id`, `gate`, `packet_digest`, `source_route`,
`captured_at`, `operator_role`, `scope`, `artifact_digests`, `status`,
`limitations`, `fallback_route`, and (where applicable) `authority_reference`,
`signature_reference`, `custody_location`, `restore_result`, `funding_period`,
or `takedown_owner`. Redact credentials and personal contact details.

## Decision options

- **A — staged dual-route sourcing (recommended):** collect primary and backup
  receipts in parallel, then owner-adjudicate the digest-bound index. This gives
  the best resilience without pretending agents are authorities.
- **B — primary-only:** faster, but any inaccessible or disputed receipt blocks
  G6 and creates a single point of failure.
- **C — narrow fallback:** remain private/unsigned, metadata-only and synthetic
  until primary and backup receipts exist. This is the safe default when routes
  fail.

Recommendation: **A**, with **C** automatically applied to any lane whose two
routes cannot produce acceptable evidence. No route authorizes outbound contact
without a separate exact-recipient approval.
