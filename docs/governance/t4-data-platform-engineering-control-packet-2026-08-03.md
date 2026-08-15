# T4 data-platform and engineering control packet — 2026-08-03

This packet consolidates repository-owned T4 implementation evidence. It is
technical control evidence only; it does not constitute gate acceptance,
independent engineering assurance, source approval or release authority.

## Implemented controls

- Target architecture, data contracts, environments and release-authority
  boundaries are documented and validated against the repository schemas.
- Bronze-to-silver-to-gold pipeline execution is deterministic and bound to
  frozen inputs, versioned contracts, lineage and quarantine outcomes.
- Clean release builds produce verified manifests, SBOM/provenance structures
  and reproducible archives under a fixed source-date epoch.
- Candidate artefact checks cover contract validation, checksums, release-tree
  verification and independent comparison of two build outputs.
- Conductor status, gate dependencies and evidence links are generated from the
  machine-readable programme records and checked for drift.
- Backup/restore and release rehearsals exercise the engineering paths using
  private, synthetic or metadata-only material.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

This packet does not claim that real pilot/gold inputs are approved, that
source rights are cleared, that an independent engineering reviewer has
accepted the controls, or that G1–G6 gates pass. Signed provenance, custody,
external assurance and release authority remain separate records.
