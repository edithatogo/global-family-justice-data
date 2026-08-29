# G2 canonical sitemap terminal evidence — 2026-08-29

The three frozen canonical New Zealand child-sitemap endpoints were requested
strictly in order with zero retries and no redirect following. Each returned
HTTP 200, parsed successfully with the frozen streaming parser and passed the
exact-host and byte-budget controls.

The run persisted all 2,302 returned observations (2,289 unique locators and 13
duplicate observations) in the digest-bound exposure ledger. The responses
totalled 797,706 bytes. Every observation had a parseable timestamp, but none
was later than the frozen `2026-08-29T05:17:40Z` exposure cutoff.

The lineage therefore stops terminally on its frozen
`fewer_than_two_eligible_editions` condition, with zero eligible editions. This
is useful negative evidence: canonical enumeration works, but this publication
manifest cannot supply the prospectively new editions required for G2.

No returned locator, page or candidate document was opened. No extraction,
rights clearance, G2 acceptance, publication or release occurred.
