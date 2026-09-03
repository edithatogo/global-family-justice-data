# Real B0 cohort intake — 2026-09-03

The repository-owned intake verifier examined every inventory-declared raw
payload without network access. It requires a local file and an exact
SHA-256 match before a source can enter B0 replay.

Command: `uv run python scripts/assemble_b0_evidence_cohort.py --output
data/federation/real-b0-cohort-intake-2026-09-03.json`.

Result: terminal stop. The inventory contains six real editions, but their
payload paths are not present in this checkout. Consequently zero editions
are eligible for empirical replay. Acquisition manifests and declared hashes
are retained as metadata; they are not source-byte custody evidence.

No synthetic fixture was substituted, no source was downloaded, and no replay
or layer promotion was claimed. To unblock WI-G4-MED-02, place the exact
authorized bytes at the inventory paths (or provide a separately authorized
immutable byte receipt), rerun the verifier, then execute the existing
source-recomputing replay and bind its receipt.
