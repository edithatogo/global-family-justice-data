# Monitor metadata preservation — 2026-08-31

Eight previously unpreserved completed Actions runs now have exact metadata
retention, selected from the captured 20-run, six-workflow inventory. Twelve
other runs already had receipt bindings. This is a bounded inventory snapshot,
not a claim that future runs or all historical exposures are preserved.

The authoritative file and archive bindings are in
`data/methods/g2/monitor-preservation-2026-08-31.json`.

## Results and limitations

- Seven receipts pass modern run/source identity and route-schema verification.
- Run 33240200746 has legacy artifact-bound-only provenance. Its original
  receipt lacks run/source fields; the modern validator still rejects it.
  Canonical artifact metadata and matching archive bytes supply separate
  retrospective bindings, not repaired receipt fields or equal assurance.
- Run 33304063733 remains terminal failed evidence after a timeout. Its 711-row
  partial exposure ledger is retained exactly; no novelty ledger is invented.
- Complete sitemap novelty was recomputed against the corresponding frozen
  source-contract baselines. Shared ledger objects were reused only after
  exact-byte equality. Empty ledgers remain explicit objects.
- Every downloaded archive matched its canonical provider size and SHA-256.
  Source commits were verified as ancestors of the captured canonical main.
  Offline regression tests check retained bytes, bindings and dispositions.

No execution log was opened or retained. No raw response, statistical source
file or publisher endpoint was accessed. No monitor was rerun or retried.
Response hashes without response bytes do not establish response replayability.
Artifact expiry is recorded separately from durable Git metadata retention.

## Advisory disposition

The bounded-artifact reader supplied a pure allowlist reader and strict metadata
validator. The separate preservation-inventory reviewer recommended retaining
the legacy record with its weaker provenance explicitly labelled rather than
modifying it. Both mechanisms are advisory preparation, not independent
assurance or accountable gate acceptance.

All entries deny gate eligibility. G2 remains blocked; this changes neither
source rights nor maturity, publication, extraction or release authority.
The next repository-owned slice is the distinct offline API contract; no new
metadata request is implied by that preparation.
