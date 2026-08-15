# G2 prospective blind-holdout plan — 2026-08-15

Status: prepared; execution not authorized. This is a new experiment lineage,
not packet 06 and not a continuation or repair of packets 01–05.

Machine-readable design:
`config/g2_blind_holdout_plan.json`.

## Objective

Test whether two fresh, role-separated analyst agents can independently extract
the same critical facts from previously unseen exact editions under a contract
frozen before source-content exposure. A pass can support only the bounded
formats, languages, structures and indicators represented by the selected
holdout. It cannot by itself accept G2, rights, publication or release.

## Panel advice and preserved dissent

- Methods panel report SHA-256:
  `e30a1014eafa0f595b1c37cfd596e5c9672067179661775d128667f1ab8e1179`.
  Tracked copy:
  `data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/panels/methods-design-report.json`.
  It recommends 24 editions for stronger within-stratum evidence.
- Governance/risk report SHA-256:
  `0b9e1424c46e9a80cf1ee0b98d85800f960ee2b24442ad54cbffb714ce739f2e`.
  Tracked copy:
  `data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/panels/governance-risk-report.json`.
  It recommends 12 editions to reduce acquisition, rights and operational
  exposure.

Recommendation: 24 primary editions plus six pre-ranked reserves. The larger
design is preferred because this exercise is intended to provide evidence
beyond a four-row calibration. The 12-edition design remains a bounded
alternative if the owner prioritizes cost and completion probability over
within-stratum depth.

## Prospective scope

The recommended 24-edition design uses one row per edition and six editions in
each mutually exclusive stratum, applied in this precedence order:

1. embedded raster or dashboard PDF;
2. structurally complex mixed-layout PDF;
3. non-English text-native PDF;
4. English text-native table or narrative PDF.

The design requires at least 12 jurisdictions, no more than two editions per
jurisdiction and no more than one edition per source series. These are the
methods panel's recommended confirmatory constraints. The governance panel's
12-edition option is preserved as a separate, lower-burden design; it is not
silently blended into the recommendation.

Six stratum-matched reserves are ranked before content inspection. Allocate at
least one to every stratum; allocate the remaining two to the strata with the
largest eligible metadata frames, breaking ties by lexical stratum identifier.
Rank within strata using a SHA-256-seeded deterministic procedure whose seed is
frozen in the candidate manifest. A reserve may replace an ineligible primary
only before the final manifest is sealed. No substitution, exclusion or
replacement is permitted after sealing.

The holdout is PDF-only. Results cannot be generalized to APIs, dashboards,
HTML, spreadsheets, OCR-dependent scans, other languages or unrepresented
court/statistic structures.

## Definition of unseen

An eligible edition must:

- have no edition identifier, content digest, locator, target value or
  field-boundary answer used in packets 01–05, their diagnostics or comparator
  investigations, tests, contract calibration or extractor preparation;
- not have been opened, rendered, transcribed or content-inspected by either
  future extractor;
- be selected from metadata only before source bytes or page content are
  exposed to the extraction roles;
- have its identity, provenance, integrity and eligibility frozen in the final
  candidate manifest;
- pass exact-edition rights, privacy, security and prohibited-data screening
  before extraction.

The universe registrar must produce a complete exposure ledger and deterministic
non-overlap receipt. Any uncertainty about prior inspection makes the edition
ineligible.

## Role separation

Distinct agent sessions must perform:

- metadata-only universe registration;
- deterministic candidate and reserve selection;
- acquisition custody, integrity verification and packet sealing;
- locator and eligibility review without extraction;
- primary extraction;
- secondary extraction;
- deterministic comparison;
- post-seal source-fidelity advice;
- post-seal methods advice;
- post-seal governance/risk advice.

Each role receives a separate immutable bundle, explicit artifact allowlist and
denylist, fresh no-history session and access receipt. Extractors may not inspect
the exposure ledger, universe, selection algorithm/receipt, candidate rankings,
reserves, previous calibration outputs, other extractor artifacts, comparator
output or post-run panel material. The sole owner remains the only adjudicator.

## Frozen thresholds and stopping rules

- 100% concordance on every declared critical field;
- at least 99% concordance across populated comparable fields;
- exact equality after only the frozen NFC and whitespace normalization;
- no fuzzy matching or critical waiver;
- any critical difference stops the experiment;
- no correction/calibration rerun, post-seal exclusion, reserve substitution,
  scope adjustment or follow-on packet;
- digest, role-isolation, source-integrity, rights/privacy/security or
  prohibited-data failure stops before extraction or invalidates the run;
- every stopped run returns to the sole owner for disposition.

The comparator must independently enforce candidate scope, component keys,
controlled codes, required fields, exact source-edition digests and all
packet-bound invariants.

## Dependency sequence

1. Owner selects the 24- or 12-edition design and authorizes metadata-only
   candidate discovery.
2. A selector agent creates a ranked candidate/reserve manifest without opening
   source content.
3. Advisory agents review eligibility, prior-exposure risk, strata and public
   metadata/terms evidence.
4. The owner separately approves the exact candidate manifest and authorizes
   acquisition/content inspection/extraction.
5. A custodian acquires and seals exact bytes, manifests, contracts and role
   boundaries. Any failed screen stops the run before extraction.
6. Fresh primary and secondary agents extract independently.
7. The deterministic comparator runs once. Any critical mismatch stops.
8. A role-separated panel advises on results; the sole owner adjudicates. No
   automatic G2 promotion occurs.

## Current authorization boundary

Preparation of this plan is authorized. Candidate sourcing, downloading,
content inspection, extraction, contact, publication, release and G2 acceptance
are not authorized. The next decision packet authorizes only metadata-level
candidate discovery; exact-edition execution still requires the later manifest-
bound owner decision.
