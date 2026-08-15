# G2 metadata-search successor owner-decision packet

## Decision requested

Decide whether to freeze and later execute a separately identified,
provider-isolated metadata-search successor. No execution is authorized by this
packet. An executable decision can be recorded only after the detached manifest
is bound to a signed freeze commit.

The failed predecessor and stop evidence remain immutable. Because the prior
aggregate response cannot be reconstructed completely, a repaired continuation
or resubmission of `G2Q-001` through `G2Q-004` is not an available option.

## Option A — freeze the provider-isolated successor (recommended)

Freeze 204 never-submitted query definitions and four prospectively different
replacement definitions as 208 new `G2S2Q-` queries. If separately authorized
after the signed freeze, submit exactly one query in each of 208 provider calls,
with no retries.

Trade-offs:

- preserves the original bounded 208-position search structure without
  pretending the contaminated positions are unseen;
- produces per-query attribution if the provider honors isolated calls;
- makes the lineage total explicit: four failed prior submissions plus 208
  successor submissions equals 212;
- introduces four prospectively different search formulations, so the successor
  is a redesign rather than an exact repetition of the original scientific
  frame; and
- cannot establish non-overlap with the unknown URLs in the failed aggregate
  response.

Contingencies:

- stop immediately if a provider response is still not attributable to its one
  submitted query;
- stop on any retry need, access attempt, classification ambiguity, budget
  mismatch, or manifest drift;
- if provider behavior cannot meet the frozen output contract, terminate or
  design a different provider method before any further submission;
- if the completed bounded result is insufficient, return for a separate scope
  decision without adaptive queries or silent shrink; and
- keep every candidate metadata-only and unrequested pending later authority.

Rationale: this is the only prepared route that retains bounded coverage while
explicitly isolating the irreconstructable exposure and correcting every high
stop-panel finding.

## Option B — terminate the metadata-expansion lineage

Preserve the failed execution and successor design as terminal evidence and make
no further provider submissions.

Trade-offs:

- avoids all additional search exposure and provider uncertainty;
- has the simplest evidentiary boundary; but
- does not expand the candidate frame, leaves G2 blocked, and requires a new
  methods route if the programme is to continue.

Contingency: design a different bounded discovery method prospectively and bring
its exact contract back for a new owner decision before any access.

## Recommendation

Choose Option A only after reviewing the exact detached manifest and signed
freeze commit. The authorization must be narrow: 208 named successor queries,
208 isolated provider calls, zero retries, passive metadata retention only, and
no URL or source access. Do not authorize or imply reconstruction or
resubmission of `G2Q-001` through `G2Q-004`.

## Exact future owner wording

The following wording is suitable only after replacing the bracketed bindings
with the exact current values and verifying them:

> I approve Option A in the G2 metadata-search successor owner-decision packet
> dated 2026-08-16. I accept `G2HOLDOUT-METADATA-EXPANSION-20260816-02` as a
> separately identified redesign, not a repair or continuation of the failed
> predecessor. I bind this decision to signed freeze commit `[COMMIT]` and
> `SUCCESSOR_DESIGN_MANIFEST.sha256` SHA-256 `[MANIFEST_SHA256]`.
>
> I acknowledge that the failed aggregate response is incompletely
> reconstructable. `G2Q-001` through `G2Q-004`, their exact query texts, and the
> unknown passively exposed URLs remain contaminated or unavailable. I do not
> authorize their resubmission and I do not accept any claim that the unknown
> prior exposure was captured or cleared.
>
> I authorize only the 208 exact `G2S2Q-` queries in the bound successor query
> manifest. A fresh registrar may make exactly 208 provider calls, with exactly
> one logical query per call and zero retries. The four prior submissions and
> 208 successor submissions must be reported as 212 cumulative lineage
> submissions. Each event must capture its ISO execution date and timezone-aware
> provider-call start and finish timestamps within the decision's authorized
> interval.
>
> Passive search-index results may be recorded as metadata-only HTML, file, or
> other URL hypotheses, with URL kind and domain recomputed and `requested:
> false`. Passive direct-file URLs may appear in exposure and candidate records
> but never in the proposed HTML allowlist. Only canonical official HTTPS HTML
> URLs may be proposed for that allowlist.
>
> No result URL, landing page, file endpoint, HEAD request, redirect, snippet,
> source excerpt, target fact, source content, outbound contact, publication,
> release, rights acceptance, structural inspection, extraction, or G2 passage
> is authorized. Any contract, attribution, boundary, retry, budget, binding, or
> provider failure stops the run without adaptive rescue and returns to me.

The accepted decision must then be represented with the exact structured
semantics required by `successor-owner-decision.schema.json`. The record
must supply a bounded `valid_from` and `valid_until`, the exact design and query
manifest descriptors, and the freeze commit. A separately generated authority
receipt conforming to `successor-authority-receipt.schema.json` must record the
two commit-object and signature checks. The execution verifier does not trust
those status fields alone: it reruns `git cat-file`, `git verify-commit`, and
commit-tree blob hashing for the frozen design manifest and owner decision.

After the owner-decision record is committed, the detached *design* manifest is
not regenerated to include that later decision. Instead, the execution bundle
binds both the frozen design manifest and the separately hash-bound authority
receipt. This preserves the prospective freeze while avoiding a circular hash
between the design, decision, and authority receipt.

## Current authority state

No owner decision is recorded here. The user’s general instruction to proceed
predates the exact successor manifest and signed freeze binding, so it cannot be
treated as the digest-bound future execution authorization described above.
