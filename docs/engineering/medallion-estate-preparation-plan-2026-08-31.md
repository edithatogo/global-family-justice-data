# WI-G4-MED-04 — public estate preparation

Status: in-progress repository-owned preparation. The publication-bearing work
item remains planned; its dependencies and acceptance evidence are unchanged.
This plan implements the next item in the approved autonomous continuation
queue, before the separate WI-G4-MED-05 federation track.

## Baseline and preceding delivery

PR #138 merged at signed commit `00172e86684b1ab7f61deb58899ec71026d4a2bf`
on 2026-08-31T12:55:09Z. All 17 exact-head hosted checks passed. After a transient
PortableSSD disconnection interrupted one local run, Git object integrity and
all 1,010 source manifest entries verified. A fresh full `autonomy-full` run at
the unchanged commit exited zero: 1,144 tests passed twice (50.19s and 40.76s),
reported coverage 82%, restore/bootstrap checks and deterministic distribution
and release checks passed. The interrupted run remains documented in PR #138;
it is not a successful validation. Cleanup left one worktree and local main.

The non-mutating bootstrap plan for this phase completed. It identified the
canonical checkout without applying configuration or creating repositories.
Its six Hugging Face creation descriptions incorrectly say private despite
the public configuration. The portfolio also lacks the configured source
archive. These are declaration/reporting gaps, not evidence of remote creation.

## Recommendation, options and rationale

Recommended: build a deterministic, offline six-role estate preparation bundle
from the exact checked-in bootstrap, archive-target, portfolio and product
declarations. Reconcile identity, type, public visibility, canonical ownership,
payload policy, minimum gate and declared role links. Produce manifest-bound
draft cards and a verification report that explicitly distinguishes desired
configuration from observed availability, rights and publication authority.

Options:

- Reconcile declarations and independently recompute the draft bundle. This
  makes the missing estate preparation executable without opening publication
  gates; selected. It adds tests and explicit failure states.
- Only edit prose/cards. Cheaper, but would not catch missing roles, divergent
  namespaces, wrong types, changed bytes or accidental publication claims.
- Create or publish the estate now. This would yield operational evidence, but
  requires the existing publication/dependency interlocks and exact applicable
  authority; not authorized by this preparation plan.

No new standards-conformance claim is made by these internal contracts.
DCAT-AP, Croissant, RO-Crate, PROV-O, OpenLineage, partner registration and
zero-copy references remain requirements of the following federation track.

## Ordered implementation and evidence

- [x] Obtain role-separated advisory review; freeze concrete input/output
  contracts and negative cases before functional implementation.
- [x] Reconcile all six declared roles, including source archive and Gold-only
  explorer, with planned rather than observed status. Correct the bootstrap
  visibility description using configuration and regression tests.
- [ ] Implement bounded offline declaration reconciliation, exact input hashes,
  role-specific layers/payload/gates, explicit links and canonical ownership.
  Reject missing/duplicate/extra roles, ambiguous identities, type/visibility
  drift and contradictory declarations. No caller-supplied pass flags.
- [ ] Generate deterministic public-safe draft cards and manifest; independently
  regenerate all expected bytes in verification. Missing or modified artifacts,
  extra files, unsafe paths/links and unsupported input shapes fail closed.
- [ ] Add negative tests and a conspicuously synthetic rehearsal. Distinguish
  declaration consistency from actual remote availability, retrieval, custody,
  rights, accepted Gold, release authority and publication.
- [ ] Bind supporting evidence and this plan into Conductor continuation
  context without making WI-G4-MED-04 publicly executable or changing its
  acceptance-bearing mapping or dependencies.
- [ ] Advisory review, full local validation, signed commits, reviewed PR,
  exact-head hosted checks, history-preserving merge and local cleanup.

## Contingencies and stopping rules

Malformed or contradictory declarations stop bundle generation; do not infer a
namespace, silently drop a role, or treat an empty inventory as absence. A
pending or unavailable remote remains an explicit unverified fact, not a
private/local authoritative fallback. Draft links are desired locators, not
proof of reachability. Do not place source bytes or extracted material in this
bundle. Missing exact-edition rights, safety, gate, retrieval or custody evidence
remains separately required for publication and factual estate acceptance.

No new source request, source acquisition, remote creation/configuration,
cross-repository write, publication, release, rights clearance, maturity or
Gold promotion, or G2/G4 acceptance is enabled by this track. Routine Git PR
delivery remains covered by standing owner direction. Preserve earlier failed
evidence and report factual gaps together at the end of the authorized queue.

## Advisory contract freeze

The role-separated advisory review recommends a pure compiler, not reuse of
`bootstrap.build_plan`, which performs account and remote discovery. Inputs are
the exact bytes of `config/bootstrap.toml`, `config/archive_targets.toml`,
`portfolio/products.toml` and `.gfjd/product.toml`. Bound each input by SHA-256;
parse bounded TOML without execution or discovery. Resolve a blank bootstrap
namespace only from the explicit archive-target namespace, never an account.

Output is an internal versioned estate manifest, five draft dataset cards and
one draft static explorer card/entry point. Use fixed safe artifact names and
recompute the complete artifact set and bytes in verification. Bind compiler
implementation and artifact hashes without a circular manifest self-hash.
Every role includes its intended identity, type, public visibility, payload
policy, layer constraints, minimum gate and canonical control-plane reference.
All factual availability, rights, custody, accepted Gold and publication states
remain unverified. Draft links have `requested: false`; no data loads or source
payloads occur. Metadata drafts do not prove Hugging Face card conformance.

The benchmark's existing experimental classification must remain explicit;
do not silently promote it to an accepted observation product. Retain distinct
GitHub G6 and role-specific Hugging Face gates. The unresolved-rights upload
flag cannot override the stronger metadata-only and exact-edition requirements.
An explicit diagnostic must preserve that distinction.

Bootstrap review found both private prose and a hardcoded `--private` command,
plus omission of the existing Space SDK argument. Reuse one configured command
builder for planning and applying, tested with mocked execution; no actual
creation is authorized or needed. Existing public configurations remain public.

Negative cases include role omission/duplication/addition, namespace/type/name/
visibility conflict, unsafe paths, modified/extra/missing artifacts, fabricated
licence or availability, accidental active explorer loads and schema drift.
Tests must assert that the offline compiler performs no subprocess, credential,
transport or remote-discovery calls. This advisory review is not acceptance.

Target layer policy comes from the approved maximal-public-medallion plan dated
2026-08-26: source archive B0, observations B1/Silver/Gold, explorer accepted
Gold/Platinum only. Catalogue is cross-layer metadata; outcomes is separately
governed evidence and benchmark remains experimental. The latter roles must not
be assigned invented analytical maturity. The compiler records the policy
reference and hash alongside prospective target rules, not qualification claims.

## Implementation ledger

- `5f91da8`: shared configured creation-command builder fixes private/public and
  Space SDK plan/apply drift. A regression first failed on the hardcoded private
  proposal. All 13 bootstrap tests then passed; Ruff and strict typing passed.
  Calls in these tests are mocked; no remote repository was created.
- The portfolio now includes the missing source archive as a planned generated
  distribution under `gfjd-platform-release`, matching the approved topology.
  Existing benchmark classification is unchanged. The six-role declaration
  regression and all 13 bootstrap tests pass (5.29s).

Compiler, bundle verification, supporting evidence, phase review and full
validation remain in progress. This ledger does not claim future delivery.
