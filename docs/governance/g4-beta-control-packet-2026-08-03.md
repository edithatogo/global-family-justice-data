# G4 beta control packet — 2026-08-03

This packet records repository-owned beta controls and rehearsals. It is a
private candidate control state, not authorization for a public beta.

## Implemented controls

- Source census and availability atlas build from the machine-readable source
  and jurisdiction registers.
- Harmonised demo/core pipeline with provenance, contracts and deterministic
  build checks.
- Outcomes evidence catalogue and jurisdiction-context structures retain source
  edition and method links.
- Comparability, quarantine and release-diff controls fail closed when clocks,
  denominators, rights or suppression states are incompatible.
- Candidate product packaging exposes version, provenance, definitions and
  limitations.
- Threat, privacy, rights, disclosure and supply-chain policy checks run in the
  local quality harness.
- Backup/restore and correction/release rehearsals run against private,
  synthetic or metadata-only material.

## Validation path

```bash
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

The packet does not establish a public beta, live service, current legal/right
clearance, human accessibility/localisation review, safeguarding/consent,
regional participation or G4 authority acceptance. Real-source products remain
metadata-only, quarantined or private until their source and participation
evidence is complete.
