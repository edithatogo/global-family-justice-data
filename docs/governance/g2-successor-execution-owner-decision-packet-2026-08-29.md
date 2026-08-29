# G2 successor execution grouped owner decision packet — 2026-08-29

Evidence ID: `E-G2-PROSPECTIVE-SUCCESSOR-EXECUTION-PREPARATION-20260829`

## Decision

### Option A — staged bounded execution (recommended)

Authorize the 16 frozen metadata queries first. Permit later exact-source access,
two isolated extractions, exact comparison and advisory review only when every
prospective interlock passes and the selected HTTPS URLs are deterministically
bound into the orchestrator allowlist. This minimizes approval churn while
retaining a hard stop before any unknown source is requested.

Trade-off: execution can still stop between stages; a passing run proves only
bounded reproducibility. Contingency: any mismatch ends the lineage without
repair, retry, substitution or promotion.

### Option B — metadata registration only

Authorize only the 16 query calls and return for a second decision after exact
selection. This offers the tightest human checkpoint but adds another approval
and does not increase deterministic assurance over Option A's interlocks.

### Option C — defer

Keep the complete bundle as repository evidence and perform no external work.
This has no external risk but leaves G2-C04 and G2-C07 blocked.

## Frozen scope and controls

- 16 ordered metadata queries, one call each, zero retries;
- requested result prefix 10 and absolute safety cap 50 per query;
- all observed locator-only results recorded as exposure, up to 800 total;
- cumulative exposure rebuilt from 142 repository JSON evidence artifacts,
  yielding 839 URL aliases and 14 content-digest aliases;
- exact six-role policy, initially inactive with empty network allowlists;
- peer address checked against prospectively validated public DNS before any
  response body is read, with TLS verification for the original hostname;
- at most four exact sources, 25 MiB each and 100 MiB total;
- 100% critical and at least 99% overall populated-field concordance;
- no fuzzy matching, waiver, repair, failed-output reuse, automatic rerun,
  rights clearance, publication, release, maturity promotion or G2 passage.

The preparation packet is at
`data/methods/g2/G2PROSPECTIVE-SUCCESSOR-20260829-02/execution-control/preparation-packet.json`.
Its digest must be inserted into the owner decision record after this packet is
merged; the execution contract must bind that immutable decision before the
first query.

## Recommended owner wording

> I approve Option A in the G2 successor execution grouped owner decision
> packet dated 2026-08-29. I authorize the exact 16 prospectively frozen
> metadata queries, in order, one call per query and zero retries, under the
> bound result, exposure, resource, network, peer-verification and terminal-stop
> controls. All observed locator-only results up to the absolute cap must be
> recorded as exposure; no result URL may be opened during registration.
>
> If and only if candidate selection reproduces with zero cumulative exposure
> overlap and every binding, schema, role-isolation, public-network and
> pre-source interlock passes, I authorize the orchestrator to request only the
> exact selected HTTPS source URLs bound by that interlock, within the frozen
> four-source and byte limits. I then authorize two fresh artifact-isolated
> extractions, one network-disabled exact comparator and one role-separated
> advisory review. Any failed interlock or stopping rule terminates the lineage;
> no repair, retry, substitution, waiver or failed-output reuse is authorized.
>
> This authorization is aggregate-only and does not clear rights, accept G2,
> promote maturity or gold evidence, or authorize publication or release. A
> passing result must return to me for grouped accountable G2 adjudication.

## Current boundary

Preparation only. No query, result URL, landing page, source file or source
content was accessed, and no extraction or comparison occurred.
