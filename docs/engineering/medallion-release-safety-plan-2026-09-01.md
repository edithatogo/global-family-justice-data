# WI-G5-MED-03 — complete candidate assurance preparation

Status: in progress, repository-owned preparation only. Baseline signed main
`e7bbe5f1b392347fa4873eecc52d807a100a5bd4`, PR #151. Full gate passed with 1,931
tests twice, 84% coverage and 17 green hosted checks. No source or network access,
publication, rights clearance or gate acceptance is enabled by this work.

## Options, recommendation and rationale

Implement a full-inventory assurance coordinator with explicit per-dimension
coverage. Reuse restore fixity, lifecycle history, layer qualification and Gold
count diagnostics, while adding candidate-wide bounded scanning and exact
dependency/provenance bindings. A blanket wrapper around repository scanning is
insufficient: existing repository scans skip binary containers and large text.
Existing archive PDF/ZIP routines are not sufficiently hard-bounded to use as
the candidate-wide untrusted parser. Authentic audits, rights/disclosure decisions,
remote retrieval and signing authority remain separate factual requirements.

Do not silently drop inactive, auxiliary, transformation or package objects.
Unsupported formats are visible blockers, not successful scans. Relabelling a
container as text or auxiliary must not obtain a pass. Role-separated advice
recommends compiler-controlled applicability, fixed severity, no matched-value
echoing, and independent recomputation of supplied evidence rather than trusting
precomputed success receipts. Missing evidence is reported, never invented.

## Full implementation sequence and acceptance scope

- [x] Candidate-byte scanner with hard text/JSON/CSV/XLSX/ZIP bounds and explicit
  unsupported outcomes for other formats; immutable finding codes and no output
  excerpts. This is a component, not complete WI-G5-MED-03 preparation.
- [x] Full candidate inventory/root/role-edge/locator binder; exact supplied-bank
  membership and SHA-256/BLAKE3/size, preserving all declared categories.
- [x] Typed qualifier/restore/lifecycle evidence-input binding and independent
  recomputation; reject wrong candidate/time/scope associations. Do not accept
  precomputed "passed" reports as proof.
- [x] Pure supplied-byte lock/SBOM dependency graph and package-binding checks;
  retain vulnerability-feed freshness, authenticity and signatures as unverified.
- [x] Eight-dimension coordinator: fixity, secrets, prohibited data, disclosure,
  dependencies, provenance, supply chain and locators for every inventory member.
  Compiler-owned applicability and finding severity; no caller-provided waivers.
- [x] Fictional all-role rehearsal and adversarial tests including unsupported
  package/media, auxiliary secret, omitted history, false audit/disclosure success,
  lock/SBOM mismatch, unsafe locator and rehashed report forgery.
- [ ] Role-separated review, full validation, signed reviewed PR, CI, merge and
  local cleanup; then audit the entire authorized queue and remaining gaps.

Hosted review remediation rejects disclosure borrowed by unrelated Gold bytes and
scope-order-dependent lifecycle matches. Both regressions failed before commit
`d30d70d`; association now requires the exact eligible Gold `rows` digest and a
unique lifecycle content match among same-identity sibling roles.

Second hosted-review remediation requires exact source edges from derived data and
transformations to the native immediate-predecessor bytes. Missing edges remain
missing provenance and wrong edges fail. Inactive historical artifacts without
supplied bytes remain digest-only gaps even when a newer sibling exists. Both
regressions failed before commit `9640d23`; the focused suite passes 176 tests.

Exact-head hosted-review remediation requires qualification wrapper candidates to
match logical object, edition and layer before bytes. Mismatched identities reject;
an unrelated duplicate digest no longer creates ambiguity. Both regressions failed
before commit `fa3d650`; the focused suite passes 178 tests.

Subsequent hosted-review remediation preserves a failed/pending native lineage
result even with an exact source edge, requires lifecycle content SHA-256/BLAKE3/
size and declared source bindings to agree with the candidate, and permits package
dependency success only through an exact validated package binding. All three
regressions failed before commit `8e437cd`; the focused suite passes 181 tests.

Further review remediation requires a derived source target's layer to equal the
immediate predecessor and reports multiple eligible provenance roles as unsupported
instead of rejecting the complete operation. Both regressions failed before commit
`b22e048`; the focused suite passes 182 tests. Distribution sizes already require
exact integer type and `size = true` already has a negative regression.

The first exact-head closeout retry stopped fail-closed because a nested-ZIP test
fixture embedded wall-clock metadata and produced different collected IDs across
parallel workers. Commit `c56f58d` fixes the fixture timestamp; no production
contract or assertion was loosened.

All seven tasks above remain part of this track. A scanner-only or status-matrix
delivery must not be labelled completion of the full coordinator. Actual public
release-candidate assurance remains separately unmet even after preparation works.

## Frozen first component: supplied-byte scanner

`scan_candidate_bytes(raw, media_type)` returns metadata only, deterministically.
`verify_candidate_scan(raw, media_type, report)` recomputes it. Raw must be plain
bytes, nonempty and at most 8 MiB; media_type is a bounded string at most 128
characters matching lowercase ASCII type/subtype tokens (letters, digits, dot,
plus and hyphen; each token starts with a letter). Reject invalid API types/budgets with fixed errors before hashing or
parsing. Return input SHA-256/BLAKE3/size, declared media, scanner status, fixed
finding codes/severities, per-check coverage, component fingerprints, limitations
and false authority. Never return source text, matched values or member names.
Only compiler fingerprints read files; no temporary files, network or execution.

Supported profiles are text/plain, text/csv, application/json,
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet and application/zip.
PDF, Parquet, DuckDB, gzip, ODS and every unknown media remain unsupported unless
a subsequent bounded implementation is explicitly added to this plan and tested.
This is a coverage limitation, not evidence those formats are safe or unsafe.

Text uses strict UTF-8 (optional BOM), rejects NUL and disguised binary/container
signatures (ZIP, PDF, Parquet, gzip, SQLite/DuckDB markers). JSON additionally
uses the existing strict bounded structured preflight (1 MiB, depth 16, 50,000
nodes, strings 4,096, containers 2,000, duplicate/nonfinite/control rejection).
Scan decoded JSON keys/strings as well as raw text so escaped credentials cannot
bypass literal-pattern checks. CSV parsing is strict and bounded to 1,000 rows,
64 columns, 10,000 cells and 4,096 characters/cell, with consistent widths;
check prohibited header names and decoded cell values. Empty/malformed tables
fail closed. Plain text receives literal secret scanning only; its prohibited
data/disclosure coverage remains explicitly unsupported rather than inferred.

Reuse the existing fixed secret patterns and prohibited public-data header set.
JSON dictionary keys and CSV headers are checked case-insensitively after strip.
No semantic claim that arbitrary text or a field outside that set is safe.
Disclosure, rights and comprehensive privacy always remain unassessed here.
Secret/prohibited-field findings are compiler-classified critical and cannot be
downgraded. Invalid format/unsafe container conditions are high; unsupported
coverage remains an explicit blocker rather than a low-severity pass.

ZIP-compatible content must pass `medallion_xlsx._package` hard preflight before
any decompression: at most 128 members, 16 MiB declared expansion, 8 MiB/member,
ratio at most 200, stored/deflate only, no traversal, duplicate/case-colliding
paths, links/special files, directories, encryption, active-content names or .bin.
Reads stay bounded and verify CRC/actual size for every member. Do not call the
older broad `_scan_zip`. Inspect each member exactly once. Nested containers,
unsupported binary members or unsupported member extensions remain blockers;
never extract, recursively unpack or execute them. Member names may be examined
for format routing and forbidden credential filenames/suffixes, but reports use
only member-content hashes and aggregate counts, never those names.

ZIP members support .txt/.md/.py/.toml/.yaml/.yml/.cff as strict text, .json as
strict structured JSON, .csv as bounded CSV, and .xml/.rels through bounded XML.
Textual code/config members are not semantically certified. XML uses the existing
`_xmls` UTF-8/DTD/entity/depth/node bounds before checking decoded text/attributes
for secret patterns and prohibited field tokens. XLSX additionally requires its
core content-type/workbook members and passes the same XML constraints; do not
claim source extraction or workbook semantic correctness from scanner success.
CSV/JSON/XML members with unsupported coverage make the package coverage explicit.
Unknown member extensions are unsupported even if bytes happen to decode.

Review remediation: decode namespace declarations too, including unused prefixes
and numeric character references. After `_xmls` hard preflight, a bounded second
in-memory XML pass observes namespace events; members are not decompressed again.
Bound namespace events across the package to 100,000 and each prefix/URI to 4,096
characters. Scan full expanded tags as well. Both used/unused escaped-namespace
regressions failed before this fix; the scanner suite now passes 71 tests.

Report separate secret and prohibited-data results using checked_no_findings,
failed or unsupported, along with the exact limited check scope. Overall scanner
status is failed for findings, unsupported for any unsupported required scanning,
otherwise checked_no_findings. A checked result is not public clearance; all
rights/privacy/disclosure/external-assurance/publication/release facts stay pending.

## Remaining coordinator design constraints

Before implementing subsequent components, freeze their exact interfaces and
applicability matrix in this plan. Preserve the complete declared denominator:
up to 1,502 candidate members, 8 MiB/object, 26 MiB unique bytes, structured roots
1 MiB, and independent category/evidence budgets checked before hashing. Supplied
receipts need both byte bindings and exact candidate/time/role associations.
Historical tombstones preserve metadata without requiring unsafe payload retention.
Any unavailable historical payload must remain explicit; it cannot be relabelled
as verified source fixity or erased from lifecycle coverage.

Unknown units and non-tabular data cannot borrow Gold count-cell diagnostics.
Lock/SBOM agreement cannot prove vulnerability freedom, artifact authenticity or
key custody. Locator syntax cannot prove remote safety, anonymous availability
or actual withdrawal. No "not applicable" state comes from user-supplied assertions.
The final report must distinguish bounded mechanical results, missing/unsupported
technical coverage, factual assurance, owner acceptance and release authority.

## Frozen candidate inventory and native-evidence envelope

Coordinator API: `assess_candidate_assurance(plan_raw, expected_plan_sha256,
scope_raw, candidate_bank, evidence_bundles)`, plus exact recomputation verifier.
Internal `prepare_candidate_inputs` uses the same arguments and returns parsed
plan/scope, exact candidate bytes, typed bundles, descriptor fingerprints and
metadata inventory counts. It never scans, runs evidence or contacts providers.

Plan exact keys: contract_version (`gfjd-candidate-assurance-plan-v1`), state
(`preparation`), candidate_id, as_of, scope_sha256, evidence_bindings. Candidate ID
uses the bounded opaque identifier syntax; time is explicit UTC seconds. The
scope SHA and plan SHA independently bind exact supplied bytes. evidence_bindings
is exactly qualification, restore, lifecycle, dependencies, each null or SHA-256
of the supplied bundle's typed descriptor. Null requires no corresponding bundle;
nonnull requires exactly one matching bundle. There are no unbound extras.

Scope exact keys: contract_version (`gfjd-candidate-assurance-scope-v1`),
candidate_id, objects. It describes the complete declared candidate release,
never an unstated selected subset. objects is 1–1,502 unique object_id entries.
Each object has exactly object_id, logical_object_id, edition_id, layer, role,
lifecycle, sha256, blake3, size_bytes, media_type, edges, locators. IDs are opaque;
layer is b0/b1/silver/gold/platinum/cross_layer; role is data/metadata/transformation/
package/manifest/dependency/locator_record. Lifecycle uses the existing four
states; it does not establish maturity. Size is a positive integer, not bool.
Media uses the scanner's syntax, never arbitrary diagnostic text.

Each edge is exactly relation and target_object_id. Relations are source,
metadata, transformation, package_member, dependency, manifest or locator.
Targets exist within this scope, and duplicate relation/target pairs are rejected.
Edges remain declarations until a relevant compiler verifies them. Package-member
edges must later reconcile the entire bounded unpacked member-hash multiset;
generic adjacency is not proof of derivation. Role alone cannot waive any scan.

Locators is exactly github and huggingface; each value is null or an HTTPS
declaration on github.com/huggingface.co respectively, with nonempty path and no
user info, port, query, fragment, backslash, control or malformed percent escape.
Reuse the strict restore locator validator. Null stays missing_evidence, not
not_applicable. No locator is requested. Non-typed embedded URLs in text remain
outside locator assurance; this limitation must be reported explicitly.

Candidate bank membership is exactly the unique object SHA-256 set. Each byte
object is at most 8 MiB; total unique bytes at most 26 MiB. Each of the seven role
categories has an independent 8 MiB budget, with shared byte identities charged
to every category where they appear. Within one category count each digest once.
Shared digests must have identical BLAKE3/size/media declarations. Check all sizes,
membership and budgets before SHA/BLAKE3 work. Every declared object remains in
the report, including duplicates by content, inactive members and metadata.
Decoded plan/scope keys and strings must also be checked against the existing
literal secret patterns before returning control metadata; a match fails with a
fixed diagnostic and is never echoed. This prevents a credential-shaped object
ID or escaped locator/control value from leaking through the report itself.

The external evidence-bundle tree is bounded before fingerprinting: plain dicts,
lists, strings, bytes, ints/bools/null only; depth at most 12, 50,000 nodes, at most
2,000 entries/container, strings at most 4,096 without controls/surrogates, bytes
at most 8 MiB each, and total byte leaves at most 64 MiB counting repeated leaves
independently. All dict-key and string-value UTF-8 bytes together are at most
1 MiB before descriptor construction. Integer magnitude is bounded to 4,096 bits
before conversion/serialization. No subclasses, paths, callables or floats. Each typed descriptor
node is tagged: bytes becomes [bytes,SHA-256,size]; strings/ints/bools/null retain
their value with a type tag; lists preserve order; dicts sort string keys and
contain their recursively tagged values. Hash canonical JSON of this descriptor.
This is a deterministic input binding, not authenticated provenance.

Native bundle keys are exact, using the existing APIs:

- qualification: scope_raw, scope_sha256, layer_contract_raw, record_bank,
  payload_bank, as_of;
- restore: plan_raw, expected_plan_sha256, scope_raw, expected_scope_sha256,
  layer_contract_raw, replica_banks;
- lifecycle: plan_raw, expected_plan_sha256, scope_raw, layer_contract_raw,
  checkpoint_raw, event_bank, receipt_bank;
- dependencies: lock_raw, sbom_raw, package_bindings_raw, project_name.

The input helper checks shapes and byte-leaf bounds but does not trust nested
claims. The coordinator invokes the corresponding native recomputation only
after all candidate and evidence budgets/bindings pass. All native times must
equal coordinator as_of; restore release_id and dependency candidate binding must
equal candidate_id. Qualification/restore roots, wrappers and every supplied
payload must match the candidate bank by exact bytes, never an ambient cache.
The complete restore inventory must equal the candidate bank, not a subset.

Qualification associations use candidate logical_object_id/edition_id/layer plus
the exact wrapper artifact role and byte hash; equal hashes alone do not associate
different objects. Every qualification cell remains visible, including inactive,
invalid or missing evidence. Native lifecycle artifact identity/source/content
bindings must reconcile matching candidate cells. Current active lifecycle heads
must be present by exact identity/hash/BLAKE3/size. Historical inactive payloads
may be unavailable after removal: retain explicit missing historical payload
coverage, without fetching, retaining unsafe bytes, claiming fixity or erasing
their metadata. Supplied historical bytes must agree exactly when present.

The coordinator must not treat missing native bundles as successful checks.
Wrongly bound supplied evidence rejects the operation. Well-bound but blocked
native results remain blocked; they cannot be repaired or converted into a pass.
Disclosure uses only mapped Gold count diagnostics and retains accountable review
as pending; other formats/units remain unsupported. A separate exact dependency
parser/SBOM/package contract will be frozen before that component is implemented.
No not_applicable state is granted merely from a role or a supplied receipt.

## Frozen supplied dependency evidence

Implement `assess_dependency_evidence(lock_raw, sbom_raw, package_bindings_raw,
*, project_name, candidate_id, as_of, candidate_bank, scope_objects)` and its exact
verifier in a pure module. No path-based lock loader, package import, installation,
registry request, audit command or supplied code execution. Existing LockedPackage,
LockInventory and deterministic SPDX builder may be reused in memory; a synthetic
Path label on LockInventory is metadata only and must never be opened.

All three metadata inputs are nonempty bytes at most 1 MiB; candidate bank uses
the inventory's 8 MiB/member and 26 MiB total bounds, checked before hashing.
The lock is strict UTF-8 TOML with bounded parsed tree (depth 16, 50,000 nodes,
2,000 entries/container, strings 4,096, integers 4,096 bits, finite numbers).
Reject unsupported native TOML datetime values rather than coercing them. Scan
decoded key/string values for existing secret patterns before returning any
identity metadata. SPDX and bindings use strict JSON preflight. The raw lock,
SPDX and bindings must all occur exactly by hash/bytes in the candidate bank.

Lock version is exactly integer 1. package is a nonempty list of at most 500
records. Each record requires a bounded normalized Python package name and
nonempty bounded version, source, and optional dependency/distribution arrays.
Exactly one record matches project_name after canonical normalization. Duplicate
name/version pairs and colliding computed SPDX IDs reject. Every dependency name
in core, optional and development groups must resolve to a supplied package;
references from non-project packages back to the project root reject rather than
being silently dropped by the existing SPDX builder. Unknown fields are retained
in the bound raw bytes but never treated as validated semantics.

Dependency items are dicts with name and optional version/source/marker; groups
are bounded dicts of such arrays. Build a conservative all-branch graph: project
core dependencies are runtime_direct; optional/development groups are
development_direct; non-root packages include all declared groups. All locked
versions of a referenced canonical name participate; this is not an environment-
specific solver or proof of actual imports. Do not silently omit unresolved edges.
Precompute the expanded SPDX relationship count and reject more than 5,000
before building the document; its complete canonical bytes must remain within
1 MiB. Oversized graphs stop, never truncate edges or select convenient versions.

The project source is exactly editable='.'. Non-root package sources are exactly
registry='https://pypi.org/simple'. Other source kinds remain unsupported and fail
this bounded graph contract. Source locations are never requested. Each sdist
record and wheel entry requires url, hash and size, allowing additional metadata
such as upload-time without claiming its authenticity. URL is HTTPS on
files.pythonhosted.org, with the same no-credential/query/fragment/port/control
rules as restore locators. Hash is sha256: followed by 64 lowercase hex; size is
a positive integer, not bool. Conflicting size declarations for a shared digest
reject. Distribution declarations without bytes remain explicitly unavailable.

Recompute the entire SPDX document using existing build_spdx_document with scope
build, release_version from the project lock record, created_at equal as_of,
namespace_base='https://global-family-justice-data.example/spdx', and
project_uri='https://github.com/edithatogo/global-family-justice-data'. Compare
canonical complete supplied SPDX, not field presence or a supplied status. The
example namespace is a declaration and is never published or requested.

Package bindings exact keys: contract_version (`gfjd-candidate-package-bindings-v1`),
candidate_id, lock_sha256, sbom_sha256, packages. packages contains at most 500
unique object_id entries, each exactly object_id, name, version, distribution_sha256.
Each points to a candidate role=package object and an exact declared non-root
lock package/distribution. Recompute candidate bytes' SHA/size and require the
locked distribution size too. A declaration cannot bind an unrelated archive.
Every unbound candidate package stays explicitly unsupported; not all packages
are Python distributions, and no other package may borrow these checks.

Report bound input hashes, package/edge/distribution counts, exact validated
candidate package bindings, missing distribution digests, unbound package object
IDs, and component fingerprints. Do not emit registry responses, source bytes or
raw unvalidated lock fields. Internal graph/SPDX consistency may be checked;
artifact authenticity, signatures, provenance attestations, vulnerability-feed
freshness/completeness, actual imports and release authority remain unverified.
Neither a supplied audit success nor an SBOM license field grants clearance.

## Frozen coordinator applicability and report rules

Scan every unique candidate digest once, then retain results for every inventory
object/role edge. Report no source excerpts. Fixity and locator syntax apply to
every object. Secrets/prohibited-data statuses come from the bounded scanner;
role labels never suppress findings or unsupported coverage. Do not introduce a
role-only not_applicable shortcut for any dimension.

Disclosures remain unsupported except an exactly mapped Gold data object's
recomputed quality/quarantine diagnostics. Verified bounded count diagnostics may
be checked_no_findings; failed diagnostics remain failed, and absent checks remain
missing_evidence. This never supplies the pending accountable disclosure decision.

Qualification mapping is compiler-controlled: data maps source for B0 and rows
for B1/Silver/Gold; transformation maps contract for B1/Silver; manifest maps
manifest for Platinum. Metadata may map a wrapper's own file digest or exact
capture/safety/custody/rights/restore/receipt/history/checkpoint/semantic/quality/
policy/disclosure/owner/scope/federation artifact roles. Match logical_object_id,
edition_id and layer before bytes. Record the matched role explicitly. More than
one different eligible role for a candidate is unsupported ambiguous provenance,
not a convenient selection. Every supplied qualification wrapper must have a
corresponding candidate wrapper entry. Cells with no supplied wrapper remain
visible as missing; they are not assigned a fabricated wrapper or dropped.

Native qualification/restore control bytes must occur in the candidate bank,
including inactive wrapper payload references. Native replica membership equals
candidate membership. The restore bundle must reference the same scope/contract
as any qualification bundle. Lifecycle current active heads must match exact
candidate identities, bytes and active state; matching historical objects must
match declared size/BLAKE3/state too. Missing inactive historical payloads appear
as digest-only gaps. A shared identity with inconsistent bytes/state rejects.
For B0 an exact object/edition identity cannot change source bytes. For derived
objects different historical revisions remain distinct by content hash. Supplied
source edges must agree with the native source digest and object/edition; missing
source edges remain explicit missing provenance. When qualification and lifecycle
both supply a source binding for the same object/edition, those digests must agree.
For derived lifecycle evidence, the source edge must target the exact same logical
object and edition at the immediate predecessor layer; digest equality alone cannot
associate an unrelated object.

Provenance may establish only the mapped native check or declared control-file
association. Data derivation requires its mapped cell's verified lineage (B0
retains capture authenticity as a separate pending fact). Nonmapped candidates
remain missing_evidence; arbitrary equal hashes do not establish association.
Package-member edges reconcile the scanner's complete member-content-hash multiset
before package composition can be internally checked; this is not executable
package authenticity. Unsupported package scanning remains unsupported composition.
Composition evidence combines with native provenance by fail-closed severity and
cannot downgrade a failed native-provenance result.

Dependencies and supply-chain graph checks apply to exact dependency bundle
inputs and validated candidate distribution bindings. Unbound packages remain
unsupported; missing bundles stay missing_evidence. Non-executable applicability
is not inferred merely from data/metadata labels: without a suitable compiler
proof, keep other members unsupported rather than claiming not_applicable.
Actual import coverage, signatures, audit freshness, publisher authenticity and
key custody remain separate unverified facts even for matched internal graphs.

Report per-object eight-dimension statuses, scanner codes/severities, exact mapped
evidence references, package composition results and missing/unsupported coverage.
Native reports are recomputed and hash-bound; emit only closed-code/count/digest
summaries, mapped candidate identities and all cell statuses, not arbitrary nested
source or review strings. Preserve lifecycle historical gaps and declared provider
backlog. All control identifiers emitted from native evidence must reconcile with
guarded candidate identifiers or be represented by hashes.

Mechanical coverage completeness requires every required dimension to be checked
without failure/missing/unsupported states; it is not factual acceptance. No
source-byte acquisition, comprehensive safety, absence of unresolved critical
risks, rights, promotion, publication, public restore, release or gate authority
is established. Release remains blocked regardless of a successful mechanical
subset. Findings use compiler-owned severity and are never downgraded by callers.
