# Global Family Justice Data Project

A reproducible international source census and harmonised data platform for family-justice reporting, process, outputs, administrative outcomes, user experience, and child and family outcomes evidence.

## Project objective

The project is designed to answer four questions without conflating them:

1. **What is published?** An auditable catalogue of official and credible family-justice data and reports for every jurisdiction searched.
2. **How do systems operate?** Source-faithful measures of demand, throughput, timeliness, process, resources, and access.
3. **What decisions and subsequent events occur?** Orders, appeals, enforcement, repeat applications, return to court, and related administrative outcomes.
4. **What happens to children and families?** A structured catalogue of user experience, safety, stability, wellbeing, equity, and longer-term outcomes evidence, usually drawn from surveys, evaluations, cohorts, or linked research rather than routine court statistics.

The unit of analysis is a **family-justice matter in a defined legal and institutional setting**, not an institution that happens to be called a “family court”. Family matters may be handled by specialist, civil, district, magistrates’, religious, customary, child-protection, or administrative bodies.

## Current status

**Version 0.2.0 — v1 production roadmap and hardening scaffold.**

This repository is not yet the stable data product. The roadmap now defines a staged path to a mature v1.0 with release gates for global discovery, data quality, reproducibility, security/privacy, governance, operations, documentation, and sustainability.

Start with:

- `ROADMAP.md` — stages, delivery tracks, and critical path to v1;
- `docs/strategy/V1_RELEASE_CRITERIA.md` — binding definition of done;
- `docs/strategy/DELIVERY_TRACKS.md` — twelve track charters;
- `PROJECT_PLAN.md` — programme scope, sequencing, resources, and controls;
- `ARCHITECTURE.md` — target data and release architecture.
- `docs/strategy/V1_EPICS.md` — executable v1 epic backlog.
- `docs/strategy/GITHUB_PROJECT_MODEL.md` — GitHub Projects fields, views, milestones, and definitions of done.

## What stable v1.0 means

Version 1.0 will be reached only when the project is:

- **globally auditable:** every in-scope jurisdiction has a documented coverage status and search evidence;
- **scientifically defensible:** definitions, clocks, denominators, cohorts, and comparability are explicit;
- **fully traceable:** every published observation points to an exact source location and transformation lineage;
- **reproducible:** a clean environment can validate and build the public release;
- **secure and ethical:** public outputs contain aggregate, non-identifiable information and pass rights and disclosure review;
- **operationally supportable:** releases, corrections, monitoring, backup, restore, and rollback have named owners and tested runbooks;
- **durable:** artifacts are archived, versioned, citable, and funded for post-release review cycles.

A global source census can be complete even when a jurisdiction publishes no useful data. Absence, inaccessibility, or non-comparability are explicit findings, not reasons to omit a jurisdiction.

## Core release products

The v1 release bundle is intended to include:

- jurisdiction and responsible-institution register;
- source and reporting census;
- outcomes-evidence catalogue;
- matter and indicator ontology;
- bronze, silver, and bounded gold datasets;
- jurisdiction profiles and global data-availability atlas;
- quality, coverage, methods, and limitations reports;
- CSV, Parquet, and DuckDB files;
- schemas, checksums, build metadata, citation file, and archival persistent identifier.

The first release will not include identifiable records, causal claims unsupported by study design, or a composite country ranking.

## Repository principles

- Preserve original source language, labels, definitions, units, and calculations before harmonising.
- Keep source-native, normalised, and comparative data in separate layers.
- Retain negative findings and failed comparisons.
- Distinguish prospective listing waits, retrospective case duration, first-hearing waits, and pending-case age.
- Do not pool means, medians, percentiles, or threshold measures without an explicit approved method.
- Model federal and devolved systems at the level that controls the relevant family-justice function.
- Retain provenance to page, table, cell, API query, dashboard filter, or equivalent locator.
- Never silently overwrite a released value.
- Keep restricted person-level linkage research outside the public repository.

## Data layers

- `data/seed/` — human-maintained jurisdiction, source, indicator, evidence, and observation templates.
- `data/raw/` — source manifests and only lawfully redistributable immutable source files.
- `data/bronze/` — source-native extracted tables.
- `data/silver/` — normalised long-format observations with source meaning retained.
- `data/gold/` — reviewed, explicitly comparable analytical releases.
- `data/quality/` — generated validation, coverage, audit, and lineage reports in the target architecture.

## Local validation

The current scaffold uses Python 3.11 or later.

```bash
python -m pip install -e ".[dev]"
make check
```

For a dependency-light structural check:

```bash
PYTHONPATH=src python -m gfjd.validate
```

After changing tracked files, regenerate the checksum manifest before the full check:

```bash
make manifest-update
make check
```

## Contribution workflow

1. Read `CONTRIBUTING.md` and the relevant methods documents.
2. Open the appropriate source, correction, or methods issue.
3. Preserve original wording and exact provenance.
4. Run validation and tests.
5. Obtain second review for gold-layer data or material methods changes.

Potential security, credential, or privacy issues must follow `SECURITY.md`, not a public issue.

## Governance and support

- `GOVERNANCE.md` defines decision bodies and independence safeguards.
- `MAINTAINERS.md` defines accountable operating roles.
- `SUPPORT.md` defines corrections and support principles.
- `docs/operations/RELEASE_PROCESS.md` defines release and patch controls.

## Working title

“Global Family Justice Data Project” remains a descriptive working title. The institutional host, public identity, domain, and long-term repository ownership must be settled before public beta.
