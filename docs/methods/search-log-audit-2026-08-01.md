# Search-log receipt audit

Audit date: 2026-08-01  
Reviewer: analyst-agent

The 164 entries currently marked `draft` in `data/census/search_log.csv` were cross-checked against `build/public-searches/search-receipts.json`. The receipt bundle contains one record for each draft entry and preserves jurisdiction, language, query, URL, access status, byte count, checksum where available, and error details where access failed.

The audit confirms record-to-receipt completeness and preserves fail-closed outcomes. `URLError`, zero-byte responses, and other blocked retrievals remain `source_inaccessible` or `search_incomplete`; they are not converted into no-source findings and do not promote coverage. Search-log rows remain `draft` pending the normal review-ledger workflow because receipt completeness does not by itself establish institutional coverage or rights.

No external requests were sent during this audit.
