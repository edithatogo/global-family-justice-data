# Executable conductor and evidence plane

The conductor has two connected but deliberately separate responsibilities:

1. **Programme control:** tracks work, evidence, maturity, defects, exceptions, dependencies, and accountable gate decisions.
2. **Technical execution:** runs reviewed, fixed-operation workflow DAGs and emits tamper-evident receipts.

Keeping the planes separate prevents a successful build from being treated as proof that a scientific, legal, governance, or operational criterion has been accepted.

## Programme state

Authoritative configuration and records are held in `config/tracks.toml`, `config/stage_gates.toml`, and `programme/`. The conductor validates identifiers and dependencies, calculates effective evidence status, identifies ready work, and produces a canonical state digest. Gate decisions must cite that digest; subsequent state changes make an old approval stale rather than silently carrying it forward.

Every controlled state transition appends an audit event linked to the previous event hash. `gfjd conductor audit` verifies sequence, link, and content integrity.

## Evidence-review packs

`gfjd conductor pack G1` creates a review snapshot rather than an approval. A pack includes:

- gate metadata and exact conductor state digest;
- criterion-by-criterion status and no-go conditions;
- evidence index and current evidence effectiveness;
- validation, programme status, maturity, defect, exception, and audit snapshots;
- manifest and SHA-256 digests for every included artifact.

`gfjd conductor verify-pack ... --check-current-state` checks both internal integrity and whether the programme still matches the packed state.

## Executable workflows

Workflow definitions are reviewed TOML. They may call only operations registered in `gfjd.workflow`; arbitrary shell commands and executable configuration are not accepted. The runner:

- validates the DAG and output ownership before execution;
- acquires a repository-scoped lock;
- records expanded input digests and operation parameters;
- executes steps in dependency order;
- validates declared output contracts;
- records stdout/stderr where applicable;
- writes step receipts linked by hash;
- writes a terminal run receipt;
- supports dry runs and safe resume after a failed or interrupted run.

Resume reuses a step only when its prior receipt is valid and its current inputs and outputs still match the recorded hashes. A changed dependency or artifact therefore forces re-execution.

## Trust boundary

The conductor can prove that defined checks ran against defined bytes. It cannot prove that a source is legally redistributable, a translation is correct, a court pathway was fully mapped, an observation is scientifically comparable, or an institution is ready to support v1.0. Those claims require named reviewers and evidence outside the code path.
