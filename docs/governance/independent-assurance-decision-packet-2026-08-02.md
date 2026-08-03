# Independent assurance decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `f96dcfdf031b58773f3f89090b3f507b8ae6cc3a`
- `MANIFEST.sha256` SHA-256: `78c8e78c8a8f3638d461d63d5d9e37c34642ac53b7396d6be56ee8dc5a5df98f`
- Scope: G2–G6 methods, quality, security, privacy, rights, accessibility,
  operations, custody and release assurance.
- Panel inputs: methods/quality, security/privacy/legal/supply-chain and
  product/accessibility/operations agents.

Agent panels provide pre-assurance advice only. They cannot sign assurance,
create legal rights, provide consent, appoint independent authorities or accept
a gate.

## Owner policy selection

The owner approved **Option A in principle** on 2026-08-02: run role-separated,
digest-bound agent pre-assurance now, then obtain named accountable or
specialist sign-off for G5/G6. Agent reports remain advisory and cannot create
independent assurance, legal clearance, consent, signatures, custody, funding
or gate acceptance.

## Options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| A | Role-separated digest-bound agent pre-assurance, followed by named accountable/specialist sign-off | **Recommended** | Allows autonomous remediation now while preserving genuine assurance boundaries |
| B | Commission fully external independent assessors | Strongest later route | Highest independence, but requires identities, engagement and resources |
| C | Owner-only review | Not sufficient | Fast but cannot establish independence for G4/G5 |
| D | Defer assurance and retain a private candidate | Safe fallback | Avoids unsupported claims while external review is unavailable |

Recommendation: use **A now**, then **B or named specialist sign-off** for G5/G6
closure.

## Required packet contents

- Frozen HEAD, manifest, product, contract and SBOM digests.
- Scope, exclusions, data-flow and aggregate-only boundary.
- Methods package, pilot register, real source receipts and independent
  re-extraction/discrepancy log.
- Lineage, edition identity, rights/privacy/security dispositions.
- Threat model, retention/deletion controls, supply-chain and tamper results.
- Human accessibility/localisation/usability and harms review for beta/release.
- Live-like operations, custody, signed provenance, restore and support
  evidence.
- Finding IDs/severity, evidence references, uncertainty, abstentions,
  conflicts, remediation owner/deadline and verdict.
- Accountable authority identity, role, scope, signature, timestamp and
  residual-risk decision.

## Contingencies and promotion rules

- Missing role/report → `pending_authority`.
- Critical/high finding or disagreement → `adjudication_required`; block gate.
- Missing real data or failed re-extraction → descriptive-only/quarantine.
- Rights/privacy uncertainty → metadata-only or exclusion.
- Packet mutation → invalidate reports and rerun.
- Missing human review, consent, live operations, custody, signing or funding
  → private/unsigned candidate only.
- G5/G6 promotion requires accountable specialist sign-off and a clean,
  reproducible rebuild; panel consensus alone is never sufficient.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | A, B, C or D |
| Authority | Repository owner or formally delegated authority |
| Decision date | ISO date |
| Immutable reference | Decision/minute/reference identifier |
| Conditions | Scope, exclusions and residual-risk conditions |
| Status | `approved_in_principle`, `accepted` or `deferred` |
