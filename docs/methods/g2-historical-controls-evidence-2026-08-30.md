# Historical-route offline controls and the remaining methods decision

Status: repository preparation; no external execution or G2 acceptance.
Supports WI-G2-04/07. Their status and acceptance-bearing mappings do not change.

## Implemented evidence

`gfjd.g2_historical_controls` is a separate versioned offline audit/evaluator.
It does not modify frozen v1 snapshots, failed packets or future-monitor code.
The checked-in audit is
`data/methods/g2-audits/historical-persisted-exposure-2026-08-30.json`.

The inventory covers 234 persisted files under `data/methods/g2`: JSON objects,
arrays and JSONL (including empty ledgers), plus hash-only auxiliary manifests,
instructions and CSV. It checks 194 distinct path/digest references. References
to identical bytes at another inventory path are labelled explicitly. This is
not an audit of every hosted run, external conversation, CSV or prose locator.

Normalization yields 4,622 distinct locator identities, 82 edition identities,
85 series identities, 30 source identities, four product identifiers and 18
content digests. These are conservative metadata identities, not 4,622 usable
or accessed sources. Proposed/control URLs can be included in the deny set.
All normalized identities are hash-only in the public audit; no source text,
title, snippet or new private path is copied into it.

The evaluator uses synthetic responses only. It requires audit reproduction,
complete single-page enumeration, the proposed fixed historical window, exact
locator/format/date structure, deterministic ordering and unchanged limits.
All parsable locators are retained before eligibility checks; invalid or
incomplete responses cannot yield selected hypotheses. Malformed/unparseable
responses fail explicitly and cannot establish complete exposure. Outputs
never authorize access, extraction, maturity, publication, release or G2.

Offline audit command (choose a new output path; overwriting is rejected):

```sh
python -m gfjd.g2_historical_controls --output build/historical-controls/audit.json
```

The audit must be rebuilt at a later freeze: repository additions, edits or
omissions make verification fail. This output is deliberately outside the
input subtree to avoid self-referential hashing. No network runner is added.
The `a26ae08` hosted-review fix also requires inventory membership and every
input digest to match the authoritative `MANIFEST.sha256` subset before an
audit can be built. It never repairs that manifest. Missing files in a partial
checkout cannot disappear into a new apparently valid audit. The existing
audit bytes are unchanged; 32 focused tests cover the strengthened control.

## Why historical unseen-selection is still blocked

Three persisted facts remain explicit blockers:

1. The 29 August successor observed 280 results but retained zero complete
   locator records. Its terminal decision forbids reconstruction, repair and
   reuse. Changing the discovery provider does not make unknown results unseen.
2. The 16 August passive annex records incomplete reconstruction of 13 observed
   blocks. A missing count is not zero exposure.
3. The initial future-edition registration stopped at an oversized GOV.UK child
   sitemap without complete enumeration. Preserved earlier locators do not
   establish complete traversal of that response.

The audit successfully inventories persisted metadata while explicitly refusing
to claim complete historical exposure. No complete historical unseen-cohort
execution packet can honestly be frozen from these records.

## Role-separated advisory review

The exposure-inventory agent recommended preserving unknown exposure as a hard
block, incorporating all monitor families and retaining product IDs without
inventing download URLs. The code-review agent found two omissions: directory
symlinks could hide a subtree, and case-sensitive scheme detection could omit
uppercase HTTP(S) locators. Both were corrected with regression tests.
Additional tests cover reference drift, timezone-equivalent cutoffs and more
than 100 returned locators. These are analyst-agent opinions, not independent
specialist assurance. No dissent supporting an unseen historical claim was
received; absent historical evidence remains an explicit limitation.

## Grouped decision: what the next exercise should prove

**Recommended A — bounded reproducibility without a project-unseen claim.**
Prospectively prepare a fresh historical cohort with exposure marked uncertain,
fresh artifact-isolated extraction agents, a frozen semantic contract, exact
100% critical / at least 99% populated concordance and terminal stopping rules.
No failed cohort/output is repaired, reused or retrospectively promoted.
This changes the evidential claim, not the facts or thresholds. It removes the
unprovable historical-unseen requirement but cannot prove generalisation or
independence from model training, and does not itself satisfy G2-C04/C07.
The owner must approve that material methods change. Exact staged access and
execution remain subject to the separately bound authorization; no placeholders
are offered as an execution packet here.

Concise proposed policy decision:

> I approve prospective preparation of a new historical-edition exercise that
> claims bounded, artifact-isolated reproducibility, not project-unseen or
> generalisation evidence. Preserve unknown exposure, all failed evidence,
> fresh role isolation, exact thresholds, quarantine and terminal stopping
> rules. Return one digest-bound execution bundle before external access.
> This does not accept G2, waive rights or authorize publication or release.

**B — retain the future-edition route unchanged.** Lower methods-change risk,
but dependent on publishers. Authentic first-publication evidence after the
exposure cutoff may establish temporal disjointness; an index timestamp alone
does not. Existing bounded monitoring remains the contingency for A as well.

**Rejected — declare missing history resolved by switching to an official
index.** That would claim evidence we do not possess. No additional approval
wording can manufacture the missing observations.

No source-resolution or extractor bundle is presented as ready: an official
index currently identifies landing-page hypotheses, not exact edition URLs;
historical exposure and compatibility with the approved pilot scope remain
unresolved. Preparation does not authorize a UK-only replacement of that scope.
