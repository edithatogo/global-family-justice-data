# G1 owner control and risk adjudications — 2026-08-05

This packet records the owner’s supplied decisions. The time-bounded risk
decisions use `2026-09-30` as the explicit review/expiry date. R20 is an
unexpired hard no-go condition.

## Owner control acceptance

I accept the repository-owned portions of G1-C03, G1-C04 and G1-C06 as
recorded in the current digest-bound decision packet. This acceptance is
limited to repository policy, architecture, operating controls, risk/threat
baselines and metadata-only/quarantine rules. It does not constitute
specialist security, privacy, legal, rights, safeguarding or independent
technical assurance. Those remain separately mandatory.

## Risk adjudications

### R02 — incompatible clocks/statistics

**Decision:** mitigated but open. The repository must not compare incompatible
clocks, denominators or statistics. Comparisons remain quarantined until
methods adjudication, comparability evidence and accountable quality review are
complete.

**Expiry/review:** 2026-09-30. **Reopen trigger:** any new clock, denominator,
statistic or cross-jurisdiction comparison. No publication or release is
authorized.

### R10 — disclosure or family harm

**Decision:** mitigated but open. Outputs remain aggregate-only, suppressed
where necessary and metadata-only where disclosure or contextual harm cannot
be ruled out. No fine geography, identifying detail or family-level inference
may be published.

**Expiry/review:** 2026-09-30. **Reopen trigger:** any disclosure incident,
new small-cell risk or proposed increase in granularity. This is not privacy,
safeguarding or legal clearance.

### R11 — credentials/build-chain compromise

**Decision:** mitigated for repository-owned preparation only. Locked
dependencies, pinned workflows, security scans, provenance and signed-commit
controls remain mandatory. No deployment, signing or release may occur without
current security assurance, key custody and incident-response evidence.

**Expiry/review:** 2026-09-30. **Reopen trigger:** secret exposure, dependency
alert, unexpected digest or workflow change. This is not independent security
assurance.

### R15 — funder or institutional influence

**Decision:** mitigated but open. The owner retains decision rights; conflicts
and attempted influence must be recorded; no funder or institution may suppress
findings, comparisons or gaps.

**Expiry/review:** 2026-09-30. **Reopen trigger:** any conflict, suppression
request or governance change. This does not create independent governance.

### R16 — maintenance funding

**Decision:** open planning risk. Private repository preparation may continue,
but no live service or release may proceed without a committed operating plan,
staffing, succession and funding evidence covering the required period.

**Expiry/review:** 2026-09-30. **Reopen trigger:** any launch, service or
publication proposal without committed resources. This is not a funding
commitment.

### R20 — unresolved operational weakness

**Decision:** hard no-go condition. No release, deployment or publication may
proceed while required operational ownership, support, restore, custody,
monitoring or incident controls are incomplete.

**Expiry:** none; active until required evidence passes. **Reopen trigger:**
every release-candidate or go-live proposal. This is not a waiver.

## Specialist boundary

Specialist security, privacy, legal, rights, safeguarding, local-review and
independent technical assurance remain pending and are not waived. Affected
evidence remains `in_review`, `metadata_only`, `quarantined` or
`pending_authority` until separately resolved.
