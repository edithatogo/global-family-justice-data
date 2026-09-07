# Public entry inspection: bounded selector stop

## Evidence and limitations

Lineage `G2-PUBLIC-CONTEXT-20260907-01` was frozen at signed commit
`ae5f7ce695f1336f94b905ee66fb09aa0ace592c`.
Plan SHA-256: `f254dcdcd2b921ee4a50dc7708393867e5e640565e83dd2afbd4c5572b952062`.
Receipt `g2-public-context-receipt-2026-09-07.json` SHA-256:
`3b145e33dd3e9b664f5dd1ffa7f449f4be68b0dfa672c71dae543aed1fbf05c4`.

The one-shot run observed the official collection (112524 bytes; 123 parsed
links) and selected January–March 2026 release page (99172 bytes; 106 parsed
links). It then stopped with `missing or ambiguous dashboard detail`. The
combined reason does not distinguish absence from multiplicity, and it does
not establish that the public page has no dashboard link. The selector's
strict label/path contract was not satisfied. No candidate-link text or raw
HTML was retained, so no retrospective reconstruction of that cause is claimed.

The receipt binds attempted URL and body hashes, not archived page bytes. It
records no Power BI request, retry, script execution, cookie or credential use,
dashboard query, extraction, rights clearance, publication or G2 acceptance.
The receipt and empty private execution lock remain immutable failed lineage
evidence. All preceding failures and their locks remain unchanged.

## Role-separated review

Offline `public_context_review` confirmed the receipt's scope and limits. It
recommended a consolidated browser-discovery decision, rather than another
speculative selector revision. This is advisory agent review, not independent
assurance or accountable acceptance. The implementation adopts that proposal
for the next owner choice; no new external action was taken.

## Grouped next choice

**Option A — recommended: one bounded anonymous browser inspection.** Allow
ordinary public navigation and JavaScript, including automatic model/query
requests needed to load one public dashboard, solely to observe its supported
request metadata. This can establish access context that static HTML does not
expose, but materially expands the previous no-script/no-query access scope.

Prepare a fresh isolated browser context with no inherited account session.
Freeze a 15-minute session limit, at most six top-level public navigation
steps and one dashboard load. Confirm enforceable network/output controls
before starting; otherwise stop at the implementation boundary. Do not sign
in, accept terms/consent, bypass a restriction, manually replay an API call,
change dashboard filters, export/download or publish. Stop on authentication,
access denial, unexpected destinations or exhausted limits. Retain only a
redacted request contract: no HAR, response body, cookie/authorization value,
raw resource identifier or source screenshot. Automatic dashboard traffic is
part of this proposed permission, not permission for extracted-value acceptance.

**Option B — lower access:** the owner supplies a current public entry URL or
a genuinely new location containing the exact original bytes. This may avoid
discovery, but a URL alone does not establish browser/network permission or
recover missing historical artifacts. Exact-original recovery still requires
hash verification.

**Contingency:** pause the dashboard route if anonymous supported access cannot
be established. A static-only cohort is a separate methods/scope choice, not
an automatic fallback pass. No change to concordance thresholds is proposed.

Suggested concise authorization for Option A:

> I authorize the bounded anonymous browser inspection described here, including
> normal public-page JavaScript and automatic dashboard requests needed to
> observe access metadata. No login, credentials, terms acceptance, manual API
> replay, filter changes, exports, publication or G2 acceptance is authorized.

Record the decision once, then implement within those bounds without another
approval for routine digest changes, tests, documentation, CI or merge.
