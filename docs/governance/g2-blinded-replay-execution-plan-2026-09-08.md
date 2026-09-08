# G2 blinded replay execution plan — 2026-09-08

Status: `prepared_not_executed`  
Target: `WI-G2-07` / `G2-C07`  
Claim limit: a successful run may establish bounded reproducibility only; it is not independent assurance or G2 passage until owner adjudication.

## Frozen controls

- Cohort: the four exact editions already bound by `G2PKT-MATERIAL-ORCHESTRATED-20260826-01`.
- Inputs: only the five hash-verified source artifacts in `data/raw/files/g2-controlled/`.
- Roles: extractor A, extractor B, network-disabled comparator and advisory reviewer.
- Workspaces: two fresh, physically distinct allowlists created and verified by the orchestrator before delegation.
- Blindness: no expected values, prior outputs, semantic-review answers, comparator output or cross-agent communication may enter either extractor workspace.
- Thresholds: 100% agreement on every critical field and at least 99% agreement across populated fields.
- Stop rules: any scope/hash/schema/isolation/prohibited-data/seal failure, critical discrepancy, repair, retry, substitution, waiver or output reuse terminates the lineage.
- Public boundary: no network, source publication, rights clearance, release or G2 passage.

## Execution sequence

1. Run `scripts/prepare_g2_blinded_replay.py` from a clean checkout.
2. Verify the emitted workspace manifest, exposure receipt and role bundles.
3. Execute two fresh extractors using only their role bundle and allowlisted inputs.
4. Seal both outputs before the comparator can access them.
5. Run the network-disabled exact comparator.
6. Run role-separated advisory review and record dissent or abstention.
7. Bind outputs, receipts, comparator, review and manifest into a new evidence packet.
8. Return the packet to the owner for a single `WI-G2-07` / G2-C07 adjudication.

## Contingencies

- Fewer than two valid workspaces: stop; do not shrink scope.
- Any workspace contamination: quarantine and preserve the failed lineage; do not repair or rerun automatically.
- Concordance failure: retain immutable failed evidence and return for a new owner decision.
- Successful comparator: keep work items in review until owner acceptance is recorded.

## Recommended decision wording

I authorize one fresh blinded replay under this exact packet and its digest-bound workspace manifest. I authorize no source acquisition, contact, rights clearance, publication, release or G2 passage. A passing comparator result must return to me for separate owner adjudication; a failed interlock or discrepancy terminates the lineage.
