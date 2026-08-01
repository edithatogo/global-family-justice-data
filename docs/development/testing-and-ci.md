# Testing and CI applicability

The repository's fast pull-request quality harness is deliberately deterministic:
strict Ruff and mypy, unit tests across Python 3.11–3.14, property/adversarial
tests, branch coverage budgets, integration rehearsals, platform smoke tests,
distribution reproducibility, CodeQL, dependency review, and the scheduled
Bandit/pip-audit/zizmor security workflow all run from locked inputs.

The frontier assessment records Mutation, MT, and Contract as candidate gaps.
Contract coverage is already enforced by `gfjd harness contracts` and the schema
contract tests. Mutation testing is deferred while the project is alpha because
the current branch-aware coverage and adversarial suites provide the bounded,
replayable signal without adding an unbounded CI lane; it will be reconsidered
when the stable-core coverage ratchet reaches G2. MT (manual/GUI testing) is
not applicable to this headless data and CLI repository; the cross-platform CLI
smoke matrix is the replacement control.

Secret scanning is provided by GitHub repository secret scanning and push
protection, which are declared enabled in `config/github_repository_controls.toml`.
No third-party secret-scanner action is added so credentials do not leave the
hosted GitHub security boundary. The repository's public-boundary security
command and CodeQL remain required repository-owned checks.

Expensive or externally hosted controls remain scheduled or platform-owned;
their receipts are retained by the relevant workflow and are not treated as
evidence of publication readiness.
