# WI-G4-MED-06 — shared medallion schema compatibility

Status: accepted; repository-owned technical compatibility only.

## Objective

Adopt the immutable cross-repository medallion v1–v4 contract family used by
Global Medicines Atlas and Archive Govt NZ without changing GFJD's native layer
meanings. Provide byte-pinned schemas, portable canaries, offline validation,
explicit semantic projection, packaging and drift detection.

## Authoritative inputs

- Global Medicines Atlas remote commit
  `0190183f6b313ad21746c5b15b7cf4bd7153085c`, inspected 2026-09-03.
- Archive Govt NZ remote commit
  `dcc8f37f5642fc6b4337c49bd482b126325e6b6c`, inspected 2026-09-03.
- The v1–v3 schemas are byte-identical across both repositories:
  - v1 `4c1ee81b026c64cf8f962d602cd64441a4a023c132346349c8b27dab0981f10e`;
  - v2 `bf31ee62a3566a8fde512748b79f644e0fab760f60924e4eb9d510d3c1ef6f8a`;
  - v3 `5d0f472b124701ef66dcc1a5c39670826b8e95e5faf576cc394a3cd22df9419c`.
- Global Medicines Atlas v4 federation schema
  `ac28485a70e0853266e4c140f9a07cd557eb27816b0b408b9bf2927a4cffacec`.
- GFJD's accepted native B0/B1/Silver/Gold/Platinum and quarantine contracts.

## Decision and mapping

Recommended and adopted: compatibility projection, not layer renaming. GFJD B0
source bytes map to shared `bronze_b2` raw evidence. GFJD B1 and Silver are
different native stages within the shared `silver` class and remain
distinguishable through v2 field-lineage records; their internal transition is
not misrepresented as a v1 promotion. Gold and Platinum map to the corresponding
shared classes but retain GFJD's owner-acceptance and release gates.

Renaming GFJD to GMA's B0/B1/B2 vocabulary would simplify labels but break
accepted native contracts and historical evidence. Schema-only vendoring would
be smaller but would not enforce the v1 and v4 semantic rules. The compatibility
projection preserves both systems and fails closed on ambiguity.

## Acceptance criteria

1. Root `contracts/medallion/v1` through `v4` are byte-identical to the pinned
   upstream schemas and portable fixtures.
2. Installed GFJD packages contain exact schema bytes and detect copy drift.
3. An offline validator applies Draft 2020-12 format checking, shared v1
   promotion semantics and complete v4 identity/lifecycle/recovery semantics.
4. A versioned explicit GFJD mapping prevents direct B0/B1 aliasing and records
   the non-representable native B1-to-Silver boundary.
5. Positive, negative, mutation, no-network and packaging tests pass.
6. The implementation is included in the source manifest, generated Conductor
   status, implementation ledger and full repository quality gate.

## Plan

- [x] Inspect current remote partner revisions and reproduce schema digests.
- [x] Add portable v1–v4 schemas, documentation and positive/negative canaries.
- [x] Begin with a failing import test for the GFJD compatibility validator.
- [x] Implement packaged schema verification, validation and explicit mapping.
- [x] Add a deterministic retained compatibility receipt and independent verifier.
- [x] Update the executable Conductor work/evidence records and implementation status.
- [x] Run focused review and installed-package/reproducible-distribution inspection.
- [x] Run the full autonomous closeout gate (2,139 tests twice, 85.05 percent
  coverage, exact federation rehearsal and reproducible package/release builds).
- [~] Deliver a signed, reviewed PR with exact-head CI and history-preserving
  merge.

## External boundary

This track establishes repository-owned technical compatibility only. It does
not prove live partner interoperability, actual source or Parquet bytes, remote
retrieval, partner registration, rights, maturity, Gold promotion, publication,
release or G2–G6 acceptance. Those facts remain in WI-G4-MED-02/04/05 and their
existing gates.

## Contingencies

- Any upstream byte drift requires a new reviewed contract version or explicit
  pin update; immutable v1–v4 bytes are never silently replaced.
- A GFJD concept that has no lossless shared representation remains native-only
  with an explicit mapping limitation.
- A schema-valid but semantically contradictory record is rejected.
- Missing live evidence leaves interoperability unverified without blocking
  completion of this repository-owned compatibility implementation.
