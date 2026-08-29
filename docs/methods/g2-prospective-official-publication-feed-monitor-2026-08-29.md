# G2 prospective official publication-feed monitor — 2026-08-29

Evidence ID: `E-G2-FUTURE-OFFICIAL-FEED-PREPARATION-20260829`

This route replaces ambiguous sitemap `lastmod` evidence with one exact,
publisher-controlled structured index. It uses GOV.UK's public Search API as an
official publication index with no free-text query, filtered to the family
justice taxonomy, official/national-statistics formats and the frozen
post-exposure period. GOV.UK documents that this API supports strict parameters, publication
timestamp ranges, deterministic ordering and a maximum count of 1,500.

The frozen request returns at most 100 metadata records on one page. Complete
enumeration is mandatory: a declared total above 100, a result-count mismatch,
schema drift, redirect, unexpected content type, host or path, missing or
invalid publication time, duplicate locator, byte-budget breach or any network
failure terminates the run. Every result locator is exposure. The monitor never
opens a result URL and cannot acquire, extract, clear rights, accept G2,
publish or release anything.

At least two strictly post-cutoff records with an official- or
national-statistics format are needed before candidate access can even be
considered. Zero candidates is a valid monitoring result; novel exposure or a
candidate threshold is action-required and must be preserved before another
run. A qualifying result remains metadata only and must pass a later exact
source-access interlock under the already approved staged route.

Primary interface documentation:
`https://docs.publishing.service.gov.uk/repos/search-api/using-the-search-api.html`.
