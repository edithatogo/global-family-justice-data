# Canonical responsibility declarations and federation coverage audit

Status: in progress; repository-owned preparation within WI-G4-MED-05.
Baseline: signed `7f55714e2f5c5a288c5eb322c99f869ca035c4b0`, merged PR #148.
The complete local gate and all 17 hosted checks passed. This phase does not
establish legal ownership, partner registration, zero-copy custody or acceptance.

## Recommendation, options and limitations

Implement one bounded ownership/reference declaration checker, then audit every
federation requirement against existing code and evidence. A scope-bound sidecar
can detect contradictory declarations without assigning ownership from a GFJD
URN or matching bytes. Unchecked prose is simpler but cannot fail on conflicts.
Actual ownership authentication or transfer is a different operation and is not
enabled. Keep all partner-native identifiers unchanged and unrequested.

The archive partner's pinned owner/epoch/lease implementation applies to its
named repositories, not a GFJD transfer. GMA producer metadata is not an ownership
attestation. Do not import either vocabulary as an accountable GFJD authority.
If a relationship is unknown, record unresolved rather than guess a target.

## Frozen contract

`assess_ownership_references(raw, expected_sha256, scope_raw,
expected_scope_sha256, metadata_bank, estate_inputs)` returns a deterministic
report. The verifier takes the same arguments and a report and recomputes every
field, rejecting boolean/integer aliases. First regenerate the existing exact
reference reconciliation; no caller report is trusted.

Envelope keys: contract_version (`gfjd-canonical-ownership-declarations-v1`),
state (`preparation`), scope_sha256 and objects. Require exact lower-case SHA-256,
at most 1 MiB, existing strict JSON limits and one record per scoped object
(1–100); duplicates, omissions, extras and unknown keys fail closed.

Object keys: object_id, canonical_id, content_sha256, relationship and target.
The first three fields must exactly match the reconciled scope, including null
content hashes. relationship is canonical, reference or unresolved. target is
null or exactly owner_id and native_object_id. owner_id is gfjd or an explicitly
selected partner ID. native_object_id is nonblank opaque text up to 512 characters
under shared strict-JSON controls; preserve it byte-for-byte and never resolve it.

- canonical requires owner_id gfjd and native_object_id equal to the scoped
  canonical_id. This is declared canonical responsibility, not authenticated or
  legal ownership.
- reference requires a selected partner owner_id and a supplied native identity.
  The GFJD canonical_id is a local reference handle, not a newly owned copy.
- unresolved requires target null. No target or canonical responsibility is
  inferred from a hash, namespace, URI shape or metadata field.

Multiple explicit reference handles may name the same partner/native target.
Reject different non-null content hashes for that target. A null alongside a
known hash remains an explicitly missing content binding; do not fill it in.
Equal hashes across different native identities do not merge identities or
establish semantic equivalence. Report shared-target groups and all unresolved
and missing-content IDs. Sort output records/groups deterministically, while
retaining the original envelope and scope byte hashes (reordering input changes
those hashes and is not falsely called byte-identical evidence).

Bind input, scope, estate and metadata hashes plus compiler/helper fingerprints.
Return no input metadata/source payloads. Report declaration_consistency only;
authenticated ownership, legal rights, transfers, partner acceptance, observed
custody, semantic equivalence and estate-wide zero-copy remain unverified/false.
All authority flags remain false. No network, source loader, partner mutation,
publisher or runtime executor exists. Fixed exceptions do not disclose rejected
input content. Only compiler/helper fingerprint reads are performed.

## Ordered work

- [x] Checker/verifier and meaningful negative-first tests.
- [x] Exact coverage, target/relationship mismatch, unselected partner,
  contradictory shared-target hashes, retained nulls, distinct identity/equal
  bytes, duplicate objects, bounds, forged reports and no-network tests.
- [x] Requirements-to-evidence coverage matrix covering estate roles, canonical
  declarations, standards profiles, lifecycle/replay, Parquet references and
  partner boundaries. Identify concrete missing cross-contract guards only.
- [~] Role-separated advisory review; full validation; signed reviewed PR;
  exact-head CI; history-preserving merge and local cleanup.

The audit must distinguish completed limited preparation, unfinished broader
technical coverage and missing factual evidence. In particular, DCAT vocabulary
closure, general JSON-LD/full standards validation and partner record semantics
are not silently complete. Actual registration, authenticated ownership, rights,
verified payloads, remote retrieval and accepted Gold remain separate. WI-G4-MED-05
and E-FEDERATED-MEDALLION-REGISTRY retain their factual states. After this audit,
continue other eligible repository-owned preparation without claiming federation
acceptance or waiving the remaining requirements.

## Implementation and audit ledger

The checker and exact verifier implement the frozen declaration-only contract.
The missing-coverage test failed against a stub before implementation. All 42
ownership tests pass; combined ownership, reference and autonomous-context
validation passes 106 tests (3.26s). Ruff and module mypy pass.

`docs/engineering/federation-coverage-matrix-2026-09-01.json` maps ten requirement
groups to 61 existing implementation, test and retained-evidence file references.
It explicitly records unfinished broader technical coverage as well as missing
facts; neither is reclassified as completed. Acceptance remains false.

Role-separated read-only review found no actionable issue in the implementation,
completed tests, matrix or frozen contract. No additional cross-contract guard
is justified by this bounded scope. Review is advisory only and did not certify
factual ownership, standards conformance or gate acceptance. Full local gate,
exact-head hosted review/CI and delivery remain pending at this source freeze.
