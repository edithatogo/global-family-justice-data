# G2 cumulative-exposure successor execution — owner decision packet — 2026-08-16

Status: awaiting sole-owner decision. This packet authorizes nothing.

## Bound preparation

- owner preparation decision commit:
  `1129d06c012624c3ff7d1ea1b92214dda1da87c2`;
- signed successor freeze commit:
  `7c74ad35b7ebed26c4b3716be3afca9b9bf4fae5`;
- detached design-manifest SHA-256:
  `5a9b809ce7bcc123f24602c9a95478c32908e8534884b3daa6e5105c77b691ca`;
- exact query-manifest SHA-256:
  `27df88d028e7b6f6d26b33e3374ad2d7a55f5a6a91d266641636d84bde18003e`;
- cumulative exposure-ledger SHA-256:
  `e43628df4592ab3386ad811d0871532d2fe40e6af7f169455994447572b8242d`.

## Options

### Option A — authorize the exact bounded metadata search

Recommended. Authorize the frozen 208 queries as isolated search-index calls,
one query per call and zero retries, during a prospective 24-hour interval. The
registrar may persist title/URL metadata hypotheses only. Complete-chain
exposure verification must run before any result can enter advisory review.

Trade-off: the 672-URL cumulative denylist makes a further fail-closed stop
likely, but this is the only option that can produce new unseen discovery
evidence without weakening the exposure contract.

Contingency: any authority, attribution, budget, boundary or overlap failure
terminates the lineage. No filtering, repair, subset promotion or rerun is
permitted.

### Option B — retain the frozen design without execution

Preserve the design as evidence that the control gap was remediated, but defer
all network work.

Trade-off: avoids further exposure while leaving WI-G2-07 and G2 blocked.

### Option C — terminate metadata-search discovery

Archive this design as unused and prepare a different prospective evidence
method.

Trade-off: avoids repeated provider-index contamination but requires a new
methods design and delays the blind holdout.

## Recommendation

Choose Option A only with a fresh 24-hour interval that begins after the signed
decision and authority receipt exist. The design is reproducible, all 609
current observations are denied, and the complete predecessor chain now fails
closed. No source or result URL access is needed.

## Exact approval wording

Replace both bracketed timestamps with a prospective 24-hour interval before
accepting:

> I approve Option A in the G2 cumulative-exposure successor execution owner
> decision packet dated 2026-08-16. I accept
> G2HOLDOUT-METADATA-EXPANSION-20260816-03 as a separate preparation bound by
> signed freeze commit 7c74ad35b7ebed26c4b3716be3afca9b9bf4fae5,
> detached design-manifest SHA-256
> 5a9b809ce7bcc123f24602c9a95478c32908e8534884b3daa6e5105c77b691ca,
> query-manifest SHA-256
> 27df88d028e7b6f6d26b33e3374ad2d7a55f5a6a91d266641636d84bde18003e,
> and cumulative exposure-ledger SHA-256
> e43628df4592ab3386ad811d0871532d2fe40e6af7f169455994447572b8242d.
>
> I authorize the exact 208 frozen queries, one query per search-index call and
> zero retries, from [VALID_FROM] until [VALID_UNTIL]. All 609 observations from
> the failed predecessor and all URLs in its complete digest-bound predecessor
> chain remain denied. Passive results may be recorded only as title/URL
> metadata hypotheses with requested false.
>
> No result URL, landing page, file, HEAD endpoint, redirect, source content or
> contact is authorized. No snippet, source excerpt or target fact may be
> persisted. Any scope, attribution, budget, authority, access-boundary or
> cumulative-overlap failure terminates the lineage without filtering, repair,
> subset promotion or retry.
>
> This decision does not authorize source inspection, extraction, rights
> acceptance, publication, release or G2 passage.
