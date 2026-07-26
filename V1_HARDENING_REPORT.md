# v1.0 hardening report

**Assessment date:** 19 July 2026  
**Repository release:** v0.3.0 engineering and programme-control baseline  
**Target:** stable, hardened and supportable v1.0

## Executive answer

The plan, ten programme tracks, six-stage roadmap and executable conductor have been built out substantially. The repository now contains working code for programme-state validation, evidence-gated progression, acquisition, schema validation, harmonisation, quarantine, lineage, deterministic releases, release verification, security scanning and command-line operation.

It would nevertheless be inaccurate to call the international project itself v1.0. The software foundation is an alpha baseline; the governance approvals, international source census, pilot source editions, reviewed observations, external assurance, production operations and funded maintenance model still have to be earned through the conductor.

## What is now implemented

### Programme architecture

- Ten authoritative tracks, T0–T9, covering governance through sustainability.
- Six dependent gates, G1–G6, mapped to v0.4, v0.5, v0.6, v0.7, v0.9 and v1.0.
- Fifty-eight controlled work items and fifty-nine evidence records.
- Separate maturity, risk, defect, exception, decision and audit registers.
- Binding v1.0 criteria and explicit no-go conditions.
- A capability-based roadmap: time elapsed or a version label cannot make a gate pass.

### Conductor/control plane

- Validates IDs, cross-references, dependencies and dependency cycles.
- Computes track progress, maturity and gate readiness.
- Distinguishes implemented, reviewed and formally accepted work.
- Requires accepted evidence with path, checksum, reviewer and review date.
- Enforces submitter/reviewer separation for accepted evidence.
- Blocks gates for unresolved dependencies, required work, evidence, maturity, risks, defects and exceptions.
- Requires a separate recorded governance decision before a gate is treated as passed.
- Applies locked, atomic register mutations and writes before/after events to an append-only JSONL audit log.
- Generates human-readable status and programme dependency graphs from the machine-readable state.

### Data and release code

- Twelve JSON Schema-backed data contracts and semantic cross-register checks.
- Controlled local-file and public-network acquisition with checksums, content limits, rights-aware storage routing and SSRF protections.
- Acquisition manifests and post-acquisition verification.
- Declarative source mapping into the normalised observation contract.
- Silver-to-gold promotion with dual-review, provenance and comparability checks.
- Reason-coded quarantine instead of silent row loss.
- Lineage-index generation.
- Repository secret/public-data safety scans.
- Deterministic release assembly with sorted files, fixed build epoch, checksum manifest, release metadata, dependency SBOM and verification.
- Release-to-release diff tooling.
- A stable-release interlock that refuses a v1 build unless G6 has passed.

## Verified baseline

The current repository passes:

- integrated validation: **16 checks, 0 errors, 0 warnings**;
- public-data/security scan: **pass**;
- functional suite: **37 tests pass**, including repository-manifest integrity;
- branch-aware package coverage: **69.35%**, above the enforced v0.3 floor of 65%;
- generated conductor artefact consistency: **pass**;
- deterministic pre-v1 release build and verification: included in the local/CI quality gate.

Coverage thresholds rise at later gates and reach an 85% package target plus mutation testing for critical fail-closed logic at G5.

## Current programme truth

- Active gate: **G1 — Foundation controls accepted**.
- Gates passed: **none**.
- G1 state: **blocked by assurance**.
- Self-assessed maturity floor: **L1**.
- Evidence-assured maturity floor: **L0**.
- Gold observations: **0**.
- Programme risks: **20**, including **19 open critical/high** items.
- High-priority source-rights findings requiring definitive review: **5 informational findings**.

This is the intended fail-closed result. Implemented software and draft documents are not allowed to self-certify organisational maturity.

## Highest-value improvements

### 1. Earn G1 through real governance

Appoint the host, sponsor, release authority, track owners and deputies. Independently review and accept the charter, scope, architecture, aggregate-data boundary, threat model, rights workflow, pilot universe and RACI. Record accepted evidence and the formal G1 decision through the conductor.

### 2. Prove twelve end-to-end pilot systems

Create institutional maps, search logs, source editions, immutable acquisition manifests, bronze tables, mapping files, review records and representative gold observations for twelve heterogeneous jurisdictions. Include API, spreadsheet, HTML and difficult PDF/dashboard pathways, then independently re-extract a risk-based sample.

### 3. Harden the connector and data platform layer

Add maintained source-specific connectors, conditional requests, rate limiting, retries/backoff, source-drift fingerprints, historical fixtures and scheduled monitoring. Move large or restricted source evidence to governed object storage while retaining public checksums and manifests.

### 4. Complete external assurance and public safeguards

Commission independent methods, security/privacy/legal, accessibility and localisation reviews. Test interpretation with court administrators, researchers, lived-experience advisers and child-rights experts. Keep Tier 3/4 data out of direct comparison interfaces.

### 5. Make operations survivable

Implement signed provenance, independently administered archival deposit, monitored scheduled jobs, alert ownership, backup/restore, correction/incident service objectives and deputy-led release/rollback exercises. Run the v0.9 release candidate for at least 30 days in a production-like environment.

### 6. Fund and staff the 1.x line before launch

Secure named capacity and committed funding for at least twelve months after v1.0, including regional verification, translation, data engineering, methods, security and release operations. The conductor correctly prevents “launch and abandon” from satisfying G6.

## Recommended immediate sequence

1. Complete and independently accept the eight G1 criteria.
2. Resolve or formally disposition G1-blocking risks.
3. Record the G1 decision and move to the reproducible pilot.
4. Build one complete vertical slice before scaling connector count.
5. Freeze only those methods and contracts that survive pilot evidence.
6. Expand to the global source census, then the public beta, release candidate and stable release in gate order.

The repository is now capable of controlling that sequence. The next constraint is no longer the absence of a plan or core scaffolding; it is disciplined execution, evidence and independent assurance.
