# Verification record

**Baseline:** `0.6.0-alpha.2`
**Verification date:** 2026-07-27
**Environment used:** Linux x86_64, CPython 3.13.5, Git 2.x, uv 0.10.0.

This is an engineering verification record, not a programme-gate decision.

## Completed checks

| Check | Result |
|---|---|
| Python compilation | Passed for `src`, `tests` and `scripts` |
| Test suite before final manifest freeze | 43 passed, with the manifest test intentionally deferred until final source freeze |
| Stable-core branch coverage | 69.56%; configured floor 65%; all configured critical-module thresholds passed |
| Contract lock | Passed after regeneration |
| Schema and semantic validation | Passed with zero errors and zero warnings in the final pre-freeze run |
| Conductor generated files | Regenerated and verified current |
| CI workflow policy | Passed in the final pre-freeze run |
| Desired repository-control policy | Passed; expected warnings remain for unapplied live controls and pending real CODEOWNERS |
| Dependency lock audit | Passed against the committed lock |
| Five-format synthetic ingestion | Passed; five fictional mapped and promoted observations, zero quarantined |
| Outcomes-evidence build and verification | Passed with zero empirical records and explicit gaps |
| Comparability build and verification | Passed on synthetic output |
| Portable warehouse | Built and verified; 23 jurisdiction seeds, 18 source seeds, 32 indicators, 13 matter types, zero empirical gold rows |
| Backup and restore rehearsal | Built, verified, restored and receipt-verified |
| Bootstrap discovery plan | Passed; remote mutation remained blocked without authenticated owner/namespace |
| Wheel inspection and double build | Passed; byte-identical |
| Source-distribution inspection and double build | Passed after deterministic metadata normalisation; byte-identical |
| Deterministic release double build | Passed; byte-identical release ZIPs and both releases independently verified |

The final source-manifest test, Git-bundle verification and clean clone from the packaged bundle are performed after this document is frozen and are recorded in the outer handoff package receipt.

## Environment limitations

- Outbound package retrieval was unavailable. A fresh `uv sync --frozen --all-extras` could not be completed because uncached wheels could not be downloaded.
- Ruff and mypy were therefore not executable in this container. Their locked CI jobs remain configured and must run on the authenticated development/CI environment.
- A wheel smoke test can install with `--no-deps` against already provisioned dependencies; this does not substitute for a fresh lock-exact installation.
- No GitHub or Hugging Face remote was created here because no verified operator account or namespace was available. The bootstrap deliberately fails closed in that state.

## Truth boundary

No G1–G6 gate has been approved. No empirical international court observation or outcomes study has been fabricated. Live GitHub protections, Hugging Face Trusted Publisher configuration, source rights, institutional appointments and independent assurance remain external evidence requirements.
