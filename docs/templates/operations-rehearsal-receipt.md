# Operations rehearsal receipt

This receipt records a local or synthetic rehearsal only. It is not evidence
of hosting, independent custody, signing, live monitoring, support ownership,
or production readiness.

## Frozen identity

- Candidate digest:
- Rehearsal ID:
- Started/finished (UTC):
- Operator (agent or named operator):
- Environment:

## Exercises

| Exercise | Result | Receipt/evidence reference | Follow-up |
|---|---|---|---|
| Clean release rebuild | pass/fail | | |
| Backup and restore | pass/fail | | |
| Correction/takedown workflow | pass/fail/not-run | | |
| Rollback/incident workflow | pass/fail/not-run | | |
| Monitoring/alert simulation | pass/fail/not-run | | |

## Boundary (mandatory)

- custody class: `local-rehearsal-only`
- signature status: `unsigned`
- live host established: **no**
- independent custodian established: **no**
- accountable service owner/deputy established: **no**

Any attempted production or independent-custody claim invalidates this
receipt and must be recorded as a failed verification.
