# WI-G5-MED-01 — complete declared inventory restore preparation

Status: in progress, repository-owned offline preparation. Actual anonymous
public restore and the factual WI-G4-MED-04/05 dependencies remain unmet.
Baseline: signed main `f61e35ea880acdfa6c5f9b0c1bfb6ff11a1acd0d`, PR #149.
Its full gate passed and source manifest verifies; no source request is enabled.

## Options, recommendation and rationale

Reuse the complete five-layer qualifier independently over two supplied replica
banks. Bind the complete inventory and every wrapper-to-payload edge, including
inactive references and additional release artifacts. This gives stronger scope
coverage than a projection-only rehearsal or another repository ZIP restore.
The existing local control-plane backup remains useful but is not public
medallion restore evidence. A real network retriever would require separately
authorized exact locations and must not be inferred from this preparation.

Role-separated advice identified denominator loss through active-only filtering,
shared-digest budget bypass, unbound review time and false success from an
expected failing report. The contract below addresses those cases explicitly.
Do not reduce scope or borrow from another bank when any object is unavailable.

## Frozen inventory and replica contract

`prepare_replica(plan_raw, expected_plan_sha256, scope_raw,
expected_scope_sha256, layer_contract_raw, replica_bank, provider)` is an internal
preparation helper returning validated byte banks and metadata. It performs no
source semantic parsing. `assess_restore_rehearsal` takes the same first five
arguments and `replica_banks` keyed exactly github and huggingface; its verifier
adds a report and recomputes the complete result. All source bytes are supplied,
never obtained through a path, callback, subprocess, network or ambient cache.

Plan keys are exactly contract_version (`gfjd-two-replica-restore-plan-v1`),
state (`preparation`), release_id, scope_sha256, layer_contract_sha256, as_of,
expected_qualification_sha256, record_sha256, payload_sha256, auxiliary_sha256,
inventory and providers. Digests are lowercase SHA-256; release_id uses the
existing bounded opaque identifier syntax. as_of is an explicit UTC instant
validated by the existing projection timestamp checker. Bind the entire
canonical qualification report, not just its supplied self-hash.

The separately supplied qualification scope and exact pinned layer contract must
match both the plan and each bank's bytes. The plan's release association and
scope completeness are declarations, not authenticated release evidence.
The root plan is an external trust anchor for this computation, not a recursively
self-hashed inventory member. All other declared roots and artifacts are members.

The three digest lists are unique lists of up to 500 items each. record_sha256
selects all supplied wrappers; payload_sha256 must equal the union of every raw
wrapper's artifact references, including invalid/inactive/quarantined wrappers.
Do not derive preservation coverage from filtered qualifier results. Additional
release artifacts (packages, metadata or other opaque files) are explicitly
listed in auxiliary_sha256 and receive fixity checking only, not format, safety
or executable-dependency validation. They cannot substitute for required payloads.

Inventory is exactly the unique union of those three lists plus scope and layer
contract digests (at most 1,502 members). Each entry has exactly sha256, blake3
and size_bytes; sizes are nonnegative integers, not booleans. Duplicate inventory
digests, missing/extra membership and any digest/size disagreement fail closed.
Overlapping byte identities across categories are allowed, but role membership
and category budgets remain independent and visible.

providers is exactly github and huggingface, each with exactly locators: a map
covering every inventory digest. Locators are bounded HTTPS declarations on
github.com and huggingface.co respectively, with a nonempty path, no user info,
query, fragment, port, backslash or control text. No locator is requested;
provider labels/host checks do not prove administrative independence or custody.

Plan, scope, layer contract and each wrapper are at most 1 MiB and explicitly
preflighted before older parsers: strict UTF-8 JSON, no duplicate keys/nonfinite
numbers/control or surrogate text, depth at most 16, 50,000 nodes, strings at
most 4,096 characters, lists/dicts at most 2,000 members. Existing narrower
qualification constraints still apply. Oversized complete scopes stop rather
than truncate. Arbitrary payload or auxiliary bytes are never JSON-preflighted.

Each replica is a distinct logical digest-keyed supplied bank with exact inventory
membership. Check type, membership and all budgets before hashing: each artifact
at most 8 MiB, each record/payload/auxiliary category at most 8 MiB, total unique
bytes at most 26 MiB per bank. Scope/contract/wrapper metadata retains its 1 MiB
individual limit. Count shared bytes in every applicable category budget.
Recompute SHA-256, BLAKE3 and size for every object in both banks. Do not borrow
missing bytes from the peer or shared root arguments. Roots must also be present
and exact in each bank.

Reconcile all wrapper metadata with the existing declared scope. Preserve
wrapper-to-payload edges and all object/layer cells. Build the semantic-processing
subset only from active, structurally valid wrappers and supported role names.
Hash inactive bytes but never decode/process them merely because they were
restored. A digest shared with an eligible active edge may be processed for that
edge only; inactive cells remain ineligible. Missing/invalid layer records stay
visible even when the declared inventory is fully present.

## Frozen replay and report contract

Prepare and verify both complete replicas before invoking either qualifier.
Run `qualify_layers` separately using each replica's own root, record and eligible
payload bytes and plan-bound as_of. Require each whole canonical report hash to
match expected_qualification_sha256 and require the reports to match exactly.
No precomputed report, repaired output or first-bank result substitutes for the
second computation. Existing source/container safety ordering remains intact.

Report complete supplied inventory fixity and exact expected-report reproduction
separately from offline rebuild success. An expected failing qualification may
reproduce exactly, but cannot produce successful rebuild or release claims.
The rebuild result requires at least one active non-B0 layer; every active cell
must have no blockers, verified completeness/fixity/quarantine, and for non-B0
layers verified lineage and reproducibility. B0 quality must be verified; Gold
quality must be verified. Preserve all pending factual requirements. No active
transformation is not an automatic rebuild pass. Inactive/absent cells remain
in the denominator with their stated lifecycle and are not promoted.

Return metadata only: plan/root/input/output hashes, per-provider byte/category
counts, preservation edges and processing eligibility, the recomputed qualification
report, all cell statuses, component fingerprints and explicit limitations.
Do not return source/auxiliary bytes. Anonymous retrieval, administrative provider
independence, no-cache acquisition, remote availability, real release inventory
completeness and public restore remain unverified. Rights, promotion, publication,
release, transfer and gate authority are false. Fixed errors do not expose input.
Disclose implementation fingerprint file reads; no other loader is present.

## Ordered implementation and contingencies

- [~] Complete-inventory replica verifier and denominator/budget tests.
- [ ] Independent full five-layer replay wrapper and exact report verifier.
- [ ] Missing/corrupt peer objects, inactive-only dependencies, shared identities,
  scope/time substitution, unsupported/failed qualification and no-loader tests.
- [ ] Preserve a conspicuously fictional full-five-layer rehearsal report and
  targeted failures; index only supporting preparation, never factual restore.
- [ ] Role-separated review, full validation, signed reviewed PR, exact-head CI,
  history-preserving merge and local cleanup.

Any contract, inventory, budget, fixity or expected-result binding failure rejects
the operation. A reproducible blocked qualification stays blocked; it is not
repaired into a pass. No actual source handling, provider retrieval, publication,
G5 acceptance or dependent gate advancement is authorized. After this bounded
machinery is verified, prepare the remaining lifecycle and release-safety work,
then group actual execution/evidence requirements without concealing technical
coverage gaps or reclassifying factual dependencies as complete.
