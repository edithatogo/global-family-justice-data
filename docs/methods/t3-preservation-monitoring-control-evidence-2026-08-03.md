# T3 preservation and monitoring control evidence — 2026-08-03

This packet records repository-owned T3 controls. It is not evidence of a live
network monitor, independent custody or rights clearance.

## Preservation controls

- Acquisition manifests bind source ID, edition ID, retrieval time, URL,
  storage locator and SHA-256.
- `gfjd acquire verify` detects missing or tampered stored bytes.
- `gfjd preservation` fails closed unless edition identity, content checksum,
  rights disposition and preservation decision reference are present.
- `MANIFEST.sha256` binds checked-in registers and control documentation.
- Backup/restore rehearsal verifies the repository control state; it does not
  establish independent archival custody.

## Monitoring controls

- `scripts/source_monitor_offline.py` and the scheduled
  `.github/workflows/source-monitor.yml` calculate deterministic review-age and
  metadata-health indicators from the checked-in source register.
- Source health states distinguish stale review, missing URL, unknown rights and
  metadata-only routing.
- Drift and broken-link findings must be recorded as new dated search/log rows;
  they are never silently repaired.

The workflow uploads a report artifact but does not claim that a network fetch,
alert delivery or incident response occurred.

## Verification commands

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
PYTHONPATH=src uv run python -m gfjd manifest --verify
PYTHONPATH=src uv run python -m gfjd conductor check-generated
```

## Remaining boundaries

The packet does not claim a live scheduler, alert delivery, incident response
owner, independent archive custodian, source-specific permission or complete
catalogue-wide rights audit. Those remain G3/G5/G6 evidence and authority
requirements. Until they are supplied, T3 outputs are preservation-ready
control evidence and monitoring rehearsal evidence only.
