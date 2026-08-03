# G1 authority-record access plan — 2026-08-03

This plan separates each authority record and defines how it may be obtained,
verified and bound to G1. It is an intake plan, not evidence that any authority
exists. No outbound contact is authorized by this document.

## Authority lanes

| Lane | Record required | Acceptable access route | Required fields | Verification | Fallback |
|---|---|---|---|---|---|
| Governance owner / host | Charter, sponsor/host and decision rights | Owner-signed repository record or immutable governance minute; host record if distinct | Authority identity, scope, date, decision rights, expiry, reference | Verify signer role, packet hash and manifest entry | Keep G1 conditional |
| Deputies / escalation | Named owner and deputy assignments | Versioned RACI/track-charter record with deputy acknowledgement | Role, accountable owner, deputy, escalation route, acknowledgement, dates | Check every critical track and acknowledgement status | Time-bounded no-deputy exception; dependent work blocked |
| Ethics/security/privacy | Boundary and prohibited-data acceptance | Named accountable security/privacy authority record | Scope, prohibited data, aggregate boundary, residual risks, conditions | Panel consistency check plus accountable sign-off | Quarantine affected scope; no promotion |
| Architecture/release authority | Architecture, contracts, environments and authority model | Named technical authority review record | Revision, contract set, environments, release powers, conditions | Recompute file hashes and compare review digest | Keep release authority undefined; no RC |
| Risk/rights authority | Risk, threat, rights and disclosure disposition | Named specialist review or written legal/rights decision | Findings, severity, exact editions, redistribution treatment, residual-risk owner | Cross-check source register, rights queue and risk register | Metadata/citation-only or quarantine |
| Pilot-scope authority | Frozen pilot universe and GBR-EAW decision | Owner decision record against scope-options packet | Selected option, included candidates, exclusions, rationale, date, expiry | Compare scope decision with jurisdiction register and intake config | Retain original five; GBR-EAW remains out of scope |
| Local/independent reviewers | Local verification and independent assurance appointments | Named reviewer acceptance or completed review receipt | Identity/role, independence, jurisdiction, methods, conflicts, date, digest | Validate reviewer scope and evidence hashes | Preserve unverified/descriptive-only status |

## Intake sequence

1. Freeze the current G1 packet and manifest.
2. Collect one lane record at a time; never infer a missing lane from another.
3. Store only redacted, repository-safe records and SHA-256 bindings.
4. Update the evidence index and blocker register after each lane.
5. Run the role-separated agent panel for consistency and contradiction checks.
6. Obtain accountable owner adjudication of panel findings.
7. Regenerate the owner bundle and manifest.
8. Run strict validation and Conductor readiness.
9. Attempt G1 acceptance only if every mandatory lane passes.

## Access and authorization boundaries

- Agent panels may identify routes, prepare forms, check hashes and recommend
  options. They cannot appoint authorities, sign, create rights or consent, or
  accept G1.
- Email or other external contact requires an exact recipient/message/scope
  list and explicit owner authorization immediately before sending.
- A conversation approval is recorded as policy input only; gate acceptance
  requires the immutable, digest-bound record described above.
- If a lane cannot be obtained, record `pending_authority` or
  `evidence_missing`; do not downgrade the criterion or infer completion.

## Recommended route

Use owner-held governance with analyst-agent operational continuity, named
specialist reviewers for non-substitutable lanes, and a smaller evidence-
complete pilot subset if the full scope cannot be supported. Keep all uncertain
rights, local review and participation claims quarantined until their own lane
records are present.
