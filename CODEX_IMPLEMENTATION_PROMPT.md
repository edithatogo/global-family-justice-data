# Codex implementation brief — Global Family Justice Data Project

## Mission

Take this repository from the current **0.6.0-alpha.2 bootstrap-ready alpha** as far as responsibly possible toward a stable, hardened, mature v1.0 implementation. Work autonomously, use the entire repository as context, and make concrete changes rather than merely proposing them. Preserve the distinction between technical implementation and evidence that only real institutions, researchers, source owners, reviewers, or operators can provide.

The desired result is a repository that is easier to trust, operate, extend, audit, reproduce, and hand over. Every material feature should be accompanied by an executable contract, negative tests, deterministic evidence or receipts, documentation, and a clear failure mode.

## Truth and safety boundaries

These constraints are non-negotiable.

1. **Do not claim that G1–G6 has passed.** A gate passes only through independently accepted evidence and an accountable gate decision bound to the exact conductor-state hash.
2. **Do not manufacture governance evidence.** Do not invent names, appointments, approvals, signatures, licence decisions, ethics approvals, source-rights determinations, lived-experience review, funding, or institutional authority.
3. **Do not fabricate international research or empirical data.** Synthetic fixtures must remain unmistakably fictional. Do not convert illustrative seed sources into reviewed evidence or gold observations.
4. **Do not weaken fail-closed controls to make checks pass.** Fix the underlying problem. Do not suppress validation, reduce security checks, lower coverage without a recorded rationale, mark evidence accepted, or bypass release gates.
5. **Keep the public repository aggregate-only.** Do not add identifiable case-level records, sealed material, credentials, tokens, private endpoints, or personal data.
6. **Preserve source fidelity and comparability discipline.** Do not auto-upgrade quality or comparability tiers, infer outcomes from throughput, or merge incompatible clocks, statistics, cohorts, denominators, matter types, or court levels.
7. **Keep workflow execution constrained.** Reviewed workflows may invoke registered operations, not arbitrary commands from data or configuration.
8. **Treat archives, source files, dashboards, spreadsheets, HTML, PDFs, API responses, and build artifacts as untrusted input.** Maintain path, size, link, compression, network, content, provenance, and checksum controls.
9. **Use current primary documentation for external technical interfaces.** For GitHub, Python packaging, SLSA/in-toto, accessibility tooling, and other changing interfaces, consult official specifications or official documentation before implementing assumptions.
10. **Be explicit about what remains external.** A technically complete control is not proof that it has been operated successfully in production or independently reviewed.

## Repository orientation

Read these before changing the architecture:

- `README.md`
- `IMPLEMENTATION_STATUS.md`
- `PROJECT_PLAN.md`
- `ROADMAP.md`
- `V1_0_RELEASE_CRITERIA.md`
- `MATURITY_MODEL.md`
- `config/project.toml`
- `config/tracks.toml`
- `config/stage_gates.toml`
- `config/workflows.toml`
- `config/quality.toml`
- `docs/architecture/conductor-system.md`
- `docs/architecture/executable-conductor.md`
- `docs/programme/v1-assurance-case.md`
- `docs/quality/testing-strategy.md`
- `docs/quality/quality-evidence-summary.md`
- `docs/quality/mutation-assurance.md`
- `docs/operations/github-controls-evidence.md`
- `docs/engineering/release-provenance.md`
- `VERIFICATION.md`

The current code includes a working T0–T9/G1–G6 programme conductor; schema-backed validation; rights-aware acquisition; mapping, promotion, quarantine and deterministic release controls; multi-format connector, outcomes-evidence, comparability, warehouse and resilience modules; CI/repository-policy and package-inspection modules; and a plan-first Git/GitHub/Hugging Face bootstrap. Some advanced modules are not yet exposed through the main CLI or covered by the original test suite. Treat them as implementation assets to integrate and test, not as completed production services.

The complete catalogue/public-product layer, general workflow scheduler, hash-bound gate packs, applied-live-GitHub snapshot service, canonical quality summary, mutation service, full global census, accessibility automation, signed publication provenance and production platform remain **planned work**. Implement them only with truthful contracts, tests and migration paths.

Do not replace working controls with a fashionable framework unless the migration is demonstrably safer, simpler, fully tested, and backwards-compatible.

## Initial execution protocol

1. Unpack or clone into a clean path. Do not work inside a previously generated `build/`, `dist/`, `.venv/`, or cache tree.
2. Record the source archive or commit SHA-256 and the current Git commit when available.
3. Inspect the repository, contract lock, manifest, generated conductor views, lockfile, workflows, open programme defects/exceptions, and current validation output.
4. Run the fastest static checks first, then the complete harness. Use the repository’s locked environment.
5. Diagnose every failure. Correct implementation, tests, contracts, generated files, documentation, and manifests together.
6. Make small, reviewable changes. Keep tests passing between work packages.
7. At the end, run the full clean-room verification sequence and produce a concise implementation report with exact results and unresolved external dependencies.

Preferred commands for the present tree:

```bash
uv sync --frozen --extra dev
uv run python -m compileall -q src tests scripts
uv run python -m pytest -q
uv run python -m gfjd validate
uv run python -m gfjd conductor check-generated
uv run python -m gfjd.manifest --verify
uv run make release-rehearsal
uv run make check
```

As you implement new quality-summary, mutation, applied-controls, workflow, or provenance capabilities, add explicit Make and CI targets rather than documenting commands before they exist.

When a command is unavailable because of network or platform restrictions, use the best available locked environment, document the limitation, and do not represent an unexecuted check as passing.

## Work programme

Proceed in this order unless evidence in the repository supports a safer dependency order.

### Work package 1 — close and strengthen the existing harness

- Run the full suite, branch coverage, property/adversarial tests, mutation rehearsal, all integration rehearsals, package build/inspection, wheel reproducibility, release double-build, backup/restore, source-health baseline, policy audits, quality-summary verification, manifest verification, and clean extraction test.
- Fix nondeterminism, stale generated files, platform assumptions, hidden network dependencies, flaky tests, unsafe temporary-file handling, or receipt gaps.
- Raise critical-module tests where fail-closed branches are not directly asserted.
- Keep `config/coverage_baseline.json` honest and ratcheted; do not merely lower thresholds.
- Expand negative tests for malformed JSON/TOML/CSV, duplicate keys, Unicode/case collisions, archive bombs, path escapes, link attacks, partial writes, interrupted runs, stale approvals, state-hash drift, and rewritten evidence.
- Ensure every verifier recomputes meaning from source evidence rather than trusting self-reported status fields.
- Ensure build/test output is excluded from source distributions, backups, manifests, and mutation copies where appropriate.

### Work package 2 — applied GitHub controls and CI/CD evidence

The repository currently verifies a normalised snapshot but does not itself prove live GitHub settings.

Implement a reviewed capture path that:

- uses the GitHub API with least-privilege credentials and no token logging;
- captures raw responses for the repository identity, Actions permissions/selected Actions, rulesets, merge queue, protected environments, security settings, retention settings, and CODEOWNERS state;
- records API endpoint, status, ETag or equivalent, capture time, repository ID/full name, default branch, source commit, tool version, and raw-response digests;
- normalises the evidence into `schemas/github_repository_snapshot.schema.json`;
- preserves raw evidence outside public release artifacts unless publication is explicitly safe;
- verifies freshness and exact desired-state conformance;
- detects incomplete permissions or unsupported settings rather than treating missing responses as disabled controls;
- has fixture-driven contract tests for API evolution, pagination, 403/404 ambiguity, renamed rulesets, multiple environments, merge-queue absence, and enterprise/org inheritance;
- runs as a protected, manually reviewable workflow and becomes required evidence for G5/G6 without making ordinary forks require secrets.

Improve CI evidence aggregation so that independent jobs upload checksum-bound receipts and a final job composes them without unnecessarily rerunning the entire harness. Bind the final quality summary to:

- exact source commit and workflow run identity;
- dependency and Action locks;
- contracts and generated views;
- test/JUnit/timing/coverage/property/mutation results;
- policy, CodeQL, dependency, Bandit, and workflow-security results;
- package and release artifact hashes;
- reproducibility comparisons;
- clean-install and platform-smoke results;
- applied repository-settings evidence where applicable.

Add a machine-readable schema and independent verifier for any new summary or capture artifact.

### Work package 3 — supply-chain and release provenance

- Ensure the source distribution and wheel are deterministic when built twice with the same toolchain and epoch.
- Add isolated install tests from the built wheel and sdist without importing from the checkout.
- Verify console scripts, package data, schemas, configuration defaults, minimum Python, and read-only use after install.
- Generate standards-conformant SBOM and provenance using current official specifications; retain the existing independent verification logic.
- Bind the consolidated quality summary and applied-settings evidence into release provenance without creating circular build dependencies.
- Add signing/attestation verification suitable for protected CI, while keeping local unsigned rehearsals explicit.
- Add release-index and archival-deposit records with persistent identifiers as nullable/pending until real services are selected.
- Test rollback, correction, withdrawal, supersession, and release-to-release compatibility.
- Add a clean-room script/container that builds and verifies from a source archive with network disabled after dependency provisioning.

### Work package 4 — accessibility and public-product assurance

Retain static checks and add browser-level tests using a maintained accessibility engine where practical:

- keyboard-only navigation and visible focus;
- skip-link behaviour;
- landmarks and heading hierarchy;
- form labels and error association;
- table headers/captions/scopes;
- zoom and reflow;
- reduced motion;
- contrast and non-colour cues;
- accessible names and link purpose;
- no external active dependencies;
- CSP enforcement;
- screen-reader-oriented smoke checks.

Use deterministic local fixtures. Store accessibility reports as checksum-bound evidence. Do not claim full conformance based only on automation; preserve a gate requirement for manual assistive-technology and lived-experience review.

### Work package 5 — real connector contracts and source drift

Do not invent empirical values. Implement the reusable machinery and fixtures required for real sources:

- connector registry, ownership, version, review date, source-family metadata, and deprecation state;
- conditional requests, ETags/Last-Modified, retries with bounded exponential backoff, rate limiting, timeout budgets, content-length/stream limits, and public-network/redirect controls;
- source-structure fingerprints and human-readable drift diffs;
- historical lawful fixtures and golden connector receipts;
- API pagination and query/filter provenance;
- dashboard-export capture and filter-state receipts;
- spreadsheet merged-cell, formula, hidden-sheet, date-system, locale, and data-type tests;
- HTML row/column-header and multi-table disambiguation;
- PDF/manual transcription double-entry and adjudication support without OCR as an assumed default;
- source-edition versioning, revisions, corrections, series breaks, and supersession;
- rights-routing so bytes, extracts, quotations, metadata, and redistributable outputs follow recorded decisions;
- monitor scheduling, drift alerts, owner acknowledgement, escalation, and revalidation.

For every real connector, require a preserved fixture, checksum, contract, expected source-edition identity, row/column or query range, negative cases, drift cases, quarantine cases, owner, and review date.

### Work package 6 — data quality, comparability, and outcomes methods

Strengthen executable support without substituting code for expert judgment:

- dual extraction/re-extraction sampling and concordance reports;
- mapping disagreement and adjudication records;
- denominator, missingness, suppression, revision, and series-break semantics;
- prospective versus retrospective wait-time checks;
- completed-case versus filed-cohort checks;
- unit/statistic/clock incompatibility guards;
- quality-grade and comparability-tier decision logs;
- sensitivity and inclusion/exclusion reports;
- outcome-study risk-of-bias and appraisal workflows;
- evidence-map update/deduplication/versioning;
- clear separation of routine administrative outcomes, user experience, safety, wellbeing, stability, compliance, return-to-court, and causal evaluations;
- tests that prevent throughput from being interpreted as child/family benefit.

Do not create a composite international ranking unless a later accepted methods decision explicitly authorises one.

### Work package 7 — operations, observability, and resilience

Implement production-ready but provider-neutral controls:

- structured logs with correlation/run/source/release IDs and secret redaction;
- metrics for connector health, drift, queue age, validation/quarantine, review backlog, release duration, product health, corrections, and incidents;
- health/readiness checks and bounded alert rules;
- incident, correction, takedown, rollback, key rotation, and disaster-recovery runbooks tied to executable rehearsals;
- backup encryption and retention interfaces without committing keys;
- two-location preservation metadata and periodic restore sampling;
- recovery point/recovery time measurements;
- failed-job resumption and idempotency tests;
- primary/deputy operational handover rehearsal templates;
- service-level evidence schemas and a 30-day soak report generator.

Keep cloud-provider-specific adapters optional and isolate credentials from the public repository.

### Work package 8 — performance, scale, and developer experience

- Benchmark representative small, medium, and large synthetic datasets.
- Bound memory, database, archive, row, column, and runtime usage.
- Add chunked/streaming paths where required without weakening whole-batch validation.
- Test concurrent workflow locks and interrupted writes.
- Improve error messages, CLI JSON stability, exit codes, shell completion if justified, and `--help` coverage.
- Add development containers or reproducible environment definitions only when they can be kept locked and minimal.
- Ensure Windows, macOS, and Linux path semantics remain supported; avoid POSIX-only assumptions in Python code and tests.
- Add architecture decision records for material choices.

### Work package 9 — documentation, governance interfaces, and handover

- Keep README, implementation status, roadmap, release criteria, architecture, methods, runbooks, schemas, CLI help, changelog, citation, support, and security documents aligned.
- Add an operator quick start, contributor vertical-slice tutorial, connector-author guide, release-owner guide, incident guide, and independent-review guide.
- Generate a traceability matrix from v1 release criteria to work items, evidence IDs, controls, tests, and reports.
- Clearly label example/template evidence and prevent it from satisfying a gate.
- Preserve a machine-readable remaining-work backlog with owner role, dependency, gate, acceptance evidence, automation state, and external dependency.

## External work that must remain pending unless genuine evidence is supplied

Codex may improve templates, import tooling, validation, and workflows for these items, but must not mark them complete without authentic inputs:

- institutional host, accountable appointments, deputies, and release authority;
- approved licence and publication identity;
- real GitHub settings captured from the intended repository;
- source-rights and redistribution determinations;
- complete multilingual international searches and negative findings;
- local legal/institutional verification;
- reviewed source editions, extractions, observations, and outcome studies;
- independent re-extraction, methods, security, accessibility, privacy, ethics, child-rights, lived-experience, and misuse review;
- real production monitoring, incident, correction, restore, rollback, takedown, and soak evidence;
- archival deposits and persistent identifiers;
- funded 1.x maintenance, succession, and service commitments.

Represent these honestly as blocked, draft, pending, or not started in the conductor and documentation.

## Definition of technical completion for this engagement

Do not stop at a prose recommendation. Complete all safe implementation available in the environment, then meet the following as far as the repository and credentials allow:

1. No uncommitted accidental build/cache/private files in the deliverable.
2. Formatting, linting, compilation, strict typing, schemas, contract lock, semantic validation, security scan, CI policy, repository desired-state policy, generated conductor views, and manifest pass.
3. Complete tests pass with branch coverage at or above configured floors and no unexplained skip/quarantine.
4. Property/adversarial tests pass.
5. All reviewed mutations are killed; no mutation error or survivor is ignored.
6. All integration rehearsals build and verify.
7. Wheel and sdist build, pass adversarial inspection, install in clean environments, and expose the expected CLI/package data.
8. Repeated wheel and release builds are byte-identical under the declared epoch, or a precise root cause and corrective plan is documented.
9. Release directory, archive, manifest, SBOM, provenance, lineage, products, backup, restore, and quality summary verify independently.
10. A clean extracted copy passes manifest verification and a representative full harness.
11. CI workflows pass the repository’s own policy audit and use immutable reviewed Action identities.
12. Protected release workflows fail closed while licence, identity, gate, repository-settings, or other required evidence is pending.
13. Documentation and changelog describe exactly what was implemented and what remains external.
14. The final output includes a new source ZIP, SHA-256, verification report, and a concise change summary.

## Final response format

Return:

- a precise summary of implemented changes grouped by architecture, data, CI/CD, quality, security, operations, documentation, and tests;
- exact commands executed and results;
- coverage, mutation, reproducibility, package, release, manifest, and clean-room outcomes;
- known limitations and external blockers without euphemism;
- paths or links to the final repository archive, SHA-256, verification report, and any migration notes.

Do not describe work as complete merely because it is planned. Do not call the product v1.0 until the conductor and authentic external evidence support that statement.
