# G2 formal-run evidence index — 2026-08-15

Status: initial formal run completed and failed closed; diagnostic evidence
only. No extracted value, method, right, gate, publication or release is
accepted.

## Frozen inputs

- Owner policy decision: signed commit `2627ed68d3545a6f2d95dbc68a922e449ef71355`.
- Frozen packet: `G2PKT-REAL-PILOT-20260815-01`, SHA-256
  `c76b2314c68d3bf269e1e8ce3c8abd02206a6ea26ee8aaedcabc2dcdbf723e06`.
- Frozen packet commit: signed commit
  `0c392210fcb92d3e492b56670fde448f0426570b`.
- Hardened comparator commit: signed commit
  `22a716f6d02aa07b8f18759e89a4ad3775456d6b`.

The comparator hardening occurred after packet 01 was frozen. It added exact
sample-scope and component-key checks and changed the bound concordance schema.
Packet 01 therefore remains diagnostic and must be superseded by a fresh packet
before formal reliance.

## Local-private sealed outputs

The full outputs remain under ignored `build/g2-real-pilot/` storage. The
repository records their digests without publishing their contents.

| artifact | SHA-256 | state |
|---|---|---|
| primary output | `c8df8674ab736997f951e58553ad630e46d9cb32b083528db842a8f4b38001f5` | 4 schema-valid rows; local-private |
| primary receipt | `0def41bcf2a36a7ce963c3fe447f7e980b445cff5834ba65c721dd3e0f4208c0` | schema-valid |
| secondary output | `244d0da6fe4f2d181452bb9b674391a5fc9850f5cf4d92cbcc193094741a86bb` | 4 schema-valid rows; local-private |
| secondary receipt | `f5430d9b3dbcdb22c3afbe3970961769042129e52374778b9e34242278ac15ed` | schema-valid |
| diagnostic concordance receipt | `2972a30820e0f30c98f1ca44fad1104c2db6684221083b1e3af61852ac1b16a9` | fail |
| diagnostic differences | `46079e1c783256757002ede07dbf794d7356304c8a574c1df658acc03f69c866` | 23 differences |

Four source keys matched. All requested headline and component numeric facts
matched. The diagnostic comparator recorded 58/76 critical-field matches
(76.3158%) and 59/82 populated-field matches (71.9512%). Eighteen differences
were critical. The owner-approved threshold therefore failed and cannot be
waived.

## Agent-panel advice

| report | SHA-256 | verdict |
|---|---|---|
| methods/data-quality | `46b15b6516076eb70be0957b6fef5b239a95f121fa768fd557ce7d9fd8fe7e94` | fail; 7 clerical/encoding, 3 source ambiguity, 8 overloaded-contract differences |
| rights/security/disclosure | `9b5b5eecc79d122682cad7163cb49aa345b2681267e1e2da20fb28f617963eee` | fail for release/redistribution; local-private quarantine recommended |

The reports are advisory and remain local-private with the sealed evidence.
They cannot decide methods, rights, gates, publication or release.

## Current disposition

- All four rows remain `in_review` and quarantined.
- AUS remains quarantined because the displayed percentage and prose order the
  clearance ratio differently.
- ZAF remains under hard methods quarantine because the clock text conflicts,
  components do not reconcile to the reported total and court coverage is
  incomplete.
- BRA remains a partial-year dashboard snapshot and may not be reinterpreted as
  cases, people or an annual total.
- USA-MN remains a source-defined statewide Family case-group clearance
  statistic pending the revised contract and fresh rerun.
- All four exact editions and full extraction artifacts remain local-private;
  the current public boundary is metadata/citation only unless the owner records
  a different exact-edition decision.

## Required next evidence

1. sole-owner decision on the refreeze, atomic field contract, explicit-only
   date rule, source-ambiguity quarantine and local-private rights boundary;
2. a superseding packet bound to the current schema/comparator and a canonical
   source-quotation plus atomic-semantic contract;
3. two fresh role-separated extractions and comparator recomputation;
4. digest-bound methods and rights/security panel advice on the fresh result;
5. sole-owner G2 adjudication. G2 remains blocked until those steps pass.
