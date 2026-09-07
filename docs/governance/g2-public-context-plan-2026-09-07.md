# Bounded public-page request-context inspection

The owner approved the preceding recommendation with “Proceed with your
recommendations.” Scope is the prepared public-page inspection only: no login,
credentials, source files, scripts, model requests, query POSTs or G2 acceptance.

## Frozen prospective route

Bind the plan in `data/methods/g2/G2-PUBLIC-CONTEXT-20260907-01/plan.json`
and `scripts/discover_g2_public_context.py` to a signed commit before access.
Read the recorded GOV.UK collection. From explicit links select the greatest
calendar year/quarter using only the four literal quarter month ranges; this
selects a public entry context, not an accepted source edition. Require one
distinct newest URL. On its release page select a unique public Power BI view
anchor/iframe; if absent, allow one uniquely dashboard-labelled directly linked
GOV.UK detail page beneath that release path, then one unique public view.
No guessing, alternative selection after failure, or historical resource reuse.

At most four GETs: collection, up to two release HTML pages, one view HTML.
Accepted body limit is 2000000 bytes per response, with one extra oversize probe.
The 30-second socket timeout is not a DNS or total-runtime deadline. Public-peer
TLS and identity encoding are required. Reject redirects, wrong MIME, ambiguous
links, unexpected selected hosts, URL credentials/ports, base elements, duplicate
URL attributes, and any scope failure. No cookies are sent or retained.

## Custody and outcomes

All bodies and raw public-resource parameters stay in process memory. Receipts
contain safe base locators, full-URL hashes, resource-parameter hashes, body
hashes/lengths and attempt times, never source snippets, raw query parameters,
headers or arbitrary exception text. Every attempted URL is registered by hash
before requesting. An exclusive private lock and checkpoint prevent repeats.
The lock is not a source archive. No evidence maturity or rights are promoted.

Even HTTP 200 and a public view link do not establish a models/query request
contract. If static HTML cannot establish that contract, report the missing
fields; do not fetch scripts or invent headers. A transport/selection failure
terminates the lineage. Preserve both earlier failed lineages unchanged.

## Role-separated advice and delivery

Offline `public_context_review` recommended deterministic quarter selection,
unique dashboard links, strict URL/HTML checks, redacted receipts and no inference
of anonymous query access from a public view. These constraints are implemented.
Alternatives are exact-original recovery from a new known backup or pause; no
new backup is currently identified. The review is advisory, not independent
assurance. Complete offline tests and review before freeze; afterwards register
the outcome in Conductor, run full validation, and deliver through passing CI
and a history-preserving PR merge. Gate acceptance remains separate.
