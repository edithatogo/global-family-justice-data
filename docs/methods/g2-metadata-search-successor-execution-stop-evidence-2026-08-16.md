# G2 metadata-search successor execution stop evidence — 2026-08-16

Status: `in_review`; terminal failed execution evidence. This record does not
support G2 passage, candidate promotion, source access, publication or release.

## Authorized execution

The fresh registrar verified the signed design freeze, owner decision and
authority receipt, then submitted all 208 frozen `G2S2Q` queries in manifest
order. Each query used one provider call. There were zero retries. The run
retained title-and-URL metadata only and did not request any result URL, landing
page, file, `HEAD` endpoint, redirect or source content. It made no contact and
persisted no snippets, source extracts or target facts.

The execution produced 1,034 result records and 609 unique canonical passive
hypotheses: 329 HTML, 235 file and 45 other. Every exposure record has
`requested: false`.

## Terminal stop

The frozen verifier found passive-result overlap with the reconstructable
predecessor exposure ledger and returned only:

`candidate overlaps reconstructable predecessor exposure`

The registrar therefore stopped the lineage. It did not filter the overlaps,
repair the sealed output, retry a query or promote the 599 non-overlapping
results. The signed evidence commit is
`e02d7b0aa015cda7b1ae24e7eb45066fc3077811`.

| Artifact | SHA-256 |
|---|---|
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/registrar/execution-bundle.json` | `5cf8a003d863d4b4543db338e705bd111f37af97521643e32505a6b7ab0d4954` |
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/registrar/registrar-event-log.json` | `9a4a5c3ddac81620e65032091b6f8451ba10820e1a266c7e116f0209e5bb3c48` |
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/registrar/registrar-boundary-receipt.json` | `9f63c586bc3ceb6d2a9d2cd16ba3db8763ffde4a4cc03124b3adbcef04c5af64` |
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/registrar/semantic-verification-stop-receipt.json` | `f298b7f0dae1c6cc9d83336054c3e83044b6155882f54c10630be06d622580ab` |
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/panels/network-disabled-exposure-audit.json` | `7f7185b2a308624b0728f1e42aadd3439b8d60062939c195bbec1f26295e2b91` |
| `data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/panels/stopped-execution-advisory-review.json` | `ac12623837e3c66241de4b2db824414e292dfb4239e195387d6016b6b9c89fba` |

## Network-disabled review

The exposure audit independently recomputed all counts and confirmed the
zero-request metadata boundary. It found 10 overlaps in the immediate ledger
used by the frozen verifier and 23 overlaps across the complete digest-bound
predecessor chain. The frozen stop is valid, but its immediate-ledger check
understates cumulative exposure.

The separate methods/governance review found the network execution compliant
up to semantic verification and confirmed that the overlap requires terminal
failure. All 609 observed URLs are now exposed for future unseen-edition work.
No subset may be retrospectively selected from this failed lineage.

## Repository remediation and remaining decision

A separate prospective helper now traverses the complete digest-bound exposure
chain with binding, path and depth checks. It does not modify or relabel the
frozen verifier or this failed run. Any future successor must freeze the full
609-URL exposure set, use complete-chain non-overlap verification and receive a
new exact owner authorization before any network request.

The sole owner must separately choose whether to prepare that successor or end
the metadata-search route. Until then, `WI-G2-07` and
`E-PILOT-INDEPENDENT-ASSURANCE` remain `in_review` and G2 remains blocked.
