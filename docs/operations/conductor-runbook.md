# Programme conductor operations runbook

## Routine review

Run `gfjd validate --strict`, `gfjd conductor status` and `gfjd conductor next` at each programme-assurance review. Review overdue risk dates, open P0/P1 defects, expired evidence, dependency-ready work and the first unpassed gate.

## Work-state change

Use `gfjd conductor work <id> --status <state> --actor <role> --note <reason>`. The state machine prevents unsupported transitions. A work item cannot become accepted unless all linked evidence is accepted or waived.

## Evidence review

1. Confirm the evidence file is repository-contained and complete.
2. Confirm the reviewer is independent of the owner role.
3. Run `gfjd conductor evidence <id> --status accepted --reviewer <role>`.
4. The conductor calculates the SHA-256 value and records reviewer/date through an atomic mutation.
5. Re-run validation and inspect the audit event.

A missing path, owner-reviewer conflict, stale checksum or expired record blocks acceptance.

## Gate decision

A gate decision must not be recorded until `gfjd conductor gate <gate>` reports `ready_for_decision`. Record the governing minute, resolution or decision identifier with `gfjd conductor decision`. Conditional decisions do not count as passage unless the configured policy explicitly changes.

## Direct edits

Direct CSV edits are visible in Git but bypass the runtime audit event. Protected branches should require review and should normally permit state changes only through conductor commands or a reviewed administrative migration.

## Recovery

The control state is Git-versioned and human-readable. Restore the last accepted revision, run full validation, compare the audit log and repository diff, then reapply any authorised events. Never repair a passed gate by silently editing generated status output.
