# G1 owner decision packet — 2026-08-03

## Packet identity

- Frozen source revision: `fb3a7c5c48839f6c2061a671465c1b14fd486aed`
- Manifest binding: current `MANIFEST.sha256` entry for this packet (the
  manifest is regenerated after every packet change; do not copy a stale
  manifest-file digest into an approval record).
- Decision authority: repository owner.
- Advisory input: `docs/governance/g1-agent-panel-synthesis-2026-08-02.md`.
- Current state: G1 remains `blocked_by_assurance` and `conditional`.

This packet supersedes the 2026-08-02 packet for any future decision. It
does not itself accept G1.

## Recommended decision

Select **Option A**: the repository owner retains G1 and release accountability;
the analyst-agent deputy provides operational continuity only; panel findings
remain advisory; specialist, rights, consent, operations, staffing and funding
authorities remain separate.

## Alternatives and contingencies

- **Option B:** owner acceptance with a time-bounded no-deputy exception.
- **Option C:** delegate G1 to a formally appointed external authority.
- **Option D:** defer G1 while repository-owned preparation continues.
- Missing authority or unresolved assurance keeps G1 conditional.
- Any packet mutation invalidates this packet and requires regeneration.

## Required owner fields

| Field | Required value |
|---|---|
| Selected option | A, B, C or D |
| Authority | Repository owner or formally delegated authority |
| Decision date | ISO date |
| Immutable reference | Decision/minute/reference identifier |
| Conditions | Scope, residual-risk and expiry conditions |
| Status | `accepted`, `deferred` or `rejected` |

The owner decision must reference this exact packet revision and manifest
digest. Conversation approval, panel consensus, tests or generated artefacts
cannot substitute for the accountable record.

No outbound enquiry, publication, or downstream gate promotion is authorized
by this packet.
