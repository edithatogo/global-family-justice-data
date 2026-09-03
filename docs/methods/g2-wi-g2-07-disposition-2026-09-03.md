# WI-G2-07 disposition record — 2026-09-03

Status: repository-owned evidence reconciliation; not G2 acceptance.

The current orchestrated blinded lineage is preserved as immutable terminal
failed evidence. It cannot satisfy the approved re-extraction threshold.

The disposition is bound to packet `G2PKT-MATERIAL-ORCHESTRATED-20260826-01`
(SHA-256 `1dcfe445a2179670fa4cc759e7e98774974a6b7c62639734e1d31d27e92b6b7b`)
and terminal result SHA-256
`5b1dd48d3f73e5a8e8faa8b7f9e6dfe2e9ae5a0815c3f05be33e3c298b31700e`.

| measure | observed | required |
|---|---:|---:|
| critical concordance | 58/76 (76.3158%) | 100% |
| populated-field concordance | 42/60 (70%) | at least 99% |

The comparator stopped on 18 critical differences. No repair, fuzzy match,
waiver, failed-output reuse or automatic rerun is permitted. The four-row
outputs remain quarantined and the advisory review remains advisory only.

WI-G2-07 can close only after a new authorized lineage produces a valid,
threshold-passing exact comparator receipt and the sole owner records a
digest-bound adjudication. This record does not claim independent assurance,
rights clearance, G2 passage, publication or release.
