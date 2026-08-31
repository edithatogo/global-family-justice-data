# WI-G4-MED-05 — offline federation preparation

Status: in progress, repository-owned preparation only. Factual federation,
partner registration and publication remain separately required. Work follows
the approved medallion autonomous continuation queue, one track at a time.

## Baseline and recommendation

Start from signed main `048c4bd5d3172b989bfbc3b8033deab8d8e5a74f`, PR #139.
Its full local gate passed; all 1,031 source manifest entries verified before
changes. The non-mutating bootstrap plan completed without warnings. No remote
configuration was applied. The preceding estate plan records exact delivery.

Recommended: implement bounded, offline federation preparation in reviewable
phases. Bind normative artifacts and implementation versions; distinguish
structural validation, semantic profile checks and independently supplied
factual evidence. Synthetic positive fixtures exercise machinery, not real
publication dates, dataset licences, custody or accepted Gold.

Options and trade-offs:

- Selected: pinned offline standards validation plus deterministic metadata
  generation, explicit missing-fact results and reference-only partner drafts.
  This costs more than prose but is reproducible and avoids remote resolution.
- Internal JSON alone is simpler, but cannot establish the required standards
  compatibility. It is useful only as an explicitly named preparation contract.
- Immediate partner writes or publication would create external evidence but
  are outside this preparation scope and depend on existing factual gates.

## Ordered phases

- [~] Standards foundation: primary-reference inventory, supplied hash-bound
  artifacts, strict bounded parsing and offline OpenLineage 2-0-2 schema
  validation. Unknown references and unsupported facet schemas fail closed.
  Do not treat base-schema success as complete lineage or standards acceptance.
- [ ] RDF/JSON-LD preparation: DCAT-AP, RO-Crate and PROV-O using offline
  normative contexts/shapes where available; Croissant profile preparation with
  explicit validation coverage. No homegrown subset is full conformance.
- [ ] Canonical identity, six-role estate and zero-copy reference reconciliation;
  prospective partner/registry records without cross-repository mutation.
- [ ] Deterministic draft bundle, exact recomputation and conspicuously fictional
  positive/negative rehearsals. Actual drafts preserve missing factual fields.
- [ ] Conductor supporting evidence, advisory review, full validation, reviewed
  signed PR delivery, exact-head CI, history-preserving merge and local cleanup.

Each coherent phase may have its own PR. Completing a foundation phase does
not complete WI-G4-MED-05 or authorize starting a different track early.

## Standards selection and advisory findings

Primary technical documentation research is implementation work, not court
source discovery. The selected versions are:

- [DCAT-AP 3.0.1](https://semiceu.github.io/DCAT-AP/releases/3.0.1/), SEMIC
  Recommendation, CC BY 4.0. RDF provider and controlled-vocabulary requirements
  extend beyond a JSON structure check; official SHACL coverage must be stated.
- [RO-Crate 1.3](https://www.researchobject.org/ro-crate/specification/1.3/index.html),
  Recommendation dated 2026-06-22. Documentation is Apache-2.0; context and
  examples are CC0. Root metadata requires publication and licensing properties;
  a build timestamp or software licence cannot supply unknown dataset facts.
- [Croissant 1.1](https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html),
  published 2026-01-29, specification CC BY-ND 4.0. Reference the unchanged
  specification; the vocabulary is not a full validation schema. Role-separated
  advice identified missing creator, publication and licence facts in real drafts.
- [PROV-O](https://www.w3.org/TR/prov-o/): distinguish entity/activity/agent
  relationships and never fabricate actual execution or accountable authority.
- [OpenLineage 2-0-2](https://openlineage.io/spec/2-0-2/OpenLineage.json),
  JSON Schema 2020-12, Apache-2.0 implementation repository. Base schema permits
  lifecycle-incomplete RunEvents and extension facets; enforce a separate bounded
  preparation profile, not an unsupported full-lineage claim.

Advisory input recommends JobEvent/DatasetEvent for prospective metadata, not
fabricated RunEvents. Event time describes a metadata event, never source
publication. Full run lifecycle validation belongs to the later lineage phase.

## Foundation contract and controls

Before code, freeze this scope: consume exact supplied OpenLineage schema bytes
at upstream commit `e47a7d5a7d2e6887fe5ed737754f3f03a3721b08`, SHA-256
`69f68bee00b9beac88a87059c0102410e7bb05f3f43c46d02a0409831eceb0d2`.
Preserve the upstream schema unchanged with its licence notice. Validation has
no filesystem fallback, network resolver, source loader, executor or uploader.
Strict JSON rejects duplicate keys, non-finite numbers, unsafe control text,
excessive bytes, depth or collection count. Use a resolver with an explicit
local-only resource registry and enabled format checking. No arbitrary caller
schema, unknown remote reference or unvalidated facet is accepted.

The foundation API returns structural/profile findings and false factual and
authority claims. It accepts only design-time JobEvent/DatasetEvent in this
phase; RunEvent is explicitly unsupported, not silently reinterpreted. Tests
cover schema tampering, missing bindings, malformed dates, missing identifiers,
duplicate keys, resource bounds, unsupported types/facets and network denial.

No new runtime dependency is needed for the first phase: use the locked
jsonschema/referencing libraries. Any later RDF dependency must be selected
from primary documentation and locked before use.

## Contingencies and boundaries

If a standard has no complete machine-readable validator, record exactly which
profile checks run and retain unverified full conformance. If mandatory factual
metadata is absent, emit a pending preparation result rather than invent it.
Unknown normative bytes, context, reference or schema version stops validation;
there is no automatic network fallback or silent upgrade. No source or partner
locator is requested by validation. Avoid credentials, personal data and source
payloads; preserve earlier failed evidence. Actual publication, registration,
rights, custody, Gold, maturity and G2–G6 acceptance remain unchanged. Group any
genuine authority/factual gap at the end of the authorized queue.

## RDF advisory research for the following phase

The role-separated RDF adviser identified the specification-linked
[DCAT shape directory](https://github.com/SEMICeu/DCAT-AP/tree/729eddfc176d0afee5850ade6528f96f72579412/releases/3.0.1/html/shacl).
Use `html/shacl`, not the different sibling generated `shacl` directory.
Core `shapes.ttl` is 20,619 bytes, SHA-256
`7fe9815e0f32b10f5cbce74fa6ccd0290aae3ef9e5080fb84e2d8093eb984d1d`;
`range.ttl` is 12,490 bytes, SHA-256
`24d3bfd0fa17a3d0e877c9ebb91c8174124e5038538e1bf081b2cb679ad0f1b2`.
These are research bindings, not yet vendored or executed in this phase.

Upstream imports include mutable vocabularies. Never enable automatic imports
or invent vocabulary-membership triples. Pin a local closure separately and
report any missing controlled-vocabulary validation. Prefer explicit bounded
Turtle/N-Triples, disabled imports/advanced rules/JavaScript and a locked engine;
library flags alone do not provide operating-system isolation. These limitations
must remain visible in later validation reports.

PROV-O representation is distinct from full
[PROV-CONSTRAINTS validity](https://www.w3.org/TR/2013/REC-prov-constraints-20130430/).
Do not label a small application profile as full constraint validation or
infer actual activities from planned transformations. The advisers' findings
guide implementation; neither is independent specialist assurance or acceptance.

## Implementation ledger

- `ecd3671`: start this preparation track and close out the verified estate PR.
- `3998ea3`: retain unchanged OpenLineage schema/licence with exact upstream
  attribution and package-resource declarations. Three resource tests verify
  byte identity, schema identity and package access. The upstream root tree was
  checked for a NOTICE file; none was present at the pinned commit.
- `5ace634`: bind this plan in autonomous context; preserve the planned
  publication-bearing work item and acceptance evidence. The combined asset
  and autonomy suite passes 39 tests (1.50s), including explicit WI-G4-MED-05
  exclusion from executable publication actions. `uv lock --check` passes;
  no dependency version changed.

- `1a021a1`: implement `gfjd.federation_openlineage.validate_design_event`.
  A meaningful failing test first demonstrated missing schema binding. The first
  validator implementation then exposed that optional format dependencies were
  absent: three invalid-date tests failed to reject their inputs. Explicit local
  format checks now reject those dates without changing the normative schema or
  installing optional packages. All 43 validator tests pass; combined with the
  asset/autonomy tests, 82 pass (3.43s). Lint, formatting and strict module typing
  pass after the formatting correction in this commit.

## Foundation API and precise validation scope

`validate_design_event(event_bytes, schema_bytes)` takes both inputs explicitly
and returns a deterministic report or raises `FederationError`. Callers may
read the packaged `gfjd/federation_specs/openlineage-2-0-2.json` as a resource,
but the validator itself performs no filesystem or network access. The report
binds event and schema bytes; its contract version identifies this bounded
profile. Bind repository commit and dependency lock separately in any enclosing
execution receipt. This function does not observe actual metadata events.

Supported inputs are design-time JobEvent and DatasetEvent only. Unknown fields,
runtime fields, nonempty facets and absent/blank identifiers are rejected.
The profile deliberately narrows producer identifiers to HTTPS DNS-form URLs
without user information and timestamps to explicit known offsets without leap
seconds. These restrictions are GFJD preparation limits, not assertions that
the upstream standard prohibits other representations. No locator is requested.

JSON Schema validation uses the complete unchanged upstream schema, enabled
format checking and an explicitly local registry. Independent profile checks
reject unsupported structures even when the broader base schema permits them.
Success reports `schema_validated: true`, `profile: design_event_only`, and
`factual_evidence`/`full_conformance: unverified`; all authority flags are false.
It does not inspect dataset content, grant rights or certify safe publication.

The foundation review and complete delivery checks remain in progress. Later
metadata generation, RDF checks, partner contracts and full federation work
remain unchecked above. No result is registered as factual acceptance evidence.

## Foundation review correction

The role-separated code reviewer found that chained validation exceptions could
print the rejected event in a normal traceback. Two new regression cases first
failed (schema-invalid fictional input and invalid UTF-8). Suppress the original
exception chain in ordinary rendering; retain the fixed public-facing error.
This does not claim that an introspective debugger cannot inspect process memory.

The initial full local run at `99d3d1d` was intentionally interrupted to apply
this correction and is not a successful validation. Its log is retained locally;
the corrected commit requires a new complete run and exact-head hosted checks.
