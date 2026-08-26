# Public B0 monitoring, replay and supersession

The public B0 monitor retrieves every pinned provider locator in the custody receipt without using
a local cache. It records only identity, availability, final host, size and SHA-256/BLAKE3 results;
source bytes are discarded after each bounded request.

`.github/workflows/source-monitor.yml` runs weekly and on demand from `main`. Each run validates
the custody and supersession contracts, checks all replicas, uploads a temporary workflow artifact,
and creates an append-only public prerelease tagged `b0-monitor-<run-id>-<attempt>`. These tags are
monitoring evidence, not product releases or programme-gate decisions.

The monitor fails closed after publishing its receipt when any replica is unavailable, redirects to
an unapproved host, exceeds its expected size, or differs by either digest. An outage does not
authorize replacement, deletion, overwriting, or promotion. Repair adds a new public replica and a
new custody receipt; historical receipts remain unchanged.

`data/preservation/public_b0_supersession.json` is the canonical append-only snapshot graph. A
correction or new edition adds a node and a directed `supersedes -> snapshot_id` edge. The verifier
rejects missing nodes, self-links, duplicates and cycles, and emits a deterministic topological
replay order. An empty edge set means the current snapshots are independent; it is not evidence
that their underlying statistics are comparable.

Local verification:

```bash
uv run gfjd archive verify-custody data/preservation/public_b0_custody_20260827.json
uv run gfjd archive verify-supersession data/preservation/public_b0_supersession.json
uv run gfjd archive monitor \
  --custody data/preservation/public_b0_custody_20260827.json \
  --output build/public-b0-monitor/receipt.json \
  --checked-at 2026-08-27T00:00:00Z \
  --source-commit "$(git rev-parse HEAD)" \
  --run-id local-rehearsal
uv run gfjd archive verify-monitor build/public-b0-monitor/receipt.json
```
