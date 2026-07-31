# Codex operating instructions

Codex reads this file before doing any work in the repository.

1. Read `START_HERE.md`, then `BOOTSTRAP_AND_HANDOFF_PROMPT.md`, then `CODEX_IMPLEMENTATION_PROMPT.md` in full.
2. Treat `MANIFEST.sha256`, the Git history, `config/`, `schemas/`, `programme/`, and the two prompts as authoritative inputs.
3. Preserve the existing commit history. Never squash, reset, force-push, delete a remote branch, or replace a mismatched `origin` merely to simplify setup.
4. Run the source manifest check and the complete local quality gate before material changes. Fix failures; do not lower controls to obtain green output.
5. Use the plan-first bootstrap workflow in `scripts/bootstrap_workspace.py`. New GitHub and Hugging Face repositories are private by default.
6. Continue autonomously through safe, testable work. Make small coherent commits, maintain an implementation ledger, and keep the working tree reviewable.
7. Do not fabricate empirical court data, governance approvals, source-rights decisions, reviewer identities, institutional appointments, external assurance, or stage-gate completion.
8. Keep synthetic fixtures conspicuously fictional and the public repository aggregate-only.
9. The programme conductor governs evidence and release authority; a passing technical workflow cannot certify a programme gate.
10. Before ending a work session, rerun relevant checks, commit coherent completed work, and update `IMPLEMENTATION_STATUS.md` or a clearly identified continuation ledger.
11. For single-maintainer autonomous work, build `build/autonomy/autonomy-context.md`, use `autonomy-fast` during iteration, and run `autonomy-full` at phase closeout. Treat its external-boundary list as fail-closed.
