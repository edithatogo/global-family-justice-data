# T0 acceptance runbook

This runbook converts the implemented T0 controls into a bounded review package.
It does not confer authority or record acceptance by itself.

## Repository preparation

The maintainer:

1. runs `make PYTHON='uv run python' autonomy-full`;
2. builds and verifies `build/governance` and `build/gate-packs/G1`;
3. confirms the source revision and every evidence SHA-256 in
   `programme/evidence_register.csv`;
4. sends the immutable G1 pack digest to the named reviewers;
5. continues only unrelated repository-owned work while review is pending.

## Genuine inputs still required

Record real names and evidence references for:

- host or sponsor and executive release owner;
- accountable owner and consenting deputy for each critical track;
- methods, data, technical, quality, security/privacy, service and international
  accountabilities;
- an independent assurer who did not produce the reviewed implementation;
- conflicts declarations and any recusals;
- disposition of R02, R10, R11, R15, R16 and R20;
- the G1 decision authority, decision date and immutable decision reference.

No placeholder handle, role label, automated test result or maintainer assertion
may substitute for these inputs.

## Review sequence

For each G1 evidence record, the genuine reviewer checks the registered file
against its SHA-256 and supplies their role, review date, status and notes. The
maintainer then records that supplied decision with:

```bash
gfjd conductor evidence EVIDENCE_ID accepted \
  --reviewer "GENUINE REVIEWER ROLE" \
  --reviewed-on YYYY-MM-DD \
  --notes "Reference to the fixed review record"
```

The accountable authority separately dispositions each critical risk:

```bash
gfjd conductor risk RISK_ID \
  --actor "GENUINE ACCOUNTABLE ROLE" \
  --status accepted \
  --notes "Immutable risk-acceptance reference"
```

Risk severity must not be reduced merely to pass the conductor; supply
`--residual-severity` only when the referenced assessment independently supports
the change. Accepted critical risks may cease blocking early governance gates but
continue to block release-candidate gates until closed or genuinely reduced. When
all G1 criteria, work, risk and maturity controls are genuinely satisfied, record
work acceptance and the gate decision using the conductor CLI. Rebuild the
governance pack after every accepted record; reviewers approve a digest, never a
moving branch.

## Solo-maintainer boundary

The maintainer can prepare, test, hash, transmit and record supplied decisions.
The maintainer cannot create the appointments, consent, independence, risk
acceptance or decision. If no independent reviewer or deputy is available, G1
remains blocked while autonomous technical implementation continues.
