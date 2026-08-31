# WI-G4-MED-04 — public estate preparation

Status: completed repository-owned preparation. The publication-bearing work
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
- [x] Implement bounded offline declaration reconciliation, exact input hashes,
  role-specific layers/payload/gates, explicit links and canonical ownership.
  Reject missing/duplicate/extra roles, ambiguous identities, type/visibility
  drift and contradictory declarations. No caller-supplied pass flags.
- [x] Generate deterministic public-safe draft cards and manifest; independently
  regenerate all expected bytes in verification. Missing or modified artifacts,
  extra files, unsafe paths/links and unsupported input shapes fail closed.
- [x] Add negative tests and a conspicuously synthetic rehearsal. Distinguish
  declaration consistency from actual remote availability, retrieval, custody,
  rights, accepted Gold, release authority and publication.
- [x] Bind supporting evidence and this plan into Conductor continuation
  context without making WI-G4-MED-04 publicly executable or changing its
  acceptance-bearing mapping or dependencies.
- [x] Advisory review, full local validation, signed commits, reviewed PR,
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

- `f9bba0b` records the portfolio reconciliation; `f98db63` binds this plan in
  autonomous continuation context without enabling publication. All 34 autonomy
  tests pass, including the exclusion of WI-G4-MED-04 from executable actions.
- `6af1074`: pure offline compiler and exact byte/set verifier. All 28 tests
  pass, including fictional-namespace rehearsal, changed authority fields,
  altered cards, missing/duplicate/extra roles and invalid declaration types.
  Role policy is prospective; the factual states remain unverified.
- `b6770fa`: fresh-only bounded filesystem CLI and tests. All 20 CLI tests pass
  locally, including real declaration roundtrip, preserved partial writes,
  unsafe links, missing/extra directories, and explicit capability failure.
- Separate role reviewers cross-reviewed the compiler and filesystem wrapper
  without finding actionable contradictions. Their advice is not acceptance.
- Combined 95 bootstrap/autonomy/compiler/CLI tests pass (8.31s), with Ruff
  formatting/lint and strict typing passing. Full phase validation remains due.

## Bound draft and limitations

The current eight-file draft bundle is `data/estate/preparation-2026-08-31-02`.
Its manifest SHA-256 is
`b31d8c78392accaada2bd612736d4b1e7db310ffc2061e3faa2e4a4907b643cb`.
Generation and independent exact recomputation passed. The real intended
repository declarations are metadata, not synthetic empirical observations;
the separate test fixtures use an explicitly fictional namespace. No source
artifact or extracted observation is in this bundle.

Run `python scripts/prepare_medallion_estate.py --verify` with that directory to
recompute every artifact from the bound current configuration and compiler.
`--output` requires a fresh directory whose parent already exists; an existing
or partial output is preserved and never repaired or overwritten automatically.

The filesystem CLI requires POSIX descriptor-relative operations and no-follow
directory/file opening. It explicitly fails before any read or write when those
capabilities are unavailable, including Windows. POSIX-specific tests declare
this platform condition; the capability-failure test remains runnable elsewhere.
The pure bytes-in/bytes-out compiler is portable, but no Windows filesystem
verification or full Hugging Face card-standard conformance is claimed.

E-HF-ESTATE-DRAFT-20260831-02 is supporting `in_review` evidence only.
E-HF-PUBLIC-MEDALLION-ESTATE remains missing and WI-G4-MED-04 remains planned.
Full local validation, reviewed PR delivery and cleanup passed as recorded below;
hosted estate publication and federation are not completed by this plan.

## Hosted review correction — mandatory policy bytes

PR #139 review identified that v1 emitted a policy hash without verifying the
referenced policy bytes. Its original full local validation passed 1,199 tests
twice (96.08s and 83.79s), but those tests did not cover the missing binding;
green validation did not justify accepting that gap or merging.

- [x] `d0949b5`: v2 requires a fifth supplied input at the exact policy path.
  `SOURCEFILES` still names four TOML configurations; the input bank additionally
  requires the approved policy bytes. They must match the frozen policy hash
  before any TOML parsing. Missing, changed, empty or oversized policy fails.
  The manifest binds all five input hashes and computes its policy hash from
  the supplied bytes; there is no implicit policy-file lookup or fallback.
- [x] The missing-policy regression failed on v1. All 57 updated compiler/CLI
  tests pass (1.08s), including fifth-file bounds and tampering. Ruff and strict
  typing pass. The contract version is now `gfjd-offline-estate-v2`.
- [x] Generate and exactly verify draft 02. Draft 01 and its eight files remain
  byte-identical to signed head `6f1f815`; its SHA-256 remains
  `555da748161253174a9da789bc35001f29a5bd0a57f1854fde811bb81b9bafe1`.
  Retain that historical implementation for v1 recomputation; do not repair or
  relabel it as current v2 evidence.
- [x] Post-fix advisory review, full local validation and exact-head hosted
  checks, resolved review, history-preserving integration and local cleanup.

The four-configuration contract above records the initial interface; this v2
correction adds mandatory policy bytes without broadening execution authority.

## Delivery closeout

PR #139 merged at signed commit `048c4bd5d3172b989bfbc3b8033deab8d8e5a74f`
on 2026-08-31T13:34:47Z. Post-fix role-separated advisory review confirmed the
mandatory policy binding and preserved historical draft. All 17 exact-head
hosted checks passed and the actionable review thread was resolved. Full local
validation exited zero: 1,208 tests passed twice (81.70s and 128.43s), reported
coverage 82%; package, restore, bootstrap and deterministic distribution checks
passed. Integration preserved signed history. Local cleanup left one worktree
and main only; no remote branch was deleted. This closes preparation, not the
publication-bearing work item or its missing factual evidence.
