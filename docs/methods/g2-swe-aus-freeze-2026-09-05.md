# Swedish/AUS prospective extraction freeze

User direction: freeze the exact cohort and extraction contract. Contract:
`data/methods/g2-swe-aus-freeze-20260905.json`, SHA-256
`808318acb41fe055b3ff2c7b8e9bc352fa64bae1f40a1b0485bbe3c3f07d5398`.

The scope is 10 Swedish worksheet rows (B:D, rows 9–18, headers row 8)
and four AUS table rows (PDF page 102, Table 3.3.1(a)). Source digests,
context locations, output fields, exact lexical rules, semantic exclusions,
100% critical/99% populated thresholds and terminal stopping rules are frozen.
Expected extracted values are deliberately absent from the role contract.

This is a known-source preparation contract supporting WI-G2-04 and WI-G2-07.
It is not an unseen cohort, a successful run or acceptance-bearing review.
Execution bundles and the comparator implementation still require bindings
before any prospective execution; previous failed outputs cannot be reused.
No canonical work-item acceptance mapping is changed by this preparation.

PR 159 merged on 2026-09-05. This freeze begins from origin/main; the divergent
local main branch is preserved rather than reset.
