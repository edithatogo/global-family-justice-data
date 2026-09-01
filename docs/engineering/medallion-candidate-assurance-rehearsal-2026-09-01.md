# Fictional complete candidate-assurance rehearsal

Status: repository-owned supporting evidence only. Functional source is signed
commit `5b2acf37111aa9f0bd1da2e682e350293cf46676`.

The coordinator binds the complete declared candidate bank before hashing, scans
each unique digest once, reports all seven roles and every lifecycle declaration,
recomputes typed qualification/restore/lifecycle/dependency evidence, reconciles
package-member hash multisets, and emits eight dimensions for every object.
Verification recomputes the entire report and rejects a rehashed success forgery.

The fictional all-role rehearsal contains seven objects and reports seven rows in
each dimension. It intentionally remains blocked: provenance and dependency
evidence are missing, disclosure is unsupported, the package is unsupported, one
plain-text prohibited-data check is unsupported, and both locators are absent.
This is evidence that missing/unsupported states survive—not a release failure
being disguised as a pass. Focused component and coordinator validation passed
172 tests before closeout review.

Adversarial coverage includes escaped JSON credentials, used and unused escaped
XML namespace credentials, XML event/string bounds, unsafe ZIP metadata, nested
containers, malformed formats, prohibited headers, complete candidate and role
budgets, evidence-tree bombs, wrong bindings, whole-SPDX drift, dependency graph
ambiguity, package-byte mismatch, package-member multiset mismatch, inactive
objects, auxiliary secrets, preflight-before-scan, scan-once deduplication,
network-disabled locator syntax and forged report self-hashes. Hosted review then
identified two sibling-association defects. Commit `d30d70d` added meaningful
failing regressions and now requires exact Gold row mapping for disclosure plus a
unique lifecycle content match across sibling roles; the focused suite passes 174
tests. A second hosted review then identified missing source-edge enforcement and
incorrect treatment of missing historical bytes when a newer sibling existed.
Commit `9640d23` requires an exact immediate-predecessor edge for derived native
provenance and preserves unmatched inactive artifacts as digest-only gaps. The
focused suite now passes 176 tests.
An exact-head review then found digest-only wrapper association. Commit `fa3d650`
requires wrapper logical object, edition and layer identity before digest matching;
both mismatched-identity and unrelated-duplicate regressions now pass. The focused
suite passes 178 tests.
The following completed review found three further fail-closed defects. Commit
`8e437cd` prevents exact edges from masking failed native lineage; matches lifecycle
SHA-256, BLAKE3, size and declared source; and prevents unbound package objects from
borrowing dependency success through shared metadata bytes. The focused suite
passes 181 tests.

No network, provider, source, package installer, executable, vulnerability feed or
locator was requested. Internal consistency does not establish actual inventory
completeness, comprehensive privacy/security, rights/disclosure acceptance,
publisher or artifact authenticity, vulnerability freshness, remote restore,
custody, signing, release authority, maturity promotion or gate passage.
