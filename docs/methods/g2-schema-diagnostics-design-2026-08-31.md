# Structural diagnostics before a future metadata contract

Status: repository-only, fictional-input-tested design; not a publisher schema,
execution packet, campaign, authorization or G2 evidence acceptance.
Plan: `g2-schema-redesign-plan-2026-08-31.md` (plan commit `6ffd559`).

## Implemented boundary

`gfjd.metadata_shape.inspect_shape` is a pure bytes-to-diagnostics function.
It has no filesystem, transport, subprocess, command-line or campaign interface.
It is not connected to either the failed historical evaluator or the existing
monitor. Neither evaluator nor any prior receipt, audit or bundle was changed.
It has been exercised only with fictional JSON, never the failed raw response.

Outputs contain input size/fingerprint, JSON type counts, pooled field-type
counts, allowlisted field names, fingerprints of unknown names, missing-field
counts, row/container counts and fixed failure codes. All scalar contents are
omitted: titles, locators, timestamps, formats, numeric values and booleans.
The structural counts are measurements of shape, not source statistics.
Fields are pooled across all object levels, not assigned semantic paths.

`inspection_complete=true` means structural traversal completed within limits.
It does not mean valid publisher schema or complete source enumeration.
`enumeration_complete=null`, `eligibility=not_assessed`, and every authority
flag remains false, even for an apparently ideal fictional input. No hypotheses
or selected candidates are emitted. Partial summaries are discarded on limits.

## Resource and disclosure limits

- Pre-parse bound: 2 MiB; oversized input is not hashed or parsed.
- Post-parse inspection bounds: depth 16, 10,000 visited values, 128 members per
  object and 1,000 elements per array. `json.loads` materializes the byte-bounded
  input before these checks; they are not parser-time allocation limits.
- Duplicate keys, invalid UTF-8/JSON, non-finite numeric values and excessive
  parser recursion return fixed incomplete-result codes without exception text.
- Unknown keys at every level use domain-separated SHA-256 with surrogate-safe
  encoding. Neither unknown-name fingerprints nor the whole-input fingerprint
  are anonymization; low-entropy information can be guessed.

Actual future diagnostic retention/publication remains separately governed.
This implementation does not authorize receiving arbitrary data or processing
personal, sensitive, case-level or source content.

## Evidence and options

The failed receipt proves schema/enumeration rejection but retains no unexpected
key names. We cannot infer them from its nine locators or its response digest.
The existing monitor accepts extra root keys but performs eligibility evaluation;
substituting it would not establish schema or field semantics.

Role-separated agent `metadata_schema_design_advice` recommended a separate
diagnostic instead of documentation alone or relaxing the old evaluator.
Trade-off: diagnostics improve error visibility but cannot establish the values
or meanings of total/start, format, timestamp, pagination or publication identity.
Those require authoritative interface evidence, not a more permissive parser.

No blocking issue remained in the synthetic-only code review. The reviewer
requested the parser/inspection budget distinction and boundary/fingerprint
tests; these are included. Advice is not independent assurance.

## Next useful work and contingency

Any future schema-discovery packet must prospectively bind an exact official
endpoint, safe receipt fields, limits, retention, roles and terminal stops.
The discovery stage must end before selection and returned-link access.
Authoritative documentation then establishes required/optional/prohibited fields
and their semantics before a separate successor evaluator is frozen.

No exact external packet is offered against missing interface evidence here.
If safe diagnostics are insufficient, retain uncertainty and request narrowly
scoped authoritative documentation access; never log extra values opportunistically.
Existing authorized future-edition monitoring remains unchanged. G2 stays blocked.
