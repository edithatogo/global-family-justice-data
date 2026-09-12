# G2 partitioned official-manifest route (2026-09-12)

**Evidence ID:** `E-G2-PARTITIONED-MANIFEST-ROUTE-20260912`  
**Status:** `in_review` — repository-owned preparation only  
**Gate:** G2 — Reproducible pilot proven

The previous official-manifest attempt terminated before candidate selection:
one partition redirected and an earlier child manifest exceeded its per-response
budget. This packet freezes a materially distinct successor design that uses the
canonical trailing-slash partitions and a streaming parser. Each partition is a
separate, explicitly bound request; redirects are prohibited, and no returned
locator may be opened during registration.

The machine-readable contract is
`data/methods/g2/G2PARTITIONED-MANIFEST-20260912-01/contract.json`. It raises
only the bounded partition budget (64 MiB) while retaining a 256 MiB campaign
budget, a one-million-locator cap, zero retries and complete exposure
registration. It does not broaden hosts, permit search providers, or permit
candidate-document access.

## What this unblocks

- A deterministic route is ready for owner-authorized manifest-only execution.
- The prior redirect and response-size stops remain immutable and are not
  repaired or reused as successful evidence.
- If execution succeeds, the result can support a fresh metadata-only selection
  receipt; it still cannot establish source rights, concordance, maturity L2,
  G2 passage, publication or release.

## Remaining gate

The repository cannot create a qualifying empirical result without a separately
authorized network execution and exact source artifacts. Until that occurs,
`WI-G2-CLOSE` remains blocked at evidence-assured maturity L1. No source bytes,
candidate URLs, extracted values or provider response are asserted here.

## Stop conditions

Any binding mismatch, redirect, non-success response, malformed manifest,
partition or total byte overflow, prior-exposure overlap, incomplete enumeration
or insufficient eligible editions terminates the successor lineage. There is no
retry, repair, substitution, fuzzy matching, waiver or failed-output reuse.
