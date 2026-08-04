# G1 evidence index — 2026-08-04

This refreshed index reconciles the G1 evidence map after the T4–T9 and
risk-mitigation passes. `in_review`, `draft` and `conditional` remain
non-acceptance states.

| Criterion | Current evidence | State | Remaining blocker |
|---|---|---|---|
| G1-C01 charter/decision rights | `GOVERNANCE.md`; owner packet | in_review | Host/sponsor and independent decision-rights record |
| G1-C02 methods scope | `docs/methods/v0.3-methods-contract-manifest.json` | accepted technical | Accountable methods authority |
| G1-C03 ethics/security boundary | `docs/governance/t7-security-privacy-rights-supply-chain-control-packet-2026-08-03.md` | in_review | Accountable ethics/security acceptance |
| G1-C04 architecture | `docs/governance/t4-data-platform-engineering-control-packet-2026-08-03.md` | in_review | Accountable/independent technical approval |
| G1-C05 RACI/deputies | `docs/governance/roles-and-raci.md`; track charters | in_review | Named consenting deputies and acceptance |
| G1-C06 risks/rights/threats | `docs/governance/t7-security-privacy-rights-supply-chain-control-packet-2026-08-03.md`; `docs/governance/risk-mitigation-control-packet-2026-08-04.md` | in_review | Specialist rights/legal/privacy/security review and risk adjudication |
| G1-C07 Conductor control | `docs/architecture/conductor-system.md` | done internally | No repository-control blocker; does not substitute for other criteria |
| G1-C08 pilot universe | `data/seed/jurisdiction_register.csv`; G3/T9 verification controls | in_review | Owner scope decision and local/second-review evidence |

## Exact binding

The owner-ready handoff is `docs/governance/g1-owner-acceptance-bundle-2026-08-04.md`.
All file-level hashes are recorded in `MANIFEST.sha256`. The current gate
decision remains conditional in `programme/gate_decisions.csv`.

## Closure rule

G1 can be accepted only when every criterion has accepted evidence, required
reviewer/consent records, closed or explicitly permitted critical/high risks,
and an accountable owner decision references the exact final packet and
manifest. No agent panel, local test or repository owner statement can create
the missing third-party authority or human evidence.
