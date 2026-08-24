# G2 rights, privacy, security and disclosure agent-panel advice — 2026-08-24

This is a durable synthesis of role-separated advisory review. It is not legal
advice, specialist assurance, independent assurance or an owner decision.

## Role-separated findings

The rights/privacy review found that the England and Wales ODS has existing
edition-bound OGL v3 screening, subject to attribution, exclusions and
third-party-content checks at the point of reuse. It recommended no current
redistribution of the dashboard, FCFCOA PDF or DataJud responses. The DataJud
request retained no case-level hits, but its terms and the absence of a general
redistribution decision support private aggregate-only handling.

The security/disclosure review found the current selected values aggregate and
low disclosure risk, while the complete workbook, dashboard response/model
artifacts and annual report contain broader unreviewed content. It recommended
restricted local quarantine, least-privilege access, no source bytes in Git,
and immediate isolation if personal, sensitive, contact, narrative or
small-cell material appears.

## Options

1. **Controlled private quarantine — recommended.** Retain hashes, locators,
   aggregate target values, query/request digests, citations and dispositions
   in Git; keep source bytes and content-bearing derivatives in restricted
   local storage. Consider ODS reuse only after an exact-edition check.
2. **Strict metadata-only deletion.** Retain only public metadata and delete
   controlled bytes after an approved, verified deletion process. This reduces
   exposure but removes useful reproducibility evidence.
3. **Permission-first reuse.** Seek source-owner confirmation before any reuse.
   This may increase certainty but adds external dependencies and is not needed
   for current private quarantine.
4. **Exclude restricted routes.** Use only a separately cleared ODS derivative.
   This narrows the pilot and still requires a new scope and rights decision.

## Recommendation, trade-offs and contingencies

Adopt controlled private quarantine and a metadata-only public/Git boundary.
This preserves evidence while preventing public redistribution; the trade-off
is continued controlled-storage and retention overhead. If the ODS
exact-edition notice or third-party exclusions are ambiguous at reuse time,
retain metadata-only handling. If personal, sensitive, identifying, contact,
narrative or small-cell material appears, stop the affected processing and
quarantine it immediately. If source-owner permission later resolves a route,
record a separate digest-bound rights decision before redistribution.

No panel member claims legal authority, privacy/security certification,
independence from the repository owner, or authority to pass `G2-C06`.
