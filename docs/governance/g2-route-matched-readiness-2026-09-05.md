# G2 route-matched execution readiness

The approved C04/C07 scope has three missing route/jurisdiction cells after
the successful SWE/AUS supporting run:

| Jurisdiction | Route | Existing binding | Current status |
|---|---|---|---|
| BRA | API | DataJud packet and source digest recorded | preparation only |
| GBR-EAW | Spreadsheet | `G2PKT-REAL-PILOT-20260821-01` bound to `data/methods/g2/G2REAL-PILOT-20260821-01/packet.json` (SHA-256 `ef9391489d63428e29f9e89b386c957348e4e5ac3b35389e59b7039caf4bd2b5`) | preparation binding recovered; execution and acceptance remain blocked |
| GBR-EAW | HTML/dashboard | dashboard packet and source digest recorded | preparation only |

The attached machine-readable packet binds those exact candidates and freezes
the intended fresh two-agent extraction, exact comparator and source-accuracy
review. It authorizes no source access, network, extraction, contact,
publication, release or G2 acceptance. The GBR-EAW spreadsheet binding is now
resolved from the existing repository record `G2PKT-REAL-PILOT-20260821-01`.
This is a known-source calibration packet, not a new successor run, and does
not by itself authorize execution or establish a qualifying C04/C07 result.

Review corrections bind the BRA class-filtered response (`626d1829…`) and
dashboard quarterly response (`4009c22c…`), rather than the predecessor API
response or dashboard entry page. All three packet paths and digests are
checked against the approved source scope by `tests/test_g2_route_readiness.py`.

The current local availability assessment is
`g2-source-availability-reconciliation-2026-09-05.md`: none of these three
exact extraction inputs was found in the bounded scan. Recover the original
artifacts and dashboard support bindings before execution. Reconcile existing
owner authorizations first; an artifact refresh alone is not a reason for
another approval. If recovery fails, a changed acquisition or pilot scope
requires one grouped decision. A passing run still requires accountable
disposition and does not itself pass G2.
