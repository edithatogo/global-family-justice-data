# Actual-configuration federation metadata drafts

Status: in progress, repository-owned preparation within WI-G4-MED-05.
Baseline: signed main `de3455342595535b0054425aa615162c9e94a79c` (PR #147).
Full validation passed; this slice does not complete factual federation.

## Options, recommendation and contingencies

Generate usable, incomplete metadata from the supplied actual configuration,
without routing it through a fictional replay scope. This is the recommended
additive API: it preserves existing bundle no-copy contracts and keeps missing
facts visible. Another fictional example would exercise machinery but would not
show the actual configuration's gaps. Creating published-looking distributions
would incorrectly imply evidence that is absent.

Use only the two pinned profiles actually assessed here: RO-Crate context and
GFJD Croissant declaration profile. Existing DCAT, OpenLineage, PROV and partner
APIs remain unchanged and are not silently claimed as draft coverage. Invalid or
conflicting configuration fails closed; missing factual metadata produces an
incomplete draft, not invented values. No network or source content is required.

## Frozen API and output contract

`prepare_config_metadata_draft(estate_inputs, standards)` returns a deterministic
dictionary of artifact bytes. Its verifier takes the same inputs and artifacts
and regenerates the exact set and every byte. `estate_inputs` is the existing
estate compiler's exact four TOMLs and frozen policy bytes. Regenerate that
estate first; do not accept a caller's precomputed estate manifest.

The standards bank contains exactly `ro-crate-1.3-context.jsonld` and
`gfjd-croissant-profile-v1.json`, each no more than 256 KiB and matching the
existing pinned digests. No resource lookup or loader fallback is available.

Return all eight regenerated estate artifacts under `estate/`, ten generated
metadata documents (one Croissant and one RO-Crate draft for each of the five
dataset roles), `metadata-assessments.json`, `declaration-report.json`, README
and `draft-manifest.json`. Explorer remains a Space declaration in the report;
do not fabricate a Dataset or source/edition/release object for it.

Dataset names start with `Draft:` and use the exact reconciled configured
repository identifier. Descriptions explicitly say prospective preparation and
derive only from the role and declared payload policy. Croissant uses the exact
profile context/type/version scaffolding and no factual URL or identifier.
RO-Crate uses the pinned context, local root and descriptor scaffolding.
Scaffolding links are profile targets, not verified conformance claims.

Omit dataset publication dates, licences, creators, publishers, distributions,
file hashes/sizes/formats, record sets, release versions and runtime lineage.
Do not infer them from a namespace, software licence, build time or matching
bytes. Desired hosted links stay in the declaration report, labelled desired
and requested false; none is treated as observed publication.

The report covers every role, retains the regenerated estate declarations and
diagnostics, and lists missing publication, licensing, creator/publisher,
content, release, lineage and receipt facts. Explorer has no dataset-profile
assessment. Include field-level provenance for generated name and description:
exact estate-manifest hash plus JSON pointers to the reconciled role fields,
the derivation rule, and the full bound original input map. Profile scaffolding
is separately bound to its normative/profile bytes. This is configuration
provenance, never source/edition provenance or ownership authentication.

The manifest binds every input, profile and generated artifact plus compiler
and component fingerprints. Reports retain false authority and unverified
publication, source truth, ownership, custody, full conformance, accepted Gold,
maturity and gates. Only implementation/helper fingerprint reads are permitted.
Fixed exceptions must not disclose rejected input contents. No clock, network,
filesystem source loader, execution, registration or publisher is invoked.

## Ordered work

- [x] Add the generator and exact verifier with meaningful negative-first tests.
- [x] Validate all six roles, real configured identifiers, ten incomplete
  documents, exact provenance, no inferred facts, wrong/missing/extra inputs,
  rehashed forgeries, determinism and no network.
- [ ] Preserve a generated actual-configuration snapshot after the compiler's
  signed source freeze. Bind its source commit and input/artifact hashes; index
  it as supporting preparation only. Historical snapshot tests verify retained
  bytes and scope, not equality with a later compiler. No input source payload
  or claimed factual acceptance is included.
- [ ] Role-separated advisory review; full gate; signed reviewed PR; all
  required exact-head CI; history-preserving merge and local cleanup.

Canonical ownership declarations and the remaining standards/partner coverage
audit follow this slice. Actual registration/publication and acceptance-bearing
evidence remain separately pending. No new owner decision is needed for this
offline implementation.

## Implementation ledger

The generator returns 22 bound artifacts from the actual configuration, including
ten explicitly incomplete dataset-profile documents. Explorer remains a Space
and its missing licensing fact is labelled space-content licensing, not dataset
licensing. The missing-profile test failed against the initial stub before
implementation; all 24 focused tests now pass (0.98s). Ruff and module mypy pass.
The 36 autonomous-context tests also pass. The retained-snapshot integrity test
initially failed because its receipt was absent; preserve the generated files
only after the signed compiler freeze.

Role-separated read-only advisory review found no actionable issue in the
compiler, field provenance, missing-fact handling or exact verifier. It did not
execute tests or certify factual evidence. The snapshot, complete local gate,
hosted review/CI and delivery remain pending at this compiler freeze.
