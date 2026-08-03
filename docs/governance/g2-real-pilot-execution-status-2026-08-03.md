# G2 real-pilot execution status — 2026-08-03

## Status

**Prepared, not executed.** The repository-owned execution handoff is ready,
but a real pilot cannot be represented as complete until the entry conditions
below are satisfied. No synthetic or metadata-only result is promoted as real
pilot evidence.

## Entry conditions

1. G1 is accepted by the accountable owner against a current packet with an
   immutable reference, conditions and expiry.
2. The pilot scope is frozen (original five candidates or an explicitly
   recorded substitution decision).
3. Each selected edition has complete bytes, a receipt, SHA-256 and a rights
   disposition suitable for the intended use.
4. A second extraction and row-level difference report are retained.
5. Methods adjudication, rights/security review and independent assurance are
   recorded by the required accountable or independent roles.

## Candidate disposition

| Candidate | Current disposition | Blocking reason |
|---|---|---|
| INT | Deferred/quarantine | Access and category/rights resolution incomplete |
| AUS | Preparation only | Rights and independent review incomplete |
| USA-MN | Preparation only | Access agreement/403 path and rights incomplete |
| BRA | Preparation only | Rights and local/independent review incomplete |
| ZAF | Preparation only | Rights and local/independent review incomplete |
| GBR-EAW | Out-of-scope preparation | Scope decision required before promotion |

## Prohibited transitions

- Do not mark `E-PILOT-CENSUS`, `E-PILOT-METHODS-ADJUDICATION` or
  `E-PILOT-RIGHTS-SECURITY` accepted from this status alone.
- Do not send enquiries or follow-ups without an exact recipient/message list
  and explicit owner send authorization.
- Do not publish a pilot result or move G2 to accepted.

The detailed sourcing and review protocol remains in
`docs/governance/real-pilot-evidence-sourcing-plan-2026-08-03.md` and
`docs/governance/g2-blocker-handoff-2026-08-03.md`.
