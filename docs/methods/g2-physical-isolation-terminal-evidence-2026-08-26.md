# G2 physical-isolation replacement terminal evidence — 2026-08-26

`G2PKT-MATERIAL-ISOLATED-20260826-01` is immutable terminal failed evidence.
Extractor A called the mandatory workspace-verification function with one
argument although the frozen implementation required two. The resulting
`TypeError` occurred before verification or source inspection. Extractor B was
interrupted immediately.

No source input, extraction output, extractor receipt, seal, comparison or
concordance metric was created. Network access, repair and retry did not occur.
The tracked terminal receipt is byte-identical to the sealed private receipt
and has SHA-256
`d24b32ac97029fca9d7c7f5e5833493b434e2e4dd7c21b4f7bc63153cfcad982`.

The physical-workspace implementation itself was subsequently hardened with a
one-path verifier and an explicit command-line interface:

```text
python -m gfjd.g2_role_isolation verify <workspace>
```

The CLI is covered by positive, digest-mismatch, traversal, existing-workspace,
extra-entry and tamper tests. That remediation does not revive or validate this
lineage. A network-disabled role-separated consistency review, SHA-256
`7238d589652c2a4b9985227fa56b505392181eebe20e3df0b47da8805e6a9e6e`,
confirmed the substantive stop and gate boundaries. G2-C04, G2-C07 and M06
remain blocked.
