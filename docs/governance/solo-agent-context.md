# Canonical solo-agent context

The authoritative execution context for this repository is the combination of
`AGENTS.md`, `START_HERE.md`, `BOOTSTRAP_AND_HANDOFF_PROMPT.md`,
`CODEX_IMPLEMENTATION_PROMPT.md`, the configuration under `config/`, and the
single-owner operating model. Agents must read those files before mutation.

For a locked environment, the one-command validation entry points are:

```bash
make PYTHON='uv run python' autonomy-fast
make PYTHON='uv run python' autonomy-full
```

`autonomy-context` writes a bounded resume packet under `build/autonomy`,
including the repository state and SHA-256 drift receipt. Build output is
intentionally not committed; the packet is regenerated at each handoff and
must verify before autonomous work continues.

The owner remains the only authority for rights, publication, formal gate
adjudication, exceptions, and outbound contact. Agents may execute the
repository-owned validation and evidence preparation path, but must stop at
those external boundaries and record the blocker.
