# G1 owner decision packet — 2026-08-02

## Packet identity

> **Superseded for acceptance.** Subsequent governed changes have altered the
> repository and manifest after this packet was frozen. Do not use the source
> revision or manifest digest below for a new acceptance. Regenerate a fresh
> owner packet from the current manifest before recording `G1=accepted`.

The current external dependency handoff is recorded in
`docs/governance/external-blocker-snapshot-2026-08-03.md`.

- Frozen source revision: `3bde005983542c0ee1094c67ed36211656996b9e`
- `MANIFEST.sha256` SHA-256: `f676c6c9f664ff055f3e63cb63b1baf58245b3f871a48c4935741ed66ac81837`
- Decision authority: repository owner.
- Advisory input: digest-bound role-separated agent-panel synthesis at
  `docs/governance/g1-agent-panel-synthesis-2026-08-02.md`.
- Current Conductor state: G1 `blocked_by_assurance`, decision
  `not_evaluated`.

This packet presents the accountable decision. It does not record a decision
until the owner supplies the selected option, decision date, immutable
reference and any conditions through the Conductor decision command.

The downstream evidence handoff is maintained in
`docs/governance/g2-blocker-handoff-2026-08-03.md`; it must not be treated as
G1 acceptance or as a substitute for the accountable conditions below.

## Owner policy selection

The owner approved **Option A in principle** on 2026-08-02: owner retains G1
and release accountability; an agent deputy may provide operational continuity
only; agent panels remain advisory; and specialist, rights, consent,
operations, staffing and funding gates remain separate. This approval does not
replace the formal signed, digest-bound acceptance record required to move G1
to `accepted`.

## Decision options

### Option A — owner acceptance with agent continuity deputy (recommended)

You accept the G1 charter, aggregate-only and prohibited-data boundaries,
decision rights, risk/rights baseline and bounded pilot scope. A named agent
deputy provides operational continuity and escalation; the deputy cannot
approve gates or replace specialist authority. Specialist panel findings remain
conditions for downstream gates.

Rationale: this is the most coherent model for a single-person repository. It
provides continuity and structured challenge without inventing a second human
authority.

### Option B — owner acceptance with formal no-deputy exception

You accept the same G1 scope but explicitly waive the deputy requirement for a
defined period and record the continuity risk and mitigation.

Rationale: workable if no stable agent identity can be maintained, but weaker
for succession and escalation. Deputy-dependent criteria should remain blocked
unless the exception is explicitly permitted by the G1 criteria.

### Option C — delegate G1 to an external governance authority

You nominate an actual host or governance body, transfer the defined decision
rights, and obtain its digest-bound acceptance.

Rationale: strongest separation, but it is an external appointment and cannot
be created by repository code or an agent panel.

### Option D — defer G1

Keep G1 in review while continuing unrelated repository-owned preparation.

Rationale: safest option if the scope, ethics boundary, or continuity model is
not yet settled.

## Recommendation

Select **Option A**, subject to these conditions:

1. the approved packet digest remains fixed;
2. the agent deputy is identified as an operational role only;
3. all panel findings remain advisory and are not treated as acceptance;
4. rights, local verification, human consent, independent assurance,
   hosting/custody/signing, staffing and funding remain separate gates; and
5. the candidate remains private and unpublished.

## Contingencies

- Missing deputy identity → use Option B and keep continuity-dependent work
  blocked.
- Unresolved ethics, security or rights issue → quarantine affected scope and
  defer G1 acceptance.
- Packet mutation → invalidate this packet and regenerate the digest.
- Panel disagreement → record `adjudication_required`; do not promote.
- No owner decision → record transparent deferral; G1 and downstream gates
  remain blocked.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | A, B, C or D |
| Authority | Repository owner or formally delegated authority |
| Decision date | ISO date |
| Immutable reference | Meeting/minute/decision identifier or equivalent |
| Conditions | Explicit scope and residual-risk conditions |
| Status | `accepted`, `deferred` or `rejected` |

Only after these fields are supplied may the maintainer run:

```bash
gfjd conductor decision G1 --status STATUS \
  --authority "ACCOUNTABLE AUTHORITY" \
  --reference "IMMUTABLE DECISION REFERENCE" \
  --conditions "EXPLICIT CONDITIONS" \
  --notes "Link to this packet and signed decision record"
```

The owner decision must be bound to the exact packet digest. A conversation
approval, panel consensus, local test or generated artefact alone cannot move
G1 to `accepted`.

## Dependency disposition plan

The panel classified G1 dependencies as follows:

| Class | Items | Closure route |
|---|---|---|
| Owner-decidable | Charter, scope, aggregate-only/prohibited-data/security boundaries, RACI, pilot subset, escalation, residual-risk posture, deputy model and private-candidate policy | Owner digest-bound decision |
| Agent-evidenced | Completeness, conflicts, threat modelling, methods dependencies, rights triage and continuity checks | Role-separated advisory reports with options, rationale and contingencies |
| Non-substitutable | Legal rights, local/human verification, independent assurance, consent/safeguarding, hosting/custody/signing, live support, staffing and funding | `pending_authority`, `evidence_missing`, `waived_for_scope` or `excluded`; never inferred as accepted |

If the objective is literally to remove external dependency from the current
scope, the only honest route is to re-scope to a private public-source,
metadata-only and synthetic-rehearsal product: no participant data, uncertain-
rights redistribution, live service, signed release or G6 claim. That is a
scope exclusion/deferment, not a passed gate. Each exclusion requires owner
rationale, expiry and a reopen trigger.
