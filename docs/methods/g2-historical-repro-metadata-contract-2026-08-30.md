# G2 historical reproducibility — metadata-stage execution contract

Campaign: G2HISTORICAL-REPRO-METADATA-20260830-01.
Policy: D-G2-HISTORICAL-REPRO-POLICY-20260830.
Status: prospective metadata-stage preparation; external execution unauthorized.

This is a separate lineage. The previous historical-unseen proposal, evaluator,
failed campaigns, observations and receipts remain immutable. The only
prospective change is the owner-approved evidential claim: bounded,
artifact-isolated reproducibility without project-unseen/generalisation claims.

## Exact metadata stage

The JSON bundle binds the exact GOV.UK official-index request already proposed
in `G2HISTORICAL-PROPOSAL-20260830-01`. Only the endpoint and fixed historical
window are inherited, not that proposal's complete-history or unseen policy.
One GET; no retry, redirect, pagination, search-provider query or adaptive
window; maximum 2 MiB response, 100 results, 120-second socket timeout.
No result URL, landing page or source file may be opened.

The strict input contract is a JSON object with `results`, integer `total`
and optional integer `start=0`, without other root fields. Every result has
exactly `link`, `public_timestamp`, `format`, `title`. Links must be GOV.UK
`/government/statistics/` slugs; formats are official/national statistics;
timestamps must be explicit and zoned. Unknown structure stops rather than
being silently accepted. This contract is synthetic-tested, not confirmed
against a live historical response. Any required API-schema revision would
be a prospective redesign, not repair of a failed response.

Register every returned locator before eligibility assessment. Unexpected
locator text is retained only as a digest and causes a stop; absent/unparseable
locators record incomplete exposure. Titles and raw responses are not persisted.
No content or value extraction occurs. Current-response enumeration must be
complete; historical gaps are explicitly retained as limitations instead of
being misrepresented as resolved.

Rank hypotheses by publisher timestamp then canonical locator, with timestamp
at least `2024-01-01T00:00:00Z` and before `2026-08-29T05:17:40Z`. Exclude every
enumerated prior locator conservatively, including known failed editions.
Preserve all observed metadata, including excluded/out-of-window locators.
Two to four surviving landing-page hypotheses permit metadata-stage completion;
fewer than two ends this lineage. No automatic replacement or retry.

## Role and access controls

One fresh metadata registrar receives the bundle, bound code/policy/audit and
separately signed owner authorization. It runs only the exact command below
after all bindings and current inventory verify. It does not inspect or repair
failed sealed outputs. A separate network-disabled agent reviews resulting
receipt, exposure completeness and claim limitations before owner handoff.
Neither role can accept a gate or authorize later access.

Verification-only command:

```sh
python -m gfjd.g2_historical_repro data/methods/g2-repro/metadata-bundle-2026-08-30.json
```

Execution adds `--authority-path` and `--authority-commit` only after the owner
approves this exact bundle. The authority file must be byte-identical to the
file in that verified signed commit and contain `metadata_request_authorized:
true` plus the exact `bundle_sha256`. Preparation cannot supply this authority.
Verification explicitly selects SSH, `ssh-keygen` and the absolute repository
`config/ssh_allowed_signers` path. That existing owner-signer policy is bound in
the bundle; ambient Git signer settings cannot expand its trusted signer set.
An exclusive attempt marker and execution directory prevent a second attempt;
transport pins a validated public address and verifies the peer before TLS/body
processing. Redirects and non-JSON/non-200 responses stop.

Receipts belong under `data/methods/g2/G2HISTORICAL-REPRO-METADATA-20260830-01/`.
The attempt marker is under `.gfjd/g2-attempts/`, outside the pre-request audit
subtree. New receipts enter the next exposure inventory; historical snapshots
are not rewritten. Attempt and receipt creation are write-once. Failures never
authorize source access; partial/incomplete exposure is explicitly retained.

## Later stages and decision boundary

Source-resolution, exact-edition identity, failed-cohort exclusion by content
and edition aliases, aggregate/privacy/rights checks, pilot-scope compatibility,
source-byte budgets and fresh extractor bundles remain unapproved. A UK-only
metadata response cannot replace approved multi-jurisdiction/route scope.
Actual extraction retains 100% critical / at least 99% populated concordance,
two fresh isolated agents, network-disabled exact comparison, quarantine,
terminal stopping and owner adjudication. None of those stages runs here.

Recommended next decision, only after final bundle validation:

> I authorize the one exact metadata request in the bound
> G2HISTORICAL-REPRO-METADATA-20260830-01 bundle. No retries, returned-URL access,
> source access, extraction, publication, release or G2 acceptance is authorized.

Alternative: retain current future-edition monitoring without this historical
request. The metadata-only approach tests feasibility at bounded cost but may
stop on schema, scope or count limits. It avoids claiming an all-stage execution
packet when exact editions do not yet exist. Role-separated panel advice
recommended this staged boundary; it is not independent specialist assurance.
