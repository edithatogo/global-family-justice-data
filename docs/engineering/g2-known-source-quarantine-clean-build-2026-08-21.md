# G2 known-source quarantine clean build — 2026-08-21

Evidence ID: `E-CLEAN-BUILD`

## Result

The final two-row known-source packet
`G2PKT-REAL-PILOT-20260821-03` was rebuilt from its fresh primary extraction
output into deterministic bronze, silver, quarantine and gold layers. The
receipt is local and digest-bound at:

`build/g2-real-pilot-20260821-01/G2PKT-REAL-PILOT-20260821-03/quarantine-pipeline/receipt.json`

Receipt SHA-256:
`b317a4f5fa79e317af9843470bf1d91f4cf5d1b9d4bbec33a4f58cf258a6a4ba`.

The build produced two bronze rows, two silver rows, two quarantine records
and **zero gold rows**. The runner rejects a scope mismatch, duplicate source
record key, absent required mapping field, or a non-quarantine input row.
`verify_g2_quarantine_pipeline` passed against the recorded output digests.

## Reproduction

From a checkout containing the exact local packet-bound primary output:

```python
from pathlib import Path
from gfjd.g2_quarantine_pipeline import build_g2_quarantine_pipeline

root = Path.cwd()
build_g2_quarantine_pipeline(
    packet_path=root / "data/methods/g2/G2REAL-PILOT-20260821-03/packet.json",
    extraction_path=(
        root / "build/g2-real-pilot-20260821-01/"
        "G2PKT-REAL-PILOT-20260821-03/primary/output.json"
    ),
    output_dir=(
        root / "build/g2-real-pilot-20260821-01/"
        "G2PKT-REAL-PILOT-20260821-03/quarantine-pipeline"
    ),
)
```

## Boundary

This is a real-input, quarantine-only engineering receipt. It supports the
clean-build portion of G2-C03 but does not itself accept the evidence, resolve
methods or rights/security questions, promote a row, pass G2, authorize
publication, or release data.

