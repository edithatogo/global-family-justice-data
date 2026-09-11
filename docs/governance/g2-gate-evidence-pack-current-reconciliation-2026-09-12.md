# G2 gate evidence-pack current reconciliation (2026-09-12)

**Evidence ID:** `E-G2-GATE-CURRENT-RECONCILIATION-20260912`  
**Packet status:** `in_review`  
**Gate:** G2 — Reproducible pilot proven  
**Prepared:** 2026-09-11  
**Accountable authority:** repository owner and sole accountable decision-maker

This append-only reconciliation supersedes no historical receipt. It records the
current merged head and its parent manifest snapshot while preserving the earlier G2 addendum as
immutable lineage. It does not create a response, maturity promotion, gate
acceptance, rights clearance, publication or release authorization.

## Current bindings

| Binding | Value |
|---|---|
| Merged `main` | `c7dfcdf1625f85f35f3c5c35763c32f62e7e8f3f` |
| Parent `main` `MANIFEST.sha256` snapshot SHA-256 | `d403d552736878781d910d34cff1fa659831f72d0624dfafaaf4941946a50e30` |
| Historical addendum | `docs/governance/g2-gate-evidence-pack-addendum-2026-09-12.md` |
| Historical addendum SHA-256 | `9e3a8fa5d2bd209171f9fca1fa783f91ff14313cb04d8cdb098208b8527def9a` |
| BRA execution packet | `data/federation/bra-aggregate-replay-execution-packet-20260911.json` |
| BRA packet SHA-256 | `4620b15a9b96c8b9a66429ebff63d7f770c1b89b80b346c306f06541edb64855` |
| BRA executor-preparation SHA-256 | `306d796ac663901121058dd4c64d4de7166f57243bf98aab0e99a9890be3dfa4` |

## Current disposition

- G2 remains `blocked_by_maturity`; evidence-assured maturity remains L1
  against the required L2 floor.
- The bound BRA packet remains `awaiting_owner_execution_authorization`.
- No provider call, response receipt, semantic review or L2 reassessment is
  present in this reconciliation.
- Existing replay receipts remain repository-owned supporting evidence only.
- Rights, privacy, security, disclosure, publication and release boundaries are
  unchanged and fail closed.

The next executable action remains the single packet-bound BRA request after a
valid owner authorization record and runtime credential are available. Failure
or absence of either keeps the lineage stopped; no retry or substitution is
permitted.
