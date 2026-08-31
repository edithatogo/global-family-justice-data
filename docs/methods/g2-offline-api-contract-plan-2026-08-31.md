# Distinct offline API contract plan

Repository-only implementation under standing autonomous direction. Baseline:
signed `a10d905`, PR #135, all 17 hosted checks and `autonomy-full` passed;
696 tests passed twice, 79.38% coverage. One local worktree remains.

## Scope, options and recommendation

Implement a new pure metadata parser, separate from every frozen campaign.
Use the pinned official API interface evidence already in the repository.
Accept only named semantic fields and documented incidental presenter keys;
bound all JSON structure and discard incidental values. Preserve update time
and first-publication time separately without claiming exact-edition identity,
candidate eligibility, complete historical exposure or G2 acceptance.

The alternative is documentation-only preparation, which leaves the known
interface incompatibility unresolved. Widening a failed frozen evaluator or
retrying its consumed request is not an option. Recommended implementation is
synthetic-first, without transport or live response access.

## Tasks

- [x] Establish clean signed baseline and commit this prospective plan.
- [x] Implement/test the isolated parser with bounded structural diagnostics,
  strict enumeration, locator checks, duplicate rejection and date separation.
- [x] Prepare a digest-bound repository-only contract bundle with explicit
  limits, metadata retention, roles, limitations and future authorization needs.
- [x] Obtain separate advisory review; fix substantive defects.
- [x] Update supporting Conductor evidence without changing acceptance mappings.
- [x] Validate, sign, PR, await exact-head checks, merge and clean local branch.
  PR #136 merged signed `3c9d9ec`; `autonomy-full`, 745 tests twice,
  79.57% coverage and all 17 hosted checks passed; local branch removed.

## Controls and contingencies

Two MiB maximum response, 100 results, complete single-page enumeration,
strict duplicate-key/nonfinite rejection, bounded depth/nodes/strings. Unknown
keys or invalid types terminate evaluation with fixed diagnostic codes; no raw
values, titles, incidental metadata or unknown key names enter the report.
Returned locators are never accessed. Empty results remain metadata-only.
Null/missing first-publication evidence cannot fall back to update time.

No network transport or automatic retry is added. A future exact request must
be separately bound to current cumulative exposure, execution controls and an
owner decision. This parser is not deployed-schema evidence or execution
readiness. No source access, extraction, rights clearance, publication, release,
maturity promotion or G2 passage is authorized. Estimate: one small pure module,
synthetic tests, one advisory review and normal local/hosted CI; zero requests.
