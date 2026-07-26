# Architecture

## Design goals

The architecture must preserve source meaning, support multilingual and heterogeneous reporting, make every public value traceable, and allow a release to be rebuilt from a clean checkout plus authorised external storage.

## Logical layers

1. **Registry layer** — jurisdictions, institutions, sources, indicators, outcomes evidence, and transformation metadata.
2. **Raw manifest layer** — retrieval recipes, source versions, checksums, rights, and storage references. Raw source files are included only where redistribution is permitted.
3. **Bronze layer** — source-native extracted tables with minimal structural change.
4. **Silver layer** — normalised records retaining original labels and definitions.
5. **Gold layer** — reviewed analytical tables containing only explicitly approved comparisons.
6. **Publication layer** — release packages, profiles, atlas, documentation, and machine-readable quality reports.

## Core invariants

- Raw and bronze inputs are immutable within a release.
- Generated silver and gold files are never hand-edited.
- Every silver/gold record references a source and transformation lineage.
- Original language and source definitions are preserved.
- Missing, suppressed, unavailable, not applicable, and not searched are distinct.
- Tier 3 and Tier 4 records cannot enter direct-comparison products.
- Public outputs contain no person-level family-justice records.

## Proposed repository layout

```text
.
├── data/
│   ├── seed/          # human-maintained registries and templates
│   ├── raw/           # manifests; redistributable sources only
│   ├── bronze/        # source-native extracts
│   ├── silver/        # normalised observations
│   ├── gold/          # approved comparative releases
│   └── quality/       # validation and audit outputs
├── docs/
│   ├── methods/
│   ├── strategy/
│   ├── operations/
│   ├── decisions/
│   └── templates/
├── schemas/           # versioned data contracts
├── src/gfjd/          # validation, acquisition, transformation, and release code
├── tests/              # unit, integration, contract, and regression tests
└── dist/               # generated release artifacts; not hand-maintained
```

## Identifiers

Identifiers must be stable, opaque enough not to encode changeable meaning, unique across releases, and never reused. Human-readable labels may change without changing IDs. Deprecated records remain resolvable and point to any replacement.

## Versioning

- Repository/software uses semantic versioning.
- Schemas and ontologies carry independent versions.
- Data releases record repository commit, schema versions, ontology versions, input source versions, and transformation versions.
- Patch releases correct data or documentation without breaking contracts.
- Minor releases add backwards-compatible fields, indicators, or jurisdictions.
- Major releases may change contracts or semantics and require migrations.

## Reproducible releases

A release build should:

1. validate registries and schemas;
2. verify source manifests and expected inputs;
3. execute transformations in dependency order;
4. run quality and comparability checks;
5. produce CSV, Parquet, DuckDB, documentation, and quality reports;
6. generate checksums and build metadata;
7. compare against the prior release and require approval for material changes;
8. package and archive immutable artifacts.

## External storage

Large, licensed, or access-controlled source artifacts belong in managed object or archival storage. The repository stores metadata, checksums, access conditions, and retrieval references. Restricted person-level data are outside this architecture entirely.

## Reliability and observability

Production workflows should expose:

- successful and failed retrievals;
- source change and staleness status;
- row counts and schema changes by stage;
- validation failures and warning trends;
- data lineage completeness;
- release build duration and artifact checksums;
- unresolved corrections and incidents.
