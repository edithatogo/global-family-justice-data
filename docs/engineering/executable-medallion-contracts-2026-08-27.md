# Executable medallion layer contracts

`config/medallion_layers.json` is the versioned machine-readable contract for
B0, B1 Bronze, Silver, Gold and Platinum. `gfjd.medallion` validates the
contract, validates independently evidenced layer records and verifies an
immediate promotion against the canonical digest of its predecessor.

The contract is deliberately separate from the frozen G2 extraction schemas.
It does not alter, repair or reinterpret any historical G2 packet or output.

Every layer has its own required evidence. A later-layer artifact cannot prove
an earlier layer mature, and promotion cannot skip a layer, change object
identity or use a non-active predecessor. Gold requires an accountable owner
decision reference; Platinum additionally requires a release-gate reference.
Their presence is validated as a binding field, but the validator does not
invent or accept either decision.

Quarantine is an orthogonal lifecycle state. Quarantined records remain visible
in coverage with reason codes and a disposition reference, but cannot be
promoted. Withdrawal and tombstoning likewise cannot be used as promotion
inputs. Negative tests cover missing layer evidence, layer skipping, digest
drift, object substitution and quarantine bypass.

This implementation establishes executable contract behavior only. It does
not establish operated B1-to-Platinum datasets, lineage replay, layer maturity,
G2 or G4 acceptance, publication or release readiness.
