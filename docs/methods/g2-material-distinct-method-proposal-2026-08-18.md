# G2 materially distinct prospective evidence method proposal — 2026-08-18

## Status

Repository-only advisory preparation artifact (no network or source access).

## Objective

Create a materially distinct blind-holdout discovery method for future G2 that is not search-index based, does not reuse exposed outcomes, and is ready for a future exact owner authorization.

## Scope (exact)

- Track: `G2`, workstream for post-blind-holdout successor.
- Candidate pool: deterministic, versioned, repository-only candidate manifest derived from existing jurisdictional source-register assets in-repo (no network calls).
- Exclusions:
  - no reuse of any of the `615` observed URLs,
  - no reuse of canonical URLs in the full cumulative exposure ledger,
  - no re-selection of previously excluded/contaminated candidate identities.
- Candidate plan: fixed oversampled frame of `96` rows for planning (no adaptive replacement).
- No active extraction, no source content access, no URL/file/landing requests, no snippets.

## Exposure model

1. Cumulative exposure ledger (hash-linked, append-only): denied URLs, candidate exclusions, exposure reasons, and evidence bindings.
2. Full predecessor-chain verification before publication of any proposal.
3. Candidate status states: proposed / exposed / excluded / eligible / rejected.
4. All observed URLs from this stop lineage remain exposure until explicitly superseded by future non-overlapping, re-authorized methods.

## Option A (recommended): Official publication-manifest route

- Discovery source: deterministic crawl of official publication manifests/indexes only.
- Controls:
  - strict host/domain allowlist,
  - manifest schema + parser validation,
  - bounded parser time/bandwidth,
  - zero result/request permissions.
- Stop: malformed payload, schema drift, host drift, domain mismatch, or non-reproducible manifest.
- Resource estimate: medium planning + execution.
- Limitation: depends on official manifest completeness and taxonomy consistency.

## Option B (fallback): Official directory route

- Discovery source: bounded traversal of official site publication directories under fixed domains and section trees.
- Controls:
  - fixed domain/schema policy,
  - parser validation,
  - bounded traversal budget.
- Stop on parser/schema drift, unexpected hosts, or domain/path violations.
- Resource estimate: medium-high.

## Common controls (all options)

- No network source/content operations until a separate owner authorization packet is approved.
- Deterministic manifests, hashes, and role-bound access profiles.
- Signed owner decisions + signed authority receipts at each stage boundary.
- Strict no-filter/no-reuse policy from terminal failed lineages.
- No waiver, partial repair, subset extraction, or successor attempt without full re-authorization.

## Role-separated panel advice (required before authorization)

- Methods panel: recommend Option A first; use Option B only if A cannot materialize a fixed frame with full compliance.
- Operations/exposure panel: verify cumulative-chain exclusion and fail-closed checks.
- Governance panel: confirm the `all 615 observed URLs are exposure` constraint and no reuse logic.

## Proposed owner authorization wording (template)

I authorize a repository-only preparatory phase for the selected option to build the fixed candidate manifest, exposure model, stopping rules, controls, limitations, and resource estimate.

I do not authorize any network, query, URL, file, landing-page, contact, or source-content access, no extraction, no rights acceptance, no publication, no release, and no G2 passage in this phase.

Execution remains terminally fail-closed: any missing/bad binding, manifest drift, authority mismatch, exposure-traversal defect, or chain verification failure stops all progression to execution and requires re-authorization.
