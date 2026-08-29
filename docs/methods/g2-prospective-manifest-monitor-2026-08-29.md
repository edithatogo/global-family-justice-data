# G2 prospective official-manifest monitor — 2026-08-29

The canonical sitemap route is now converted from repeated one-off lineages into
a single low-churn prospective monitor. It requests only the three exact frozen
official sitemap endpoints, strictly in order, with zero retries and no redirect
following. It never requests a returned locator.

Each run emits a complete JSONL exposure ledger and a digest-bound receipt. The
monitor distinguishes a successful observation with fewer than two post-cutoff
timestamps from the threshold condition needed to prepare a later candidate
interlock. Neither state opens candidate pages or implies that `lastmod` proves
first publication; explicit publication-date evidence remains necessary before
selection.

The GitHub workflow runs daily and may also be dispatched manually. Hosted
artifacts are retained for 90 days. Routine no-candidate runs require no owner
decision. If at least two post-cutoff hypotheses appear, the workflow stops at
metadata registration and the repository must prepare one grouped source-access
decision before opening any returned locator.

This is monitoring implementation evidence only. It does not establish
reproducibility, accept G2-C04 or G2-C07, promote M06, clear rights, publish a
dataset or authorize a release.
