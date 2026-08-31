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
