# Synthetic pilot operations rehearsal — 2026-08-03

This is a private repository rehearsal against synthetic/project state. It is
not live service operations, independent custody, or a release authorization.

Commands:

```bash
PYTHONPATH=src uv run python -m gfjd resilience backup \
  --output build/g2-rehearsal/gfjd-critical-state.zip
PYTHONPATH=src uv run python -m gfjd resilience verify \
  build/g2-rehearsal/gfjd-critical-state.zip/gfjd-critical-state.zip
PYTHONPATH=src uv run python -m gfjd resilience restore-rehearsal \
  build/g2-rehearsal/gfjd-critical-state.zip/gfjd-critical-state.zip \
  --output build/g2-rehearsal/restored
PYTHONPATH=src uv run python -m gfjd resilience verify-restore \
  build/g2-rehearsal/restored/restore-receipt.json
```

The backup receipt reports archive SHA-256
`72cfc923153ed52e54946af23c722bb19cf7b700a15e2a997760341a51cc880b` and
payload SHA-256
`4794d7d9fc2ccdf634359b3afc9f6c89d4849ddf2b405f1dd150ea8a97f5dd0c`.
The restore rehearsal completed with 313 restored files and matching payload
digest.

This closes the local synthetic rehearsal control only. It does not establish
live monitoring, support ownership, two-location independent custody, signed
provenance, staffing, funding, or G2 acceptance.
