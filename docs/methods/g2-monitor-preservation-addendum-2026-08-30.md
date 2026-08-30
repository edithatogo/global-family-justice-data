# G2 monitor preservation correction — 2026-08-30

This addendum supersedes only the durability statement in
`g2-three-root-lastmod-consolidation-2026-08-30.md`. Actions artifacts are
immutable while retained, not permanent archives. The API reported expiry on
2026-11-28 for artifact IDs `9725087358` and `9725349776`.

## Completed repository work

- Preserved the exact downloaded 260,984-byte, 1,212-row exposure ledger at
  `data/methods/g2/G2FUTURE-EDITION-THREE-ROOT-20260829-01/execution/run-33288137424-1/exposure-ledger.jsonl`.
- Verified SHA-256 `d485519d8332a5e640f08f95b72cd9997d0464eb395c96fe1e5c4b882e556125`
  against both already committed receipts: `33288137424-1` and `33288962808-1`.
- Compared the two downloaded artifacts byte-for-byte. One shared ledger is
  sufficient; the separate receipts preserve the different campaign outcomes.
- Added offline CI checks for exact digest, full row count, endpoint/ordinal
  coverage, metadata-only fields, the original novelty calculation and unchanged
  access boundaries. The tests first failed because the complete ledger was
  absent, then passed after exact-byte preservation.

Git and `MANIFEST.sha256` now retain and bind the complete ledger independently
of Actions artifact retention. No source response, page, document or extract
was requested. No historical receipt or failed result was repaired or promoted.

This is a supporting preservation correction, not a new G2 campaign or owner
decision. Existing work-item acceptance, G2-C04/C07, maturity and all release
restrictions remain unchanged. Other monitoring artifacts still need their own
retention assessment; this addendum makes no fleet-wide preservation claim.
