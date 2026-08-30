# G2 three-root monitor `lastmod` consolidation — 2026-08-30

Hosted run `33288137424-1`, from merged signed commit `faf520e75c059490690e7b3368b0a2e9f69dc9f2`, completed all three frozen sitemap requests and sealed 1,212 observations. It stopped fail-closed because one previously exposed California locator changed its `lastmod` value from `2026-08-28T23:40Z` to `2026-08-29T23:25Z`.

The locator path identifies a courts-of-appeal appointments news item. That classification uses only the already exposed URL string; the returned locator was not opened. It is not an exact family-justice publication candidate and establishes no edition identity.

The complete hosted exposure ledger remains preserved in the immutable GitHub Actions artifact. Its SHA-256 is `d485519d8332a5e640f08f95b72cd9997d0464eb395c96fe1e5c4b882e556125`. The repository binds the receipt and the one-record novel-exposure ledger, SHA-256 `af0b7648ecaed23164706ac39a7a196209bf773a45c3e936230285ea6adee08a`.

`G2FUTURE-EDITION-THREE-ROOT-20260830-02` is a distinct successor, not a repair or retry. It adds the changed `(URL, lastmod)` tuple to cumulative exposure and otherwise preserves the exact endpoints, cutoff, zero-retry rule, limits, stopping rules and no-returned-locator-access boundary.

This disposition does not establish candidate eligibility, reproducibility, maturity, rights clearance, G2 acceptance, publication or release. A hosted exact-head successor run is required before monitor operation can be accepted.
