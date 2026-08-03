# G5 release-candidate control packet — 2026-08-03

This packet records repository-owned release-candidate controls and
rehearsals. It is a private, deterministic candidate state, not a release
approval or publication authorization.

## Implemented controls

- v1 contracts, identifiers, methods and release criteria are surfaced under
  change control and included in the candidate manifest.
- A clean release rehearsal builds and verifies the candidate archive from an
  explicit source date epoch; the two independent rehearsal archives are byte
  identical (the generated digest is recorded in the build receipt, not
  asserted as release approval here).
- Reproducibility, manifest, SBOM, attestation-shape and release-tree checks
  are exercised by the local harness.
- Candidate quality, defect disposition, correction, rollback, restore and
  publication rehearsal records are generated without promoting the release.
- Archive manifest, provenance/lineage and signed-commit pathways are wired to
  the repository controls; custody and signing authority remain explicit.
- Local policy, dependency, security, rights and disclosure checks are run in
  fail-closed mode.
- The operating-plan and accessibility/localisation check surfaces are
  represented, with no claim that staffing, human review or funding exists.

## Validation path

```bash
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

This packet does not establish G4 acceptance, independent methods/security/
legal/accessibility assurance, source-rights clearance, dual-location custody,
external signing authority, committed operating staff/funding, or final release
approval. Candidate products remain private and draft until those authorities
provide signed, digest-bound evidence.
