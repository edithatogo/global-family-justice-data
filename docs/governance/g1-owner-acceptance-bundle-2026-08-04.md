# G1 owner acceptance bundle — 2026-08-04

This is the refreshed owner-ready G1 handoff after the T4–T9 and risk
mitigation implementation passes. It records repository-owned evidence and
the exact remaining authority boundary; it does not force G1 acceptance.

## Bound artefacts

| Artefact | SHA-256 |
|---|---|
| `docs/governance/g1-owner-decision-packet-2026-08-03.md` | `c32b6dbf613ea1e342a704c4f72b5124cf536fa63a75e078b1e68909c30e4e6c` |
| `docs/governance/g1-evidence-index-2026-08-03.md` | `18f9e148de53e19cc082fde0967adbe5356ee4e973e27bc4b70e7a0ecc16a513` |
| `docs/governance/g1-control-gap-matrix-2026-08-03.md` | `00bbe85cd506c64be8f54a678e67e38932bfce1bef5435ccfab57989cb15c872` |
| `docs/governance/g1-panel-pre-assurance-2026-08-03.md` | `d579b735fb57c74b383ef295106eaaaa5f5521932ac85ccbf0d01205b3c1d20c` |
| `docs/governance/risk-mitigation-control-packet-2026-08-04.md` | `523f055f0ef173c98d2d33ecb7c31403b264f1140dc556f2ee361472193cb622` |

The file-level evidence bindings are authoritative in `MANIFEST.sha256`; the
manifest itself is intentionally not recursively hashed in this table.

## Current owner decision state

The recorded owner decision is conditional repository-governance acceptance,
not G1 passage. The Conductor must reject a transition to `accepted` while
mandatory work, evidence, reviewer records, residual risks or dependencies are
incomplete.

## Remaining G1 acceptance fields

- owner-held host/sponsor and decision-rights record (supplied in the
  single-person owner decision);
- explicit no-deputy exception and owner-unavailability pause rule (supplied);
- accountable ethics/security/architecture/risk/rights acceptance;
- required specialist, local or human review records;
- pilot-scope decision and supporting evidence;
- accountable decision reference bound to the final packet and manifest.

Agent-panel advice, local tests and repository ownership do not substitute for
these fields. The candidate remains private and unpublished.
