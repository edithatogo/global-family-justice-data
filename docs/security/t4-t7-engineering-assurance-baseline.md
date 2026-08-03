# T4/T7 engineering assurance baseline

This repository-owned baseline makes release integrity and supply-chain review
repeatable while keeping the external assurance boundary explicit.

## Automated controls

- `gfjd validate --strict` runs contract, semantic, programme and repository
  safety checks.
- `gfjd security --json` scans committed text and public-data headers for
  secrets and prohibited person-level fields.
- Contract and lock harnesses check the executable Conductor and dependency
  boundaries.
- Release builds emit `MANIFEST.sha256`, deterministic metadata, lineage and an
  SPDX-shaped `SBOM.spdx.json`.
- Release verification rejects missing, malformed or structurally incomplete
  SBOMs, and rejects any manifest mismatch.

## Assurance boundary

These controls establish a reviewable technical baseline. They do **not**
establish independent security, privacy, legal, licence, vulnerability,
accessibility or supply-chain assurance. A named specialist must review the
digest-bound candidate and record findings, evidence references, uncertainty
and disposition before T7 or a downstream release gate can pass.

## Fail-closed response

If a scan, manifest, SBOM, rights queue or threat-model check fails, quarantine
the candidate, preserve the report and keep it unsigned, unpublished and
metadata-only where applicable. Never convert a local pass into an external
approval or a signed-provenance claim.
