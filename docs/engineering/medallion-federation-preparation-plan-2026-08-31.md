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
