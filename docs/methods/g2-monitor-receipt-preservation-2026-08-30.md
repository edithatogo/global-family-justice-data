# Remaining G2 monitor receipt preservation — 2026-08-30

## Plan and disposition

Preserve the five completed metadata monitor runs below in Git and bind them
through `data/methods/g2/monitor-preservation-2026-08-30.json` and the source
manifest. This extends the three-root ledger correction without modifying any
historical receipt, rerunning a campaign or changing acceptance criteria.

| Hosted run | Recorded outcome | Preserved evidence |
| --- | --- | --- |
| 33288135681-1 | No candidates | Exact receipt; existing identical 2,302-row NZ sitemap ledger; empty novelty ledger |
| 33288139446-1 | No candidates | Exact receipt; empty full and novelty ledgers |
| 33288140850-1 | No update | Exact receipt; four StatCan product-metadata observations |
| 33288142864-1 | Baseline unchanged | Exact receipt including four NZ locators and unaccepted malformed date attribute |
| 33288144647-1 | Baseline unchanged | Exact receipt including UK family-statistics publication schedule |

Two downloads of each hosted artifact matched byte-for-byte. Their provider-
reported archive digests and identities are recorded in the index; these are
distinct from the independently computed hashes of each preserved file. The
API reports that all five artifacts expire on 2026-11-28.

## Options and recommendation

- **Implemented: retain exact metadata evidence in Git**, with shared references
  for identical and empty ledgers. This removes artifact-expiry dependence with
  a small storage cost and executable fixity checks.
- Artifact-only retention is simpler but loses durable access after expiry.
- Re-querying publishers would produce new observations, not restore the old
  evidence, and is unnecessary for this correction.

The five new offline regression cases first failed on the absent index, then
passed with the preserved evidence. They check file size/hash, run/source
identity, original ledger bindings, counts, disposition and access boundaries.

## Limits and contingencies

This is retrospective preservation, not retrospective acceptance. The original
StatCan receipt does not bind `observations.json` with a separate digest; this
index binds that file now and records the limitation explicitly. Raw publisher
responses and execution logs are not preserved here. Response hashes alone do
not enable full response replay; no such reproducibility claim is made.

The UK schedule still records 24 September 2026 at 9:30am as the next publication,
not evidence that an edition has been published. NZ's `2026-45-17` attribute
remains invalid and unaccepted. None of these observations establishes candidate
eligibility. Continue the existing bounded scheduled monitors; new metadata or
contract drift follows their existing stop rules. Do not force another search,
open a returned locator, infer a publication date or rerun a failed extraction.

This closes preservation for these five named runs only, not future runs or the
entire monitoring history. G2-C04/C07, WI-G2-04/07 and maturity remain unchanged;
rights clearance, source access, publication, release and gate acceptance are
not granted. No owner decision is needed for this repository-owned correction.
