# G2-C03 clean-build owner decision — 2026-08-24

Decision maker: repository owner and sole accountable decision-maker.

By directing implementation of the recommended G2 unblock sequence, the owner
accepts `E-CLEAN-BUILD`, `WI-G2-03` and `G2-C03` for the frozen two-row
real-input quarantine build. The bound receipt verifies two bronze rows, two
silver rows, two quarantine rows and zero gold rows. Zero gold is the correct
fail-closed result.

This decision is limited to deterministic pipeline execution over the bound
input set. It does not establish broader cohort coverage, extraction
reproducibility, methods equivalence, rights clearance, publication, release or
G2 passage. A changed packet or input digest, receipt verification failure or
attempted gold promotion reopens the criterion.

Machine-readable decision:
`data/methods/g2/G2NEXT-UNBLOCK-20260824-01/c03-clean-build-acceptance.json`.
