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

- [~] Candidate-byte scanner with hard text/JSON/CSV/XLSX/ZIP bounds and explicit
  unsupported outcomes for other formats; immutable finding codes and no output
  excerpts. This is a component, not complete WI-G5-MED-03 preparation.
- [ ] Full candidate inventory/root/role-edge/locator binder; exact supplied-bank
  membership and SHA-256/BLAKE3/size, preserving all declared categories.
- [ ] Typed qualifier/restore/lifecycle evidence-input binding and independent
  recomputation; reject wrong candidate/time/scope associations. Do not accept
  precomputed "passed" reports as proof.
- [ ] Pure supplied-byte lock/SBOM dependency graph and package-binding checks;
  retain vulnerability-feed freshness, authenticity and signatures as unverified.
- [ ] Eight-dimension coordinator: fixity, secrets, prohibited data, disclosure,
  dependencies, provenance, supply chain and locators for every inventory member.
  Compiler-owned applicability and finding severity; no caller-provided waivers.
- [ ] Fictional all-role rehearsal and adversarial tests including unsupported
  package/media, auxiliary secret, omitted history, false audit/disclosure success,
  lock/SBOM mismatch, unsafe locator and rehashed report forgery.
- [ ] Role-separated review, full validation, signed reviewed PR, CI, merge and
  local cleanup; then audit the entire authorized queue and remaining gaps.

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
