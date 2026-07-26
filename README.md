# Global Family Justice Data Project

A reproducible international source census and harmonised data platform for family-justice process, performance, outputs, experiences and outcomes.

## Current status

This repository is a **v0.3.0 engineering and programme-control baseline**. It now contains an executable conductor, data contracts, validation, acquisition, harmonisation, quarantine, provenance and deterministic release tooling. It is **not** a completed international dataset and must not be represented as v1.0.

The repository is intentionally fail-closed. At this baseline:

- no stage gate has passed;
- the declared active gate is **G1 — Foundation controls accepted**;
- the evidence-assured maturity floor is **L0**, although the self-assessed implementation floor is L1;
- the seed catalogue contains jurisdictions, sources, indicators and matter types, but the gold observation layer is empty;
- draft documents and implemented code are not treated as accepted evidence without independent review.

The target v1.0 is a governed, independently assured and maintainable public-data product with stable contracts, immutable releases, tested recovery, production-like soak and a funded 1.x operating model.

## Start here

- [`V1_HARDENING_REPORT.md`](V1_HARDENING_REPORT.md) — executive implementation assessment, verified baseline and recommended next steps;
- [`ROADMAP.md`](ROADMAP.md) — integrated capability path from v0.3 to a stable v1.0;
- [`V1_0_RELEASE_CRITERIA.md`](V1_0_RELEASE_CRITERIA.md) — binding definition of done and no-go conditions;
- [`docs/architecture/conductor-system.md`](docs/architecture/conductor-system.md) — the programme control plane;
- [`docs/development/implementation-status.md`](docs/development/implementation-status.md) — what is implemented and what is not;
- [`docs/development/v1-gap-analysis.md`](docs/development/v1-gap-analysis.md) — prioritised improvements and remaining work;
- [`docs/quality/testing-strategy.md`](docs/quality/testing-strategy.md) — enforced test baseline and gate-by-gate assurance ratchet;
- [`PROJECT_PLAN.md`](PROJECT_PLAN.md) — full programme design, resourcing and operating model;
- [`docs/programme/track-charters.md`](docs/programme/track-charters.md) — ten workstream accountabilities.

## v1.0 product boundary

Version 1.0 contains four linked products:

1. a **global source census** with a reviewed coverage state for every in-scope jurisdiction;
2. a **harmonised core dataset** containing only observations that pass explicit quality and comparability gates;
3. an **outcomes evidence catalogue** covering administrative outcomes, user experience and child/family outcome evidence;
4. a **jurisdiction context library** explaining institutions, procedures, definitions and breaks in series.

“Global” applies to the documented search and coverage layer. It does not imply that every jurisdiction publishes usable data, or that incompatible measures can be ranked.

## Programme conductor

The v1 route is machine-readable and evidence-driven:

- `config/tracks.toml` defines ten durable tracks, T0–T9;
- `config/stage_gates.toml` defines G1–G6 and their mandatory criteria;
- `programme/work_items.csv` contains executable delivery packages;
- `programme/evidence_register.csv` records reviewable evidence and checksums;
- maturity, risks, defects, exceptions and gate decisions have separate controlled registers;
- conductor mutations are atomic, locked and appended to `programme/audit-log.jsonl`.

A gate is **ready** only after its evidence, work, maturity, dependencies, risk and defect controls pass. It is **passed** only after an authorised decision is recorded.

```bash
python -m gfjd conductor status
python -m gfjd conductor gate G1
python -m gfjd conductor next
python -m gfjd conductor graph
```

## Executable data path

The repository implements:

- JSON Schema-backed CSV contracts and semantic cross-register validation;
- controlled local and public-URL acquisition with checksums, rights routing and manifest verification;
- configurable source-to-observation mapping;
- silver-to-gold promotion with schema checks, dual-review requirements and reason-coded quarantine;
- lineage-index generation;
- repository secret/public-data safety scans;
- deterministic release bundles, checksums, declared-dependency SBOM, verification and release diffs;
- stable-release blocking unless G6 has passed.

Data remain separated into:

- `data/raw/` — immutable acquisition evidence and lawful source copies;
- `data/bronze/` — source-native extraction;
- `data/silver/` — normalised observations with original definitions retained;
- `data/gold/` — accepted, release-eligible observations only.

## Development and assurance checks

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
make check
```

The local/CI check compiles the package, validates contracts and programme controls, runs the test suite, verifies generated conductor artefacts, builds a deterministic 0.x rehearsal release and verifies its manifest.

Useful individual commands:

```bash
python -m gfjd validate --strict
python -m gfjd security
python -m gfjd pipeline promote \
  --input data/silver/example.csv \
  --gold data/gold/example.csv \
  --quarantine build/quarantine.csv \
  --report build/promotion-report.json
python -m gfjd release build \
  --version 0.3.0 \
  --output dist \
  --source-date-epoch 1784419200
```

## Repository principles

- Model the **family-justice matter**, not merely institutions named “family court”.
- Preserve original wording, language, unit, denominator, clock and cohort before harmonising.
- Record negative findings: “searched, no public source found” is substantive evidence.
- Never combine prospective listing waits, completed-case duration and pending-case age as one generic wait measure.
- Never silently overwrite released values.
- Keep person-level case data outside this public repository.
- Expose provenance to page, table, cell, API query or dashboard filter.
- Do not publish a composite jurisdiction ranking in v1.0.

## Release and compatibility policy

- `0.x` contracts may change through controlled migrations while the design is tested.
- `1.x` public IDs, schemas and file contracts are backwards-compatible.
- Corrections use patch releases; additive changes use minor releases.
- Every release remains retrievable with checksums, citation metadata, known limitations and a changelog.
- A version number never substitutes for stage-gate evidence.

See [`docs/standards/versioning-and-deprecation.md`](docs/standards/versioning-and-deprecation.md).

## Contribution boundary

Contributions of official sources, jurisdiction profiles, translations, acquisition mappings, tests and correction evidence are welcome. Do not commit identifiable case records, sealed material, credentials or unlawfully redistributed documents.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`GOVERNANCE.md`](GOVERNANCE.md) and [`SECURITY.md`](SECURITY.md).
