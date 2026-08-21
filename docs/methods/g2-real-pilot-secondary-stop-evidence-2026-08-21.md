# G2 known-source pilot secondary extraction stop — 2026-08-21

Evidence ID: `E-PILOT-REAL-SECONDARY-STOP-20260821`

A fresh, packet-bound secondary extraction was attempted with access restricted
to the three exact source editions, packet and row schema. It did not access
the primary output, comparator output, historical packet outputs, or the
network.

## Bound result

- Packet `G2PKT-REAL-PILOT-20260821-01`: SHA-256
  `ef9391489d63428e29f9e89b386c957348e4e5ac3b35389e59b7039caf4bd2b5`.
- Failed secondary output (empty array): SHA-256
  `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570`.
- Failed secondary receipt: SHA-256
  `18ad24bd42b2db316a58c79b12c6f43b3e282767acc1dc1680fdfce5b9ffb6b1`.

The ODS and PDF targets could be read from the permitted editions. The permitted
dashboard artifact was a Power BI embed shell and did not contain rendered
table data or the required numeric value. Because the row contract requires a
numeric value, producing a dashboard row would have required fabrication,
cross-source substitution, or unapproved additional access. The run therefore
failed closed with an empty output.

## Consequence

This is a valid failed secondary-run record, not a passing re-extraction.
No comparator is run against an empty output; no primary result is promoted.
The next valid route is to acquire a digest-bound dashboard visual/data export
or revise the packet to exclude that route under a new owner decision. Until
then all three primary rows remain quarantined and G2 remains blocked.
