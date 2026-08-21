# G2 dashboard period confirmation — 2026-08-22

This is the authorized confirmation query for the dashboard/ODS period
question. It preserves the annual result and changes only the dashboard
period filter to `Quarterly`.

## Bound query and result

- Packet: `data/methods/g2/G2DASH-GBR-EAW-20260822-02/packet.json`
- Same visual: `Volumes` → `Regional/DFJ Volumes`, visual `7945851748`.
- Same type, geography and date bounds; only `Period` changed to `Quarterly`.
- Query SHA-256:
  `3711a83674db5839ad536f3e38e7a3b1523dbfee2deb97580a8604db1d3b9eb3`.
- Response SHA-256:
  `4009c22c5e0bf115205d8488838b8c9b0f224ec627a6f9bc2f2e7be02b36fae1`.

The response explicitly includes row label `2026-Q1` with value **4,917** and
count type `Orders applied for`. No case-level records were retained.

## Methods disposition

This closes the specific period-label ambiguity: the dashboard independently
exposes an explicit `2026-Q1` row matching the ODS value and count label. The
ODS/dashboard pair may therefore be considered same-series cross-format
reconciliation evidence, not independent corroboration. The rows remain
quarantined pending denominator/reporting-universe adjudication, rights and
security assessment, and the owner’s grouped methods decision.

No value is promoted, published, redistributed or used to pass G2 by this
record.
