# WI-G2-07 blindness-control panel advice — 2026-09-10

Three role-separated advisory reviews considered the proposed machine-verifiable
blindness controls.

## Grouped recommendation

Proceed with a fresh lineage (new run and packet identifiers) using explicit
input allowlists, denylist checks, pre/post workspace inventories, digest
verification and network-disabled comparator evidence. Label any result
`bounded repository-owned blinded reproducibility`, not independent assurance.

## Options and trade-offs

- **A1 — Workspace attestation plus advisory panel (recommended minimum):**
  strongest practical repository-owned evidence with modest complexity; cannot
  prove agent memory or create independent authority.
- **A2 — Add process/container isolation:** stronger runtime separation but more
  platform complexity; still not independent assurance.
- **A3 — Accept current replay as WI-G2-07:** fastest, but overstates blindness
  and is rejected.

## Contingencies

Any denylist hit, unexpected file, shared state, digest mismatch, network event,
mutation, retry, repair, reuse or critical discrepancy terminates the lineage.
Panel disagreement is preserved as dissent and leaves WI-G2-07 in review.

Panel conclusion: implement A1 now and A2 where available; return the resulting
attestation and comparator for owner adjudication.
