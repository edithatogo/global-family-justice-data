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

Solo operation does not erase separation-of-duty requirements. The maintainer may
prepare evidence and decision packets, but independent review, institutional
appointments, source-rights decisions, publication, signing and governance
acceptance remain explicit external gates. When an independent person is genuinely
required, the autonomous loop stops with the exact artifact and decision needed.
