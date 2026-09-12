# G2 gate evidence-pack current reconciliation (2026-09-12, revision 02)

**Evidence ID:** `E-G2-GATE-CURRENT-RECONCILIATION-20260912-02`  
**Packet status:** `in_review`  
**Gate:** G2 — Reproducible pilot proven  
**Prepared:** 2026-09-12  
**Accountable authority:** repository owner and sole accountable decision-maker

This append-only reconciliation supersedes no historical receipt. It binds the
current merged head after the hosted B0 monitoring receipt was recorded, while
preserving earlier reconciliations and the BRA execution boundary as immutable
lineage. It does not create a response, maturity promotion, gate acceptance,
rights clearance, publication or release authorization.

## Current bindings

| Binding | Value |
|---|---|
| Merged `main` | `4dd9e466c9f856a97ee4c09c1f9c3519d2ca3cb1` |
| Current `main` `MANIFEST.sha256` SHA-256 | `1fdb6647706ea022f82bc16fdc56dd18ad7108e186a98091a49489741a397a64` |
| Prior reconciliation | `docs/governance/g2-gate-evidence-pack-current-reconciliation-2026-09-12.md` |
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
- Existing replay and hosted-monitor receipts remain repository-owned supporting
  evidence only.
- Rights, privacy, security, disclosure, publication and release boundaries are
  unchanged and fail closed.

The next executable action remains the single packet-bound BRA request after a
valid owner authorization record and runtime credential are available. Failure
or absence of either keeps the lineage stopped; no retry or substitution is
permitted.
