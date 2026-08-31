# G2 monitor preservation continuation

Scope: completed canonical GitHub Actions observations only; not a new monitor
campaign, source access, extraction, rights decision, publication or G2 acceptance.
Standing autonomous direction authorizes sequential repository work through PR,
exact-head CI, history-preserving merge and local cleanup.

- [x] Start from clean signed main `aaf85ba`; its completed `autonomy-full`
  passed 597 tests twice at 78.78% coverage and all 17 hosted checks. Verify the
  unchanged 953-entry manifest again before edits; run bootstrap dry-run.
- [x] Refresh six-workflow canonical metadata inventory: preceding seven days,
  completed main runs only, oldest first, maximum 30 unpreserved runs.
- [x] Implement/test bounded artifact ZIP selection before reading payloads (`ea94fbc`).
- [x] Verify each exact artifact identity and source ancestry; retain only
  route-approved metadata after schema/digest/count/boundary checks. Record
  missing artifacts, incomplete receipts and original binding gaps separately.
- [x] Add append-only preservation index and offline integrity tests; obtain
  role-separated advisory review, update Conductor supporting evidence.
- [ ] Validate fixed revision, commit, PR, await CI, merge and clean local branch.

## Recommendation, trade-offs and contingencies

Preserve exact receipt/ledger bytes in Git with separate independently computed
file hashes. Reuse existing objects only on exact-byte equality, including empty
ledgers. This costs storage but avoids relying on expiring Actions artifacts.
Artifact-only retention is weaker; rerunning publishers creates new observations
and is not permitted. Failed/partial outcomes stay failed/partial.

Use a fresh temporary directory per exact eligible archive. Download ceiling:
8 MiB; ZIP ceiling: 32 members, 16 MiB expanded, 8 MiB/member, ratio 1000.
Reject unsafe paths, links, unknown members and incompatible route schemas.
Never decompress or retain execution logs; never retain raw responses, scripts
or statistical source bytes. Original receipt hashes, counts and false access
flags must agree. Provider archive digests and verified file hashes are distinct.
An unavailable or unsafe artifact stops only that run; no reconstruction,
filtered ledger or invented observation. Report the gap and continue other
eligible independent runs. No completed run is credited before verification.

The active gate, work-item acceptance and maturity states are unchanged.
After this track merges, continue the separately versioned offline API contract;
any fresh metadata execution still requires its exact bounded authority.

## Legacy provenance disposition

Run `33240200746-1` predates receipt-internal run/source fields. The original
writer at `cc86d206f323e6f4953fee9f8cdb659323ed83c3` did not emit them.
Normal receipt-identity validation therefore stops. Role-separated advisory
review (`preservation_inventory`) recommends separate artifact-bound-only
retention: canonical GitHub metadata and verified archive digest bind the run,
attempt and source commit outside the receipt. Preserve the original bytes and
disposition; state both missing fields and deny gate eligibility. This does not
relax the modern validator, repair a receipt, or claim equal provenance strength.
It follows the existing distinction between original and retrospective bindings.
Contradictory identity or hash evidence would still stop all retention.
