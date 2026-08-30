# Single-maintainer autonomous implementation

This repository is designed so one maintainer can delegate safe, reversible
repository work without becoming the sole source of truth. The agent reconstructs
state from versioned contracts and a checksum-bound context packet, not from chat
memory.

Start or resume with:

```bash
uv sync --frozen --all-extras
make PYTHON='uv run python' autonomy-context
make PYTHON='uv run python' autonomy-fast
```

During implementation, select the first repository-owned action in
`build/autonomy/autonomy-context.md`, add a failing test where meaningful, make the
smallest coherent change, run the fast gate, commit, and regenerate the context
packet. At a phase boundary run:

```bash
make PYTHON='uv run python' autonomy-full
```

The full harness includes formatting, lint, strict typing, branch coverage,
contracts, strict repository validation, tests, generated-state drift, workflow and
repository policy, lock audit, governance and data integration rehearsals,
distribution inspection, and package/release reproducibility.

The repository owner is the sole accountable decision-maker. Role-separated
agent panels provide advice, not an additional human approval gate or independent
assurance. Follow the standing-owner direction in
`docs/governance/standing-owner-direction-policy-2026-08-20.md`: routine planning,
implementation, validation, signed repository commits, PRs, passing merges and
routine branch cleanup do not require repeated approval. Actual source facts,
rights clearance, publication and programme acceptance remain separate.

## Continue without a prompt per slice

Use `docs/engineering/medallion-autonomous-continuation-2026-08-30.md` as the
ordered remaining plan. During an active run, continue after each coherent
implementation and merge checkpoint to the next eligible repository-owned task.
If one item needs evidence or authority, preserve its blocked state and continue
another eligible item without relaxing dependencies. Group genuine owner
decisions and include a recommendation and contingency.

The resume packet carries an explicit `execution_scope` for every executable
queue item. The reviewed registry in `gfjd.autonomy` defaults unknown work to
scope review. A planned status or reassuring task title is not authorization;
in particular, WI-G4-MED-04 publication is not automatically executable.
New repository-only scopes can be added through normal tested review under the
standing policy, not by treating this registry as a new grant of authority.

The context builder is not a background agent or scheduler. It cannot continue
after a session ends without a supported continuation mechanism. An explicitly
requested thread heartbeat can resume this queue later, must avoid concurrent
writers, and must preserve all scope and stop rules. Existing monitor-evidence
preservation automation is separate and does not authorise implementation or
source access beyond its own recorded remit.
