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

- [x] Implement/test correction identity, source-recomputing history verification,
  append-prefix checks, half-open valid/recorded intervals and partition replay
  (`f18e2cc`).
- [x] Integrate B0 custody and public-safety bindings into a source-faithful
  B1/reviewed-Silver preparation path using conspicuously fictional fixtures.
  Do not manufacture real extraction or source-rights evidence
  (`b64c133`, `52b8dd4`).

  The representative implementation uses explicit XLSX sheet/header/cell
  selections and preserves OOXML lexical values and cell types, not inferred
  displayed formatting. The existing generic connector cannot supply that
  guarantee because it normalizes labels and reads cached formula results.
  PDF/manual and ODS extraction still require their own reviewed contracts and
  actual evidence; a ZIP/JSON-only toy would not establish those either.
  Custody assertions are checked for consistency, selected-source safety is
  recomputed, and current remote custody remains explicitly unverified here.
- [x] Run separate advisory review, adversarial tests and a deterministic
  synthetic end-to-end rehearsal with an independently recomputed receipt
  (`489fe72`; 8 rehearsal regression tests).
- [x] Update Conductor supporting evidence and remaining factual prerequisites.
- [~] Full validation after hosted review fixes; signed implementation commits.
- [~] PR, exact-head CI, merge and local cleanup.

No new source requests, source-content access, failed-G2-output reuse, publication,
release, layer promotion or gate acceptance is authorized. The next track after
this implementation is per-layer qualification; real custody/source evidence and
owner adjudication must remain visible wherever not actually supplied.

## Review fixes and advisory disposition

- [x] Bind append-only checks to the complete linked journal and a trusted prior
  checkpoint (`52b8dd4`). Projection event IDs alone do not detect a rewritten
  custody URL or changed outer workbook bytes that produce identical cells.
  Regression cases reject both rewrites, truncation, a wrong checkpoint and a
  replacement presented as the old journal. The caller must retain the original
  checkpoint independently; this API cannot authenticate its provenance.

Role-separated advisory review (`preservation_inventory`) reproduced the original
gap and approved the corrected bounded implementation after independently running
22 pipeline tests. The format implementation (`api_contract_advice`) added explicit
package-root relationship support without filesystem or network resolution.
Combined history, XLSX and pipeline tests: 123 passed; Ruff and strict typing pass.
This is agent advice and synthetic engineering verification, not independent
assurance, remotely observed custody or empirical source acceptance.

Remaining factual prerequisites: authorized exact editions; current genuine
custody and public-handling evidence; reviewed per-format extraction contracts;
semantic and quality adjudication; and downstream layer qualification. Raw OOXML
lexical values are not formatted display values. Source-valid clocks are never
inferred. Module hashes bind the named implementations, not the entire transitive
runtime; historical verification requires the retained implementation and lock.

The XLSX advisory re-review independently passed all 65 format tests. No material
safety/fidelity finding remained in the bounded subset; full OOXML conformance,
rendered display fidelity, formula evaluation and source-time interpretation are not
claimed. Eight rehearsal tests cover determinism, real fictional-cell changes,
tampered outputs/self-hashes and malformed or oversized verification reports.

Run `make medallion-lineage-rehearsal` to build and separately recompute the
fictional receipt. It is also part of `autonomy-full`. The frozen supporting
current report is `data/synthetic/medallion-lineage-rehearsal-2026-08-31-02.json`; verify it
with `python scripts/rehearse_medallion_lineage.py --verify` followed by that path.
Its custody assertions are explicitly fictional and never evidence of retrieval.

Pre-review-fix local checkpoint: `PYTEST_ADDOPTS='-n 2 --dist loadfile' make autonomy-full`
using the locked `.venv` interpreter exited 0. Both suite passes ran 876 tests;
branch coverage was 80.52%. Formatting, lint, strict typing, contract and generated
state checks, programme validation, policy checks, restore and integration
rehearsals, the medallion rehearsal, wheel/sdist inspection and byte-identical
wheel/sdist/release rebuilds passed. The final autonomy context verified. These
are local technical results; hosted CI and merge remain separate delivery steps.
The final advisory review also verified the frozen report hash and unchanged
in-progress/in-review statuses without a gate or maturity promotion.

### Hosted review follow-up

- [x] `89d4793`: reject impossible calendar dates, clock components and offset
  components in selected explicit date cells, preserving valid lexical text
  unchanged. Fifteen added regression cases cover impossible dates/times/offsets,
  leap days, fractions, naive times and offsets. This validates a restricted
  representation; it does not infer source time or perform date-system conversion.
- [x] Verify the cited implementation commits are retained signed-branch
  ancestors. The review used a temporary squash snapshot rather than actual PR
  head `8929f54`; all four references resolve in the preserved history. Do not
  replace them or squash the branch.
- [~] Rerun the full checkpoint and exact-head hosted checks before integration.

The original `medallion-lineage-rehearsal-2026-08-31.json` is retained unchanged
as historical synthetic evidence and requires its original implementation
(`489fe72`). Rehearsal 02 binds the tightened parser and is the current supporting
report. This is a synthetic engineering rerun, not a G2 extraction lineage or
an empirical promotion. The hosted PR is #137; its live state controls delivery.
