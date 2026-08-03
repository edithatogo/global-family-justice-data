# G6 final-release control packet — 2026-08-03

This packet records repository-owned final-release controls. It is a private
readiness bundle, not a go-live decision, publication authorization or waiver
of specialist or accountable authority review.

## Implemented controls

- The v1 criteria matrix, release-decision template and impact/misuse plan are
  checksum-bound and fail closed when evidence or signatures are absent.
- Final-quality and final-assurance control paths consume defect, rights,
  privacy, security, disclosure and quarantine records without promoting
  unresolved findings.
- Candidate artefact verification covers reproducibility, contract checks,
  manifests, SBOM/provenance shape and independent verification commands.
- Private archive/restore and correction rehearsals exercise the two-location
  custody protocol without claiming that a second administrator or live
  custody exists.
- Service handover, support, monitoring, correction-channel and release-calendar
  fields are represented as explicit required records.
- Publication, accessibility, citation, limitations, benefits, harms and
  misuse products are version-linked in the candidate control surface.
- The 12-month operating-plan and funding-continuity fields remain explicit and
  fail closed until committed resources are evidenced.

## Validation path

```bash
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```

## Non-substitutable boundaries

This packet does not accept G5, sign a release, appoint an independent archive
custodian, establish two independently administered locations, create a live
service/support rota, publish products, clear rights or legal/security risks,
provide human accessibility review, or commit funding and staff. G6 remains
blocked until those evidence and accountable-authority records are supplied.
