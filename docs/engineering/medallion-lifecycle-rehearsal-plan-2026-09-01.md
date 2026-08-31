# WI-G5-MED-02 — append-only lifecycle preparation

Status: in progress, offline preparation only. Baseline signed main `1b43ea3`,
PR #150, full gate exit 0 with 1,867 tests twice, 84% coverage and 17 green CI
checks. Its source tree remains the baseline; actual public restore is unmet.

## Recommendation, alternatives and contingencies

Implement a separate immutable artifact lifecycle journal. Existing projection
history verifies transformations and correction time; extending those events
with publication claims would conflate reproducibility and public operations.
A state-only current catalogue would lose withdrawals and supersession history.
The selected journal preserves every historical artifact and both provider
declarations, including disagreement. It prepares all lifecycle operations but
never performs or proves public takedown, discoverability or republication.

Role-separated advice recommends immutable exact-edition identities, strict
prefix checking, no resurrection of tombstoned artifacts, no fallback to older
active content, and digest-only/closed-code audit records. Syntactic restrictions
cannot certify arbitrary identifiers as non-identifying; actual content safety
and owner dispositions remain separate requirements.

## Frozen input contract

Public API `assess_lifecycle_journal(plan_raw, expected_plan_sha256, scope_raw,
layer_contract_raw, checkpoint_raw, event_bank, receipt_bank)` and exact verifier
with the same inputs plus report. All bytes are supplied; no loader, callback,
network, provider mutation or payload decoding. Implementation fingerprint reads
are disclosed. An internal input helper validates/binds all structures before
the state machine runs.

Use strict JSON preflight with the existing restore metadata limits: 1 MiB per
structured input, depth 16, 50,000 nodes, 4,096-character strings, 2,000 members,
duplicate/nonfinite/control/surrogate rejection. Each bank is a plain digest-keyed
dict of bytes, at most 500 events and 1,500 receipts, at most 8 MiB each. Validate
all types, membership and size budgets before hashing. Fixed diagnostics contain
no rejected input. Digests are lowercase 64-hex; opaque IDs use the existing
bounded identifier syntax; timestamps are explicit UTC seconds with trailing Z.

Plan exact keys: contract_version (`gfjd-lifecycle-plan-v1`), state
(`preparation`), scope_sha256, layer_contract_sha256, checkpoint_sha256,
event_sha256 (ordered unique file-digest list, 1–500), receipt_sha256 (unique list,
at most 1,500), as_of. The plan digest is the external computational anchor.
The layer contract must match the existing pinned five-layer contract, unchanged.

Scope exact keys: contract_version (`gfjd-lifecycle-scope-v1`), artifacts.
Artifacts are 1–500 unique entries with exactly artifact_id, object_id,
edition_id, layer, source_sha256, content_sha256, content_blake3, size_bytes.
artifact_id is SHA-256 of canonical entry excluding artifact_id. Object/edition
IDs are opaque; layer is one of b0/b1/silver/gold/platinum; size is a nonnegative
integer, not bool. All entries with the same object_id and edition_id must name
the same source_sha256; B0 content_sha256 must equal source_sha256. Different
content under a B0 edition identity is forbidden; derived corrections may retain
source edition identity but acquire a new immutable artifact ID. Identical
content digests must have identical declared BLAKE3 and size across the scope.
The complete inventory is exactly the union of all event artifact_id and nonnull
predecessor_artifact_id references. Inactive/history membership never disappears.
These are metadata declarations, not acquired or validated source bytes.

Checkpoint exact keys: contract_version (`gfjd-lifecycle-checkpoint-v1`),
event_sha256. Its list is an unchanged canonical ordered prefix of the plan's
event list, including empty initial prefix. Every historical event is replayed;
no cached checkpoint state is accepted. Supplied checkpoint consistency is not
authenticated archival custody.

Event exact keys: contract_version (`gfjd-lifecycle-event-v1`), event_id,
previous_event_id, operation_id, operation, recorded_at, artifact_id,
predecessor_artifact_id, new_state, reason_code, disposition_sha256,
receipt_sha256. event_id hashes canonical event excluding event_id. Each file
digest separately binds its exact serialization. previous_event_id is null only
for the first event and otherwise the immediately preceding event ID. operation_id
is globally unique opaque text. Times strictly increase globally and cannot
exceed plan as_of. No unknown extensions are accepted.

Operations: register, quarantine, withdraw, tombstone, correct, supersede,
republish, observe. States use the existing four lifecycle states. Closed reason
codes: initial, correction, supersession, withdrawal, disclosure, security,
rights, policy, restoration, provider_loss, monitoring. No free-text narrative,
source excerpt, returned response, credential, locator or removal detail is
accepted in this journal. Future actual location evidence is separately bound.

Every event binds three supplied metadata receipts: disposition_sha256 plus two
ordered receipt_sha256 entries, in github then huggingface order. Receipt bank
membership is exactly the union of those references, with no omitted historical
receipts or unused extras. Disposition exact keys: contract_version
(`gfjd-lifecycle-disposition-v1`), operation_id, artifact_id, recorded_at,
reason_code, state (`preparation`). This is a scope-binding preparation record,
not an owner approval, legal decision or factual assurance.

Provider receipt exact keys: contract_version (`gfjd-lifecycle-provider-v1`),
operation_id, artifact_id, recorded_at, provider, declared_status. All scope and
time fields exactly match the event. Status is available, withdrawn,
tombstone_visible, unavailable or unknown. These are explicitly unverified
declarations, not observations authenticated by this verifier. Different providers
may disagree; neither can fill the other's missing record or copy its status.

## Frozen replay rules

Each logical series is (object_id, layer); its head is an immutable artifact.
All references must be within the full scope. Register is allowed only once per
series and introduces an unseen artifact, with no predecessor and new_state
active or quarantined. An artifact cannot be introduced twice.

Quarantine: current active head -> quarantined. Withdraw: current active or
quarantined head -> withdrawn. Tombstone: current withdrawn head -> tombstoned.
Republish: current withdrawn head -> active; a tombstoned artifact cannot be
reactivated. These operations name no predecessor and cannot act on stale heads.
Observe preserves the current head's exact state, including tombstoned state,
and appends fresh provider declarations; it never creates availability facts.

Correct/supersede introduces an unseen artifact in the same logical series,
with predecessor_artifact_id exactly the current head and new_state active or
quarantined. The previous head may have any canonical state. An active or
quarantined predecessor becomes withdrawn; withdrawn/tombstoned predecessors
remain so. Its successor edge is retained. This permits a new exact revision
after a tombstone without resurrecting the tombstone or changing old bytes.
Correction uses reason correction and supersession uses reason supersession;
register uses initial. Other reasons remain closed codes. No cycle, branch,
stale parent, cross-object/layer edge or silent byte mutation is allowed.

Replay every event in order, deriving all historical state intervals and the
complete current inventory. No query or downstream view may fall back from a
withdrawn/quarantined/tombstoned head to an earlier active artifact. Historical
transitions remain in the report, including superseded and inactive members.
Layer lifecycle is not maturity: active is a declared operating state only.
No event grants rights, promotion, publication, transfer, release or gate authority.

For each event compare both provider declarations with desired state: active
expects available; quarantined/withdrawn expects withdrawn; tombstoned expects
tombstone_visible. Report agreement, mismatch and unknown separately, per provider
and for the latest state of every artifact. Unavailable or conflicting declarations
remain backlog; a later matching declaration is only declared recovery, not a
successful remote restore. Superseding an old artifact does not silently update
its provider status: its earlier available declarations now disagree with its
withdrawn state until an explicit observation for that historical artifact is
appended. Such historical observe operations alone may target non-head artifacts;
they preserve their exact state and never change the series head.

## Ordered work and acceptance limits

- [x] `c483cea`: Strict complete-inventory/event/receipt/checkpoint input validation.
- [x] `c483cea`: Full state machine, historical views and provider reconciliation.
- [x] `c483cea`: Negative tests for rewritten prefix, changed edition bytes, missing historical
  records, stale/cross-series edges, tombstone resurrection, unsafe extensions,
  provider disagreement, digest substitution and forged reports.
- [x] Preserve a fictional all-operation rehearsal with explicit provider loss and
  declared recovery, separately indexed as supporting preparation only.
- [~] Role-separated review, full validation, signed PR, CI, merge and local cleanup.

Any structural, digest, history or transition violation fails the whole replay.
Provider mismatch is retained as an explicit fail-closed operational backlog,
not silently repaired or used as proof of an actual takedown. Actual execution
remains gated by public restore, safety/rights and owner authority. WI-G5-MED-02
stays planned until its factual acceptance criteria are met.

## Implementation and review checkpoint

Signed functional commit `c483cea` implements the contract. All 64 focused tests
pass, as do Ruff and both-module mypy. Initial RED evidence demonstrated missing
input rejection and the absent replay API. Review identified missing exact reason
pairings; three fully rebound tests failed before the correction and now pass.
Historical interval tests verify half-open boundaries, implicit withdrawal timing
and that observations do not split or alter lifecycle transition intervals.

The fictional report is
`data/synthetic/medallion-lifecycle-rehearsal-2026-09-01.json`, SHA-256
`82d2eaf0610b1a4c2eb9c93c1d9753fc5f65b187d1b157a9db365142523f98d0`.
Recompute with `.venv/bin/python scripts/rehearse_medallion_lifecycle.py --verify`
followed by that path. It covers five logical layer series, seven immutable
artifacts, 15 events, all eight operation types, and provider loss/recovery
declarations. A separate counterexample retains the implicit predecessor
withdrawal backlog instead of borrowing the successor's matching declarations.
The report is supporting preparation, not E-PUBLIC-SUPERSESSION-OPERATIONS.
Full validation and hosted delivery remain pending at this checkpoint.
