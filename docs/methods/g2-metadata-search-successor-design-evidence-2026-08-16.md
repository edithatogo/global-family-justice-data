# G2 metadata-search successor design evidence

## Status

`G2HOLDOUT-METADATA-EXPANSION-20260816-02` is a separately identified,
source-disabled redesign. It is prepared but not authorized. It is not a repair,
refreeze, continuation, execution receipt, successful search, source-access
record, or G2 acceptance artifact.

The failed 2026-08-15 design and the 2026-08-16 stop evidence remain immutable.
No network, search provider, result URL, landing page, file, source content, or
external contact was accessed while preparing this successor.

## Why a separate lineage is required

The failed call submitted `G2Q-001` through `G2Q-004` together and returned an
unattributable aggregate response. Thirteen result blocks were observed, but
the exact passive URL set cannot be reconstructed. Consequently:

- the four prior query IDs and their exact texts are contaminated and unusable;
- the repository does not claim that the unknown prior URLs were captured;
- non-overlap can be checked only against reconstructable known URLs;
- a complete-annex continuation is unavailable; and
- no future decision may authorize those four prior query texts as though they
  were unseen or fully accounted for.

The successor therefore retains the 204 definitions that were never submitted
and prospectively replaces the four contaminated definitions with four
textually distinct, frozen definitions. Successor IDs use the separate
`G2S2Q-` namespace.

## Corrected controls

The design freezes:

- 208 unique logical successor queries;
- exactly 208 provider calls, one logical query per call;
- zero retries;
- four prior submissions plus 208 prospective submissions, or 212 cumulative
  lineage submissions after a complete future run;
- an ISO `searched_on` date plus timezone-aware call start and finish timestamps
  captured at execution rather than a preauthorization date constant;
- passive `html`, `file`, and `other` URL classes recomputed from each URL;
- a recomputed lower-case result domain;
- `requested: false` for every passive result, exposure, and candidate record;
- passive direct-file and other URLs in exposure/candidate projections but never
  in the proposed HTML allowlist;
- only canonical, official-host, HTTPS HTML URLs in the proposed allowlist;
- no result URL, landing page, file, HEAD, redirect, snippet, source excerpt, or
  target-fact access or persistence; and
- explicit acknowledgement that prior aggregate reconstruction is incomplete.

The semantic verifier recalculates query and result digests, call isolation,
dates, URL kinds, domains, official-host status, projections, known predecessor
overlap, lineage counts, and all zero-access boundaries.

## Exact artifacts

- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-plan.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-plan.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-query-manifest.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-query-manifest.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-execution-bundle.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-authority-receipt.schema.json`
- `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-owner-decision.schema.json`
- `src/gfjd/g2_metadata_search_successor.py`
- `scripts/build_g2_metadata_search_successor_manifest.py`
- `scripts/build_g2_metadata_search_successor_design_manifest.py`
- `tests/test_g2_metadata_search_successor.py`
- `tests/test_g2_metadata_search_successor_design.py`
- `docs/governance/g2-metadata-search-successor-owner-decision-packet-2026-08-16.md`

`SUCCESSOR_DESIGN_MANIFEST.sha256` is the detached exact-artifact binding. A
future decision must additionally cite the signed freeze commit containing that
manifest. The execution verifier requires a digest-bound structured owner
decision and authority receipt, reruns `git verify-commit`, verifies both Git
objects are commits, and recomputes the manifest and decision blobs from their
respective commit trees. It also requires the prospective chronology `freeze
verification <= decision <= decision verification <= receipt generation <
authorization start < authorization expiry`; provider calls cannot precede the
authorization start. Until then, every execution and access flag remains false.

The ignored historical `execution-stop.json` was promoted byte-for-byte at its
panel-referenced tracked path. `lineage-index.json` binds its ignored historical
location and the passive annex's preserved ignored-build pointer to the exact
tracked equivalents without altering any historical receipt bytes.

## Verification evidence

The focused test suite covers schema validity, deterministic query generation,
immutability of the failed manifest, four textually distinct replacements,
captured ISO dates and monotonic timestamps, one-query-per-call isolation, passive PDF acceptance,
HTML-only allowlisting, and adversarial mutations of authority, retry, date,
classification, domain, exposure-completeness, and lineage counters.

This evidence establishes only that the successor is internally enforceable and
source-disabled. It does not establish provider behavior, candidate adequacy,
source eligibility, reproducibility, methods acceptance, rights clearance, G2
passage, publication, or release readiness.
