# Implementation status at v0.3.0

## Executive assessment

The repository has moved beyond a documentation scaffold. It now provides a coherent engineering and programme-control baseline for progressing toward v1.0. The current implementation can validate its own contracts, control work and evidence state, acquire and fingerprint sources, map and promote observations, quarantine non-compliant records, build lineage and produce deterministic pre-v1 releases.

It is not yet a mature international service. The most important missing components are accepted governance evidence, a completed jurisdiction universe, production source connectors and preserved editions, reviewed observations, external assurance, production infrastructure and a funded operating team.

## Implemented controls

| Capability | Status | Principal artefacts |
|---|---|---|
| Ten-track programme model | Implemented | `config/tracks.toml`, track charters |
| Six evidence stage gates | Implemented | `config/stage_gates.toml` |
| Work-package backlog | Implemented | `programme/work_items.csv` |
| Evidence register and four-eyes checks | Implemented | `programme/evidence_register.csv`, conductor validation |
| Maturity floor | Implemented | `programme/maturity_assessment.csv` |
| Risk, defect and exception gates | Implemented | machine-readable programme registers |
| Formal gate decisions | Implemented | `programme/gate_decisions.csv` |
| Atomic mutation and audit trail | Implemented | conductor lock, atomic CSV write, JSONL events |
| Data contracts | Implemented | 12 configured contracts and JSON Schemas |
| Semantic validation | Implemented | jurisdiction/source/indicator/matter/lineage checks |
| Controlled acquisition | Implemented | file and HTTP acquisition, checksum, rights route, SSRF guard |
| Mapping and promotion | Implemented | structured mapping and silver-to-gold pipeline |
| Quarantine | Implemented | reason-coded rejected rows and promotion report |
| Deterministic release | Implemented | fixed epoch, sorted files, normalised ZIP, manifest and SBOM |
| Stable-release interlock | Implemented | v1 build blocked unless G6 is passed |
| CI and code scanning | Implemented baseline | multi-version tests and CodeQL workflow |
| Test coverage of critical paths | Implemented baseline | conductor, validation, acquisition, promotion, release and CLI tests |

## Verification baseline

The current repository test suite, including repository-manifest verification, passes in hosted CI. CI enforces the staged branch-aware coverage floor in `docs/quality/testing-strategy.md`; the lower current threshold is not the v1 target.

The integrated validator currently passes with 22 checks, no errors, 14 overdue-risk warnings and seven high-priority source-rights review notices. Those findings are intentionally visible and are not treated as gate clearance.

## Current programme truth

The repository deliberately reports an evidence-assured maturity floor of L1. This does not mean no engineering work exists. It means that the maturity assessment is not yet supported by accepted L2 evidence across every mandatory dimension.

The following remain true:

- G1 is passed under the recorded owner decision;
- G2 remains blocked because its required evidence-assured maturity floor is L2 while the current floor is L1;
- draft files are not accepted evidence;
- fresh real replay evidence remains supporting reproducibility evidence and has not been promoted to Gold;
- no global coverage claim has been earned;
- no external methods, security, accessibility or operational assurance has occurred;
- no production recovery or 30-day release-candidate soak has occurred.

## Code boundary

The implementation is suitable for controlled pilot development. It should not yet be treated as a hosted production service. Network acquisition is synchronous, source-specific connectors are not yet present, signing and independent archive deposit remain deployment concerns, and there is no public dashboard/API implementation in this repository.

Those boundaries are intentional: v0.3 proves and controls the core workflow without falsely asserting that organisational or international coverage work is complete.
