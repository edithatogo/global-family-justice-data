# G2 agent-blinded known-edition terminal stop — 2026-08-25

The owner-authorized four-route run executed under the prospectively frozen
design `G2BLIND-KNOWN-EDITION-20260825-01`. Two fresh role-separated agents
produced four-row, schema-valid outputs from source-only bundles. Both outputs
and their receipts were sealed before comparison.

The separate comparator verified the packet, source-output receipts, hashes,
seals and role boundaries without reading source artifacts. Its single exact
comparison invocation wrote a differences artifact containing five critical
differences across the API and dashboard routes. The affected fields were
`ambiguity_codes`, `extraction_uncertainty`, `source_locator` and
`indicator_code`.

The comparator then stopped while validating its concordance receipt because
the frozen packet ID `G2BLIND-KNOWN-EDITION-20260825-01` does not match the
repository receipt schema's required `G2PKT-...` pattern. Consequently no
schema-valid `concordance.json`, threshold result, critical-concordance metric
or overall-concordance metric was issued.

The stop is terminal under the frozen rules. No output was repaired, renamed,
normalized, waived, reused or rerun. The sealed content-bearing outputs and
differences remain private outside Git. Their hashes and the redacted field-level
disposition are bound in
`data/methods/g2/G2BLIND-KNOWN-EDITION-20260825-01/terminal-stop.json`.

G2-C04 and G2-C07 remain `in_review`. This failed run does not promote earlier
lineages, authorize publication or release, clear rights, promote gold data or
pass G2.
