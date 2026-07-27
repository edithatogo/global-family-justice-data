# Source access fallback record

On 2026-07-27, bounded HTTP retrieval of the two CEPEJ landing pages in the
source register returned `403 Forbidden`. The original URLs remain canonical;
they were not replaced or treated as evidence.

The Council of Europe publication endpoint was reachable and the 2024
evaluation report was downloaded to the ignored build workspace under
`build/source-fetch/`. Its SHA-256 and retrieval details are recorded in the
generated `cepej-fallback-manifest.json` (not committed because it is an
acquisition receipt). The machine-readable mapping is tracked in
`data/seed/source_access_fallbacks.csv`.

The report is not a substitute for the CEPEJ-STAT raw database. No values,
coverage claims, or source rights have been promoted from this fallback. A
reviewer must confirm licensing and whether any report table is suitable for a
specific indicator before it can enter an evidence bundle.
