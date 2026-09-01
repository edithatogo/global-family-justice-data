# WI-G4-MED-02: exact projection and replay

Status: historical first slice; repository-owned implementation subsequently
completed and moved to `in_review`. Acceptance-bearing empirical evidence remains
missing.

## Plan

- [x] Implement and test an offline exact-string JSON projection API, with source
  and transformation-code hashes, per-field source locators, explicit clock
  fields, deterministic snapshot identity and a recomputing verifier.
- [x] Integrate custody/safety evidence-binding mechanics using fictional inputs;
  real public B0-to-B1 and reviewed Silver partition rebuilds remain unperformed.
- [x] Add append-only correction history, ordered supersession and cycle checks,
  bitemporal intervals and partition-level replay verification.
- [ ] Complete layer qualification and return acceptance evidence through the
  existing Conductor process. This slice cannot satisfy the full work item.

The completed repository implementation and its limits are recorded in
`medallion-lineage-history-plan-2026-08-31.md` and merged PR #137. On 2026-09-01
the work item moved from `in_progress` to `in_review`: this prevents autonomy from
repeating completed synthetic implementation while retaining
`E-MEDALLION-LINEAGE-REPLAY` as missing until an empirical public B0 rebuild and
review actually exist.

## Options and recommendation

Start with an explicit one-to-one string-field projection. It can preserve exact
labels and values while testing provenance and deterministic replay without
unseen editions, source access or semantic inference. It is deliberately less
capable than a generic transformation engine.

Defer numeric conversions, expressions, joins and format-specific extraction:
these require separate contracts and tests. Do not reuse failed G2 outputs as
fixtures or infer source dates to populate the clock fields.

## First-slice contract and boundaries

The new, separate `gfjd-json-projection-v1` contract binds a source SHA-256,
explicit output-to-source field mapping, nullable `valid_from` and required
`recorded_at`. Non-null timestamps must be explicit UTC instants. These are point
fields, not a claim of complete bitemporal history or authoritative source dates.

Only a nonempty UTF-8 JSON array of string-valued objects is supported. Duplicate
keys, absent mapped fields, invalid shapes, digest mismatch and size/row/cell
budget excess stop with an error. No coercion, fuzzy matching or default date is
permitted. Mapping order cannot affect the result; source row order is retained.

Every output value binds its source JSON pointer and exact source bytes. A
receipt binds the contract, current implementation module, output and field
lineage. Verification recomputes the entire result using the same implementation
bytes, not caller-supplied success flags or self-consistent result hashes.

The API does no network access, acquisition, file writes, publication or layer
promotion. Its candidate receipt always has `promotion_authorized=false`.
It is not a rights, safety, disclosure, custody or source-truth assessment.
Synthetic tests prove mechanics only; external evidence remains required for
the full work item. Inputs must already have passed applicable handling controls.

## Contingencies

Missing or conflicting source bytes produce no replay result and remain subject
to metadata-only/quarantine handling upstream. Preserve historical outputs;
changed inputs or contracts yield a new snapshot identity. Implementation
changes invalidate current-code replay of old receipts; retain the original
implementation for historical verification rather than rewriting old evidence.

## Implementation evidence

Implementation commit: `08fe50a` (module and 30 synthetic regression cases).
The focused suite passes. Tests cover exact strings and row order, pointer
escaping, explicit clocks, malformed contracts and sources, duplicate keys,
byte/row/field/cell budgets and receipt tampering, including false-versus-zero.
This is supporting implementation evidence only. WI-G4-MED-02 remains in
progress; its acceptance-bearing lineage/replay evidence remains incomplete.
