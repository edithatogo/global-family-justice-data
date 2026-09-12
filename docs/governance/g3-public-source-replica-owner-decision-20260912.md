# G3 public source-replica owner decision packet — 2026-09-12

**Decision required:** repository owner and sole accountable authority  
**Purpose:** reconcile the already-public B0 source-byte replicas before any
further G3/G4 promotion. This packet is repository-owned preparation; it is
not a rights opinion and does not itself delete, retain, publish, release or
clear any source.

## Exact affected replicas

The following six inventory records are listed in
`data/preservation/public_b0_custody_20260827.json`. Each has an identical
Hugging Face dataset replica and GitHub release replica; the SHA is the
source-byte identity recorded by the custody register.

| inventory | SHA-256 | current rights class | Hugging Face replica | GitHub replica |
|---|---|---|---|---|
| `ARC-GBR-EAW-2026Q1` | `8ea470874a6d24ca0db2c7253dd4141f595304262617248c2063ecd0e4cb1c96` | `review_required` (OGL/third-party conditions require recheck) | [FCSQ 2026 Q1](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-GBR-EAW-2026Q1/FCSQ_2026_Q1.zip) | [FCSQ 2026 Q1](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-GBR-EAW-2026Q1__FCSQ_2026_Q1.zip) |
| `ARC-AUS-FCFCOA-202425` | `e251da7a9424aeba5e8c9e53a7f33fc5901769b10e6e0ea27f5b446bc5fd2ee9` | `unknown` (conditional notice; exceptions unresolved) | [annual report](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-AUS-FCFCOA-202425/annual-report-2024-25.pdf) | [annual report](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-AUS-FCFCOA-202425__annual-report-2024-25.pdf) |
| `ARC-BRA-CNJ-2026` | `3415d516d756f48d7337e83e6faa8477644fe98b5cedb43cb04999f59fd5a71f` | `unknown` | [Justiça em Números](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-BRA-CNJ-2026/justica-em-numeros-2026.pdf) | [Justiça em Números](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-BRA-CNJ-2026__justica-em-numeros-2026.pdf) |
| `ARC-SWE-DOMSTOLSVERKET-2026` | `47a751d419ffc4861eda29580654cc1a5053a2852f05052e5c387b61c6dceceb` | `unknown` | [family-cases workbook](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-SWE-DOMSTOLSVERKET-2026/Cases%20filed%20and%20determined%2C%20family%20cases%20in%20district%20courts%202025.xlsx) | [family-cases workbook](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-SWE-DOMSTOLSVERKET-2026__cases-filed-and-determined-family-2025.xlsx) |
| `ARC-ZAF-JUD-202425` | `24991662becb0c299624d5dae43f45425f8dac77bc7a3c93eac0fd012c3485ce` | `unknown` | [annual judiciary report](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-ZAF-JUD-202425/annual-judiciary-report-2024-25.pdf) | [annual judiciary report](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-ZAF-JUD-202425__annual-judiciary-report-2024-25.pdf) |
| `ARC-USA-MN-MJB-PERF-2024` | `329314940f94aedc369d92992d5eb335c22f717984cc4f90020d14d94e7cd38b` | `review_required` (official terms restrict reproduction; agreement may be required) | [performance measures](https://huggingface.co/datasets/edithatogo/gfjd-source-archive/resolve/16e804c5d2bbcc650b78c0c0dea0b6e34ef7663d/sources/ARC-USA-MN-MJB-PERF-2024/Annual-Report-2024-Performance-Measures.pdf) | [performance measures](https://github.com/edithatogo/global-family-justice-data/releases/download/b0-source-archive-2026-08-27.1/ARC-USA-MN-MJB-PERF-2024__Annual-Report-2024-Performance-Measures.pdf) |

These URLs and hashes are reproduced from the custody record; no new source
request or provider contact is made by this packet. Existing retrieval and
exposure receipts remain immutable.

## Options

### A — Retain all replicas after exact clearance

Obtain and record exact-edition permission or a licence covering both provider
replicas, attribution, third-party components, database rights and derived
extracts for every row. Until each row is cleared, it remains metadata-only and
ineligible for promotion.

### B — Remove or quarantine every uncertain/restricted replica (recommended)

Remove the six source-byte replicas from the GitHub release and Hugging Face
dataset, retain only hashes, locators, custody/exposure receipts and derived
metadata, and record provider-specific removal receipts. This is the safest
fail-closed path while preserving reproducibility lineage without asserting
rights.

### C — Split by evidence class

Retain only editions with a documented exact-edition licence (currently none is
unconditionally cleared in the custody register), and remove/quarantine all
`unknown` or `review_required` rows. This reduces exposure but still requires a
separate clearance record for any retained row.

## Recommendation and contingency

Recommend **B** unless the owner can bind exact permission for each replica.
If removal cannot be completed immediately, use **C** as an interim owner
control: mark all affected rows quarantined, disable further promotion and
record an expiry and reopen trigger. If any provider cannot supply a removal
receipt, preserve the locator and hash as an unresolved exposure and keep G3,
publication and release blocked.

## Single grouped owner wording

> I select Option **[A/B/C]** for the six exact public source-replica pairs
> listed in the G3 public source-replica owner decision packet dated
> 2026-09-12, binding each inventory ID, SHA-256, provider locator and current
> custody/exposure receipt. Until the selected conditions are evidenced, every
> affected source remains metadata-only, quarantine/comparison-ineligible and
> unavailable for publication or release. This decision is not legal advice,
> rights clearance, independent assurance, G3 passage or release
> authorization. Any unresolved provider action remains a recorded exposure
> and reopens the decision.

No retention, deletion, takedown, rights clearance or publication action is
authorized by this preparation packet alone.
