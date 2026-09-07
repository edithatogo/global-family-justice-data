# Dashboard structural capture: HTTP 401 terminal stop

## Exact evidence

- Lineage: `G2-DASHBOARD-STRUCTURAL-20260907-01`.
- Signed freeze: `87eed766b35455517380f3c2fedd96bf1ba73a2b`.
- Plan SHA-256: `e1d1336c211a82cfa2fb6aaba37b0d64cbd9232f44c98d28f28fd3fe2aedcfe6`.
- Receipt: `g2-dashboard-structural-capture-2026-09-07.json`.
- Receipt SHA-256: `88aa80a1f9a7427907b455e9616ba1092162153fa11a678932776554a10553e7`.
- Started: `2026-09-07T02:59:20.967473+00:00`.
- Finished: `2026-09-07T02:59:22.749910+00:00`.

One exact bodyless GET received HTTP 401. The runner stopped before reading or
retaining a source body. There was no retry, redirect, credential use, query,
extraction or publication. This is a response-status observation, not proof
that the public dashboard is unavailable, that a login is required, or that
any specific missing header would resolve access. No response body/hash or
source custody is claimed. The empty restricted vault is an execution lock.

## Disposition and repository-only investigation

Preserve the frozen plan and receipt unchanged as terminal failed evidence.
Do not remove the lock or rerun this lineage. The earlier DataJud-dependent
failure also remains unchanged. No G2 criterion, work item or maturity is
promoted; WI-G2-04/07 still lack qualifying empirical evidence.

An offline filename/metadata-key search found no recorded resource-key/header
contract in the existing dashboard packet. Its source fields record candidate
identity, entry-page digest, model/query endpoint, section and visual identity,
but do not establish a complete executable request context. This bounded search
does not prove that such context exists nowhere. No source body, credential or
external page was inspected during this investigation.

## Next options and recommendation

Offline outcome reviewer `dashboard_scope_review` confirmed the receipt and
the missing source-derived access-context binding. It recommended preserving
the stop, preparing public-context discovery offline, and grouping any new
access authorization once. It made no network request and did not claim that
401 proves a particular authentication requirement. This is agent advice,
not independent assurance or an owner decision.

1. **Recommended: qualify the public entry-page access context first.** A
   separately bounded inspection of the official public dashboard entry page
   and its documented public embed configuration could establish a supported
   access contract. Do not guess headers, sign in, use account credentials or
   bypass access controls. Return the evidence-backed request contract before
   another models/query request. This adds one diagnostic stage but avoids
   another speculative source attempt. It requires authorization for the new
   page access; the current one-GET scope is exhausted.
2. **Recover exact originals from a genuinely new backup location.** This
   preserves historical identity without relying on current access, but no
   such location is presently identified. Verify exact hashes before use.
3. **Qualify available static sources only.** This may be cheaper and simpler,
   but reduces route diversity and needs an explicit scope decision; it cannot
   silently satisfy the existing API/dashboard coverage requirement.

If public context is unavailable or authenticated access is required, stop
and present that factual boundary rather than inventing a workaround. No
rights clearance, G2 acceptance, publication or release follows from any
preparation recorded here.

## Prepared repository-only discovery plan (not executed)

Start from the official collection locator already recorded in
`data/seed/source_register.csv`, source `GBR-EAW-MOJ-FAMILY-Q`:
`https://www.gov.uk/government/collections/family-court-statistics-quarterly`.
Before execution, freeze a bounded HTML-only route contract: this root plus at
most two directly linked GOV.UK family-court release pages and one directly
linked public Power BI view page. No search, script execution, redirects,
authentication, cookies, source files, models endpoints, query POSTs or
historical token reuse. Resolve follow-on locations solely from the current
page's explicit links and reject ambiguous selection or unexpected hosts.
Record every attempted URL as exposure, with no automatic retry or replacement.

Proposed budget: at most four HTML GETs, at most 2000000 accepted body bytes
each plus one oversize probe each, 30-second per-socket timeout, and no paid
services. Treat this as request-context qualification only. Persist only safe
locators/hashes and a redacted contract; keep prohibited content out of Git.
If those HTML pages do not establish an exact anonymous contract, stop and
return the missing field list rather than fetching scripts or guessing headers.

The owner's next decision can simply authorize this bounded public-context
inspection. It does not need a new long-form governance acceptance and does
not authorize using the resulting context for a source request yet.
