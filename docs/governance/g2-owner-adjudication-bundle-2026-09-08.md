# G2 owner-adjudication bundle — 2026-09-08

Status: `pending_owner_adjudication`  
Scope: bounded four-source exact-edition exercise only.  
Claim limit: repository-owned reproducibility evidence; not independent assurance, rights clearance, G2 passage, publication or release.

## Bound implementation and semantic records

All repository records are on signed merge commit `c4c9260194798bc50a40c5c8d2bf4583e728c35a`.

| Record | SHA-256 |
|---|---|
| Exact-custody semantic review | `d3fd4c5ce857413806d3fd00bc7b6086fe0d0ef1880afdcd1c02ef8d02385648` |
| Dual-extraction preparation record | `8f4d9578335082b9af41ed462ff9339a612e1194473f764e60454ce98df41174` |

The exact source custody hashes and locators are recorded in the four custody records referenced by the preparation record. Source bytes remain outside Git under controlled local custody.

## Sealed run artifacts

The build directory is ignored and must be verified by hash before any decision record refers to it:

| Artifact | SHA-256 |
|---|---|
| Path A output | `c0f9623085f7836a70e7b5da5980642541751b9407129f1bff539594ce399b9f` |
| Path A receipt | `cbfd331306bd40dccd079b939a42a88b59770f7c01b8bb4bf87b9e65e0d91c06` |
| Path B output | `285a98470bd8d6ac2427a4f9684aa22566ce1d1540c956e97ee49ee49bdd61e02baf` |
| Path B receipt | `37dcd4d0fda29d5118b9476a07f8841d82434d7de0d5dfab5ef48913351cabd9` |
| Exact comparator receipt | `4db4970725714e3dd1fa87aa7adb8e8e0716035e62014f8f4ccca1c447d0f46b` |
| Difference report | `6c406b29bbded8386e83f17ed9781c3e3388f430fac894e53189dab93c35a5c6` |

The comparator result is `critical_concordance=1.0` and `overall_populated_field_concordance=1.0`. Path B now uses a separate implementation and fresh process over the same exact bytes, with a raw-source recheck. It remains repository-owned evidence, not agent-blinded independent assurance.

## Decision requested

I, the repository owner, may record one of the following decisions:

**Accept bounded evidence.** I accept this sealed run only as supporting repository-owned evidence for the four named exact editions and frozen contract. I do not accept `WI-G2-04` or `WI-G2-07` as complete, because this separate-process path-B implementation is not agent-blinded role-separated assurance. Rights, privacy, security, semantic equivalence, publication, release and G2 passage remain separately controlled.

**Keep in review.** I retain both work items in review pending a stronger role-separated or external assurance record.

**Reject.** I reject the run and preserve all artifacts as immutable failed or superseded evidence.

Any acceptance must name the option, owner identity, commit, record hashes, scope, conditions, expiry and reopen trigger. It must not relabel this repository-owned recheck as independent assurance.

## Recommended option

Accept only as bounded repository-owned supporting evidence, keep `WI-G2-04`, `WI-G2-07`, G2-C04 and G2-C07 in review, and retain all rights/publication/release restrictions. This resolves a technical preparation gap while preserving the accountable gate.
