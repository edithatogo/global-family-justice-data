# External operations approval register

`external-operations-approval-register.csv` is the machine-readable, fail-closed
register for operations facts that cannot be established by local repository
tests. Each row remains `pending` until the named authority records the exact
evidence and decision against the release digest.

The register covers five independent controls: hosting, archival custody,
signing/provenance, support/incident operations and committed funding. A panel
or agent may check the evidence packet for completeness, but cannot approve a
host, become a custodian, sign a release, accept service ownership or commit
funding.

Allowed lifecycle values are `pending`, `in_review`, `accepted` and `rejected`.
Only `accepted` with non-empty, digest-bound evidence may satisfy a gate. A
`rejected` or expired decision invokes the row's contingency and keeps release,
deployment and archive transitions blocked.

The register does not authorize contact, deployment, signing or expenditure.
