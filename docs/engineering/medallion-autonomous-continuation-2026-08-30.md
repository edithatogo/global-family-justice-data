# Medallion autonomous continuation

Status: implementation complete; repository-owned execution preparation, not gate
acceptance. Validation and delivery are tracked by the exact-head checks and
merge state of [PR #127](https://github.com/edithatogo/global-family-justice-data/pull/127).

## Immediate prerequisite

- [x] Replace status-only autonomous execution classification with explicit
  repository-only work scopes; unclassified and acceptance-bearing work must
  remain outside the executable queue.
- [x] Bind this continuation plan and the standing-owner policy into resume
  packets; align the operator guidance with sole-owner decision rights.

Delivery requires full local validation, reviewed signed commits, passing
exact-head hosted checks and verified merge before local branch cleanup. The
linked PR is the delivery record; this document does not assert a future merge.

The inspected resume packet incorrectly put WI-G4-MED-04 (public Hugging Face
publication) into the repository-owned queue because it was planned. This is
a preparation-control defect, not evidence of an unauthorised publication.

## Ordered remaining queue

1. WI-G4-MED-02: implement and test append-only correction history, explicit
   valid/recorded intervals, acyclic supersession and deterministic partition
   replay. Begin with conspicuously synthetic fixtures, never failed G2 outputs.
2. WI-G4-MED-02: integrate verified B0 custody/safety bindings with source-faithful
   B1 and reviewed Silver rebuilds. Implement local contracts and fixtures first;
   actual source access must match an existing bounded authorisation or wait.
3. WI-G4-MED-03: prepare independent per-layer qualification and quarantine
   checks. Respect Conductor dependencies; preparation is not acceptance.
4. WI-G4-MED-04/05: prepare estate manifests, federation metadata and dry-run
   verification. Public writes and cross-repository changes require their exact
   applicable authority and cannot be inferred from a planned work item.
5. WI-G5-MED-01/02/03: prepare restore, lifecycle and safety rehearsals as their
   dependencies allow. Actual remote execution and factual completion remain
   separately evidenced. G6 publication remains gated.

## Execution recommendation and alternatives

Recommended: continue through safe repository-owned slices during an active
run, with focused tests while iterating and full validation at coherent phase
boundaries. Complete the signed-commit, PR, exact-head CI, review and merge
cycle under standing direction. Refresh the resume packet and select the next
eligible action; a merge is not itself a reason to ask for another prompt.

One-PR-per-prompt operation is simple but adds owner overhead. Unrestricted
autonomous publication would reduce pauses but exceeds the existing authority
and is not an option this plan enables. Scheduled continuation could resume the
same bounded queue between sessions; this plan is not a scheduler and does not
claim that such an implementation schedule is active.

## Contingencies and stop rules

- Preserve unrelated work; do not run competing writers in the same checkout.
- If an item needs external facts or authority, record the precise missing
  input and continue any other eligible repository-owned item without relaxing
  dependencies or reclassifying the blocked item as complete.
- Group genuine owner decisions, with recommendation, trade-offs and fallback.
  Do not request approval for routine artifact hashes, tests or advisory input.
- Agent panels advise; the owner alone accepts governance decisions. No agent
  output creates source facts, rights clearance or independent assurance.
- Failed bounded G2 lineages remain terminal; never restart them as ordinary
  engineering retries. Existing monitor authorisations remain unchanged.
- Pause when no authorised work remains, validation cannot be repaired within
  the workflow limits, or a material authority/scope boundary is reached.

The explicit execution-scope registry is a conservative routing control, not
new authority. Adding an entry requires review against the work item and current
owner policy. Status and a title containing reassuring words are insufficient.

## Implementation evidence

Signed implementation commit `8fdb351` adds the explicit execution-scope guard,
resume inputs and aligned sole-owner guidance. All 23 focused autonomy tests
pass, including unknown and malformed identities/statuses, acceptance states,
publication exclusion and non-mutating classification. Formatting, lint and
typing pass. This is repository-owned safety remediation only; the correction
history and all factual medallion acceptance criteria remain open.

## Review fixes

- [x] `c8de5d2`: preserve the mandated AGENTS, START_HERE, bootstrap prompt and
  implementation prompt order, with an exact-order regression assertion.
- Implementation SHA `8fdb351131bb6832d9b06fa40630fd40f5517bc6` is a verified
  signed ancestor of this branch. Integration preserves that ancestry by
  fast-forward; no squash or rebase is permitted. Deleting a merged local branch
  does not delete commits reachable from main.

The scope guard routes resume advice; it is neither a network sandbox nor an
executor. Existing command and source-access controls remain mandatory.
