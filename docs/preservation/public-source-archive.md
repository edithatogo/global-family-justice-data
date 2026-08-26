---
license: other
pretty_name: Global Family Justice Data exact-edition source archive
tags:
  - public-records
  - family-justice
  - data-preservation
---

# GFJD public exact-edition source archive

This is the public Bronze B0 preservation layer for the Global Family Justice Data project.
It contains exact source editions acquired from official publishers, alongside content digests and
a fail-closed public-safety receipt. It is an archival source collection, not a harmonised dataset,
a Gold release, or a claim that the editions are comparable.

Each object is stored under `sources/<inventory-id>/`. The authoritative identity is its SHA-256
and BLAKE3 digest in `public_b0_safety.json`; filenames and hosting URLs are locators only. A second
provider-separated copy is retained as assets on the corresponding GitHub archival release.

The source publishers retain any applicable copyright or database rights. Redistribution here is
for preservation, reproducibility, verification, and public-interest research. Attribution should
name the original publisher and exact edition. Third-party material within an edition may carry
different conditions. If a publisher supplies a corrected or superseding edition, the archive
appends it and links the relationship rather than overwriting historical bytes.

Safety controls reject credentials, prohibited person-level data fields, encrypted or active PDF
content, unsafe archive members, and digest mismatches. Passing this control does not establish
semantic equivalence, methods acceptance, publication readiness, or a downstream programme gate.

Project repository: https://github.com/edithatogo/global-family-justice-data
