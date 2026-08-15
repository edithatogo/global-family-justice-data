# G2 packet-05 evidence index — 2026-08-15

Status: final calibration rerun completed, failed closed and terminated by the
sole owner. Local-private diagnostic evidence only. No output, method, right,
gate, publication or release is accepted.

## Frozen packet and authority

- Packet: `G2PKT-REAL-PILOT-20260815-05`.
- Packet SHA-256:
  `6e10d325249fe8942942e9139f04773bb6b169f3e75d06ef691145b34996e198`.
- Signed freeze commit: `dee7fd9ef61f2885e5d61b4269642d82a14e867a`.
- Input-manifest SHA-256:
  `254db9e0f9b97633b5d6f3a4b9687f624e74d1d6987b00d7c32a21a6bd98ddea`.
- Owner decision:
  `docs/governance/g2-packet05-domain-owner-decision-2026-08-15.md`.
- Decision commit: `a22330fe5ae53dfc2782bea00e85feacfeefc400`.
- Executable domain amendment commit:
  `9c9935befcf593dfa8e4cbfe2b1b7068d33438de`.

## Local-private sealed artifacts

| artifact | SHA-256 | state |
|---|---|---|
| primary output | `5d61825d7edcd080b4b11adfac1d0f2b458e7f633b064781d1b8ba64eda65044` | four schema-valid rows; sealed |
| primary receipt | `e5d9858e1e434f0471a5239f6d1f9b5bd026b315ca4a366e0e65947649cbd173` | schema-valid and digest-bound |
| secondary output | `f17f3e32536b6acc8dd8341e8c770943fba09f693e4b00814ef18cb61685654d` | four schema-valid rows; sealed |
| secondary receipt | `fc0a92ced048cf7a20852dd7b3d2668aa3418c5fad2f16cc281fc75a931be8b5` | schema-valid and digest-bound |
| concordance receipt | `4c3bd5a5e4a129ef35dde024ebcf01331a45f474c55a438ebef6266cc5b68386` | fail |
| differences | `ce1f59024f781952a773823c27182c773fc8732b6de9089a2d4754f07d231402` | one critical difference |

The two runs matched all four source keys and 167/168 critical comparisons
(99.4048%). They matched 155/156 populated-field comparisons (99.3590%). The
overall threshold passed but the non-waivable 100% critical threshold failed.

The sole difference is BRA `cohort_definition_quote`:

- primary: `Tipo Processo (casos novos) Ano 2026 Dados até 30/04/2026`;
- secondary: `Processo (casos novos) Todos Ano 2026 Dados até 30/04/2026`.

Direct source inspection supports the primary sequence. `Todos` belongs to
separately labelled coverage filters and is not part of the bounded cohort
sequence. This does not permit repair of either sealed output.

## Role-separated advisory panel

| role | report SHA-256 | recommendation |
|---|---|---|
| exact source boundary | `81b4f35cc67bfd2c2af7fe69f04a7e7a9de62508f0d6875456c6c55b7351789e` | terminate; primary source-supported, secondary inexact |
| methods and reproducibility | `a73acb589903561392952be47bec30c8734724ed7137a6c1785116988986d2f1` | terminate; optional three-row sensitivity evidence cannot pass packet 05 |
| governance and contingency | `cf0378d1b100c1f9d8c5c15a0673b6c1c5bbb885760c2d1a9eaaab498eae58d0` | terminate; exclusion is a separately authorized post-failure option only |

All three schema-valid reports bind the packet, sealed outputs and receipts,
comparison and difference evidence. They are advisory and remain ignored
local-private artifacts.

## Fail-closed consequence

Packet 05 is the final calibration packet. No packet 06, fuzzy match, critical
waiver, sealed-output correction or retroactive rule is authorized. The
four-row exercise cannot establish reproducibility. All rows retain their
quarantine state; the public boundary remains metadata and citation only.

The owner selected termination in
`docs/governance/g2-packet05-disposition-owner-decision-2026-08-15.md`.
No three-row recomputation or packet 06 is authorized. Any future claim of
generalisability requires a separately approved, prospectively designed blind
holdout using unseen editions.
