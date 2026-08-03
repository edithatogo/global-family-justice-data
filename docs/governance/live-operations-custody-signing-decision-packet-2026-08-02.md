# Live operations, custody and signing decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `7d9d511873c5f18294522bab518aa74c0f134b8e`
- `MANIFEST.sha256` SHA-256: `2d2d9afc8b1372446d9d60cdb71cc7c3852ae980a327005a3242c7f13fbb149a`
- Panel inputs: hosting/operations, custody/restore and signing/release agents.

## Scope and boundary

This packet addresses hosting, service ownership, monitoring, support, incident
response, archival custody and signing for G5/G6. Agent panels may assess
completeness and rehearse procedures; they cannot host a service, accept
custody, sign a release, commit funding, or close an assurance gate.

## Options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| O1 | Private live-like rehearsal now, followed by named accountable service, custody and signing authorities | **Recommended** | Enables autonomous preparation while preserving real authority boundaries |
| O2 | Commission an independently administered hosting/archive/signing operator | Strongest later route | Improves separation and continuity, but requires procurement and funding |
| O3 | Local rehearsal with unsigned, private candidate | Safe fallback | Permits testing without unsupported deployment or custody claims |
| O4 | Owner-only self-hosting and signing | Not recommended | Creates a bus-factor and independence failure for G5/G6 |

## Recommended route

Select O1. Run a digest-bound rehearsal against the private candidate, then
obtain evidence and acceptance from named authorities for hosting, service
management, support, custody and signing. Keep the candidate private and
unsigned until every required record is accepted.

## Required evidence

- hosting operator, region, service boundary, SLA, monitoring and incident contact;
- named service/release manager and deputy, support/ticketing workflow and incident runbook;
- two-location custody with independent administration, retention and tested restore (target snapshot RPO ≤24 hours, service RTO ≤4 hours, archive-restore RTO ≤24 hours);
- restore receipt with source/restored SHA-256 values, location identifiers,
  timestamps, operator role and proof of no unauthorised writes;
- signing authority, key generation/storage/rotation/revocation/recovery procedure and signed digest;
- committed 12-month staffing and funding plan;
- rehearsal receipts recording actual outcomes, gaps, corrective owners and dates;
- authority identity, scope, decision date, immutable reference and release digest.

## Contingencies and gate rules

- Missing host or support evidence → `pending_authority`; private bundle only.
- No independent custody → local unsigned rehearsal only; archive and release blocked.
- Failed restore or signing verification → `adjudication_required`; quarantine candidate.
- Signing-key compromise → revoke/suspend, preserve evidence, issue incident record and re-sign only after review.
- Packet mutation → invalidate all reports and rerun the rehearsal.
- Missing funding or staffing → no live service or G6 claim.
- No authority decision → transparent no-decision closure; no promotion or archive.

Agent-panel verdict: **conditional** for O1/O3 preparation; `pending_authority`
for live hosting, independent custody, signing and funded support.

## Owner policy selection

The owner approved **O1 in principle** on 2026-08-02: run a private,
digest-bound live-like rehearsal now; obtain named service, custody and signing
authorities before G5/G6; require two-location restore, RPO/RTO, key lifecycle,
support, monitoring, staffing and funding evidence; and keep the candidate
private and unsigned meanwhile.

G5/G6 require accepted, digest-bound evidence for all mandatory controls. Panel
consensus or local rehearsal cannot satisfy those controls.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | O1, O2, O3 or O4 |
| Accountable owner | Named person/authority |
| Service/custody/signing authorities | Names, roles and scopes |
| Decision date | ISO date |
| Immutable reference | Decision/minute/reference identifier |
| Conditions | Scope, exclusions and residual risks |
| Status | `approved_in_principle`, `accepted` or `deferred` |
