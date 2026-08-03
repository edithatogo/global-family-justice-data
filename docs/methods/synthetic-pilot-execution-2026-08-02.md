# Synthetic pilot execution and panel review — 2026-08-02

## Execution

The approved private pilot was run with:

```bash
PYTHONPATH=src uv run python -m gfjd demo run --output build/synthetic-pilot
PYTHONPATH=src uv run python -m gfjd demo verify --output build/synthetic-pilot
```

Results:

- five heterogeneous connectors exercised: CSV, JSON, HTML, XLSX and manual
  transcription;
- five mapped/silver rows and five gold rows;
- five promoted and zero quarantined rows;
- normalized gold output SHA-256:
  `12866c222b7a183a8e9aae4d37bb2caf1c2925030f5ade1988237e23fa1febc4`;
- all rows are explicitly fictional synthetic records.

The output is a reproducible pipeline and regression receipt. It is not real
source evidence, rights clearance, local verification, participant evidence,
or a public-release claim.

## Panel review

Three role-separated analyst-agent reviews examined the output, methods note,
and Conductor implications. The panel recommendation is to accept the run as
synthetic reproducibility evidence only and retain G2 fail-closed.

The nominal second run in `build/synthetic-pilot-independent` has the same
normalized output hash, but its connector receipts still reference the primary
`build/demo` bronze outputs. It therefore does not constitute an independent
re-extraction. This is recorded as a control finding, not silently promoted.

## Isolated re-extraction

The connector runner now accepts an isolated output root. A fresh run on
2026-08-03 used:

```bash
PYTHONPATH=src uv run python -m gfjd demo run \
  --output build/synthetic-pilot-independent-20260803 \
  --connector-output-root build/synthetic-independent-bronze-20260803
PYTHONPATH=src uv run python -m gfjd demo verify \
  --output build/synthetic-pilot-independent-20260803
```

The isolated run produced distinct bronze and receipt paths while preserving
the normalized gold hash `12866c222b7a183a8e9aae4d37bb2caf1c2925030f5ade1988237e23fa1febc4`.
This closes the prior receipt-reuse control finding for the synthetic fixture.

The follow-up panel review classified this as `synthetic_only` technical
validation. The inputs and connector configurations remain the same fictional
fixtures, and the fixed execution timestamp is inherited from the reproducible
demo contract. No independent operator, blinded review, semantic adjudication,
rights/privacy/security assessment or accountable methods authority is implied.

## Required follow-up

To obtain genuine independent review, create a separately verified copy of the
synthetic input bundle, run connectors into a distinct bronze and receipt root,
record a distinct operator/agent role and recipe digest, and compare normalized
outputs plus row-level diffs. A methods authority and independent reviewer must
then adjudicate the real pilot records in
`data/methods/pilot_adjudication_register.csv`. Until that occurs, no G2 work
item or gate is accepted.
