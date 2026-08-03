# Track implementation roadmap — 2026-08-03

This roadmap separates repository implementation from evidence and authority
acceptance. It raises implementation coverage without promoting a gate.

## Work packages

| Order | Tracks | Repository-owned implementation | Recommendation | Trade-off | Contingency |
|---|---|---|---|---|---|
| 1 | T3 | Acquisition manifests, checksum inventory, preservation and drift checks | Implement first | Less visible than product work but protects provenance | Metadata-only receipts and explicit inaccessible states |
| 2 | T4 | Deterministic pipeline, contract tests, clean-build/reproducibility harness | Complete existing engineering path | Requires frozen inputs and stable contracts | Synthetic fixtures; no real-data promotion |
| 3 | T5 | Harmonisation transforms, quarantine, row diffs and quality reports | Build around panel-adjudication packets | Panel advice does not create specialist assurance | Quarantine disputed measures and publish no comparisons |
| 4 | T6 | Provenance-linked atlas, documentation, accessibility checks and responsible-use guidance | Build after source states exist | Product scope follows evidence rather than visuals | Descriptive catalogue only |
| 5 | T7 | Rights ledger, threat model, SBOM/secrets checks and fail-closed release policy | Automate continuously | Automation cannot resolve legal terms or consent | Keep restricted material metadata-only |
| 6 | T8 | Release/rollback/restore rehearsals, backup checks and incident runbooks | Rehearse on private candidate | Does not prove live service readiness | Unsigned local candidate |
| 7 | T9 | Localisation manifests, glossary, language-review queues and costed operating templates | Prepare structures and panel prompts | Human/local reviewers and funding remain external | Synthetic/localisation rehearsal; no representation claims |

## Decision options

- **Option A — sequential implementation (recommended):** complete work packages
  in the order above and re-evaluate after each evidence boundary. Lowest risk,
  slower visible feature delivery.
- **Option B — parallel implementation:** run T3/T4/T7 and documentation in
  parallel. Faster repository coverage, but more coordination and stale-input
  risk.
- **Option C — product-first:** build T6 interfaces before source and quality
  controls. Fastest demonstration, but highest risk of implying unsupported
  coverage and is not recommended.

## Gate and authority boundary

Implementation completion is not work-item acceptance. G1 remains conditional;
G2–G6 remain dependency-blocked until real evidence, rights, human/local review,
specialist or accountable decisions, custody, staffing and funding records are
present. Agent panels provide advisory options, rationale and contingencies;
they cannot create those records.

## Execution controls

Every work package must:

1. bind inputs to a commit and SHA-256 manifest;
2. produce tests or deterministic rehearsal evidence;
3. record unresolved risks and fallback disposition;
4. update the relevant Conductor work item and evidence path;
5. run strict validation, manifest generation and generated-status checks.
