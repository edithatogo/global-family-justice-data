# G2 exact-input recovery extension — 2026-09-05

This read-only recovery check extends the earlier `build/` and `data/raw/`
regular-file scan. No network requests, source reconstruction, extraction,
archive extraction to disk, or gate decisions were performed.

## Observed recovery checks

Four existing local ZIP archives were inspected in memory. Each archive was
within a 10,000-member, 300,000,000-expanded-byte, 50,000,000-byte-per-member
and 1,000:1 compression-ratio budget. Every regular member was read with ZIP
CRC verification and SHA-256 hashing; no members were written to disk.

| Archive | Members hashed | Expanded bytes | Exact matches |
|---|---:|---:|---:|
| `build/backup/gfjd-critical-state.zip` | 1,147 | 10,229,392 | 0 |
| `build/rehearsal/gfjd-0.6.0-alpha.2-rehearsal.zip` | 255 | 737,121 | 0 |
| `build/repro-first/gfjd-0.6.0-alpha.2-rehearsal.zip` | 255 | 737,121 | 0 |
| `build/repro-second/gfjd-0.6.0-alpha.2-rehearsal.zip` | 255 | 737,121 | 0 |

All 2,805 locally available Git blobs were separately hashed, including
unreachable objects exposed by `git cat-file --batch-all-objects --batch`:
68,475,849 bytes, zero exact matches. Git path history for `build/` and
`data/raw/` contained no matching original source filename. The preserved
local-branches bundle lists historical branch tips; it is Git-history recovery,
not evidence that ignored acquisition bytes were backed up.

The outer project envelope's `data/`, `docs/` and `contracts/` locations contain
four metadata/advisory files and no original source artifacts. Searches of
the checked-in governance and acquisition records did not establish an
additional owner-controlled backup locator. This is bounded absence evidence;
it does not establish permanent loss or claim an exhaustive disk search.

## Exact missing recovery set

| Artifact | SHA-256 | Recorded size |
|---|---|---:|
| BRA class-filtered API response | `626d18292c23ffe5e369b3c82c5477f9265686dca86f195021bc8f100c903da3` | 258 |
| GBR-EAW ODS | `3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2` | 990,297 |
| GBR-EAW quarterly dashboard response | `4009c22c5e0bf115205d8488838b8c9b0f224ec627a6f9bc2f2e7be02b36fae1` | 4,560 |
| Dashboard model | `668b951bbba9853609ea08bacb1da514111b75183be3c819a44c2c5d3c52f648` | Not recorded here |
| Dashboard conceptual schema | `f999b4daa44a40be1b52c1204b015d4f24153d5b6c4a2c797f38e7e329acbcf6` | Not recorded here |
| Dashboard quarterly visual query | `3711a83674db5839ad536f3e38e7a3b1523dbfee2deb97580a8604db1d3b9eb3` | Not recorded here |

The same six hashes were checked in every archive and Git blob. Packet
`G2API-BRA-TJSP-20260822-01` records the API original under
`build/g2-real-pilot-20260822-01/G2-API-BRA-TJSP-2026-class-1389.json`.
Packet `G2DASH-GBR-EAW-20260822-02` records the response under
`build/g2-real-pilot-20260822-01/G2-DASH-GBR-EAW-2026Q1-quarterly-confirmation.json`.
Acquisition metadata `G2-REAL-PILOT-ACQUISITION-20260821-01` records the ODS
filename `G2-ODS-GBR-EAW-2026Q1.ods`.

## Disposition

No original was recovered. A supplied backup containing these six exact
objects would preserve the existing source identity. Alternatively, a future
acquisition must retain newly observed hashes and be treated as new evidence
unless the bytes actually match; it cannot recreate a historical response from
documented aggregate values. The approved scope, prior successful replay,
quarantine dispositions and gate statuses remain unchanged.
