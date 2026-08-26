# Global Family Justice Data Project

A reproducible international source census and harmonised data platform for family-justice process, performance, outputs, experiences and outcomes.

## Bootstrap-ready handoff

This distribution is **v0.6.0-alpha.2**. It is delivered as a Git bundle inside a self-contained handoff ZIP so that a new local checkout retains the reconstructed checkpoint history. The root `AGENTS.md` is automatically read by Codex and directs it to the authoritative bootstrap and implementation briefs.

From a cloned checkout, the supported plan-first bootstrap is:

```bash
python scripts/bootstrap_workspace.py preflight
python scripts/bootstrap_workspace.py plan --scan-root .. --output build/bootstrap
# Apply only after reviewing the plan and authenticating `gh`:
python scripts/bootstrap_workspace.py apply --yes --github-visibility public
```

The bootstrap never force-pushes, refuses a mismatched `origin`, creates the owner-directed GFJD estate as public, inventories bounded nearby clones without modifying them, and records checksum-bound receipts. Public upload remains fail-closed for credentials and prohibited personal or identifying data. `HISTORY_PROVENANCE.md` explains how the checkpoint history was reconstructed.

## Current status

The repository is an **alpha engineering, programme-control and autonomous-handoff baseline**. It contains a working conductor, data contracts, validation, acquisition, harmonisation, quarantine, provenance, deterministic release tooling, multi-format adapters, outcomes-evidence and comparability components, resilience tooling, CI policy controls, and the local/remote bootstrap layer. It is **not** a completed international dataset and must not be represented as v1.0.

The repository remains deliberately fail-closed:

- **G1 — Foundation controls accepted** has passed through the sole owner's
  digest-bound decision; the active gate is **G2 — Reproducible pilot proven**;
- the seed material is illustrative and the gold observation layer remains empty unless explicitly populated through reviewed workflows;
- implemented code, generated documents and agent-panel advice are not real-source or operational evidence by themselves;
- GitHub/Hugging Face creation and live settings verification occur only on the operator’s authenticated machine.

## Start here

- [`AGENTS.md`](AGENTS.md) — automatically loaded Codex instructions;
- [`START_HERE.md`](START_HERE.md) — operator entry point;
- [`BOOTSTRAP_AND_HANDOFF_PROMPT.md`](BOOTSTRAP_AND_HANDOFF_PROMPT.md) — local, GitHub and Hugging Face bootstrap brief;
- [`CODEX_IMPLEMENTATION_PROMPT.md`](CODEX_IMPLEMENTATION_PROMPT.md) — autonomous continuation contract;
- [`HISTORY_PROVENANCE.md`](HISTORY_PROVENANCE.md) — provenance of the reconstructed Git history;
- [`V1_HARDENING_REPORT.md`](V1_HARDENING_REPORT.md) — implementation assessment;
- [`ROADMAP.md`](ROADMAP.md) and [`V1_0_RELEASE_CRITERIA.md`](V1_0_RELEASE_CRITERIA.md) — route and binding evidence gates to stable v1.0.

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
  --source-date-epoch 1786752000
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
