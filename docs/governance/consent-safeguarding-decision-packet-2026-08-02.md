# Consent and safeguarding decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `a2dc0092fb620e0f4138f7bb95a39f551619bf12`
- `MANIFEST.sha256` SHA-256: `b5e61cf3978b720e26764f8acba5250195ffbec078d5b24912e6597fbe6221ba`
- Scope: G4 beta participation, G5 release-candidate claims and G6 public
  release/representation boundaries.
- Panel inputs: ethics/safeguarding, participation design and safeguarding
  operations agents.

Agent panels provide advice only. They cannot grant ethics approval,
safeguarding clearance, legal authority, consent, participant agreement or gate
acceptance.

## Owner policy selection

The owner approved **C1 in principle** on 2026-08-02: synthetic,
non-participatory rehearsal only; no participant data, recruitment, beta or
participant-derived/representation claims. C2 requires a named safeguarding
authority, digest-bound consent protocol, participant protections, incident
handling and accountable acceptance.

## Options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| C1 | Synthetic, non-participatory rehearsal; no participant data | **Recommended now** | Safest immediate path while preparing protections and authority |
| C2 | Bounded consented beta after named safeguarding authority approval | Recommended later | Enables genuine participation only after protections are independently reviewed |
| C3 | External ethics/safeguarding body hosts or reviews participation | Strongest independence | Requires an actual appointment, resources and participant pathway |
| C4 | No participant research; public-source aggregate products only | Fallback | Removes participation risk but narrows claims and engagement scope |

## Required evidence for C2/C3

- Named safeguarding authority and accountable owner.
- Current risk/harms assessment and eligibility/exclusion rules.
- Plain-language, multilingual, accessible information and consent forms.
- Assent/guardian process where applicable; no minors or high-risk groups
  without specialist safeguards.
- Voluntary recruitment, no coercion, remuneration and support/referral plan.
- Withdrawal, deletion, retention and coded-identifier procedures.
- Privacy/data-flow and aggregate-only boundary.
- Incident severity, escalation, contact and adverse-event log.
- Accessibility/interpreter arrangements, debrief and feedback records.
- Consent audit trail bound to the exact packet digest.
- Staff training, insurance and funding evidence where applicable.

## Recommendation

Adopt **C1 now**. Prepare the C2 packet but collect no participant data and
make no participant-derived or representation claims. Authorise C2 only after
the owner approves the exact protocol and a named safeguarding authority
accepts it against a frozen digest.

## Contingencies and promotion rules

- Missing authority or consent → `pending_authority`/`evidence_missing`; no
  recruitment or beta.
- Vulnerable/minor participant without specialist safeguards → exclude and stop.
- Withdrawal → stop use and apply the stated deletion/quarantine procedure.
- Incident or open critical/high harm finding → suspend participation, preserve
  the incident record, escalate and rerun review.
- Protocol mutation → invalidate consent and require re-consent.
- Panel disagreement → `adjudication_required`.
- No support, service or funding → synthetic dry-run only.

G4 beta, G5 release claims and G6 publication remain blocked until the
consent/safeguarding packet, accountable acceptance and harms findings are
complete. Agent consensus cannot satisfy these conditions.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | C1, C2, C3 or C4 |
| Authority | Repository owner or formally delegated safeguarding authority |
| Decision date | ISO date |
| Immutable reference | Decision/minute/reference identifier |
| Conditions | Scope and participant protections |
| Status | `approved_in_principle`, `accepted` or `deferred` |
