# G2 96-candidate metadata expansion — owner decision packet — 2026-08-15

Status: awaiting sole-owner decision. No further network or source access is
authorized.

## Decision context

The authorized 33-entry HTML-resolution phase has stopped fail-closed. Its
tracked evidence is bound by URL-resolution manifest SHA-256
`3aefc7a6803c1bf547046ca4c0dae74307a7d21f974e385fee34193bb0df18f9`.
The corrected frame contains 26 unique PDF locators, below the frozen required
scope of 30, and 18 of 44 candidates remain unresolved. No PDF or file endpoint
was requested.

## Exact prepared design

- Plan ID: `G2HOLDOUT-METADATA-EXPANSION-20260815-01`.
- Machine plan SHA-256:
  `95aee30f7c285b5d32950e87dcb2de56880a24e6d96d5241b1563d24068fdcfa`.
- Plan schema SHA-256:
  `0c21b82781d7483882a909bdf0ee124dd349acce9e44363e908ebca8448c70a2`.
- Exact 208-row query manifest SHA-256:
  `d7419c0bc281ac9e940819d01005a922e2e6612e40ab1b573ba941eee3b8dddc`.
- Search execution-bundle schema SHA-256:
  `fa179ab2b8409fc6a28aa8043889a35bd7c0cff13d1804628a93801493821edd`.
- Detached expansion-design manifest SHA-256:
  `0cdaa6bc1ae5f10cf0a710d9abea53688a59a77af0b3457bd0df66631a5f3e37`.
- Signed freeze commit: `8a0e1c65d0e9dac9292c2ebd61efa3f496c99be9`.

The machine plan freezes four 13-record search streams, four ordered query
templates, jurisdiction/language/year ordering, exact 44+52=96 frame counts,
duplicate and ranking rules, three separated agent roles, access budgets,
recording limits, exposure controls, stopping rules and the next owner
checkpoint. Execution flags remain false.

## Option A — authorize only the search-index stage — recommended

Preserve the 44-candidate baseline and authorize a fresh metadata registrar to
execute only the 208-query public search-index stage in the exact frozen order.
The registrar may record the query, language, date, result rank, title, URL,
domain and access issue. It must not open or request any result URL, persist a
verbatim search snippet, visit an official landing page, issue `HEAD`, request
a PDF/file endpoint, download, render or transcribe source content, inspect
target facts or contact anyone. A separate network-disabled exposure auditor
then validates the candidate hypotheses and cumulative ledger.

Trade-offs: this creates more metadata exposure and work, but materially
increases the finite frame before structural preflight and follows the
predeclared contingency. It does not establish structural eligibility, exact
edition identity, source rights or G2 readiness.

The search-index receipt, candidate-hypothesis universe, exposure ledger and
proposed exact official-HTML allowlist must return for a separate owner decision
before any result or landing URL is visited. The planned official-HTML stage and
its 104-GET budget remain unauthorized.

Required controls already bound in the machine plan:

- freeze the languages, query templates, official-host rules, jurisdiction and
  stratum targets, ranking algorithm, duplicate rules, request budgets and stop
  conditions before the first new request;
- retain all 44 baseline records and add exactly 52 new, non-overlapping
  candidate records; do not silently replace, shrink or adaptively rerank the
  baseline;
- require official HTML metadata evidence, a stable candidate/edition/series
  identity and controlled eligibility fields for every new record;
- append every search-index action to digest-bound access and exposure
  receipts, including errors and uncertainty, but never verbatim snippets;
- keep all PDF/file URLs as unrequested hypotheses and all rights/privacy/
  security states preliminary;
- stop if a query budget, role boundary or no-result-URL-access rule is
  breached;
- return the search receipt and proposed official-HTML allowlist before any
  landing-page request; later stages retain the exact-96 stop condition.

Contingency: if the search-index stage cannot produce a sufficient bounded
hypothesis pool, preserve the stop and return for a decision between revising
the metadata-only search design, changing the content-defined strata or
terminating the blind-holdout lineage. Do not visit result URLs or inspect
source content to rescue eligibility.

## Option B — change to metadata-verifiable strata

Replace the content-dependent raster/dashboard and complex-layout strata with
strata that can be proven from HTML metadata alone.

Trade-off: lower access risk and cost, but changes the scientific question and
would not test the intended structural robustness. This requires a new methods
design and should not be treated as a continuation of the frozen design.

## Option C — terminate or defer

Preserve the current failed-scope evidence and perform no further access. G2
remains blocked.

## Recommendation and rationale

Approve Option A after the signed freeze commit above is populated. It is the
predeclared contingency, binds the exact search design, keeps the current
failure immutable and inserts an owner checkpoint before any result URL is
visited. Options B and C remain the correct contingencies if the fixed search
stage cannot produce a sufficient hypothesis pool.

## Recommended owner wording

> I approve Option A in the G2 96-candidate metadata expansion owner decision
> packet dated 2026-08-15. I accept the completed 33-entry HTML-resolution
> phase as a valid fail-closed stop bound by URL-resolution manifest SHA-256
> `3aefc7a6803c1bf547046ca4c0dae74307a7d21f974e385fee34193bb0df18f9`.
> Its corrected 26 unique PDF locators are insufficient for the frozen
> 30-edition primary-plus-reserve scope. The current 44-candidate frame, raw
> records, corrections, receipts, exposure ledger and panel reports remain
> immutable evidence.
>
> I accept the metadata-expansion design bound by machine-plan SHA-256
> `95aee30f7c285b5d32950e87dcb2de56880a24e6d96d5241b1563d24068fdcfa`,
> schema SHA-256
> `0c21b82781d7483882a909bdf0ee124dd349acce9e44363e908ebca8448c70a2`,
> detached manifest SHA-256
> `0cdaa6bc1ae5f10cf0a710d9abea53688a59a77af0b3457bd0df66631a5f3e37`
> and signed freeze commit `8a0e1c65d0e9dac9292c2ebd61efa3f496c99be9`.
>
> I authorize only a fresh `metadata_expansion_registrar` agent to execute the
> plan's 208-query public search-index stage in its frozen order. It may record
> query, language, date, result rank, title, URL, domain and access issue. It
> must not open or request a result URL, persist a verbatim search snippet,
> visit an official landing page, issue `HEAD`, request a PDF/file endpoint,
> download, open, render or transcribe source content, inspect target facts or
> contact anyone. A separate network-disabled exposure-auditor agent must verify
> the hypothesis universe, cumulative ledger and non-overlap.
>
> The search receipt, candidate-hypothesis universe, exposure ledger and exact
> proposed official-HTML allowlist must return to me for a separate decision
> before any result or landing URL is visited. The planned 104 official-HTML
> GETs, source-file acquisition, structural inspection and every later stage
> remain unauthorized. Any budget or role-boundary violation stops the lineage.
>
> This decision does not authorize source-file acquisition, structural
> inspection, extraction, rights acceptance, outbound contact, publication,
> release or G2 passage. No publication is authorized.
