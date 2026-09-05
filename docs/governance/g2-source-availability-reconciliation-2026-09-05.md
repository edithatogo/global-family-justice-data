# G2 source availability reconciliation — 2026-09-05

This read-only local assessment checked packet bindings and file fixity. No
external request, target extraction, source redistribution or gate decision
was performed. Historical failed records remain unchanged.

## Approved route inputs

| Route | Exact extraction artifact SHA-256 | Local result |
|---|---|---|
| BRA class-filtered API | `626d18292c23ffe5e369b3c82c5477f9265686dca86f195021bc8f100c903da3` | Not found in bounded scan |
| GBR-EAW ODS | `3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2` | Not found in bounded scan |
| GBR-EAW quarterly dashboard response | `4009c22c5e0bf115205d8488838b8c9b0f224ec627a6f9bc2f2e7be02b36fae1` | Not found in bounded scan |

The scan hashed 365 regular non-symlink files under `build/` and `data/raw/`,
totalling 87,763,312 bytes, with a 50,000,000-byte per-file limit and no read
errors. No matching original Swedish replay artifact
`19d13eafa01671a97fe94116f414d2d083375d31d584af928dcc3ede68d3a8cd`
was found either. This is bounded absence evidence, not proof that no backup
exists elsewhere.

All three packet hashes in the route-readiness record verify. Two source
identity distinctions must be preserved before execution:

- The BRA packet `G2API-BRA-TJSP-20260822-01` binds the class-filtered response
  above; `f475ae52b31f0e9a509de1be1d312bb946f4f57944717d0bda5d68d1f59df2fe`
  identifies the earlier unfiltered response, not that extraction input.
- The dashboard packet `G2DASH-GBR-EAW-20260822-02` binds the quarterly response
  above; `52d356701a10ac6519da61d82ecf3f0cb0e04921597f19a4df6fe721687ac63f`
  identifies entry HTML, not the quarterly response. Its model, conceptual
  schema and query bindings must also be recovered before a fresh run.

The local GBR-EAW ZIP has the correct archived ZIP digest, but its directory
lists 24 CSV members and one DOC member, with no ODS. It cannot substitute for
the exact approved ODS artifact. The BRA annual PDF likewise cannot replace
the class-filtered API response.

## Real B0 availability

All six paths in `data/federation/real-b0-cohort-intake-2026-09-03.json` now exist
and match that historical receipt's expected SHA-256 values:

| Inventory ID | Observed bytes | Fixity |
|---|---:|---|
| ARC-GBR-EAW-2026Q1 | 1,181,359 | Match |
| ARC-AUS-FCFCOA-202425 | 13,442,996 | Match |
| ARC-BRA-CNJ-2026 | 26,310,437 | Match |
| ARC-SWE-DOMSTOLSVERKET-2026 | 11,657 | Match |
| ARC-ZAF-JUD-202425 | 6,577,186 | Match |
| ARC-USA-MN-MJB-PERF-2024 | 1,402,492 | Match |

The September 3 missing-byte stop remains historically accurate but is no
longer a current six-object availability blocker. The existing September 4
public retrieval receipt records successful anonymous GitHub and Hugging Face
retrieval for these six objects. This assessment did not repeat those network
requests. The September 4 Swedish replay receipt records ten rows pending
review; the detailed replay artifact remains unavailable in the scanned roots.

## Executable next actions and boundaries

1. Register this current B0 fixity observation and execute authorized local
   replay/qualification against the matching sources. A fresh replay must
   carry its own receipt rather than recreate the missing historical artifact.
2. Correct the route-readiness input mapping to distinguish predecessor/entry
   identity from the actual API and dashboard response bindings.
3. Recover the three exact missing G2 artifacts and dashboard support bindings
   from an owner-controlled backup. Verify each digest before constructing
   fresh role workspaces. Retain scope and quarantine restrictions.
4. If recovery fails, return one grouped acquisition/scope decision. A new API
   response or changed dashboard response cannot be labelled the old edition.

Standing direction permits local implementation, verification and advisory
preparation. It does not remove a lineage's explicit terminal rule or supply
missing bytes. The existing route-readiness packet is preparation-only; any
execution authorization must be reconciled against the owner's actual session
directions, exact inputs and lineage history before delegation. No failed
sealed outputs are reusable and no missing result may be reconstructed from
the documented expected value.
