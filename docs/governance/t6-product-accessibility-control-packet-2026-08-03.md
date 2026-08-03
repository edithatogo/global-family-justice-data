# T6 product, documentation and accessibility control packet — 2026-08-03

This packet consolidates repository-owned T6 product and publication controls.
It is a private candidate record and does not constitute publication, human
accessibility approval, localisation sign-off or a release decision.

## Implemented controls

- Product contracts expose version, provenance, definitions, comparability
  limits, suppression states and responsible-use limitations.
- The source census/availability atlas, outcomes catalogue and jurisdiction
  context structures are linked to source editions, methods and break-in-series
  records.
- Candidate downloads and query/API surfaces are packaged with manifests,
  citations, lineage and explicit metadata-only/private boundaries.
- Documentation surfaces include methods, limitations, coverage gaps,
  accessibility exceptions, citation guidance and misuse safeguards.
- Localisation and accessibility review queues preserve language, format,
  keyboard/semantic and human-review findings without silently treating an
  agent or automated check as a participant or reviewer.
- Version-linked publication bundles can be built and verified without
  publishing or redistributing restricted material.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

This packet does not claim complete reviewed coverage, real-source rights,
human accessibility or localisation testing, consented user research, public
publication, or G3–G6 acceptance. Candidate products remain private,
metadata-only or quarantined until the relevant evidence and authorities are
recorded.
