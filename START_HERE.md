# Start here: unpack, discover, initialise and publish safely

This repository is delivered in a self-contained handoff ZIP containing a Git bundle. The outer bootstrap clones the bundle with its commit history, names the bundle remote `handoff`, and leaves `origin` available for the canonical GitHub repository.

The safest route is:

1. Keep the ZIP and its `.sha256` sidecar together.
2. Give the agent the text in `BOOTSTRAP_AND_HANDOFF_PROMPT.md` (a standalone copy is shipped beside the ZIP).
3. The agent verifies and safely extracts the archive, then runs a non-mutating discovery plan.
4. Review only genuinely ambiguous account or namespace choices.
5. The agent initialises Git, creates a **private** GitHub repository by default, adds `origin`, pushes `main` without force, verifies the remote commit, and records a receipt.
6. Hugging Face repositories remain private and opt-in until namespace, rights and publication roles are resolved.

From an already extracted tree, generate the discovery plan with:

```bash
python scripts/bootstrap_workspace.py plan --output build/bootstrap
```

Apply after inspecting `build/bootstrap/bootstrap-plan.md`:

```bash
python scripts/bootstrap_workspace.py apply \
  --github-owner YOUR_GITHUB_LOGIN_OR_ORG \
  --github-repository global-family-justice-data \
  --github-visibility private \
  --author-name "YOUR NAME" \
  --author-email "YOUR VERIFIED OR NOREPLY EMAIL" \
  --yes
```

Create the configured private Hugging Face dataset/Space repositories only after confirming the intended namespace:

```bash
python scripts/bootstrap_workspace.py apply \
  --github-owner YOUR_GITHUB_LOGIN_OR_ORG \
  --github-repository global-family-justice-data \
  --github-visibility private \
  --huggingface-namespace YOUR_HF_NAMESPACE \
  --create-huggingface \
  --yes
```

The command is idempotent where the remote identities match. It refuses to overwrite a mismatched `origin`, force-push, delete remote content, or silently choose between duplicate local clones.

See:

- `AGENTS.md`
- `AUTONOMOUS_IMPLEMENTATION.md`
- `BOOTSTRAP_AND_HANDOFF_PROMPT.md`
- `CODEX_IMPLEMENTATION_PROMPT.md`
- `HISTORY_PROVENANCE.md`

## Locked local environment

After verifying `MANIFEST.sha256`, prepare the exact development and security toolchain with:

```bash
uv sync --frozen --all-extras
uv run python scripts/bootstrap_workspace.py preflight
```

The bootstrap plan writes both a bounded clone inventory and `portfolio-reconciliation.json` before any remote mutation.
