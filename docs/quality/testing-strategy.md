# Testing and assurance strategy

## Purpose

Automated tests protect the repository's executable controls; they do not replace independent methodological, governance, security, accessibility or operational assurance. Coverage is used as a guardrail and risk signal, never as proof that the project or its data are correct.

## Current enforced baseline

The v0.3 engineering baseline enforces:

- tests on Python 3.11, 3.12 and 3.13 in CI;
- branch-aware coverage across the `gfjd` package;
- a repository-wide minimum of **65%**;
- deterministic release, stable-release interlock, conductor state, evidence independence, acquisition safety, promotion/quarantine and schema tests;
- manifest verification so unreviewed or omitted files cannot silently enter the repository snapshot.

At the time this strategy was established, the complete 37-test suite achieved **69.35% branch-aware coverage**. The threshold is intentionally below the measured result so that it detects regression without pretending that v0.3 has already reached v1 assurance.

## Coverage ratchet

| Gate | Minimum package coverage | Additional critical-control expectation |
|---|---:|---|
| G1 / v0.4 | 65% | Every gate decision and stable-release interlock has a positive and negative-path test |
| G2 / v0.5 | 75% | At least 85% for conductor, acquisition, validation, promotion and release modules; representative source fixtures |
| G3 / v0.6 | 78% | Connector contract tests and historical source-edition regression fixtures |
| G4 / v0.7 | 80% | At least 90% for critical control modules; schema compatibility and migration fixtures |
| G5 / v0.9 | 85% | Mutation testing of gate, evidence, gold-promotion, manifest and release-interlock logic; no surviving high-risk mutation |
| G6 / v1.0 | No regression from G5 | Role-separated agent-panel review advises the sole owner on v1 threat, failure and misuse coverage; release rehearsal passes in two clean environments |

A gate cannot be passed by lowering its threshold. Any temporary exception must use the programme exception process, be time-limited, name an owner and remediation date, and be accepted by the relevant gate authority.

## Test layers

1. **Contract tests** validate schemas, required columns, stable identifiers, allowed values and cross-file references.
2. **Semantic tests** protect clocks, statistics, denominators, matter mappings, missingness and gold eligibility.
3. **Control-plane tests** exercise dependency cycles, evidence review, four-eyes separation, work acceptance, risks, defects, exceptions and formal gate decisions.
4. **Acquisition tests** cover checksums, rights-aware routing, local-file preservation, public-network restrictions, redirects, size limits and tamper detection.
5. **Pipeline tests** cover mapping, transformation, lineage, deterministic IDs, promotion and reason-coded quarantine.
6. **Release tests** cover clean assembly, deterministic bytes, manifests, SBOM, verification, release diff and the G6 stable-release interlock.
7. **Operational rehearsals** cover correction, rollback, republish, backup, restore, source drift and dependency failure.
8. **Role-separated agent-panel review** re-extracts a sample, reviews methods and security, and advises the sole accountable owner whether the test inventory reflects real failure modes. It is advisory and is not independent or specialist assurance.

## Local iteration workflow

Use the smallest relevant deterministic tier while changing code, then run the
complete gate once at phase closeout:

```bash
make test-focused FOCUSED_TESTS=tests/test_module.py
make autonomy-fast
make test-timed
make check
```

`test-focused` accepts one or more test paths or node IDs, including the exact
node IDs printed by a failed run. `test` and its `test-timed` alias write
`build/test-timings-local.json` so slow tests can be identified from evidence
rather than impression. All targets accept additional pytest options through
`PYTEST_ARGS`. Do not use pytest's cache-dependent `--last-failed` as an
acceptance check: stale or missing node IDs can unexpectedly expand it to the
complete suite.

`unit-parallel` uses two workers with file-level scheduling. It is an optional
local iteration accelerator, not an acceptance receipt and not a replacement
for the serial `unit`, `test`, `autonomy-fast` or `check` targets. Do not run
parallel repository gates concurrently in multiple worktrees: validation,
coverage and release targets intentionally share local build paths.

## Required additions before G2

- Property-based tests for stable IDs, dates, value coercion and state transitions.
- Connector fixtures for API, spreadsheet, HTML and PDF/dashboard acquisition patterns.
- Failure-injection tests for interrupted writes, checksum mismatch, unavailable sources and partial release assembly.
- Golden fixtures for at least three heterogeneous jurisdictions and incompatible duration definitions.
- A separate slow integration-test marker and a nightly or scheduled execution path.

## Required additions before G5

- Mutation testing focused on fail-closed controls.
- Cross-platform and two-environment deterministic-build comparison.
- Backward-compatibility tests against every supported 1.x schema and release fixture.
- Load and resource tests for the release query layer.
- Security and privacy abuse cases derived from the approved threat model.
- Restore and incident exercises conducted through fresh, role-separated agent workspaces, with the sole owner retaining accountable acceptance.

## Reporting

Every release candidate records the test command, environment, coverage summary, excluded code, failed or quarantined tests, known limitations and links to role-separated agent-panel advice. Coverage exclusions require code-level justification, panel advice and sole-owner adjudication. Public release remains separately gated.
