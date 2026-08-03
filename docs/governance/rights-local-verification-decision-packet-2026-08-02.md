# Rights and local-verification decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `482bea8c912566a6bcac7a54d293502654f428cd`
- `MANIFEST.sha256` SHA-256: `e4bba35cdd22f2a386bfa317840ea442242a97b6e15407f927d549daa4c32986`
- Scope: T2 local/regional verification and multilingual second review; T3
  exact-edition rights, redistribution and preservation treatment.
- Current state: `EXT-COV-001`, `EXT-COV-002` and `EXT-RGT-001` remain pending.

This packet records the recommended policy and presents the accountable owner
decision. It does not create rights, local knowledge, second review or legal
approval.

## Owner policy selection

The owner approved **L1+R1 in principle** on 2026-08-02: use an
evidence-complete pilot subset with source-backed local/second review; publish
only clearly permissive exact editions; retain uncertain material as
metadata/citation-only or exclude it; and require explicit approval before any
enquiry. The local verification, independent review and rights records remain
external evidence requirements.

## Local-verification options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| L1 | Evidence-complete pilot subset with source-backed local/regional review and second review of multilingual/inaccessible searches | **Recommended** | Produces defensible claims without pretending the full universe is verified |
| L2 | All jurisdictions reviewed before any pilot claim | Conservative fallback | Strongest completeness, but delays all pilot work and may be infeasible |
| L3 | Public-source and agent-panel review only | Not sufficient for readiness | Useful preparation, but cannot replace local knowledge or independent second review |
| L4 | Retain unresolved jurisdictions as descriptive-only/excluded | Required contingency | Prevents unsupported absence or completeness claims |

Recommendation: use L1, with L4 applied to every unresolved jurisdiction or
search row.

## Rights and preservation options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| R1 | Publish only clearly permissive sources; retain uncertain material as metadata/citation-only | **Recommended** | Minimizes redistribution risk while preserving provenance |
| R2 | Seek written permission for each uncertain exact edition | Viable supplement | Can expand coverage, but requires explicit owner approval before contact |
| R3 | Use uncertain sources internally but never publish files or derived restricted values | Contingency | Preserves research utility without claiming redistribution rights |
| R4 | Exclude any source whose terms remain uncertain | Strict fallback | Safest legal posture, with lower coverage |

Recommendation: use R1, with R3 or R4 per source until a rights authority
records an exact-edition decision.

## Combined recommendation

Adopt **L1 + R1**:

- pilot claims limited to jurisdictions with completed local/second review;
- unresolved searches remain `source_inaccessible` or `search_incomplete`;
- exact-edition rights must be permissive before publication;
- uncertain sources remain metadata/citation-only or are excluded;
- preservation requires edition identity, checksum, rights disposition and
  custody decision;
- every external enquiry requires a separately approved recipient/message/scope
  packet before sending.

## Contingencies

- No local reviewer: `pending_authority`; quarantine readiness claim.
- Conflicting local reviews: `adjudication_required`; preserve both findings.
- Inaccessible or untranslated source: retain access issue; do not infer
  absence.
- Unknown licence or terms: metadata-only; no redistribution.
- Permission request needed: prepare a draft, but do not send without explicit
  owner approval.
- Changed source edition: invalidate the prior rights decision and re-review.

## Owner decision fields

| Field | Required value |
|---|---|
| Local-verification option | L1, L2, L3 or L4 |
| Rights option | R1, R2, R3 or R4 |
| Authority | Repository owner or formally delegated authority |
| Decision date | ISO date |
| Immutable reference | Decision/minute/reference identifier |
| Conditions | Scope, exclusions and residual-risk conditions |
| Status | `approved_in_principle`, `accepted` or `deferred` |

Agent panels may prepare maps, search logs, rights comparisons and
recommendations. They cannot attest local knowledge, grant legal permission,
or accept an independent second review.
