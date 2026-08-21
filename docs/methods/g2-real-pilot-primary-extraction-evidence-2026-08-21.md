# G2 known-source pilot primary extraction — 2026-08-21

Evidence ID: `E-PILOT-REAL-PRIMARY-20260821`

This records one digest-bound **primary** extraction from the three-row
known-source calibration packet. It is not a secondary extraction,
concordance result, methods adjudication, publication, or G2 acceptance.

## Bindings

- Packet: `G2PKT-REAL-PILOT-20260821-01`, SHA-256
  `ef9391489d63428e29f9e89b386c957348e4e5ac3b35389e59b7039caf4bd2b5`.
- Packet-local row schema: SHA-256
  `78f8554d8e7cd05d56958eff69bc6188902a1b280670aeab900666c6ce31abde`.
- Primary output (local controlled evidence): SHA-256
  `24256c4639978cf5c19e0e4ac04b736ec6ed0ba5efef2e8fed322cf32bfcfa45`.
- Primary receipt (local controlled evidence): SHA-256
  `e94d00bb88617d4456773f6862f1086898bcc950a4218b52d793e103afa97b4d`.

The controlled output contains three quarantined rows: the England-and-Wales
ODS target, the bounded visible dashboard target, and the FCFCOA PDF target.
The primary receipt binds the exact ODS, dashboard-entry and PDF source hashes.

## Result and limits

The primary run validates against the packet-local schema. Its dashboard row
records the visible annual-table state bounded through 1 March 2026, and does
not claim a byte-level dashboard export. All ISO dates remain null under the
packet's explicit-only date rule.

`E-PILOT-REAL-PRIMARY-20260821` remains `in_review`. A fresh secondary session
must use the packet-bound secondary bundle without reading the primary output.
Only after a digest-bound second output and exact concordance may methods and
owner adjudication be considered. All rows remain quarantined meanwhile.
