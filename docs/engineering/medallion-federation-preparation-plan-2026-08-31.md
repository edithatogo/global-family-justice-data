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

- [x] Standards foundation: primary-reference inventory, supplied hash-bound
  artifacts, strict bounded parsing and offline OpenLineage 2-0-2 schema
  validation. Unknown references and unsupported facet schemas fail closed.
  Do not treat base-schema success as complete lineage or standards acceptance.
- [~] RDF/JSON-LD preparation: DCAT-AP, RO-Crate and PROV-O using offline
  normative contexts/shapes where available; Croissant profile preparation with
  explicit validation coverage. No homegrown subset is full conformance.
- [~] Canonical identity, six-role estate and zero-copy reference reconciliation;
  prospective partner/registry records without cross-repository mutation.
- [~] Deterministic draft bundle, exact recomputation and conspicuously fictional
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
Initially these were research bindings; they are now packaged and executed as
recorded under DCAT implementation and advisory review below.

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

Foundation delivery is complete as recorded below. Later
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

## Foundation delivery closeout

PR #140 merged at signed commit `033a592511d0c2fd8afc94627097e4b5e960a390`
on 2026-08-31T14:03:57Z. The reviewer confirmed the traceback correction resolved.
All 17 exact-head hosted checks passed. Full local validation exited zero:
1,258 tests passed twice (121.87s and 119.57s), reported coverage 82%; package,
restore, bootstrap, wheel/sdist and release reproducibility checks passed. The
built wheel also contained the exact pinned schema and licence hashes.

The earlier hosted coverage job timed out while obtaining a Codecov OIDC token;
the corrected head passed that upload without changing or disabling controls.
Copilot review was unavailable because of quota; the role-separated repository
review and its correction are recorded, not mislabelled as a Copilot success.
Integration preserved history and cleanup left one local branch/worktree.

This completes the foundation phase only. The real federation registry evidence
remains missing. No source data, publication, rights or gate state changed.

## RDF phase preparation — 2026-09-01 local date

Continue from the verified foundation commit above. The source manifest verifies
all 1,038 entries and the non-mutating bootstrap plan completed without warnings.
The plan generated at 2026-08-31T14:05:36Z applied no remote changes.

First implement DCAT-AP base/range SHACL validation over bounded supplied RDF,
with the exact two upstream artifacts identified above. Pin the validator and
transitive dependencies; explicitly disable automatic imports, remote SPARQL,
JavaScript and advanced rules. Validation must not accept arbitrary caller shapes
or silently load missing vocabularies. Mandatory controlled-vocabulary closure
remains separately pending until its exact local inputs exist.

Options: pinned local SHACL is recommended for reproducible structural checks;
custom field tests alone would not execute the normative shapes; unconstrained
RDF/JSON-LD parsing would introduce implicit network/file access. Decide the
bounded engine interface after reviewing its logging and loader paths. Suppress
untrusted-input diagnostics in ordinary reports. Use fictional graph fixtures,
negative cardinality/type tests, malformed and oversized inputs, no-I/O tests,
and exact normative-byte binding. Do not claim an operating-system sandbox from
Python flags or profile checks.

RO-Crate follow-on context is pinned to release tag `1.3.0`, commit
`22fbd7e098ccd2839c80967e363a2201528a2efe`, path
`docs/_specification/1.3/context.jsonld` in the official ResearchObject/ro-crate
repository. The inspected context is 196,942 bytes, SHA-256
`5a3df1a43185501db4d45cdde5a478c57eeb1d673eedfe400488fc4c4b21dd91`.
It contains 3,069 context terms; do not confuse it with the draft context or
silently truncate it to ordinary data-input limits. It is not yet vendored here.

Croissant reference-library research at commit
`401f6fff81db26a49c0d1704f02bffc4e4fa8fe2` found implicit JSON-LD loader paths and
optional warnings for some fields required by the specification. Therefore its
successful static analysis alone cannot establish full conformance. A later
explicit GFJD profile must expose its partial coverage; any reference-library
execution needs pinned dependencies and actual I/O restrictions, not a presumed
metadata-only mode. No Croissant library or source-data loader has been run.

## DCAT adapter contract freeze

Use `pyshacl==0.40.1` and a locked RDFLib 7.x dependency. The reviewed direct
`Validator` API requires `DataGraph.from_rdflib(graph)` in this version; pin and
test that adapter rather than silently migrating its implementation interface.
Provide an isolated non-propagating logger. The public convenience entrypoint
installs stderr logging and additional loader/global setup; it is not needed.

Data input is a deliberately restricted N-Triples profile: absolute ASCII HTTP,
HTTPS or URN IRIs; IRI subjects/predicates; IRI objects or safe string/language
literals (optionally explicit XSD string). No blank nodes, escaped IRIs,
unsupported datatypes, imports, embedded shapes, arbitrary source formats or
caller-supplied parser/validator options. Preflight lexical forms before RDFLib
term construction so malformed values cannot reach its diagnostic logger.
Count statements including duplicates before graph insertion. Limit input to
1 MiB, 8,192 characters per line, 4,096 per literal/IRI, and 2,000 statements.
These are input bounds, not an operating-system resource isolation claim.

Freeze two module interfaces:

- `federation_rdf_input.parse_metadata(raw: bytes) -> tuple[Graph, int]`:
  bounded in-memory parsing with no ambient resource lookup; errors use fixed
  messages without exposing input in ordinary tracebacks or diagnostics.
- `federation_dcat.validate_catalogue(data_bytes: bytes,
  shape_bytes: dict[str, bytes]) -> dict`: require exactly `shapes.ttl` and
  `range.ttl` with the frozen upstream hashes; parse those unchanged trusted
  shapes separately. Require one typed catalogue linked to at least one typed
  dataset before evaluating shapes, so empty/untargeted graphs cannot pass.

Run the complete supplied base/range shape sets, with no extra ontology,
inference, imports, JavaScript, advanced rules, rule iteration, remote graph
mode, focus-node or shape filtering. Use maximum validation depth 15. Return
deterministic aggregate constraint/severity counts and input/shape/engine
bindings, never raw literal values or textual validation reports. Invalid
input/bindings stop; validly parsed but nonconforming graphs return a failed
shape result. Controlled vocabularies, full DCAT-AP conformance, factual
provenance, rights, partner registration and all authority remain unverified.

Reviewers recommended this narrow adapter over global logging suppression or
unbounded reference-library loaders. Regression tests must exercise malformed
IRIs/literals, unsupported datatype and import payloads, duplicate-statement
limits, missing targets/properties, wrong ranges, normative tampering, silent
diagnostics and no implicit filesystem/network calls. RDFLib and SHACL success
do not replace the later identity, publication or factual-evidence controls.

## Dependency refresh finding

Resolving the RDF dependencies flagged the existing `zizmor==1.27.0` security
tool pin as yanked. The upstream advisory
[GHSA-f42p-wjw5-97qh](https://github.com/zizmorcore/zizmor/security/advisories/GHSA-f42p-wjw5-97qh)
identifies credential disclosure in debug logging and names 1.28.0 as patched.
The checked-in Make/workflow invocations use explicit `--offline`; the advisory
says this clears credentials before the affected logging. This is evidence of
a vulnerable dependency, not evidence that this repository disclosed a token.

Select the minimal patched pin 1.28.0, refresh the lock and rerun the existing
offline workflow audit. Retaining the yanked version is not recommended; moving
to newer feature releases adds unrelated changes and is unnecessary for this
fix. No credentials are used to reproduce the issue, and no token rotation or
historical non-disclosure is claimed. Preserve all audit severities and controls.

The refreshed offline workflow audit passed with zizmor 1.28.0. The first
complete locked dependency audit also identified pip 26.1.2 as affected by
PYSEC-2026-3721 (CVE-2026-13346). Update the lock to patched pip 26.2.1;
this is a toolchain correction, not evidence of exploitation. A fresh-cache
`pip-audit --strict` over all locked extras then exited zero with no known
vulnerabilities. Preserve the initial failed audit separately from the passing
retest; no severity, dependency or audit exclusion was introduced.

## DCAT implementation and advisory review

The two pinned upstream TTL artifacts are now packaged unchanged with source,
copyright and CC BY 4.0 attribution. RDF parsing and SHACL evaluation were
implemented by separate advisory agents. Meaningful failing tests established
duplicate-statement accounting and rejection of altered normative shape bytes
before implementation. Reciprocal read-only cross-review found no actionable
issues. The combined parser, adapter, asset and OpenLineage suite passed 118
tests (5.48s); focused Ruff and strict mypy checks passed. Full phase validation
and exact-head PR delivery remain pending and are not implied by these checks.

The restricted parser performs complete lexical preflight before constructing
RDFLib terms. The adapter executes the bound base/range shapes and returns only
digests, aggregate counts and explicit unverified factual/conformance states.
Neither adapter grants access, publication, rights, maturity or gate authority.

The first DCAT full run was interrupted (exit 130) after noticing that the
regenerated programme status had not been staged; it is not passing evidence.
Include that generated view before the replacement full run. Its 14 warnings
are risk-review dates that became overdue after 2026-08-31, not DCAT failures.
Preserve them for the grouped remaining-risk review; do not advance review dates
or adjudicate risks merely to remove warnings. Project validation passes with
zero errors and these warnings retained.

### CI review correction: calendar consistency

The first hosted static job failed generated-status parity: Brisbane had
already reached September 1 while CI was still on August 31 UTC. Conductor
used host-local `date.today()` despite emitting UTC timestamps. Two regression
tests first failed when local-calendar access was prohibited. Default validation,
expiry comparisons and newly recorded Conductor calendar dates now use UTC;
explicit `as_of` and supplied dates remain unchanged. A separate regression
retains overdue warnings for an explicit September 1 assessment. The 17 focused
Conductor/clock tests, lint and formatting checks passed after the correction.

The second local full run was interrupted (exit 130) for this code correction,
not accepted as phase evidence. Regenerate the status on the UTC basis and rerun
the entire gate and exact-head CI. The known upcoming risk reviews remain
recorded above; no risk record or review date is altered by this fix.

### Hosted review correction: installed dependency contract

At `68185fa`, all 17 hosted checks passed and full local validation exited zero:
1,331 tests twice (87.81s and 81.40s), 83% coverage. Wheel resource checks also
verified both exact shape hashes. The final hosted review then identified a
distribution mismatch: the RDFLib requirement allowed 7.x versions that the
deliberately pinned runtime engine guard rejects. A new regression failed
against that range. Pin RDFLib to the tested 7.6.0 in package requirements as
well as the lock; do not weaken the guard or imply untested compatibility.
The corrected head requires fresh local and hosted validation before merge.
The two superseded historical preparation sentences identified by the ledger
review have also been clarified; factual work-item acceptance remains pending.

## DCAT delivery closeout

PR #141 merged on 2026-08-31T14:43:31Z at signed commit
`9c56ecf85355de511e63378e450f718a44c6e03d`. All 16 reported exact-head hosted
checks passed and the review thread was resolved after the dependency fix.
Full local validation passed with 1,332 tests twice (102.70s and 60.58s), 83%
coverage, and successful package/restore/reproducibility checks. The built wheel
also verified both normative shape hashes and its exact RDFLib requirement.
History-preserving integration and local cleanup left only main and one worktree.

## Supplied-byte metadata profiles — prospective contract

Continue this same federation track with RO-Crate and Croissant preparation.
The selected option is explicit, closed GFJD representation profiles backed by
the versioned references above, not a claim of full JSON-LD or standard
conformance. General-purpose JSON-LD expansion would enable implicit loaders;
custom profile checks avoid those capabilities but must reject unsupported
representations honestly. Broader interoperability remains a separate phase,
not a silent fallback. No standard or data licence is rewritten by this profile.

Use a shared `federation_metadata` module for strict supplied-byte JSON, fixed
errors and deterministic report helpers. Bound metadata to 1 MiB, depth 16,
10,000 values, 1,000 entries per collection and 4,096 characters per string.
Reject duplicate keys, nonfinite numbers, control/surrogate text and unsupported
JSON-LD contexts. No parser/assessor may read files, fetch identifiers, open
locators, run extraction or emit input values in errors. A context asset is a
separately bound technical artifact, not subject to ordinary metadata limits.

`assess_rocrate(metadata_raw, context_raw)` checks a closed flattened graph:
exact supplied 1.3 context SHA above; descriptor `ro-crate-metadata.json`;
root `./`; unique entity IDs; explicit descriptor-to-root and version links;
supported Dataset, File, Organization and licence CreativeWork declarations;
internal reference integrity and safe relative file paths. Required factual
declarations may be missing in a draft: report deterministic incomplete issues
rather than invent publication dates, licences, names or descriptions. Never
equate a declared licence with rights clearance or a file descriptor with bytes.

`assess_croissant(metadata_raw, profile_raw)` checks a hash-bound GFJD-authored
closed profile referencing, not copying, the Croissant 1.1 specification. Use a
single exact inline context; Dataset metadata and simple FileObject references;
optional flat RecordSets/Fields with explicit distribution/column references.
No FileSet globs, transformations, joins, external/scoped contexts, embedded
records or extraction. Missing creator, licence, publication or distribution
facts remain explicit incomplete issues. Supplied checksums are syntax-checked
declarations, not verified custody. No hosted dataset locator is fabricated.

Both APIs return deterministic digest-bound profile results, explicit coverage,
sorted issue codes, `full_conformance` and `factual_evidence` unverified, and all
authority false. Verification independently recomputes and compares the complete
report. Malformed/binding/unsupported input raises fixed errors; supported drafts
with missing declarations return `profile_incomplete`. Fictional complete and
incomplete fixtures, hostile syntax, context drift, reference substitution and
no-I/O tests are mandatory. Role-separated implementation and reciprocal review
remain advisory; complete local checks and exact-head CI precede merge.

### Profile assets and shared-boundary ledger

- `ef95061` packages the unchanged RO-Crate context and attribution. Exact
  SHA-256 and 196,942-byte length were verified after acquisition from the
  pinned official technical repository. No court-source request occurred.
- `dd2d6b9` adds shared strict JSON/reference/report helpers. Negative tests
  first exposed three URL guard omissions (DEL, repeated fragment marker and
  excessive length); the correction passes all 27 focused tests and strict
  typing. Report authority remains false even for complete declarations.
- Freeze `gfjd-croissant-profile-v1.json` before its assessor at SHA-256
  `e0bcf9bbfcba4101cb7bf53b8b883b137e8ba74db6aa0a2fb0ba21ca89b4ed60`.
  This GFJD-authored configuration references the upstream specification and
  contains the explicit context/field/type limits; it is not a normative schema.

The shared profile accepts explicit `YYYY-MM-DD` publication declarations only;
other valid standard date/time forms remain unsupported by this implementation.
No empty, inferred or current build date fills a missing source publication fact.

### Metadata implementation review

The RO-Crate assessor checks exact File declarations against root `hasPart`,
while permitting a metadata-only crate with no Files. Missing required keys
produce incomplete findings; malformed supplied values, including blank dates
or licence references, fail the profile. External Organization/licence IDs stay
unverified references. The Croissant assessor additionally flags missing dataset
URL, file names and field names, and rejects repeated field names in a RecordSet.
Those three omissions were corrected after failing regression tests. RecordSet
names remain optional in this profile. Content-size checks, complex creators or
licences, general JSON-LD interpretation and data loading remain excluded.

Shared-code review found raw URI brackets were incorrectly accepted. Two tests
first failed; `7c42d57` rejects raw brackets while retaining percent-encoded
forms. Reciprocal assessor reviews found no further actionable findings. The
combined metadata-helper, RO-Crate, Croissant and asset suite passes 113 tests;
formatting, lint and strict module typing pass. Full phase validation, packaged
resource verification and exact-head PR delivery are still required.

Use `assess_rocrate(metadata_bytes, context_bytes)` or
`assess_croissant(metadata_bytes, profile_bytes)` with explicit byte inputs.
The corresponding `verify_rocrate` / `verify_croissant` functions recompute
the complete report and reject changed authority flags or other forged fields.
No caller-provided success field or checksum can replace that recomputation.
`profile_complete` means only this restricted declaration profile; all factual,
full-conformance, custody, publication and acceptance states remain unverified.

## Metadata profile delivery closeout

PR #142 merged at signed commit `72d437ff800014f30f04089cc79650483c6a0d3f`
on 2026-08-31T14:59:59Z. Full local validation passed: 1,439 tests twice
(141.41s and 93.00s), 83% coverage. All 17 exact-head hosted checks passed;
there were no unresolved review threads. Built-wheel context/profile hashes
matched. History-preserving integration and cleanup left one local main/worktree.

## Canonical reference and provenance contract freeze

Continue with two separate contracts, then integrate metadata results into the
same federation bundle. Recommended: bind logical identity explicitly and
derive provenance only through existing replay verifiers. Hash-only identity
would conflate distinct logical objects; caller-asserted provenance would not
establish that transformations reproduce. No semantic equivalence is inferred.

`reconcile_references(scope_raw, expected_sha256, metadata_bank, estate_inputs)`
must verify the separately supplied scope digest, recompute the six-role estate,
and require exact object/metadata-bank membership. Scope version
`gfjd-federation-reference-scope-v1` has only `contract_version`, `state`
(`preparation`), `estate_manifest_sha256`, `objects` and `partners`.
Each object has exactly `object_id`, `canonical_id`, `kind`, `role`,
`content_sha256`, `metadata_sha256`, `media_type` and `references`.
Kinds cover jurisdiction, institution, source, edition, acquisition, observation,
transformation and release. Logical IDs and canonical URNs are unique; canonical
URNs must use `urn:gfjd:<kind>:`. Roles come from the recomputed estate. Missing
content hashes remain null and unverified, not invented. Metadata bytes are
digest-bound supplied objects; no content hash declares verified data custody.
References are bounded HTTPS metadata locators, never requested. Partners are
prospective identifiers from the named archive-govt-nz, global-medicines-atlas,
reimbursement-atlas and dataset-estate-registry interfaces, not registrations.
Bound scope/metadata to 1 MiB each, 100 objects, 8 MiB total metadata, and 20
references per object. Output contains references/digests only, no source bytes.
This meaning of zero-copy applies to this generated artifact, not the whole estate.

`prepare_projection_prov(source, contract, receipt)` recomputes the existing
projection receipt before exporting sorted N-Triples and a binding report.
`prepare_pipeline_prov(entries, sources, safety_receipts, custody_receipts,
contracts)` likewise uses complete pipeline-history replay before exporting
B0/B1/Silver derivation and verified revision edges. Use exact serialized-byte
hashes, not semantic receipt self-hashes, for artifact entity identities. Preserve
partition/revision rules. No Activity, Agent, publication or execution timestamp
is fabricated from `recorded_at` or `valid_from`. Repeated bytes do not establish
semantic equivalence; avoid false self-revision or derivation assertions.

Use PROV-O Entity/Plan/derivation/revision terms only where supported by the
recomputed inputs; this is not full PROV-CONSTRAINTS validation. The existing
replay/estate helpers read their own implementation files for fingerprints, so
the composed API must disclose that narrow file access, not claim absolute
filesystem isolation. No transport or source loader is introduced. Exact output
recomputation must reject altered edges or references even if self-hashes are
recomputed. Missing parents, cross-partition revisions, namespace/role changes,
extra bank members, digest substitution and forged authority are negative tests.
All factual/rights/gate/publication/registration authority remains unverified.

### Bundle integration contract

`prepare_bundle(scope_raw, expected_sha256, metadata_bank, estate_inputs,
standards)` returns only deterministic draft files. Recompute reference and
estate results; bind all five normative/profile artifacts by their existing
hashes before dispatching supplied metadata to OpenLineage, DCAT, RO-Crate or
Croissant checks. Recognisable malformed standard documents stop; ordinary JSON
metadata with no selected standard remains explicitly `profile_not_selected`.
Do not reinterpret those as standards-valid or fabricate mandatory declarations.
Keep metadata reports separate from desired partner references and actual
factual evidence. The bundle contains no source payloads or copied input metadata.
Its manifest binds every output and supplied input digest, and verification
regenerates the exact file set and bytes. PROV exports remain separately
recomputed outputs until their exact replay-input relationship is integrated;
no unverified prebuilt provenance blob is accepted merely to fill that slot.

## Identity, provenance and bundle implementation checkpoint

The canonical reference adapter is implemented at `a358dda`, replay-derived
PROV exports at `7d9050c`, and metadata-only bundle assembly at `ebe4cd3`.
The combined focused suite passes 62 tests (2.19s); Ruff and strict module
typing pass. Tests cover exact membership and digest binding, all four metadata
dispatch routes, incomplete declarations, rehashed output forgery, malformed
standards, missing replay parents, cross-partition revisions and no network.
Meaningful failing tests preceded scope binding and replay-receipt verification.

Role-separated read-only advisory reviews found no actionable defects in the
reference, PROV or bundle implementations. Their recommendation is to continue
with full validation while retaining an explicit pending PROV integration state.
A valid but unrelated replay must never satisfy a scoped object's provenance
requirement. The next integration must recompute one explicitly typed projection
or pipeline-history input, bind a scoped canonical object to a recomputed entity
digest, use fixed output paths and bound aggregate input size. Unknown content
hashes remain pending, rather than acquiring an invented provenance binding.

The current bundle contains estate drafts, reference metadata, assessment reports
and output hashes, never input metadata or source payloads. PROV remains a
separately replayed output until that exact relationship is implemented. This
checkpoint does not complete the federation track, factual registry evidence,
partner registration, source rights, maturity, publication or any programme gate.
Full validation, exact-head CI and reviewed signed PR integration are pending.

## Identity/provenance delivery closeout

PR #143 merged at signed commit `66abdb2186ea17bb24a9e5a6c93c17d1f9d5495e`
on 2026-08-31T15:25:54Z. Full local validation passed: 1,501 tests twice
(95.74s and 82.10s), 83% coverage, security, integration/restore and deterministic
package/rehearsal checks. All 17 exact-head hosted checks passed; automated
review completed without findings or unresolved threads. Local cleanup left
one main branch/worktree. This closes that engineering phase, not WI-G4-MED-05.

## Exact replay attachment contract freeze

Recommended next: one explicitly typed replay attachment per bundle. This is
simpler to audit than unconstrained multi-job routing while covering both
projection and complete pipeline-history replay. Caller-supplied PROV reports
are not an alternative: unrelated valid provenance must not satisfy an object's
binding. Unknown content remains pending through the ordinary bundle API.

Add `prepare_replayed_bundle(scope_raw, expected_scope_sha256, metadata_bank,
estate_inputs, standards, replay_raw, expected_replay_sha256, replay_bank)` and
the corresponding exact-output verifier. Preserve the existing bundle API.
The replay envelope is strict JSON with exactly `contract_version`
(`gfjd-federation-replay-attachment-v1`), `mode`, `selection` and `inputs`.
Bind its exact bytes to the separately supplied digest before replay.

`selection` has exactly `object_id`, `entity_role`, `event_id` and
`entity_sha256`. Require one matching scoped object with a non-null content
hash equal to the recomputed selected entity digest. Projection mode uses
`event_id: null`, and `entity_role` is `source` or `projection_rows`.
Pipeline-history mode uses an exact event ID and role `source`, `bronze` or
`silver`. Use actual bytes for source identity and the PROV module's canonical
JSON serialization for row identity; never use receipt self-hashes. Record only
byte-identity binding, not factual ownership or semantic equivalence.

Projection `inputs` has exactly `source_sha256`, `contract_sha256` and
`receipt_sha256`, referencing supplied bank bytes. Pipeline-history `inputs`
has exactly `entries_sha256`, `sources`, `safety_receipts`, `custody_receipts`
and `contracts`: the latter four are unique lists of bank digests. Parse exact
contract/receipt/entry bytes and call the existing PROV preparation functions;
complete-history replay and exact bank membership remain mandatory. Recompute
the selected entity from those verified inputs and require it in the generated
PROV graph. Every bank member must be used by the envelope. No lookup, file
loader, URL request or prebuilt provenance-report input is permitted.

Bound the envelope and each bank member to 1 MiB, the bank to 401 members and
8 MiB total, and use the existing strict metadata JSON parser for structured
inputs. Its additional depth/node/collection limits apply; an oversized valid
upstream history must fail this bounded attachment profile, not be truncated.
The existing metadata bank adds at most 8 MiB; normative assets and estate
inputs keep their own existing bounds. Existing implementation-fingerprint file
reads remain disclosed.

Add exactly `provenance/provenance.nt` and `provenance/provenance-report.json`
to the ordinary bundle. Rebuild its manifest with all output hashes, replay
input hashes, the selected canonical object/role/entity binding, and explicit
pending IDs for every other scoped object. Exact verification regenerates all
files from source inputs, rejecting rehashed output forgery. No source bytes,
input metadata, receipt contents or row values enter the output. All factual,
full-conformance, custody, rights, publication, gate and registration states
remain unverified/unauthorized.

Then add a conspicuously fictional deterministic end-to-end rehearsal using
the six-role estate, all four metadata assessment routes, canonical references
and the exact replay attachment. Exercise incomplete metadata, unrelated replay,
changed source or output, extra membership and forged authority. Rehearsal
success proves machinery only. Parquet-reference declarations, prospective
partner-interface qualification and supporting-evidence indexing remain later
items within this same federation track.

### Attachment review and implementation binding

`cd2bfc4` implements both attachment modes; `9a890b6` adds the full fictional
rehearsal and local/hosted integration hooks. The 37 focused tests pass (23.95s),
with Ruff and strict adapter typing passing. The new Make rehearsal writes and
independently verifies a content-addressed report; earlier reports are retained,
not overwritten. Its end-to-end tests run in the integration tier, with negative
cases also selected by the existing adversarial tier rules.

Review corrected three concrete issues. Pipeline contract bank keys now preserve
supplied-byte digests while deriving canonical keys required by replay; aliases
that collapse to one canonical key fail. The trailing-newline regression failed
before this correction. Rehearsal input negatives call preparation directly,
so changed output hashes cannot mask a missing input guard. A deliberately
defective-adapter regression failed before this correction. CLI output handling
rejects symlink ancestors and special files and uses bounded, nonblocking,
descriptor-checked reads. The ancestor-link regression also failed before the
correction. This is local report hygiene, not an OS sandbox guarantee.

Additionally bind exact attachment and PROV-compiler source-file hashes in the
composed manifest, alongside the existing base-bundle and replay fingerprints.
Version labels alone do not identify the relationship-generating code. This
introduces only two disclosed implementation-fingerprint reads, never a source
loader or remote lookup. Exact report verification must reject changed compiler
bindings, even when an output manifest's other hashes are rewritten.

`adeca05` implements those compiler bindings after two failing hash assertions.
The combined attachment/rehearsal suite now passes 39 tests (13.77s), with Ruff
and strict adapter typing passing. Read-only review found the raw/canonical
mapping, direct input counterexamples and filesystem corrections addressed;
full local validation and exact-head hosted delivery follow this source freeze.

Run `make PYTHON=.venv/bin/python federation-bundle-rehearsal` to generate and
verify `build/federation-rehearsal/report-<sha256>.json`. The report binds every
composed artifact hash, the four observed metadata profiles, all six estate
roles, selected entity, remaining pending object IDs and rejected counterexamples.
Fixtures are development-only, conspicuously fictional and supplied in memory.
No source bytes or input metadata are persisted by this rehearsal. The Make
integration target and hosted integration receipt upload include this check.

### Remaining federation interface work

Local technical-contract inspection (not source-data access) identified useful
prospective bindings. These are observed local snapshots, not verified hosted
revisions, accepted ownership transfers or partner registration:

- archive-govt-nz at `af427c2632239a8869684c849c0fcc1981277b02`:
  `src/archive_govt_nz/foi_ownership.py`, SHA-256
  `9bdbecd2cd84f1faff7d69b5bdad729f8add68baa98b9345b066ccc1775d031a`;
  `schemas/archive/v1/publication-receipt.schema.json`, SHA-256
  `6097ba87f4eafa04bcea8f586144cb9129961d085709fe99350e600274137c9d`.
  The ownership API is scoped to fyi-archive and archive-govt-nz; GFJD is not
  an allowed owner. Treat it as a reference, never an executable GFJD transfer.
- global-medicines-atlas at `f7550d5f84b6a831cd99c3b6882c0d33c4b0c939`:
  `contracts/medallion/v4/federation.schema.json`, SHA-256
  `ac28485a70e0853266e4c140f9a07cd557eb27816b0b408b9bf2927a4cffacec`;
  `src/global_medicines_atlas/federation.py`, SHA-256
  `2a21eb2d09a8a9ba1e956c1b0d5c123529c185d79bb31ced2c2a0cb8bebaeb78`.
  Its B0 index / B1 acquisition metadata / B2 raw evidence meanings are not
  GFJD's B0 preservation / B1 analytical representation. No direct aliasing.
- The exact named reimbursement-atlas local checkout was absent. No substitute
  repository was guessed, and no network request was made for this inspection.

Next prepare explicit checksum-bound partner-interface references with
compatibility pending; never fill live-publication fields with invented receipts
or invoke data-loading federation readers. Add the still-missing Parquet
reference declarations and consistency checks, then index engineering support
separately from factual `E-FEDERATED-MEDALLION-REGISTRY` acceptance. These
remaining items keep this federation track in progress.

## Replay composition delivery closeout

PR #144 merged at signed `d83dbcef983510b76030ff93ac5b16a7fc8f85b2` on
2026-08-31T15:50:12Z. Full local validation passed (1,540 tests twice,
107.83s/100.77s, 83% coverage), including the integrated federation rehearsal.
All 17 exact-head hosted checks passed; completed automated review had no
findings or unresolved threads. Main and remote matched; one local branch and
worktree remained after history-preserving integration and cleanup.

## Parquet and partner reference contract freeze

Recommended: additive, separately versioned declaration sidecars. Keep reference
scope v1 unchanged: `application/json` describes metadata bytes, never a verified
Parquet payload. A scope-v2 migration is possible but adds no necessary evidence
for this slice. Missing facts must remain incomplete rather than be invented.

`assess_parquet_references(declaration_raw, expected_declaration_sha256,
scope_raw, expected_scope_sha256, metadata_bank, estate_inputs)` recomputes
canonical references and returns a deterministic declaration assessment.
Its verifier takes the same inputs plus a report and recomputes every field.
The strict JSON envelope has exactly `contract_version`
(`gfjd-parquet-reference-declarations-v1`), `scope_sha256`, `state`
(`preparation`) and `objects`. Each object has exactly `object_id`,
`canonical_id`, `content_format` (`parquet`), `content_sha256`, `blake3`,
`byte_count` and `locations`. Match a unique scoped object and canonical ID;
content SHA must equal the scoped value, including null. SHA-256 and BLAKE3 are
nullable lowercase 64-hex declarations, not computed payload checks. Byte count
is null or an integer from zero through 2^63-1, never a boolean.

Each location has exactly `url` and `revision`. URL is bounded HTTPS, never
requested. Revision is null or an object with exactly `kind` and `value`:
`git_commit` requires lowercase 40-hex; `content_sha256` requires a non-null
matching content SHA; `persistent_id` requires a HTTPS identifier. These are
declared identifiers, not proof of immutability or version-specific resolution.
This permits Git, content-addressed and persistent-identifier providers without
inventing Git revisions for non-Git archives. Reject duplicate locations/objects.

Limit to 100 objects, 20 locations per object, and existing strict JSON limits
(1 MiB/depth 16/10,000 values/4,096-character strings). Missing content hash,
BLAKE3, size, locator or locator revision yields explicit missing-field codes;
unattached scope IDs stay pending. A content hash equal to supplied JSON or
N-Triples metadata bytes is a known format contradiction and fails. Otherwise
a hash alone cannot reveal Parquet format: a canonical JSON row hash must not
be promoted into verified Parquet identity. Row counts, schemas, footers and
statistics are outside this declaration-only check. Report format/digest
verification false, all rights/custody/ownership/remote/semantic states
unverified and all authority false. Zero-copy describes the output only.

`assess_partner_interfaces(declaration_raw, expected_declaration_sha256,
scope_raw, expected_scope_sha256, metadata_bank, estate_inputs, contract_bank)`
also recomputes canonical references. Envelope keys are exactly
`contract_version` (`gfjd-partner-interface-references-v1`), `scope_sha256`,
`state` (`preparation`) and `partners`. Each partner has exactly `partner_id`,
`commit` and `artifacts` (contract relative path to SHA-256 map). Require exact
coverage of the scope's selected partner IDs. Null commit with an empty artifact
map is explicitly unavailable, not an inferred compatible interface.

Non-null references must match the exact observed commit, paths and hashes
recorded above for archive-govt-nz and global-medicines-atlas. Unknown or drifted
contracts fail closed, never become valid merely through a caller-supplied
checksum. The supplied contract bank must contain exactly those referenced
bytes, at most eight members, 1 MiB each and 8 MiB total. Validate supplied
JSON Schema syntax locally; never execute supplied Python, invoke a reader,
resolve a receipt, load a source or write another repository. Pin the compiler
implementation and every input hash. Both selected upstream schemas have been
read at their exact Git commits and their recorded SHA-256 values reproduced.

Report archive ownership transfer as unsupported for GFJD (its allowlist names
only fyi-archive and archive-govt-nz), and its publication receipt as requiring
actual publication evidence. Report GMA as a prospective declaration contract,
with the B0/B1/B2 terminology mismatch explicit, no direct layer alias, and
schema plus semantic validation and authentic receipt/byte evidence still
required before interoperability acceptance. Reimbursement/estate-registry
interfaces remain unavailable until exact technical contracts are provided.
These are qualified reference bindings, not partner registration or live
interface conformance. Emit metadata/digests only, all authority false, and
verify by full recomputation. Disclose existing helper/compiler fingerprint
reads. Integrated sidecar composition and supporting evidence indexing follow
these tested adapters within the same federation track.
