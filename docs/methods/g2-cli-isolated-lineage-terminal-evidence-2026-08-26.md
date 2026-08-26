# G2 CLI-isolated lineage terminal evidence — 2026-08-26

## Outcome

`G2PKT-MATERIAL-ISOLATED-20260826-02` is terminal failed evidence. Extractor A
executed the frozen workspace-verification command with an unintended extra
`.` positional argument introduced by the orchestration instruction. The CLI
returned exit code 2 and rejected the invocation before extractor A opened a
source input. Extractor B was interrupted immediately; no B output or receipt
exists, but a direct B source-access attestation is unavailable.

No extraction output, extraction receipt or comparison artifact exists in the
current lineage tree. No comparator ran, and neither concordance threshold was
assessed. The workspaces and lineage must not be resumed, repaired or reused.

## Immutable bindings

- owner authorization commit:
  `14f7cc46c0169d884f1fb0efdb5df4d7559a0835`;
- packet freeze commit: `a8aa91c28ce5b6006671fd0ab672f2773a1f5d84`;
- packet SHA-256:
  `de73f90402400c1a87ceeb4fbc93f5f64e3c891655dac0778b07bd25ed1977cc`;
- terminal receipt SHA-256:
  `d465a0e8b7d9cd9d26b5d88d0918b51859d0e387963cda5bba2b11fb3ee1d3f8`;
- private role-separated advisory report SHA-256:
  `2c4b74035b96a36fa0689ca24b3f168945ee5df50157ee67bcc7b53030fef260`.

The advisory report found the terminal stop contract-consistent and recommended
qualified B source-access wording. It remains advisory and does not accept a
criterion, maturity level or gate.

## Conductor disposition

- G2-C04: `in_review`;
- G2-C07: `in_review`;
- M06: L1;
- G2: nine of thirteen criteria accepted and not passed;
- publication, release, rights clearance, gold promotion and maturity
  promotion: not authorized.

This receipt records a bounded failure honestly. It is not dual-review,
re-extraction, concordance, reproducibility, rights or release evidence.
