# v1 technical and data architecture

## 1. Architectural principles

1. **Release artefacts are authoritative.** A dashboard or API may fail without making the dataset unavailable.
2. **Lineage is a first-class product.** Every gold observation traces to source evidence and transformation rules.
3. **Source-native meaning is preserved.** Harmonisation adds fields; it does not erase original labels or definitions.
4. **Aggregate public boundary.** Person-level research is separated into a governed secure environment.
5. **Open and portable outputs.** Core use does not depend on proprietary software.
6. **Immutable releases, mutable working layers.** Corrections create new versions rather than rewriting history.
7. **Least privilege and separable environments.** Development, review and publication credentials are distinct.
8. **Automation with controlled manual paths.** PDFs and dashboards may require manual extraction, but every step is documented, reviewed and testable.

## 2. Logical flow

```text
Official/public sources and approved research evidence
        |
        v
Acquisition + rights check + retrieval manifest + checksum
        |
        v
Raw evidence store (immutable where lawful)
        |
        v
Bronze: source-native extraction
        |
        v
Silver: normalised structure + original definitions retained
        |
        v
Quality, mapping, comparability and disclosure gates
        |                         \
        v                          v
Gold comparative data          Quarantine / descriptive-only evidence
        |
        v
Immutable release builder
        |
        +--> CSV / JSON metadata
        +--> Parquet / DuckDB
        +--> methods, profiles and quality reports
        +--> checksums, signatures, citation and archive deposit
        |
        v
Derived website, atlas, dashboard and API/query layer
```

## 3. Repository and storage boundaries

### Public monorepo

Contains:

- code, tests, workflows and configuration templates;
- schemas, ontology and indicator dictionaries;
- jurisdiction/source metadata and redistributable aggregate data;
- methods, governance, security and operational documentation;
- release manifests, checksums and citation files.

### Controlled source storage

Contains large, restricted or non-redistributable source material where lawful. The public repository stores a manifest, rights status, checksum and access route rather than the file itself.

### Archive

Each stable release is deposited in two technically and provider-separated preservation locations under sole-owner custody. Archive identities, custody records, restore receipts and checksums are included in the release evidence pack.

## 4. Environments

| Environment | Purpose | Data boundary |
|---|---|---|
| Local development | Code and fixture development | Synthetic/test data and approved public samples |
| Integration | Connector and pipeline testing | Public or controlled aggregate sources; no production secrets in code |
| Release candidate | Rehearsal and assurance | Frozen source snapshot and candidate artefacts |
| Production publication | Public release and derived services | Approved immutable aggregate release only |
| Secure research (separate programme) | Any approved person-level linkage | Not part of the public monorepo or v1 public architecture |

Promotion between environments is automated and recorded. Production is not used as a manual editing environment.

## 5. Core entities and stable identifiers

Required entity families:

- jurisdiction and subnational jurisdiction;
- institution/court system;
- matter type and proceeding type;
- source and source edition;
- indicator and local measure;
- observation/series;
- extraction event and transformation;
- review and assurance record;
- release and artefact.

Identifiers must be stable, unique, documented and non-reusable. Human-readable names and country codes are attributes, not primary keys. A rename or political/administrative change does not silently mutate identity.

## 6. Data contracts

Each public contract has:

- schema version;
- required and optional fields;
- allowed values and semantic definitions;
- uniqueness and referential rules;
- null/missingness semantics;
- compatibility tests;
- example fixtures;
- migration guidance;
- deprecation history.

Breaking changes are prohibited in 1.x except under an emergency exception approved and documented through governance.

## 7. Pipeline controls

### Acquisition

- explicit source ID and edition;
- canonical URL/query/filter parameters;
- retrieval timestamp and agent version;
- checksum and content type;
- rights status and storage decision;
- retry/rate-limit/error records;
- source-change fingerprint.

### Extraction

- original table/field labels;
- page/sheet/cell/query/dashboard locator;
- extraction method and tool version;
- value and unit preservation;
- reviewer and review status;
- confidence/ambiguity flag.

### Transformation

- versioned rule or code reference;
- input and output identifiers;
- unit conversion and formula detail;
- ontology mapping version;
- exceptions and manual adjudication record;
- deterministic output where feasible.

### Publication

- release candidate snapshot;
- validation and quality reports;
- release diff against prior version;
- licence/disclosure/security checks;
- signed manifest and checksums;
- archive deposit and deployment record.

## 8. Public release bundle

A v1 release should include:

```text
release/<version>/
├── data/
│   ├── jurisdictions.csv
│   ├── sources.csv
│   ├── indicators.csv
│   ├── observations.csv
│   ├── outcomes_evidence.csv
│   ├── gfjd.parquet (or partitioned Parquet)
│   └── gfjd.duckdb
├── schemas/
├── ontology/
├── profiles/
├── methods/
├── quality/
├── provenance/
├── CHANGELOG.md
├── CITATION.cff
├── RELEASE.json
├── MANIFEST.sha256
├── SBOM.json
└── signatures/
```

The exact layout may evolve in 0.x but is frozen before the v0.9 release candidate.

## 9. Derived services

The website/dashboard/API must:

- load only approved release artefacts;
- expose the release version and data vintage;
- show definitions, source and comparability tier near outputs;
- prevent Tier 3/4 data from appearing as direct comparisons;
- support export of the underlying rows;
- avoid recording sensitive query content;
- degrade gracefully to downloadable files;
- be fully rebuildable from infrastructure/configuration and release artefacts.

## 10. Non-functional requirements for v1

- clean-room reproducibility of core release artefacts;
- role-separated analyst-agent preparation and verification, followed by sole-owner authorization for every production, signing, publication or release step;
- protected release branch and reviewed changes;
- deterministic identifiers and stable public contracts;
- observable failures and source staleness;
- no loss of immutable releases;
- restore of public access within two business days after a major failure;
- support for current and previous minor release;
- accessible and low-bandwidth paths to core data and documentation;
- no public exposure of person-level case data or operational secrets.

## 11. Architecture decisions required before G2

- authoritative jurisdiction identity system;
- source-edition and observation-series identifier format;
- release storage and archival host;
- workflow/orchestration approach;
- tabular/analytical release formats;
- dashboard/API technology and whether the API is required for v1;
- signing/provenance approach;
- rights-restricted source storage arrangement;
- monitoring/ticketing platform;
- localisation content model.

Each material decision is recorded as an architecture decision record with context, options, decision, consequences and review date.
