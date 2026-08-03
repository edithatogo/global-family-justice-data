# G6 final release authority decision packet — 2026-08-02

## Packet identity

- Frozen source revision: `ed4b92e79ca02f5fe06e3a2419356cfe8bffa58f`
- `MANIFEST.sha256` SHA-256: `ba5c3d2841a3fd42b5c4656caf0473756abe29f6461ecb6ab6e7e3d088dda603`
- Scope: G6 final release, publication, signing, custody and archive decision.
- Panel inputs: release governance, release criteria and release fallback agents.

Agent panels provide pre-release advice only. They cannot sign, grant release
authority, attest rights/consent/custody/funding or accept G6.

## Owner policy selection

The owner approved **F1 in principle** on 2026-08-02: retain final G6 release
authority; use agent-panel pre-release advice; and sign only after G1–G5 and all
mandatory release evidence pass. The candidate remains private and unsigned
until then.

## Options

| Option | Treatment | Recommendation | Rationale |
|---|---|---|---|
| F1 | Owner remains final release authority; agent panels provide digest-bound pre-release advice; owner signs G6 after G1–G5 pass | **Recommended** | Fits the single-person repository while retaining explicit accountability |
| F2 | Formally delegate final release to an external authority | Strongest separation | Requires an actual appointment, mandate and signed acceptance |
| F3 | Defer and retain a private unsigned RC | Safe fallback | Avoids unsupported publication and archive claims |
| F4 | Limited metadata-only preview | Conditional fallback | Only if rights-cleared and explicitly scoped; not a G6 release |

## Recommendation

Adopt **F1 for the release model**, but use **F3 until all prerequisites are
accepted**. Before G6, the owner must review the exact evidence index and sign a
digest-bound decision covering:

- accepted G1–G5 decisions;
- complete evidence index, including `E-V1-RELEASE-DECISION`,
  `E-V1-ARCHIVE-RESTORE`, `E-V1-FINAL-ASSURANCE`,
  `E-V1-FUNDING-CONTINUITY` and `E-V1-SERVICE-HANDOVER`;
- zero unresolved critical/high findings or separately permitted exceptions;
- rights-cleared products and signed provenance;
- two independently administered custody locations and witnessed restore;
- named service/release manager, support, monitoring and incident SLA;
- accessibility, security/privacy/legal and safeguarding assurance;
- committed 12-month staffing/funding; and
- publication scope, rollback, takedown and residual-risk disposition.

## Stop conditions and contingencies

- Missing authority → `blocked_by_authority`.
- Missing evidence → `evidence_missing`.
- Panel disagreement → `adjudication_required`.
- Critical/high finding → `blocked_by_assurance` and quarantine.
- Digest mutation → invalidate reports and rerun.
- Failed restore/signature or uncertain rights/accessibility → private unsigned
  RC only.
- Missing service/support/staffing/funding → static/private artifact only.
- Key compromise → revoke/suspend, preserve evidence and re-review.

Any stop condition keeps the candidate private, unsigned and non-archive-
eligible. Automated checks and panel consensus cannot satisfy G6.

## Owner decision fields

| Field | Required value |
|---|---|
| Selected option | F1, F2, F3 or F4 |
| Release authority | Named accountable authority |
| Packet/product/manifest digests | Exact values |
| Criteria disposition | G1–G6 evidence and conditions |
| Publication authorization | Explicit scope and exclusions |
| Signing/custody references | Exact evidence IDs |
| Decision timestamp | ISO timestamp |
| Immutable reference | Decision/minute/reference identifier |
| Residual risk and rollback | Explicit statement |
| Status | `approved_in_principle`, `accepted` or `deferred` |
