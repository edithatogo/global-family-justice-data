# Global Family Justice Data Project

A reproducible, international source census and harmonised data platform for family-justice performance, process, outputs, experiences and outcomes.

## Purpose

The project is designed to answer four different questions without conflating them:

1. **What is published?** A complete, auditable catalogue of public family-justice data and reports for every jurisdiction searched.
2. **How do systems operate?** Source-faithful measures of demand, throughput, timeliness, process and resources.
3. **What decisions and subsequent events occur?** Orders, appeals, enforcement, repeat applications and other administrative outcomes.
4. **What happens to children and families?** User experience, safety, stability, wellbeing and equity evidence, usually derived from surveys, evaluations or linked research rather than routine court statistics.

The unit of analysis is a **family-justice matter**, not an institution called a “family court”. Many jurisdictions hear family matters in general civil, district, religious, customary or specialist courts.

## Repository principles

- Preserve the original source, definition, language, unit and calculation before harmonising.
- Keep **source-native**, **normalised** and **comparative** data in separate layers.
- Record negative findings: “searched, no public data found” is a valid result.
- Compare only measures with compatible case types, clocks, denominators and statistical summaries.
- Do not create a single country ranking during the initial phases.
- Publish aggregate data only; do not collect identifiable case-level records in this public repository.
- Retain provenance to page, table, cell, API query or dashboard filter.

## Data layers

- `data/seed/` — starter jurisdiction, source and indicator registers.
- `data/raw/` — source manifests and, only where redistribution is permitted, immutable source files.
- `data/bronze/` — source-native extracted tables.
- `data/silver/` — normalised long-format observations with original definitions retained.
- `data/gold/` — explicitly comparable indicators and analytical releases.

## Start here

1. Read `PROJECT_PLAN.md`.
2. Review `docs/methods/scope-and-unit-of-analysis.md` and `docs/methods/indicator-framework.md`.
3. Add a jurisdiction to `data/seed/jurisdiction_register.csv`.
4. Complete a search log using `docs/templates/source-search-log.md`.
5. Add sources to `data/seed/source_register.csv`.
6. Validate the seed files:

```bash
PYTHONPATH=src python -m gfjd.validate
```

## Working title

“Global Family Justice Data Project” is descriptive and provisional. Branding, institutional ownership and the long-term host should be decided by the founding group.

## Status

Starter repository scaffold, version 0.1, prepared 19 July 2026.
