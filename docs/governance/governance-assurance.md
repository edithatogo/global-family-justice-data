# Governance assurance operation

Run `gfjd governance build --output build/governance --as-of YYYY-MM-DD`, then
`gfjd governance verify --output build/governance`. The pack includes all six gate
evaluations, every criterion and linked evidence state, defect/exception
disposition, an unsigned release-decision template and checksums.
The workflow-contract gate packs are written separately under `build/gate-packs/G1`
through `G6`; use `--gate-output` to select another controlled build location.

The build is deliberately fail-closed. It reports the conductor's current state but
does not accept evidence, pass a gate, infer a person's identity, sign a decision or
authorise publication. Generated files are review inputs; accepted evidence must be
committed through the evidence register with genuine review metadata and the gate
decision must be recorded separately by its named authority.
