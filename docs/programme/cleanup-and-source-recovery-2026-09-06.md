# Programme cleanup and source recovery

## Decision and implementation

Use a non-destructive active/completed split. The canonical register contains
81 items: 30 recorded accepted, 45 in review and six planned. Every T0–T9 track
still has unaccepted work. Consequently **no whole track is archive-eligible**.
The new generated active view omits the 30 accepted items; the completion index
retains them, their evidence IDs and dependency status. Canonical CSV rows,
historical packets, manifests, decisions and source records remain in place.
An item returned to review automatically reappears in the active view.

`make status` regenerates both indexes; `make generated` detects stale indexes.
No new parallel Conductor hierarchy, gate rule or acceptance status is introduced.

| Option | Trade-off | Recommendation / contingency |
|---|---|---|
| Active and completion indexes | Reduces daily noise without breaking evidence references | Implemented; regenerate when canonical status changes |
| Move accepted canonical rows or evidence files | Breaks dependency and digest/path bindings unless the entire model migrates | Do not do this merely for cleanup |
| Delete failed runs or restart the implementation | Loses explanatory evidence and repeats already verified controls | Preserve history; repair only demonstrated defects |

## Source recovery performed

The frozen official ODS URL returned HTTP 200 and the exact historical bytes:
990,297 bytes, SHA-256
`3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2`.
The first bounded request checked identity without retention; the second retained
only an exact match and verified disk readback. No redirect or retry occurred.
`docs/governance/g2-ods-exact-recovery-receipt-2026-09-06.json` binds current
retrieval and local custody. Its UTC timestamp is September 5; the project-local
date is September 6. The original packet and old absence receipts are unchanged.

The bytes are outside Git with mode 0600 inside a 0700 directory, under the
existing controlled-retention decision through review on 2027-08-24. They have
not been published, relabelled, extracted or promoted. Exact identity recovery
does not revive a terminated extraction lineage or establish G2 acceptance.

## Remaining G2 dependency and grouped choice

Five exact objects remain unavailable in the recorded bounded recovery scope:
the BRA class-filtered response, quarterly dashboard response, dashboard model,
conceptual schema and exact visual query. Their hashes remain listed in
`docs/governance/g2-exact-input-recovery-extension-2026-09-05.md`.
This new receipt supersedes only that report's ODS availability finding.

Role-separated source-recovery advice recommends:

1. Restore any original API/dashboard objects from a separate owner backup,
   checking every full-byte digest. Existing Git/build scans need not be repeated
   without a new location. This best preserves the already approved identity.
2. If no backup exists, prepare one prospective aggregate-only BRA/dashboard
   capture with new hashes, custody, explicit filters, budgets, semantic contract
   and isolated extraction roles. This is the recommended fallback because live
   services may no longer produce the historical response. It requires one
   grouped scope/execution decision, not repeated approvals for routine steps.
3. Alternatively, explicitly narrow the qualifying cohort to available static
   sources. This is cheaper but drops API/dashboard coverage and cannot be
   represented as satisfaction of the original four-route requirement.

A repeated live query cannot prove a past response from matching aggregate
values. Prose dashboard filters cannot recreate the missing sealed query body.
New results must be distinct evidence; failed outputs must not be reused.

Proposed concise fallback authorization, **not recorded acceptance**:

> Authorize a prospectively frozen aggregate-only BRA/dashboard successor capture
> and isolated review using new evidence identities. Preserve failed lineages,
> exact concordance thresholds, quarantine and the metadata-only public boundary.
> Return a passing result for grouped owner adjudication; no G2 passage or
> publication is authorized by this direction.

The final exact successor contract must reconcile existing stopping rules before
execution. The current recovery request did not trigger a new dynamic query.

## Other unfinished work

The active index retains L2 qualification, reviewed coverage and rights metadata,
populated qualified HF products, Explorer, interoperability and downstream gate
work. Existing code should be reused and tested, not rewritten because these
factual records are missing. Actual registry registration and archive-policy
correction were already merged and verified in the September 5 hosted receipt.
Those completed corrections should not be rediscovered as blockers.
