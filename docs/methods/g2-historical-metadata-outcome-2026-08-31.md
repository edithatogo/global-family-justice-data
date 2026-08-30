# Historical metadata request — terminal outcome

Campaign: G2HISTORICAL-REPRO-METADATA-20260830-01.
Disposition: terminal failed metadata stage; authorization consumed, no retry.
Owner authorization: signed commit `080db21a328d7b0f35891644eb7336e11b0851d1`.
Immutable receipt and attempt: signed commit `20feba93827dc9bd2c1943811b559d71e755359c`.
Supports WI-G2-04/07 as failed evidence only; neither is accepted.

## Recorded facts

Fresh registrar: `historical_metadata_registrar_20260831`.
Execution interval reported by registrar: `2026-08-30T20:53:43Z` to
`2026-08-30T20:53:51Z` (31 August in Australia/Brisbane).
The frozen command exited 2 after one GET; no retry, redirect, pagination,
returned-locator request, source access or extraction occurred.
This statement is supported by bound code, the receipt and registrar report,
not independent packet-level network telemetry.

- Received bytes: 3,777; response SHA-256
  `645914773cfeb3ab8f4dd886e0f4507b54a5097db479287d5841cdc52aadfea2`.
- Nine locator observations retained, each `requested: false`; zero hypotheses.
- Reasons: `current_enumeration_contract_failed`, `result_schema_failed`,
  `fewer_than_two_hypotheses`.
- Receipt SHA-256:
  `8f6ae331e1debc79825f3ec48a1e1e297c6daaff78fc850cb14b42f63b84ea42`.
- Attempt-marker SHA-256:
  `490b3c09588ba1e4dd3a1b86e7c47f23caee696b03ab4d29dd33c38247e38964`.

Receipt path:
`data/methods/g2/G2HISTORICAL-REPRO-METADATA-20260830-01/execution/receipt.json`.
No raw response, title or source bytes were persisted. The normalized receipt
does not preserve the exact unexpected response keys, so their identities must
not be inferred or reconstructed by another request. The count stop is not
evidence that suitable editions do not exist: schema rejection prevents that
interpretation. Complete current-response enumeration is not established.

## Exposure and frozen evidence

The separate post-request inventory is
`data/methods/g2-audits/historical-postrequest-exposure-2026-08-31.json`, SHA-256
`238327f54b70caf893941a23bbc29c85408f9c4c1cd17996e3575a6a761d477b`.
It binds 235 persisted files and 4,623 normalized locator identities, including
the new receipt; these are not counts of eligible or accessed source editions.
All three earlier exposure gaps remain. The inventory's historical gap codes
do not replace the current receipt's failed enumeration/schema disposition.
The original audit, bundle, runtime, receipt and attempt marker are unchanged.

## Separate offline advisory review

Reviewer: `historical_metadata_outcome_review_20260831`, network-prohibited.
The reviewer checked authority signature/committed bytes, bundle digest,
request endpoint/count, nine observation flags, terminal state and absence of
positive downstream authority. No network, response replay or sealed-source
inspection was performed. This is agent advice, not independent assurance.

Recommended: close this lineage terminally and retain existing separately
authorized future-edition monitoring as redundancy. No dissent from closure;
explicit dissent from interpreting zero hypotheses as absence of editions.

Alternative: prepare a prospective contract redesign using repository-owned
documentation and synthetic tests. Trade-off: more preparation and a later
separate access decision, with no guarantee of source eligibility. Any redesign
must carry these exposures and limitations; it cannot repair this receipt or
silently retry this campaign. Do not use these nine locators as selected sources.

## Post-execution harness maintenance

The unchanged pre-request test failed after execution with `stale exposure
audit`: the receipt correctly grew the inventory. That observed failure was
not suppressed. The current harness is versioned for post-execution state:

1. The original bound test bytes are preserved at
   `data/methods/g2-repro/frozen-controls/test_g2_historical_repro-20260830.py.txt`,
   SHA-256 `44a8aa64589af2363894a5ee22aa4e8d1998d21210ada9e86400a8c7b00ca1a7`,
   identical to signed freeze commit `ed7a892` at the original bound path.
2. Verification-only tests reconstruct all audited pre-request inputs and all
   bundle bindings at their original paths, checking every digest. This is a
   historical preflight-material replay, not a complete checkout or live run.
   The full authoritative manifest is restored byte-for-byte from signed commit
   `080db21`, not derived from the audit. Archived manifest SHA-256:
   `0801c39cee1320c421dd7ad73445693f22894049d639e3da45f9b6e52d060530`.
3. Separate tests assert current inventory growth, immutable terminal receipt,
   consumed marker, one request and negative authority. Live bundle validation
   now rejects the changed current harness binding before reaching audit checks.

No skip, xfail, monkeypatch, response replay, frozen-binding change or network
retry makes the suite green. Green tests mean historical verification and
post-run invariants hold, not that the metadata campaign succeeded.
The reviewer identified and corrected an initial self-derived manifest in the
new test before completion. The in-progress validation run was interrupted for
that correction and is not claimed as a completed check.

## Next step

Validation on `c0179d3`: full `autonomy-full` exited 0; 558 tests passed in both
coverage and plain runs, 78.58% branch-aware coverage, integration/restore,
deterministic package and rehearsal-release checks, and autonomy verification.
All 17 hosted checks passed on that head. PR #132 preserves the signed history.
The final documentation-only closeout retains all frozen and outcome digests.

Repository-only schema-contract preparation is possible; any external schema
discovery or successor request needs separate authorization. G2 remains 9/13,
C04/C07 and WI-G2-04/07 remain in review, and M06 remains below L2.
No source right, maturity, Gold status, publication, release or G2 acceptance
is created by this outcome.
