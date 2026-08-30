# Medallion validator hardening — 2026-08-30

## Plan and bounded implementation

Before implementing `WI-G4-MED-02` lineage and replay, strengthen its accepted
layer-contract prerequisite against malformed JSON field types. The baseline
`make check` passed with 429 tests, but direct adversarial probes found uncaught
exceptions and invalid ordinal acceptance.

Implemented corrections:

- Reject nested, non-string or blank required-evidence names before using them
  as set members or dictionary keys.
- Reject non-object quarantine contracts with an explicit validation error.
- Require actual integer ordinals; booleans and numerically equal floats are
  not valid ordinals.
- Reject non-string layer identifiers before dictionary lookup, including on
  the promotion path.
- Ensure structurally invalid loaded contracts raise `MedallionContractError`
  rather than leaking incidental `TypeError` or `AttributeError` exceptions.

Sixteen regression cases first failed against the previous implementation; all
23 medallion tests then passed, including the seven existing valid-promotion,
quarantine, missing-evidence and digest-drift cases. This is validation hardening,
not a change to the approved canonical layer sequence or evidence fields.

## Options, rationale and contingencies

**Implemented recommendation:** reject invalid types at the validation boundary.
This gives callers a stable fail-closed result and preserves valid records.
It is a small prerequisite correction before replay can depend on this API.

Coercing malformed values would accept ambiguous contracts; catching every
exception at the outer CLI would obscure the specific validation error. Neither
alternative is used. Existing malformed records remain invalid and require
correction at their source; no sealed evidence is repaired by this change.

## Remaining work

`WI-G4-MED-02` remains planned. Public field lineage, bitemporal snapshot identity,
ordered corrections, acyclic supersession and deterministic B0-to-B1/Silver
replay still need their own implementation and evidence. These regression tests
do not establish source truth, public custody, layer maturity, rights clearance,
G2/G4 acceptance, publication or release readiness.
