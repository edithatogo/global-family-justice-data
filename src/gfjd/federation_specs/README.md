# Pinned federation validation assets

These technical specification assets are not court-source data, dataset rights
records, empirical observations or publication evidence. No validator may fetch
a missing asset or resolve a remote reference implicitly.

## OpenLineage 2-0-2

`openlineage-2-0-2.json` is an unchanged copy of the OpenLineage project's
`spec/OpenLineage.json` at commit
`e47a7d5a7d2e6887fe5ed737754f3f03a3721b08`:

- Source: https://raw.githubusercontent.com/OpenLineage/OpenLineage/e47a7d5a7d2e6887fe5ed737754f3f03a3721b08/spec/OpenLineage.json
- Schema identifier: https://openlineage.io/spec/2-0-2/OpenLineage.json
- Bytes: 9,155
- SHA-256: `69f68bee00b9beac88a87059c0102410e7bb05f3f43c46d02a0409831eceb0d2`
- Licence: Apache-2.0; the unchanged upstream licence is included as
  `OpenLineage-LICENSE.txt`, SHA-256
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.

Attribution: OpenLineage project and contributors. The upstream root tree at
that commit contains no NOTICE file. GFJD's design-event profile is separate
implementation code; it does not modify the normative schema. The schema's
licence does not grant rights to any data described by a validated event.

Full schema validation and a bounded design-event profile are not proof of
complete execution lineage, source truth, full interoperability, registration,
or any accountable acceptance. Additional standards, facet schemas and
execution-lifecycle controls remain tracked in the federation preparation plan.

## DCAT-AP 3.0.1 base and range shapes

The two `dcat-ap-3.0.1-*.ttl` files are unchanged upstream artifacts from
`releases/3.0.1/html/shacl/` at commit
`729eddfc176d0afee5850ade6528f96f72579412` in SEMICeu/DCAT-AP:

| Upstream file | Bytes | SHA-256 |
| --- | ---: | --- |
| `shapes.ttl` | 20,619 | `7fe9815e0f32b10f5cbce74fa6ccd0290aae3ef9e5080fb84e2d8093eb984d1d` |
| `range.ttl` | 12,490 | `24d3bfd0fa17a3d0e877c9ebb91c8174124e5038538e1bf081b2cb679ad0f1b2` |

Source directory: https://github.com/SEMICeu/DCAT-AP/tree/729eddfc176d0afee5850ade6528f96f72579412/releases/3.0.1/html/shacl

Attribution: Copyright 2025 European Union, SEMIC DCAT-AP contributors.
Licence: Creative Commons Attribution 4.0 International,
https://creativecommons.org/licenses/by/4.0/ . The upstream recommendation's
licence statement is https://semiceu.github.io/DCAT-AP/releases/3.0.1/#license .
No content changes were made; only the local filenames have versioned prefixes.
This attribution is not an endorsement of GFJD and does not license GFJD data.

Only the base and range shape sets are included here. Controlled-vocabulary
closure, recommended shapes, deprecated-URI checks and full application-profile
conformance are not established by these files. The upstream import manifests
are not executed, and no mutable vocabulary or ontology is fetched implicitly.

## RO-Crate 1.3 context

`ro-crate-1.3-context.jsonld` is the unchanged 196,942-byte technical context at
ResearchObject/ro-crate commit `22fbd7e098ccd2839c80967e363a2201528a2efe`,
path `docs/_specification/1.3/context.jsonld` (release tag `1.3.0`). SHA-256:
`5a3df1a43185501db4d45cdde5a478c57eeb1d673eedfe400488fc4c4b21dd91`.

Source: https://github.com/ResearchObject/ro-crate/blob/22fbd7e098ccd2839c80967e363a2201528a2efe/docs/_specification/1.3/context.jsonld

Attribution: University of Technology Sydney, University of Manchester and
RO-Crate contributors. The context is CC0 1.0, as stated separately from the
documentation licence at
https://www.researchobject.org/ro-crate/specification/1.3/index.html .
No content modification was made; the filename is versioned locally. The
context identifies vocabulary terms, not proof of dataset rights or publication.
It is bound and inspected as supplied bytes, never resolved through a loader.

## GFJD Croissant declaration profile

`gfjd-croissant-profile-v1.json` is GFJD-authored configuration, not a normative
Croissant schema or a modified specification. It references Croissant 1.1 by
MLCommons Association and contributors:
https://docs.mlcommons.org/croissant/docs/croissant-spec-1.1.html .
The unchanged specification remains at that link under its CC BY-ND 4.0 terms.
GFJD's restricted checks do not establish full conformance, extraction,
publication, licence validity or custody of declared distributions.

## Pinned partner technical references

The following unchanged technical files were read from local Git objects, not
from court-source endpoints. Python files are packaged with a `.py.txt` suffix
and are never imported or executed by the reference adapter. JSON schemas are
checked for syntax only. No partner registration, operational compatibility,
publication receipt or rights to underlying data follows from these copies.

Archive Govt NZ reference commit:
`af427c2632239a8869684c849c0fcc1981277b02`, repository
https://github.com/edithatogo/archive-govt-nz .

| Local filename | Original path |
| --- | --- |
| `partner-archive-ownership.py.txt` | `src/archive_govt_nz/foi_ownership.py` |
| `partner-archive-publication.schema.json` | `schemas/archive/v1/publication-receipt.schema.json` |
| `partner-archive-LICENSE.txt` | `LICENSE` |

Global Medicines Atlas reference commit:
`f7550d5f84b6a831cd99c3b6882c0d33c4b0c939`, repository
https://github.com/edithatogo/global-medicines-atlas .

| Local filename | Original path |
| --- | --- |
| `partner-gma-federation.schema.json` | `contracts/medallion/v4/federation.schema.json` |
| `partner-gma-semantics.py.txt` | `src/global_medicines_atlas/federation.py` |
| `partner-gma-LICENSE.txt` | `LICENSE` |
| `partner-gma-NOTICE.txt` | `NOTICE` |

Attribution: the respective repository contributors; Global Medicines Atlas
copyright 2026 Edith Atogo. Both software references are Apache-2.0; their
unchanged licences and the Global Medicines Atlas NOTICE are included. The
Archive Govt NZ root at the recorded commit has no NOTICE file. Contents are
unchanged; only local filenames differ. All seven asset digests are pinned in
`tests/test_federation_specs.py`; the four contract digests and commit identities
are additionally pinned in `gfjd.federation_partner_interfaces`.

Archive ownership allowlists do not include GFJD. Global Medicines Atlas's
B0 index / B1 metadata / B2 raw definitions are not direct aliases for GFJD's
medallion layers. These limitations remain explicit in every assessment.
