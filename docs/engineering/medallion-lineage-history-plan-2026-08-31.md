# WI-G4-MED-02 — correction history and custody-bound replay

Status: in progress; repository-owned implementation. The full work item remains
subject to real B0/B1/Silver evidence and accountable acceptance.

Baseline: signed `3c9d9ec`, merged PR #136; `autonomy-full`, 745 tests twice,
79.57% coverage and all 17 hosted checks passed. Source manifest and bounded
bootstrap discovery are rechecked before material changes.

## Recommended implementation and alternatives

Extend the existing exact-string projection with an append-only, digest-bound
partition revision journal. Each revision replaces the entire named partition;
partial-row and partial-valid-interval merges are outside this contract. Distinct
source periods should use distinct partition identities unless an explicit
mapping contract says otherwise. Do not infer empirical clocks or methods.

Each event binds the exact projection receipt, source bytes, contract, partition,
explicit nullable source-valid interval and previous partition revision. Recorded
intervals are derived from ordered correction events without rewriting earlier
receipts. Unknown source-valid time is reported explicitly, never assumed valid
for a requested date. A partition's corrections form a single unambiguous chain;
cycles, forks, cross-partition parents and historical mutation fail closed.

This is simpler to audit than a generic transformation/event system, but cannot
merge competing revisions or infer partial-period corrections. Such cases stop
for a prospective contract rather than silently selecting a winner. Existing
historical receipts require their original implementation for exact replay.

## Ordered tasks

- [~] Implement/test correction identity, source-recomputing history verification,
  append-prefix checks, half-open valid/recorded intervals and partition replay.
- [ ] Integrate B0 custody and public-safety bindings into a source-faithful
  B1/reviewed-Silver preparation path using conspicuously fictional fixtures.
  Do not manufacture real extraction or source-rights evidence.
- [ ] Run separate advisory review, adversarial tests and a deterministic
  synthetic end-to-end rehearsal with an independently recomputed receipt.
- [ ] Update Conductor supporting evidence and remaining factual prerequisites.
- [ ] Full validation, signed commits, PR, exact-head CI, merge and local cleanup.

No new source requests, source-content access, failed-G2-output reuse, publication,
release, layer promotion or gate acceptance is authorized. The next track after
this implementation is per-layer qualification; real custody/source evidence and
owner adjudication must remain visible wherever not actually supplied.
