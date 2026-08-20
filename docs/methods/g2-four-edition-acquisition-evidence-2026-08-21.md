# G2 four-edition acquisition evidence — 2026-08-21

The owner authorized acquisition and aggregate-only processing of the four
exact editions in `G2-CANDIDATE-INTAKE-REAL-PILOT-20260821-01`. This record
documents the resulting local inputs without publishing source bytes.

## Bound records

- Candidate intake: SHA-256
  `d3ee890207b4a58d8b5808d43b78dbc0da47ea87eb46d5f0a304c26f96878ed5`.
- Acquisition plan: SHA-256
  `09af170d3e92b6c4e4fdb6583355c36db8e2c82f5bf3fa96953a67eb55458a15`.
- Owner direction: SHA-256
  `f0d052790af315f177a6322e13862c5b6592813bdb4b69fac93cf1f02c58dd0b`.

| Candidate | Local result | SHA-256 | Processing result |
| --- | --- | --- | --- |
| DataJud TJSP API | JSON, 884 bytes | `f475ae52b31f0e9a509de1be1d312bb946f4f57944717d0bda5d68d1f59df2fe` | `hits.hits` was empty; 20 `case_classes` aggregation buckets only. |
| England and Wales Family Court tables | ODS, 990,297 bytes | `3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2` | Valid ODS container with five members. |
| Family Court Public Law Visualisation Tool | HTML entry document, 32,569 bytes | `52d356701a10ac6519da61d82ecf3f0cb0e04921597f19a4df6fe721687ac63f` | Exact Power BI entry document captured; no rendered visual or value extraction claimed. |
| FCFCOA annual report 2024–25 | PDF, 13,442,996 bytes | `e251da7a9424aeba5e8c9e53a7f33fc5901769b10e6e0ea27f5b446bc5fd2ee9` | 340-page, unencrypted PDF. |

The first DataJud key-discovery attempt is preserved as a local receipt; it
made no API request. The aggregate query was then acquired using the current
public key documented by DataJud, with `size: 0` and a class aggregation. The
API response invariant rejects any non-empty hit list.

## Status

This is factual, hash-bound acquisition evidence for a known-source pilot.
It is not a rendered dashboard capture, extraction, re-extraction,
methods adjudication, rights determination, publication, release, or G2
passage. Source conditions remain recorded as information under the owner
direction and do not stop this bounded work.
