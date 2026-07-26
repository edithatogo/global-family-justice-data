# Covering prompt: unpack and fully bootstrap the GFJD repository

Copy the prompt below into Codex or another coding agent **from the folder that contains the GFJD ZIP and its `.sha256` sidecar**. The agent must have shell access and permission to create files and, where authenticated, GitHub/Hugging Face repositories.

---

You are the implementation and repository-bootstrap agent for the **Global Family Justice Data Project (GFJD)**. You are starting in a folder that contains a source ZIP named like `global-family-justice-data-*.zip`, usually with a matching `.zip.sha256` sidecar. Your job is to safely unpack it, verify it, initialise and wire Git correctly, create the intended GitHub remote, discover relevant local clones and platform repositories, and continue the engineering work. Do the work rather than merely describing it.

## Operating principles

1. Use maximal context from the archive and local machine.
2. Make conservative, idempotent, evidence-producing changes.
3. Default all newly created remote repositories to **private**.
4. Never force-push, delete a remote, rewrite a mismatched remote, merge unrelated histories automatically, or delete a duplicate local clone.
5. Never print, persist or commit credentials. Redact tokens from receipts and logs.
6. Do not fabricate institutional approvals, licences, source searches, outcomes evidence, reviewer identities, CODEOWNERS, GitHub protection state, Hugging Face Trusted Publisher state, or stage-gate decisions.
7. Do not mark G1–G6 passed and do not call the data product v1.0 without authentic evidence.
8. Ask at most one concise question only when an external identity choice is genuinely ambiguous and cannot be inferred safely. Routine engineering decisions do not require confirmation.
9. Prefer platform CLIs and APIs over browser automation. Use no `curl | sh` or equivalent download-and-execute pattern.
10. Keep a complete command, decision, verification and limitation record in `build/bootstrap/` and in the final handoff report.

## Phase 1 — locate and safely extract the archive

1. Enumerate candidate `global-family-justice-data-*.zip` archives in the current folder, excluding generated release bundles inside an already extracted tree.
2. When exactly one current source archive and matching sidecar exist, select them. If several exist, choose the newest semantically versioned source archive only when the choice is unambiguous; otherwise ask one concise question listing the candidates and their sizes/hashes.
3. Compute SHA-256 and compare it with the sidecar before extraction. A mismatch is a hard stop.
4. Inspect the ZIP before writing any member. Reject:
   - absolute paths;
   - `..`, empty or backslash path components;
   - symbolic links or special files;
   - duplicate or case-colliding members;
   - multiple top-level roots;
   - excessive member count, individual size, expanded size or compression ratio;
   - CRC failures.
5. Extract through a staging directory into an empty destination. Do not overwrite an existing non-empty directory.
6. If a valid extracted repository already exists, verify it rather than extracting a second competing copy.
7. After extraction, enter the sole top-level repository directory.

The archive contains `scripts/safe_extract_archive.py`, but that script is not available until after extraction. Use an equivalent short Python-standard-library preflight for the first extraction, then use the repository script for future extraction tests.

## Phase 2 — verify the source tree and read the authority documents

Run, with `PYTHONPATH=src` where installation has not yet occurred:

```bash
python -m gfjd.manifest --verify
python -m compileall -q src tests scripts
```

Read in full:

- `START_HERE.md`;
- `README.md`;
- `IMPLEMENTATION_STATUS.md`;
- `ROADMAP.md`;
- `V1_0_RELEASE_CRITERIA.md`;
- `VERIFICATION.md`;
- `CODEX_IMPLEMENTATION_PROMPT.md` if present;
- `config/project.toml`;
- `config/bootstrap.toml`;
- `config/github_repository_controls.toml`;
- `config/github_actions.toml`;
- `portfolio/products.toml`;
- `.gfjd/product.toml`;
- `docs/bootstrap/*.md`.

Treat checked-in contracts and safety interlocks as authoritative. If the manifest fails because the archive itself is internally inconsistent, diagnose the exact drift before making changes and record it. Do not silently regenerate the manifest until the source discrepancy is understood.

### Create the locked Python environment

Prefer `uv` and the committed lock. Keep the environment local and ignored:

```bash
uv sync --frozen --all-extras
uv run python -m gfjd version
uv run python -m gfjd doctor
```

Use `uv run` for subsequent Python commands when available. If `uv` is unavailable, install it through an official package manager or other official documented method. A fallback `python -m venv .venv` plus `python -m pip install -e '.[dev,security]'` is permissible only when a lock-exact installation cannot be performed; record that limitation and do not claim a frozen-environment verification. Never commit the virtual environment.

## Phase 3 — tool and authentication preflight

Detect the operating system and available package managers. Check:

```bash
git --version
gh --version
hf version
python --version
```

When a required CLI is missing, install it using an official package manager or official documented installer. Do not use unreviewed download-and-execute commands.

Inspect authentication without revealing tokens:

```bash
gh auth status --json hosts
hf auth whoami
```

When GitHub is unauthenticated, invoke `gh auth login` and let the human complete the unavoidable browser/device step. When Hugging Face setup is requested and unauthenticated, invoke `hf auth login` or document the exact blocked step. Do not place tokens in environment files committed to Git.

Determine:

- active GitHub login;
- available GitHub organisations;
- intended GitHub owner;
- active Hugging Face username and organisations;
- intended Hugging Face namespace;
- Git author name and a verified/noreply email.

Inference order for the GitHub owner:

1. explicit value supplied by the user or environment;
2. an existing matching remote/portfolio declaration;
3. the authenticated personal login;
4. a single clearly relevant organisation.

Do not choose between several plausible organisations merely because one appears first.

## Phase 4 — inventory local clones and existing platform repositories

Run a non-mutating plan before any Git or remote mutation:

```bash
python scripts/bootstrap_workspace.py plan --output build/bootstrap
```

Also supply bounded explicit roots that exist on the machine, such as the current parent, `~/Developer`, `~/Documents/GitHub`, `~/src`, `~/code`, `~/repos`, or Windows equivalents:

```bash
python scripts/bootstrap_workspace.py plan \
  --github-owner OWNER \
  --github-repository global-family-justice-data \
  --huggingface-namespace HF_NAMESPACE \
  --scan-root PATH_ONE \
  --scan-root PATH_TWO \
  --output build/bootstrap
```

Inspect:

- `build/bootstrap/bootstrap-plan.md`;
- `bootstrap-plan.json`;
- `local-repositories.json`;
- `portfolio-reconciliation.json`;
- duplicate remote groups;
- GitHub and Hugging Face remote inventory;
- dirty working trees;
- repository HEADs and branches;
- `.gfjd/product.toml` markers;
- normalised remote identities.

For every potentially related local clone, classify it in the handoff as one of:

- canonical active clone;
- related canonical product;
- generated distribution;
- experiment/benchmark;
- fork;
- archive/superseded clone;
- unrelated false positive;
- unresolved duplicate.

Do not delete, move, merge or rewire these clones automatically. Do not edit another repository unless it is clearly in scope and its current state has first been captured.

Query existing remote repositories with `gh repo list` and `hf repos ls` so you do not create a duplicate. A name match alone is insufficient: inspect owner, visibility, default branch and remote identity.

## Phase 5 — initialise Git and create/wire GitHub

Use `config/bootstrap.toml` as the default target. The expected repository name is `global-family-justice-data`, the default branch is `main`, and default visibility is private.

Before apply:

1. ensure the source tree manifest is valid;
2. ensure `.gitignore` excludes credentials, virtual environments, caches, build products and local bootstrap receipts while retaining intentional generated evidence;
3. ensure no secret or private-data scan errors exist;
4. inspect whether `.git` or `origin` already exists;
5. verify the target GitHub repository does not conflict with an unrelated repository.

Apply with explicit confirmation:

```bash
python scripts/bootstrap_workspace.py apply \
  --github-owner OWNER \
  --github-repository global-family-justice-data \
  --visibility private \
  --author-name "NAME" \
  --author-email "EMAIL" \
  --yes
```

The apply command must:

- initialise Git only when needed;
- configure local pull/fetch/rerere/autocrlf/signing defaults;
- create a commit only when content is uncommitted;
- create or attach the GitHub repository;
- retain a matching existing `origin`;
- fail on a mismatched `origin` rather than rewriting it;
- push `main` without force;
- verify local HEAD equals the remote `refs/heads/main` SHA;
- write and verify `bootstrap-receipt.json` and the hash-chained audit log.

Then inspect:

```bash
git status --short --branch
git remote -v
git ls-remote origin refs/heads/main
gh repo view OWNER/global-family-justice-data --json nameWithOwner,url,visibility,defaultBranchRef
python scripts/bootstrap_workspace.py verify
```

If the repository already exists with unrelated commits, do not use `--force`, `--mirror`, history replacement, or an automatic unrelated-history merge. Stop that mutating step, preserve evidence and report the conflict.

## Phase 6 — GitHub repository controls

Apply basic repository settings only after remote creation and permission verification:

```bash
python scripts/bootstrap_workspace.py apply \
  --github-owner OWNER \
  --github-repository global-family-justice-data \
  --visibility private \
  --apply-github-controls \
  --yes
```

Then compare live settings against `config/github_repository_controls.toml`. Apply controls that can be safely and accurately configured with the available plan and permissions. This includes, where supported and appropriate:

- default branch;
- issue/project/wiki/discussion settings;
- merge methods and delete-branch-on-merge;
- Actions default permissions;
- branch/tag rulesets;
- required checks that exactly match emitted workflow job names;
- merge queue;
- release-candidate and stable-release environments;
- dependency graph, Dependabot, secret scanning, push protection and private vulnerability reporting.

Do not fabricate CODEOWNERS or environment reviewers. `.github/CODEOWNERS.example` must remain an example until real GitHub handles and deputy coverage are supplied. Keep controls marked unverified unless a live API capture proves them. Record API responses or normalised settings snapshots without credentials.

Some controls depend on GitHub plan, repository visibility, organisation policy or administrative rights. Report these as external blockers rather than weakening the desired state.

## Phase 7 — Hugging Face topology and OIDC

If a Hugging Face namespace is authenticated and unambiguous, create the configured repositories **private** and empty:

```bash
python scripts/bootstrap_workspace.py apply \
  --github-owner OWNER \
  --github-repository global-family-justice-data \
  --visibility private \
  --huggingface-namespace HF_NAMESPACE \
  --create-huggingface \
  --yes
```

Expected repositories:

- dataset `gfjd-source-catalogue`;
- dataset `gfjd-observations`;
- dataset `gfjd-outcomes-evidence`;
- dataset `gfjd-extraction-benchmark`;
- Space `gfjd-explorer`.

Verify owner, type and visibility after creation. Do not upload production data merely to prove connectivity.

Configure Hugging Face Trusted Publishers for short-lived GitHub OIDC publication when platform support and permissions allow. Start from `templates/github-actions/publish-huggingface-oidc.yml`, replace placeholders, pin every third-party Action to a reviewed full commit SHA, and bind the publisher to the exact GitHub repository/workflow/environment. Do not add a long-lived `HF_TOKEN` when OIDC is available. If Trusted Publisher configuration requires a web-side administrative decision that cannot be automated safely, leave a precise checklist and keep publication disabled.

GitHub remains the authority; Hugging Face repositories are generated distributions. Never enable bidirectional sync or accept direct Hub edits as canonical source data.

## Phase 8 — reconcile the portfolio

After platform identities are real and verified, update the portfolio declarations through a reviewed commit:

- replace `PENDING/...` only with observed canonical identities;
- preserve `gfjd-platform` as the canonical source/control repository;
- mark Hugging Face repositories as generated distributions;
- record relevant local clone paths only where useful and non-sensitive;
- identify superseded or duplicate repositories without deleting them;
- add migration/deprecation notes when an existing repository overlaps the new topology.

Do not record personal absolute filesystem paths in public files unless deliberately approved. Keep local-only mappings in ignored bootstrap receipts or a local override.

## Phase 9 — engineering and quality completion

Create an isolated environment from the locked toolchain when network access permits. Run the strongest available harness, fixing root causes rather than suppressing checks. With `uv`, use:

```bash
uv run python -m compileall -q src tests scripts
uv run ruff format --check src tests scripts
uv run ruff check src tests scripts
uv run mypy src
uv run pytest -q
uv run python -m gfjd validate --as-of 2026-07-20
uv run python -m gfjd security
uv run python -m gfjd.manifest --verify
```

Without `uv`, run the equivalent commands from the verified active environment and state exactly which tools were unavailable.

Also exercise:

- bootstrap plan on bounded test roots;
- receipt and audit verification;
- safe ZIP extraction negative tests;
- contract lock verification;
- catalogue build and verification;
- public products;
- deterministic release double-build where release blockers permit draft rehearsal;
- wheel/sdist build, inspection and clean installed-CLI smoke test;
- CI and repository policy checks;
- remote setup in dry-run/fake-CLI tests;
- Windows/macOS/Linux path behaviour where the environment supports it.

Never weaken a threshold or release interlock simply to obtain green output.

## Phase 10 — commit and handoff

Before the final commit:

1. remove caches, transient build outputs and credentials;
2. update generated files intentionally;
3. regenerate `config/contract_lock.json` if public contracts changed;
4. regenerate `MANIFEST.sha256` only after the source tree is frozen;
5. verify the manifest again;
6. ensure the working tree is clean;
7. push without force;
8. verify the remote commit identity.

Provide a final report containing:

- extracted repository path;
- archive and manifest hashes;
- GitHub owner/repository, visibility, URL and verified remote SHA;
- whether the GitHub repository was created or attached;
- controls applied, controls verified and controls blocked;
- Hugging Face namespace and repositories created/attached;
- OIDC/Trusted Publisher state;
- table of relevant local clones and classifications;
- duplicate/conflicting remote findings;
- exact test, lint, type, validation, security and reproducibility results;
- commits created and pushed;
- changed files;
- unresolved defects, risks and external decisions;
- explicit confirmation that no force push, remote deletion, credential persistence or unsupported governance claim occurred.

Continue implementing safe, material improvements from `CODEX_IMPLEMENTATION_PROMPT.md` and `ROADMAP.md` after setup. The repository and its machine-readable contracts take precedence over this covering prompt where a later, stricter safety rule exists.

---
