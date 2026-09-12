# G2 gate evidence-pack current reconciliation (2026-09-12, revision 04)

**Evidence ID:** `E-G2-GATE-CURRENT-RECONCILIATION-20260912-04`  
**Packet status:** `in_review`  
**Gate:** G2 — Reproducible pilot proven  
**Prepared:** 2026-09-12  
**Accountable authority:** repository owner and sole accountable decision-maker

This append-only reconciliation supersedes no historical receipt. It binds the
merged `main` after PR #244 and local stale-reference pruning. It does not
create a provider response, maturity promotion, gate acceptance, rights
clearance, publication or release authorization.

## Current bindings

| Binding | Value |
|---|---|
| Merged `main` | `ffb63452122c8d9d876f075eda05a914d164637a` |
| Current `main` `MANIFEST.sha256` SHA-256 | `3ffaaea7819b66fe884481176e3ba19a44c9b36e3fbd5811da68335377d4589f` |
| Prior reconciliation | `docs/governance/g2-gate-evidence-pack-current-reconciliation-2026-09-12-03.md` |
| Prior reconciliation SHA-256 | `3a2c97dc34497a5fb4faecbc96baaf78edad2559716658b3fa1108299a2681f1` |
| BRA execution packet | `data/federation/bra-aggregate-replay-execution-packet-20260911.json` |
| BRA packet SHA-256 | `4620b15a9b96c8b9a66429ebff63d7f770c1b89b80b346c306f06541edb64855` |
| BRA credential-readiness diagnostic | `data/federation/bra-aggregate-replay-credential-readiness-20260912.json` |
| BRA credential-readiness SHA-256 | `eb0adf97d0decf56efd6ae35c8e999e5087309a90cad39ae037ecb86cc3fb1ef` |
| Merge/CI evidence | PR #244; all required checks passed; merge commit above |

## Current disposition

- G2 remains `blocked_by_maturity`; evidence-assured maturity remains L1
  against the required L2 floor.
- The bound BRA packet remains stopped because the runtime credential and owner
  authorization record are absent; no provider call was attempted.
- Existing replay, hosted-registry and hosted-monitor receipts remain
  repository-owned supporting evidence only.
- Rights, privacy, security, disclosure, publication and release boundaries are
  unchanged and fail closed.

The next executable action remains the single packet-bound BRA request after a
valid owner authorization record and runtime credential are available. Failure
or absence of either keeps the lineage stopped; no retry or substitution is
permitted.
