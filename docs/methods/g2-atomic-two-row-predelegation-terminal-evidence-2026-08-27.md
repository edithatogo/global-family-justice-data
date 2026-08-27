# G2 atomic two-row pre-delegation terminal evidence — 2026-08-27

`G2PKT-ATOMIC-TWO-ROW-BLIND-20260827-01` stopped during orchestrator workspace
construction, before either extraction role was delegated and before any
extraction output or comparison was created.

The explicit-allowlist builder rejected the bound instruction input because
the supplied expected SHA-256 (`b5eb660d…9c7c6`) differed from the actual
SHA-256 (`024bfcb9…1398`). The two source editions themselves matched their
frozen SHA-256 values, but the contract makes any workspace or
artifact-binding discrepancy terminal. No workspace was promoted, no agent
inspected source content, and no repair or automatic rerun was performed.

This record demonstrates fail-closed preflight behaviour only. It supplies no
reproducibility result. `G2-C04`, `G2-C07`, `WI-G2-04`, `WI-G2-07` and M06
remain unchanged and in review or below their required maturity. G2 remains
blocked.

The bounded next option is a genuinely fresh lineage whose manifest is
generated and independently recomputed from the committed files before its
signed freeze. Reusing this packet ID or silently correcting this failed
lineage is prohibited.

Repository-owned remediation is implemented in
`gfjd.g2_role_isolation.bind_role_inputs`: it derives the allowlist digests
from the exact files, while the workspace builder still recomputes them as a
separate check. A negative test proves that a post-binding change is rejected.
This prevents the same transcription error but does not authorize or execute a
successor lineage.
