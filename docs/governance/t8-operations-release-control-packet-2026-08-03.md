# T8 operations, reliability and release control packet — 2026-08-03

This packet consolidates repository-owned T8 operations and release controls.
It is rehearsal evidence only and does not establish live service authority,
custody, support staffing or release approval.

## Implemented controls

- Release, rollback, republish, correction and incident procedures are
  documented in the runbook and exercised against private candidate artefacts.
- Backup and restore rehearsals verify manifests, checksums, correction paths
  and recovery outputs without exposing restricted source material.
- Monitoring and source-drift controls produce deterministic receipts and
  explicit escalation/incident fields.
- Release packaging, provenance, signing-path and archive-manifest controls are
  linked to the candidate build and fail closed when required fields are absent.
- Service handover records define ownership, support rota, correction channel,
  monitoring, release calendar and succession fields as required evidence.
- External operations approval records distinguish drafts, rehearsals and
  accountable live approvals.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

Private/synthetic rehearsals do not establish live ownership, support staffing,
two-location independent custody, signing authority, external operations
approval or publication. Those records remain pending, as do downstream gate
acceptance decisions.
