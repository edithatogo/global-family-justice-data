# WI-G2-04 exact-input gap — 2026-09-08

The offline browser-control blocker is resolved as engineering evidence, but
WI-G2-04 still cannot execute its approved empirical contract. The frozen
orchestrated packet names these four exact inputs:

| Candidate | Required input | Required SHA-256 | Current state |
| --- | --- | --- | --- |
| FIN-API | `finland-metadata.json` and `finland-observation.json` | `20621bfd4d339e4f1d724b3e2016da845303938367c92cc1fac5c07e9a74575a`; `59348fe0b98c016881de8761953983fe402490a6de19094e0acf8fcab3f362f0` | absent |
| EST-XLSX | `estonia-offences.xlsx` | `81e350d37f6d402f2570f1a0b71cfe1d3ccf2c9578ed023b8b1f1a49fa02d0ab` | acquired and hash-verified |
| EST-DASH | `estonia-domestic-violence.csv` | `f0024a590b3423c8b533f95ed597e6fa6f8672b9bee1450403f09296b7fe45b9` | acquired and hash-verified |
| ZAF-PDF | `south-africa-report.pdf` | `41aee1f16221da483677619fc314060a318a5b2a6d7c4ff615a3af5f6952acee` | acquired and hash-verified |

This was checked against the repository tree. The ZAF edition was subsequently
acquired from the official Department of Justice report index and matches its
frozen hash; its custody receipt is
`g2-zaf-exact-custody-2026-09-08.json`; the bytes are retained in ignored
durable controlled storage under `data/raw/files/g2-controlled/`. Existing ODS/PDF files are different
editions and are not substitutes for the two still-absent inputs. The EST-XLSX
edition was acquired from the official Justice Statistics workbook URL and
matches its frozen hash; its custody receipt is
`g2-estonia-xlsx-exact-custody-2026-09-08.json`. No
extraction, concordance result, WI-G2-04 acceptance or G2 promotion may be
inferred from source presence alone.
The EST-DASH edition was acquired from the official Justice Statistics
domestic-violence CSV endpoint and matches its frozen hash; its custody receipt
is `g2-estonia-dashboard-exact-custody-2026-09-08.json`.

## Required next action

Acquire or restore the two remaining exact editions under the already approved source
access boundary, verify byte hashes and custody receipts, and only then run two
fresh isolated extractors plus the network-disabled comparator. If any edition
cannot be restored exactly, stop and return the bounded scope decision; do not
replace it silently.

This record is a blocker register, not an authorization to contact a provider,
accept terms, clear rights, publish, release or pass G2.

## Recovery audit — 2026-09-08

The frozen hashes were checked against reachable and unreachable Git objects;
the three hashes absent at that audit did not match. Official Estonia catalogue pages were located as metadata-only
candidates, including NH25 (2025 offences by administrative unit), but they do
not establish the frozen `EST_JUSTDIGI_DV_SNAPSHOT_20260525` CSV and were not
substituted.

The audit is reproducible from the repository at
`https://github.com/edithatogo/global-family-justice-data.git`, checked at
commit `f997f64519b4271232eb35481c09983bb898aaa4`. The local object inventory
reported `count=603`, `in-pack=5912`, `packs=2`, `prune-packable=0`,
`garbage=0`; `git fsck --full --no-reflogs --unreachable` reported 13
unreachable-object lines. For each frozen input hash, the exact command
`git cat-file -e <hash>^{blob}` returned `ABSENT` for the three hashes checked;
no matching blob was found in reachable or unreachable Git objects. The audit
therefore establishes absence from this clone's Git object database only, not
absence from external storage.

The metadata-only Estonia candidate is the stable official Statistics Estonia
NH25 locator:
`https://andmed.stat.ee/en/stat/eri-valdkondade-statistika__noorteseire/NH25`.
It remains a non-substituting hypothesis because its series identity and
edition bytes do not match the frozen EST-JUSTDIGI hashes.
