# T5 harmonisation, quality and assurance control packet — 2026-08-03

This packet consolidates repository-owned T5 controls and validation evidence.
It is advisory and technical; it does not replace accountable methods
adjudication, independent assurance, rights/legal review or gate acceptance.

## Implemented controls

- Harmonisation rules preserve source edition, clock, denominator, missingness,
  suppression and transformation lineage rather than silently combining
  incomparable observations.
- Comparability tiers, break-in-series markers and quarantine states are
  enforced before candidate promotion.
- Pilot extraction/review fixtures record dual-review, adjudication and
  quarantine outcomes; independent re-extraction controls compare outputs
  against configured concordance thresholds.
- Negative findings, inaccessible sources and non-official-only findings have
  explicit second-review queues and remediation dispositions.
- Quality reports and release-diff checks surface unresolved P0/P1 defects and
  prevent promotion when required evidence or rights states are absent.
- Candidate gold-series assurance, final-quality and methods-review records are
  linked to their evidence packets and remain in review until accountable
  acceptance is recorded.

## Validation path

```bash
PYTHONPATH=src uv run python -m gfjd validate --strict
make PYTHON='uv run python' integration-rehearsals
make PYTHON='uv run python' release-reproducibility
make PYTHON='uv run python' autonomy-fast
```

## Fail-closed boundaries

Synthetic fixtures and agent-panel re-extraction demonstrate the control path,
not real pilot or gold-series assurance. The packet does not create an
independent reviewer, resolve source rights, approve methods, clear legal or
security findings, or pass G2–G6.
