# T7 security, privacy, legal and supply-chain control packet — 2026-08-03

This packet consolidates repository-owned T7 controls. It records preparation
and fail-closed automation only; it is not specialist legal advice, rights
clearance, independent security assurance or gate acceptance.

## Implemented controls

- Aggregate-only, prohibited-data, ethics, disclosure and privacy boundaries
  are encoded in repository policy and validation checks.
- Threat, risk, source-rights and redistribution queues preserve unresolved
  decisions explicitly and prevent ambiguous material from being promoted as
  reusable data.
- Pilot, beta, release-candidate and final assurance records link security,
  privacy, rights, disclosure and supply-chain findings to their evidence
  packets and fail closed on unresolved critical/high findings.
- GitHub Actions are pinned and policy-audited; dependency review, locked
  environments, SBOM/provenance generation and local supply-chain checks are
  wired into the harness.
- Security receipts, workflow policy checks, dependency lock checks and
  repository/public-data scans can be regenerated deterministically.
- Source-rights handling supports metadata-only or quarantined fallback states
  and never infers redistribution permission from public availability alone.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' security
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

Agent-panel advice and local scanners do not create independent security or
legal authority, clear third-party rights, establish consent, or close
critical/high findings. Current specialist assurance, source-specific rights
decisions, live credential/custody controls and accountable gate acceptance
remain pending.
