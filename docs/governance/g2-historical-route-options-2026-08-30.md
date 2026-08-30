# G2 historical-edition alternative: options and decision boundary

Status: advisory proposal, not owner acceptance or execution authority.
Proposal: `G2HISTORICAL-PROPOSAL-20260830-01`.

## Recommended option A: prospectively frozen historical official-index route

Prepare one new request to the established GOV.UK publisher-controlled family-
justice statistics index. The proposal changes its lower timestamp filter to
1 January 2024 and evaluates a fixed local window ending exclusively at
`2026-08-29T05:17:40Z`. It makes no free-text or external search-provider query.
The exact proposed URL and limits are in `design/proposal.json` under the
proposal directory in `data/methods/g2/`.

This removes the requirement to wait for a newly published edition only for a
future separately authorized lineage. All existing exposure, identity, exact-
concordance, quarantine and terminal-failure rules remain. A current campaign's
new registrar observations can be evaluated only within that frozen campaign;
they remain exposure for all later campaigns.

Why recommend it: it tests a relevant historical official index at low bounded
cost rather than waiting exclusively for publishers. It does not claim that
older material is available, unseen, structurally usable or sufficient for G2.
The earlier historical source-register frame was exhausted. This is a new
eligibility and request-scope design, not a novel discovery method by itself.

Trade-offs: the index may return too many records, only exposed records, ambiguous
timestamps or no usable editions. Its UK-only metadata scope does not establish
multi-jurisdiction or route coverage, and cannot silently amend accepted pilot
scope. A publisher timestamp is not automatically first-publication evidence.

## Alternatives and contingencies

- B: retain existing future-edition monitoring. Lower change risk but dependent
  on publication schedules; recommended as parallel redundancy, not a route for
  recycling already observed candidates into an unseen historical sample.
- C: relax exposure or reuse failed material. Not recommended: this changes the
  evidence claim and contradicts current immutable stop decisions.
- Broad national sitemaps are a less targeted alternative. Existing exposed
  control-root locators do not establish fresh descendants or complete traversal.
  Do not use them as an automatic fallback after the proposed request fails.

Any over-budget, incomplete, ambiguous or insufficient result stops that lineage.
No adaptive date window, pagination, source substitution, fuzzy matching,
repair, critical waiver or automatic retry is permitted.

## What is ready and what still blocks execution

Ready: exact proposed metadata request and fixed historical window; preserved
comparison rules; three role-separated advisory opinions; explicit stop rules
and a digest-bound reference inventory. No external request has been made.

Still required before an execution decision:

1. A complete current exposure input inventory and verified normalized snapshot.
   The August 29 JSON snapshot alone is insufficient: JSONL monitor observations,
   failed partial captures, aliases and later receipts must be accounted for.
2. A historical-window evaluator with complete-enumeration and exclusion tests.
   The future-only monitor is not to be silently repurposed.
3. Exact edition resolution, source budgets, schemas, role bundles, interlocks
   and an explicit statement of compatibility with G2-C04/C07 pilot scope.
4. A signed execution freeze binding all those artifacts, followed by one
   grouped owner authorization for the defined stages.

No owner decision is being requested against these missing bindings. Their
repository-owned preparation is already authorized. When complete, present one
execution packet covering historical eligibility, metadata registration and any
precisely controlled conditional later stages. If later stages cannot yet be
bounded, state that limitation rather than implying their authorization.

## Resource estimate and claim boundary

Proposed metadata stage: one request, zero retries, at most 2 MiB, 100 returned
records and a 120-second request timeout. Freeze the local parsing budget before
execution. Budget excess ends the run, not a smaller retrospective sample.
Repository preparation is estimated at 2–4 agent-hours, subject to exposure-
coverage gaps; this is a planning estimate, not approval for paid services.
Future acquisition/extraction budgets remain unapproved and must be bound in
the execution packet rather than inferred from this metadata budget.

A future passing campaign establishes bounded reproducibility only. It still
requires methods disposition, evidence-specific maturity assessment and grouped
owner G2 adjudication. It does not prove model-training unseenness, complete
global coverage, source rights, independent assurance, publication or release.
