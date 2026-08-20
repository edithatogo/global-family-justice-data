# G2 evidence-campaign protocol — 2026-08-20

## Purpose and status

This is a repository-owned, reusable protocol for preparing a future factual
G2 evidence campaign. It reduces procedural churn: when a genuinely eligible
candidate frame exists, one grouped owner decision may bind the full bounded
campaign. It is **not** an execution authorization, source-rights decision,
pilot result or G2 acceptance.

The current deterministic protocol, receipt and their schemas are stored in
`data/methods/g2/G2EVIDENCE-CAMPAIGN-PROTOCOL-20260820-01/`. They are derived
solely from checked-in material-distinct preparation evidence.

## Current result

The preceding material-distinct frame produced zero eligible candidates because
every checked-in source-register URL overlaps the complete cumulative exposure
chain. The campaign remains blocked before any external activity. No network,
URL, source-file, content, contact, rights, publication, release or G2 action
occurred.

## Offline intake guard

`scripts/validate_g2_candidate_intake.py` validates future
repository-local candidate metadata against the complete exposure chain before
it can form part of a campaign packet. It has no network capability and rejects
the entire intake on an overlap or duplicate canonical URL. A passing intake
only supports future source-specific screening; it never verifies the source or
clears rights.

## Future campaign boundary

Before external activity, the campaign must have a digest-bound:

1. non-exposed candidate manifest, offline candidate-intake screening and
   complete cumulative exposure check;
2. resource budget and stopping rules;
3. role-bound access controls and source-specific rights/privacy/security
   screening; and
4. one grouped owner campaign authorization binding those artifacts.

That authorization is campaign-scoped, not a series of approval requests for
individual routine artifacts. A failed binding, exposure overlap, budget,
role-isolation or access-boundary check is terminal for that campaign; no
subset promotion, filtering, waiver or silent retry is allowed.

## Relation to G2

The protocol supports future factual evidence for G2-C01 through G2-C07. It
does not satisfy any of them. In particular, a real representative source set,
source-specific review, rights/security assessment, dual extraction and
methods adjudication remain mandatory.
