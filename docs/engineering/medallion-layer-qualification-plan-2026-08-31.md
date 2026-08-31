# WI-G4-MED-03 — independent per-layer qualification preparation

Status: in-progress repository-owned preparation. The acceptance-bearing work
item remains planned behind WI-G4-MED-02; neither its dependencies nor acceptance
criteria are waived by this engineering plan.

Baseline: signed `fb3f277`, merged PR #137 at 2026-08-31T11:08:17Z. Both local
post-review suite passes ran 891 tests; coverage was 80.53%. The complete
`autonomy-full` harness passed, as did all 17 exact-head hosted checks. The source
manifest verifies 989 files; bounded bootstrap discovery passed. Prior branch
cleanup left one clean main checkout before this preparation branch was created.

## Recommendation, alternatives and trade-offs

Implement a recomputing qualification matrix over the canonical B0, B1, Silver,
Gold and Platinum layers. Report completeness, fixity, rights state, lineage,
reproducibility, quality, quarantine and restore separately for every layer.
Evidence is scoped to exact objects and layers; successful publication or a
later-layer result cannot satisfy an upstream requirement.

Recommended: reuse existing source-recomputing verifiers through explicit typed
adapters, bind every input and rule, and preserve pending or failed cells when
evidence cannot be verified. Keep technical qualification separate from the
owner's accountable promotion decision. This is more work than a status-only
checklist but produces executable, falsifiable evidence.

Alternative: require only populated evidence references. This is simpler but
already covered by the existing structural layer validator and is insufficient:
a digest or claimed pass does not prove the referenced assessment. Do not use it
as a maturity result. A universal new workflow engine is also unnecessary; use
bounded adapters and explicit unsupported-evidence dispositions instead.

## Ordered implementation

- [x] Obtain role-separated advisory review of reusable verifiers, evidence
  scope, requirements and adversarial cases. Freeze the concrete adapter contract
  before functional implementation (contract below).
- [x] Implement bounded declared-scope metadata resolution and exact
  object/edition/layer binding (`df1bce4`; 28 focused tests). This establishes
  coverage and structural consistency only, not payload qualification.
- [x] Implement bounded payload resolution and exact content binding.
  Missing, malformed, conflicting, unsupported or stale evidence must not pass.
  Active allowlisted byte-bank resolution is implemented in `e42eb94` (11
  tests); `481ec55` links bytes to layer evidence and recomputed predecessors.
- [x] Recompute independently supported layer checks and emit an exhaustive
  matrix of verified, failed and pending requirements with evidence references
  and limitations. Do not turn self-reported review labels into verified facts.
- [x] Preserve all lifecycle states in coverage. Quarantine, withdrawal and
  tombstoning prohibit downstream promotion without erasing valid upstream
  evidence. Missing layers remain visible rather than disappearing from counts.
- [x] Enforce the Gold owner-decision and Platinum release boundaries separately
  from technical checks. Validate available decision bindings without inventing
  authority or treating advisory reports as accountable acceptance.
  Scoped declared review-record bindings are implemented in `432fcc6` (45
  tests). They expose current/expired/future status, conditions and conflicts;
  they never authenticate a reviewer, adjudicate conditions or accept a layer.
- [x] Implement independent Gold quality diagnostics (`e55d733`; 39 tests) and
  Platinum composition checks (`97a2cd4`; 30 tests). `481ec55` integrates them
  with predecessor-scope checks; neither grants authority.
- [x] Add adversarial tests, deterministic fictional fixtures and an independently
  recomputed rehearsal/report. Include cross-layer borrowing, digest/object
  substitution, false pass flags, missing predecessor evidence and quarantine.
- [x] Record supporting evidence and explicitly scoped resume guidance without
  bypassing programme dependency checks or changing any gate/acceptance mapping.
- [ ] Advisory review, full local validation, signed commits, PR, exact-head CI,
  history-preserving merge and local branch cleanup.

## Contingencies and authority boundaries

Where a verifier only establishes structural consistency, report that limited
fact and keep factual assurance pending. Where no supported source adapter
exists, retain the missing capability explicitly; do not select an easier
format and claim complete cohort qualification. Rights, semantic equivalence,
real remote restoration and accountable decisions require their own genuine
evidence. A failed qualification must retain useful upstream evidence and its
public-safe disposition without promoting or hiding the failed layer.

No new network/source requests, source-byte acquisition, external contact,
cross-repository writes, rights clearance, maturity or Gold promotion,
publication, release or G2/G4 acceptance is authorized. This track prepares
repository-owned mechanisms; actual factual qualification remains separately
evidenced and subject to the existing owner-controlled process.

## Frozen implementation interfaces

Advisory inputs from `api_contract_advice` and `preservation_inventory` agree on
separate layer adapters, a separately bound expected inventory, explicit missing
evidence and no authority inferred from a reference or claimed pass. Existing
structural medallion validators and pending governance templates cannot establish
substantive qualification. The canonical layer-contract bytes must also be bound.

The evaluator uses bounded digest-addressed supplied bytes only. There are no
paths, retrieval callbacks, arbitrary verifier plugins or caller-supplied pass
booleans. Every expected object and all five layers appear in coverage, including
absent, quarantined, withdrawn and tombstoned evidence. Lifecycle interlocks run
before payload processing. Layer-local mechanical success remains visible even
when its upstream factual dependencies block promotion.

1. Core evaluator: pin the canonical layer contract and separate scope inventory;
   validate exact object/edition/layer binding; recompute available B0 fixity and
   safety/receipt consistency, B1 lexical extraction, Silver projection/history;
   build the exhaustive matrix and exact-recomputation verifier. Unsupported
   source formats or unavailable payloads remain explicit, never silently omitted.
2. Gold quality adapter `assess_quality(rows_raw, policy)`: independently compute
   mandatory-field completeness, duplicate observation identity, finite exact
   decimal/nonnegative/percent bounds, explicit period ordering, small-cell
   diagnostics and source-defined comparability-signature diversity. Policy binds
   the exact Silver row bytes and explicit diagnostic threshold. Return original
   input digests and deterministic diagnostics, not selected/promoted rows. These
   metrics do not accept methods, privacy/disclosure risk or owner adjudication.
3. Platinum composition adapter `assess_release(manifest_raw, federation_raw,
   artifacts, expected_scope_raw)`: independently recompute exact declared Gold
   object membership, content digests, byte counts and federation identities.
   Reject duplicates, extra/missing objects, non-Gold roles, altered bytes and
   mismatched scope/release bindings. This internal composition contract does not
   claim DCAT/Croissant/RO-Crate conformance, accepted Gold, public retrieval or
   release authority; those remain independently required.
4. Typed authority/review evidence may establish a scoped, digest-bound record
   and expose expiry/conflicts, but authenticity and substantive acceptance may
   not be inferred from its contents. Unknown authority remains pending. The
   evaluator never performs a promotion or publication, even if mechanics pass.

Each adapter has fixed limits and a recomputing verifier. The Gold and Platinum
adapters are part of this implementation, not omitted merely because B0/B1/Silver
are easier to exercise. Fictional tests must demonstrate verified mechanics,
real detected failures and pending factual requirements together.

## Adapter checkpoint and review fixes

The metadata binder retains all five expected layer cells per object, rejects
extra or conflicting records, and pins the canonical layer contract. It does
not consume source payloads or accept referenced reports. Strict input checks
also reject overflowed JSON numbers and unpaired Unicode surrogates.

Role-separated advisory review identified non-transitive dependency reporting:
a missing B0 blocked B1 but was not carried into otherwise structurally valid
Silver. `df1bce4` propagates that blocker through descendants without erasing
their useful structural evidence. Regression cases cover missing, invalid and
quarantined ancestors, including an unaffected second object.

Platinum now rejects an empty declared cohort, avoiding vacuous composition
success. Gold reports unassessed small-cell units/values explicitly rather than
equating zero detected cells with disclosure clearance. All three adapters bind
their implementation identities and fully recompute supplied reports.

Current continuation: finish programme supporting-evidence registration, then
whole-track validation and delivery. The five-layer/eight-dimension matrix and
fictional rehearsal are implemented. No full-track validation, PR or merge is
claimed until their observed results are recorded.

The payload resolver rejects extra bank entries and entries referenced only by
inactive or malformed records before hashing payload bytes. Its 8 MiB aggregate
limit is checked before hashing. Missing active references remain visible. This
is fixity/eligibility checking, not proof that a source digest, capture claim,
quality report or review record has the right meaning for a layer.

### Coordinator integration requirements

The next coordinator must recompute the metadata and payload bindings rather
than accept their reports as caller assertions. For each active layer, it must
match role digests against the layer record's evidence, use only its explicit
versioned adapter, and cross-check inputs against the exact recomputed immediate
predecessor outputs. A missing predecessor leaves lineage pending/blocked even
if a downstream adapter can mechanically inspect its own bytes.

The eight dimensions must carry separate scoped results and limitations: declared
completeness, content fixity, rights, lineage, reproducibility, quality,
quarantine and restore. Unavailable factual evidence is pending, malformed or
conflicting evidence fails, and unsupported formats are explicit. A repository
backup rehearsal cannot stand in for a source/layer restore. A current declared
review record cannot pass rights, semantic, disclosure or owner authority.

Gold diagnostics must bind the exact Silver rows; Platinum must bind the
separately expected cohort and exact Gold content, not derive its denominator
from whatever happened to be supplied. Recorded custody assertions may be
consistent but are not a fresh remote retrieval. Preserve every failed, missing
or inactive cell and do not perform any promotion.

Follow-up advisory review approved the bounded helpers and the transitive fix
(84 independently rerun tests across input, payload and review-binding helpers).
It explicitly requires the coordinator to consume transitive blockers rather
than treating `payload_processing_eligible` as readiness, match each review's
returned `review_kind` to its artifact role, and check wrapper-to-evidence and
predecessor content bindings. These are mandatory integration checks; the helper
approval does not approve the unfinished evaluator or any programme evidence.

## Integrated implementation checkpoint

- `dd4a1e1`: B0 original SHA-256/BLAKE3/size verification, bounded text/CSV/JSON
  and XLSX container scans, and recorded custody consistency (20 tests).
  Unsupported PDF/other formats remain explicit, not counted as safety passes.
- `b252a3c`: full scoped correction-journal replay and exact supplied checkpoint
  prefix verification (33 tests). Checkpoint authenticity remains pending.
- `481ec55`: coordinator with all five layers and eight dimensions (26 tests).
  It recomputes adapters, verifies exact predecessor bytes before transforming,
  enforces role and evidence bindings, and retains missing/failed upstream cells.
- `2ed6fe6`: deterministic fictional two-revision qualification rehearsal and
  a rejected Gold substitution that preserves upstream fixity (two tests).
- `1a47674`: bounded repository-preparation resume scope and plan inclusion
  (34 autonomy tests). Current dependency-filtered routing still excludes
  WI-G4-MED-03 until its prerequisites permit it; this is not a dependency waiver.

The helper checkpoint at `dbf8b25` passed `autonomy-fast`: 702 unit tests passed,
342 were excluded by the documented unit/not-slow selector; contracts, strict
validation, generated views, policy and resume verification passed. This is not
the full final-track test result.

### Integration review and fixes

Role-separated advisory review found and reproduced missing B0 capture/custody
references being reported as complete, and content fixity failures being
misclassified as pending. `481ec55` records required missing receipts explicitly,
propagates blockers, identifies proven fixity failures as failed and preserves
independently verified original fixity when a later receipt check fails. The
reviewer reran all 26 core tests and confirmed both findings resolved.

Additional source-safety checks ensure a known negative receipt overrides an
unsupported scan, and missing/unsupported safety contributes an upstream blocker.
Known safety failures and declared quarantine stop downstream transformation.
Review conditions and authenticity remain pending rather than inferred accepted.

The synthetic report is `data/synthetic/medallion-qualification-rehearsal-2026-08-31.json`.
Recompute it with `python scripts/rehearse_medallion_qualification.py --verify`
followed by that path. It binds the fictional test builder, rehearsal and adapter
implementations. Provider-shaped fixtures are not retrieval evidence. The
acceptance-bearing E-MEDALLION-MATURITY-QUALIFICATION remains missing, and
WI-G4-MED-03 remains planned behind its existing dependencies.
