# G2 gate evidence-pack current reconciliation (2026-09-12, revision 05)

**Evidence ID:** `E-G2-GATE-CURRENT-RECONCILIATION-20260912-05`  
**Packet status:** `in_review`  
**Gate:** G2 — Reproducible pilot proven  
**Accountable authority:** repository owner and sole accountable decision-maker

This append-only reconciliation records the final disposition of the single
owner-authorized BRA replay. It supersedes no historical receipt and does not
create a qualifying provider response, maturity promotion, gate acceptance,
rights clearance, publication or release authorization.

## Current bindings

| Binding | Value |
|---|---|
| Merged `main` | `630f18e4f53ee8fef82714709314a9fd389a2b20` |
| BRA packet SHA-256 | `4620b15a9b96c8b9a66429ebff63d7f770c1b89b80b346c306f06541edb64855` |
| Owner authorization | `data/federation/g2-bra-replay-owner-authorization-20260912.json` |
| Owner authorization SHA-256 | `5d5f99f0b7284bc96a478e33c4091bea09128534bf4691c4f2b6b49fa9109699` |
| Replay receipt | `data/federation/bra-aggregate-replay-receipt-20260912.json` |
| Replay receipt SHA-256 | `0a02c2e00c38a4bb7fe9d224cc533d0edbd2893313d788ec53f1e1b4829562c3` |
| Semantic review | `data/federation/g2-bra-replay-semantic-review-20260912.json` |
| Maturity reassessment | `data/federation/g2-maturity-reassessment-20260912.json` |

## Disposition

- Exactly one POST was attempted under the corrected owner authorization.
- The response failed the frozen aggregate contract because the class bucket
  was absent or ambiguous.
- No concordance result exists; the lineage is terminal and non-retryable.
- Evidence-assured maturity remains **L1**; G2 remains
  `blocked_by_maturity`.
- No aggregate value, rights status, publication, release or Gold promotion is
  accepted from this lineage.

The next executable route must be materially distinct and separately
authorized. Replaying, repairing or inferring from this failed response is not
permitted.
