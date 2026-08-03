# Staffing and funding decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `903f3ac09fa9c93dadc3362131f539df3f03c1a7`
- `MANIFEST.sha256` SHA-256: `3e3c5959454802af54b3fb76514529afeb3370c667739d5089c4c5df8a3aa726`
- Scope: T8/T9 operating continuity, G5 release-candidate operations and G6
  12-month service/support/funding requirements.
- Panel inputs: staffing, funding and sustainability-risk agents.

Agent panels can model workload, propose RACI and audit supplied commitments.
They cannot appoint people, commit funds, accept contracts, provide 24/7
support or create accountable staffing authority.

## Owner policy selection

The owner approved **S1 in principle** on 2026-08-02, with **S3 active until
commitments exist**: plan an owner-accountable model with a named agent
operating deputy, committed specialist/service roles and a 12-month resource
plan, while retaining a private rehearsal and candidate. No live service, G6
claim or funding evidence is inferred until actual date-bound commitments are
supplied.

## Options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| S1 | Owner-accountable model with named agent operating deputy, committed specialist pool, service provider and 12-month resource plan | **Recommended for planning** | Fits a single-person repository while covering continuity and specialist needs |
| S2 | External funded host/operator and governance team | Strongest later route | Best resilience and independence, but requires real contracts and resources |
| S3 | Owner and agents only; private rehearsal and maintenance | Interim fallback | Safe for preparation, but cannot support live-service or G6 claims |
| S4 | No funded live operation; retain private unsigned candidate/static metadata archive | Strict fallback | Prevents unfunded publication and unsupported support promises |

## Recommendation

Adopt **S1 for planning**, with **S3 active until commitments exist**. Before G5
or G6, obtain a signed, digest-bound commitment covering:

- accountable owner and named agent deputy;
- service/release manager and deputy;
- support/incident contact and coverage hours;
- archive custodian and signing authority;
- security/privacy, rights/legal, accessibility and safeguarding roles;
- allocation or hours/month, skills, training and handover;
- hosting/procurement terms and support SLA;
- 12-month budget amount, currency, source, payer/approver, restrictions,
  renewal trigger and expiry review;
- staffing coverage for snapshot RPO ≤24 hours, service RTO ≤4 hours and
  archive restore RTO ≤24 hours.

## Contingencies and promotion rules

- No deputy → no live service or G6; retain private rehearsal.
- No funding → private unsigned candidate only.
- Missing specialist → quarantine its gate.
- Staffing lapse → suspend publication and incident processes.
- Partial funding → reduce pilot scope; no G6 claim.
- Funding expiry/withdrawal → freeze maintenance, close intake and retain a
  read-only archive.
- Safeguarding resources absent → no participant beta.
- Changed roles, scope or budget → invalidate the packet and re-adjudicate.

The staffing/funding gate remains `pending_authority`/`evidence_missing` until
actual date-bound commitments and owner adjudication are supplied. Agent-panel
consensus and owner intent are not funding or staffing evidence.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | S1, S2, S3 or S4 |
| Owner/deputy and role commitments | Named identities, scope and availability |
| Funding commitment | Amount, currency, source, term and approval |
| Decision date | ISO date |
| Immutable reference | Decision/contract/reference identifier |
| Conditions | Scope, staffing and renewal conditions |
| Status | `approved_in_principle`, `accepted` or `deferred` |
