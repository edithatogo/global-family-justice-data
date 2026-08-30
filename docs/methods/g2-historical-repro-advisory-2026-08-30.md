# Historical reproducibility metadata-stage advisory review

Role: `repro_policy_advice`, separate analyst-agent reviewer; advisory only.
Implementation: signed commit `50af672`; owner policy record: `59016ff`.

## Options and recommendation

1. **Recommended:** prepare this separate metadata-only successor under the
   approved bounded-reproducibility claim. Disclose unknown historical exposure;
   never describe it as project-unseen. Keep complete enumeration mandatory for
   the new response and exclude enumerated prior locators conservatively.
2. Continue future-edition monitoring only. This avoids the historical request
   but cannot guarantee when eligible material becomes available.
3. An all-stage historical execution packet is premature: exact editions,
   source identifiers, source access controls and extractor bundles do not exist.

Trade-off: this one-request route can test metadata feasibility at bounded cost,
but may terminate on schema, enumeration, overlap or insufficient hypotheses.
The API schema is synthetic-tested, not live-confirmed. A terminal result is
preserved; any successor is prospective, never a repaired passing receipt.
UK metadata hypotheses do not amend the accepted multi-jurisdiction pilot scope.

## Findings and remediation

- P1 malformed format arrays/objects could raise before recording a receipt:
  explicit type guard added; fake-transport regressions retain later locators.
- Malformed Unicode locators could interrupt exposure recording: surrogate-safe
  digest handling now records invalid locator identity without publishing text.
- P2 attempt/output paths and marker-write failure: symlink confinement occurs
  before consuming the attempt; marker-write errors enter terminal recording.
  An execution directory or marker already present forbids another attempt.
- Timestamp UTC normalization could overflow: classified as ambiguous timestamp;
  a fake-transport regression verifies terminal recording and later locators.
- Complete malformed JSON response retains its digest/size, not raw bytes, in
  an explicitly incomplete-exposure terminal receipt.

The reviewer supported freezing subject to the timestamp correction, now tested.
No remaining reviewer dissent was recorded. This is not independent assurance,
source-rights clearance, execution authorization or G2 acceptance.

## Exact next decision

Bundle: `data/methods/g2-repro/metadata-bundle-2026-08-30.json`.
SHA-256: `e166ea3785521bdcf1802bdc005383af40f054a1c349871d313c91e963107004`.

PR #131 automated review additionally required deterministic owner-signer trust.
The existing repository SSH allowed-signers policy is now digest-bound and
explicitly selected by the verifier, overriding ambient Git signer settings.
Fake-transport tests assert the exact configuration. This prospective bundle
revision precedes any execution; it does not repair an attempted lineage.

> I authorize the one exact metadata request in this bound bundle. No retries,
> returned-URL access, source access, extraction, publication, release or G2
> acceptance is authorized.

This wording is proposed, not recorded as approved. Existing owner approval
covers the policy and repository-owned preparation, not this external request.
