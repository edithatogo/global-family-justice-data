# Implementation status

**Baseline:** `0.6.0-alpha.2`
**Status date:** 2026-08-29
**Purpose:** distinguish executable engineering controls from international research and institutional evidence that remain to be completed.

This repository is a bootstrap-ready engineering and programme-control baseline. It is not a completed international family-justice dataset and is not the stable v1.0 service.

## Continuation ledger — 2026-08-30 monitor preservation

- Commit `c7438c7` preserves exact receipts for five additional completed metadata
  monitor runs, four StatCan metadata observations and digest-indexed references
  to existing identical or empty ledgers. This follows the three-root ledger
  preservation in PR #123; it does not rewrite historical receipts.
- Conductor evidence: `E-G2-MONITOR-RECEIPT-PRESERVATION-20260830`, still
  `in_review`. The [preservation report](docs/methods/g2-monitor-receipt-preservation-2026-08-30.md)
  records exact runs, provenance, options, limitations and next actions.
- The complete local `autonomy-full` harness passed on that commit: 429 tests
  both with coverage and without, 78.00% branch-aware coverage, integration,
  backup/restore and deterministic package/draft-release checks. This is
  repository validation, not G2 acceptance.
- Preservation is bounded to the named observations, not raw-response replay or
  all future monitoring history. The original StatCan receipt lacks a separate
  observations-file digest; retrospective indexing does not repair that fact.
- Continue the existing bounded monitors and retain their future receipts.
  These five observations establish no eligible edition. G2 remains 9/13;
  G2-C04/C07, WI-G2-04/07 and the evidence-specific L2 requirement remain open.

## Implemented and exercised

### Continuation — 2026-08-30 medallion validator prerequisite

The [validator hardening report](docs/engineering/medallion-validator-hardening-2026-08-30.md)
records four malformed-input boundary corrections and 16 regression cases.
Invalid evidence-name types, quarantine shapes, ordinals and layer identifiers
now fail validation explicitly. Existing valid-promotion behaviour is retained.
This supports the lineage/replay prerequisite only: `WI-G4-MED-02` remains
planned, and no G2/G4 criterion or maturity state is promoted.

| Capability | Current implementation |
|---|---|
| Repository handoff | Multi-commit Git history with checkpoint tags, Git-bundle packaging, source manifest, `AGENTS.md`, internal Codex briefs and a plan-first bootstrap path |
| Programme conductor | T0–T9 tracks, G1–G6 evidence gates, work/evidence/risk/defect/exception registers, dependency evaluation, generated status and programme graph |
| Public medallion/federation programme | The owner-approved maximal plan adds twelve acceptance-bearing work items across T3–T9 for public-only B0 custody, B1 Bronze, Silver, Gold, Platinum, orthogonal quarantine, field lineage, replay, Hugging Face roles, federation registration, dual-provider restore and immutable stable snapshots |
| Governance assurance | Deterministic six-gate assurance pack, criterion matrix, fail-closed defect/exception disposition, unsigned release-decision template and tamper-evident manifest; all T0 repository work is implemented and awaiting genuine review |
| T0/T1/T2 decision handoff | Checksum-bound governance/methods/census controls are implemented; the pending decision and evidence packet is documented in `docs/governance/t012-decision-handoff.md` |
| Autonomous solo operation | Checksum-bound resume context, explicit repository/external boundary routing, fail-closed blocker matrix, track dependency sequence, fast iteration gate and maximal checkpoint harness let one maintainer delegate implementation without relying on chat memory or self-approving governance |
| Local test iteration | Focused node/path execution, optional two-worker file-grouped unit execution and complete-suite timing receipts shorten local feedback while serial `autonomy-fast` and `check` remain the acceptance paths |
| Data contracts | Versioned JSON Schemas and CSV/TOML contracts for jurisdictions, institutions, sources, source editions, indicators, matter types, observations, evidence, reviews, search logs and coverage assessments |
| Acquisition and ingestion | Rights-aware acquisition plus declarative CSV, JSON, HTML, XLSX and controlled manual-transcription adapters |
| Harmonisation | Source-to-silver mapping, deterministic quarantine, provenance fields and dual-review gold-promotion controls |
| Synthetic reference path | Five conspicuously fictional source formats exercised end to end, producing five synthetic gold observations only in build output |
| Outcomes evidence | Study-level catalogue contract, explicit evidence-gap products and verification; the seed catalogue remains empty rather than inventing evidence |
| Comparability | Conservative semantic signatures and candidate/issue outputs that do not self-authorise international comparisons |
| Analytical release | Deterministic portable SQLite warehouse, read-only verification and deterministic release rehearsal with checksums and declared-dependency metadata |
| Resilience | Deterministic critical-state backup, hostile-archive checks, clean restore rehearsal and receipt verification |
| CI/CD policy | SHA-pinned Actions policy, merge-queue-aware required checks, desired repository controls, lock/contract audits and private-by-default release/bootstrap policy |
| Distribution assurance | Adversarial wheel and sdist checks plus deterministic wheel, normalised sdist and release double builds |
| Local/remote bootstrap | Bounded local clone discovery, portfolio reconciliation, Git identity and remote checks, public GitHub creation/attachment, non-force push verification, and public Hugging Face estate creation |
| Canonical platform topology | Public `edithatogo/global-family-justice-data` GitHub control plane plus a planned public Hugging Face source archive, source catalogue, medallion observations, outcomes evidence, extraction benchmark and Gold/Platinum explorer; operated public custody and empirical promotion remain evidence-gated |
| High-priority source rights routing | Official Council of Europe, NCSC and HCCH terms are recorded for five international sources with metadata/citation routes separated from permission-dependent or unclear redistribution; no source was promoted to open-licence status |
| T6 product controls | Deterministic candidate product bundle, catalogue, portable warehouse, accessible HTML landing page, checksum manifest and fail-closed publication flag are implemented; publication and assurance gates remain external |
| T7 assurance controls | Security/public-data scanning, rights-aware acquisition, contract/lock audits, release blockers, backup/recovery and fail-closed publication controls are implemented; role-separated agent panels advise and the sole owner adjudicates findings without claiming legal or specialist assurance |
| T8 operations controls | Deterministic release, backup/restore rehearsal, manifest verification, correction boundaries and operational runbooks are implemented; actual live custody, signing, monitoring, restore and owner-resource evidence remain required |
| T9 participation and sustainability controls | Source-language review, authoritative triangulation, non-participatory agent/tool accessibility testing and sole-owner operating-plan controls are documented; no local-human, lived-experience or participant-validation claim is made |
| Subagent panel assurance | Digest-bound, role-separated panel protocol with structured reports, conflict matrix and owner adjudication is the advisory model; the repository owner remains the sole accountable decision-maker |
| Remaining-work execution register | All unresolved issues are mapped to repository actions, external inputs, approval boundaries and fallbacks in the remaining-work implementation plan |
| Track external-gate plan | T0–T9 now have explicit external-gate options, recommended routes, contingencies, authority boundaries and fail-closed promotion/archive rules |
| Sole-owner gate policy | The 2026-08-15 digest-bound decision supersedes multi-person assurance requirements: role-separated agents advise and verify, the sole owner decides, factual evidence remains mandatory, R20 remains a release hard no-go, and outbound contact/publication still requires separate authorization |
| External authority-gate plan | Authority types, digest-bound evidence packets and permitted status transitions are defined for governance, methods, coverage/rights, product, security/legal, operations, participation and sustainability gates |
| Programme gate resolution plan | G1–G6 are mapped to remaining evidence, recommended routes, contingencies, tracks and fail-closed promotion rules |
| G2 evidence-campaign protocol | A deterministic, digest-bound campaign envelope is prepared from the exhausted material-distinct frame. It permits no external action, avoids per-artifact approval churn, and requires one future grouped authorization only after a genuinely non-exposed candidate manifest exists. A no-network intake guard now rejects duplicated or already exposed proposed URLs before a campaign packet can be assembled. |
| G2 known-source handling | Four exact known-source routes have a bound owner handling disposition: controlled private quarantine, metadata-only public/Git records, route-specific restrictions and a 2027-08-24 retention review. The owner accepted C06 only for this private aggregate-processing scope; it is not rights clearance or legal/privacy/security assurance. |
| G2 bounded concordance disposition | The owner accepted the exact two-row known-source result and conservative methods consequences as supporting evidence only. The decision records 36/36 populated critical and 40/40 configured populated matches, null-date and unscored-field limitations, no pooling/ranking, and no criterion transition or G2 passage. |
| G2 C03 clean-build acceptance | The owner accepted the verified frozen two-row real-input quarantine build for C03: two bronze, two silver, two quarantine and zero gold rows. This closes only the deterministic-pipeline criterion. |
| G2 next-unblock packet | The owner accepted the bounded C01/C02 cohort/acquisition evidence, conservative C05 non-equivalence disposition and private-processing C06 assessment. The authorized C04/C07 run subsequently stopped terminally. |
| G2 grouped acceptance and terminal blind run | The owner accepted bounded C01/C02/C05/C06, advancing G2 to 9/13. The authorized four-route agent-blinded known-edition run produced five critical differences and then failed concordance-receipt validation on its frozen packet ID; it is immutable terminal failed evidence and C04/C07 remain in review. |
| G2 materially distinct successor | The bounded campaign acquired and structurally screened four new route-distinct official aggregate editions, then stopped before extraction when a role wildcard touched rejected artifact metadata outside the frozen scope. No comparator ran. M07 and M10 factual components are prepared for review; M06, C04, C07 and G2 remain blocked. |
| G2 physical role isolation | Explicit-allowlist role workspaces and a one-path verifier CLI are implemented and tested. The first isolated replacement lineage stopped before source access because the extractor used the former two-argument API incorrectly; its terminal receipt is immutable and a final CLI-bound option is awaiting one grouped owner decision. |
| G2 CLI-isolated successor | The owner authorized and the repository froze a second isolated lineage. It stopped terminally during extractor A preflight because prose punctuation became an extra CLI argument; A opened no source, B was interrupted without a direct source-access attestation, no outputs exist and no comparator ran. C04/C07 and M06 remain blocked. |
| G2 orchestrator-bound successor | Orchestrator preflight, two fresh sealed four-row extractions, scope/schema/seal verification and exact comparison completed. The lineage failed terminally at 58/76 critical and 42/60 populated matches. No repair or rerun occurred; C04/C07 remain in review and M06 remains L1. |
| G2 atomic field remediation | The terminal differences are converted into generic executable rules over the existing atomic row schema: separate locator facets, source-text preservation, controlled semantic codes, explicit-only clocks and null-date provenance. Fictional adversarial tests avoid calibrating to failed outputs; no new cohort or run is authorized. |
| G2 prospective successor hardening | A separate repository-only successor design fixes the terminal campaign's result-overflow policy and all five automated-review findings: contract-anchored authorization, complete digest/locator exposure aliases, exact role isolation, connected-peer validation and locator-only complete provider-result recording. The predecessor remains immutable; no successor query or source access has been authorized or executed. |
| G2 prospective successor execution preparation | The exact 16-query manifest, 142-input cumulative exposure snapshot, inactive six-role bundles, peer-reporting transport contract, resource limits, terminal stops and one grouped owner-decision packet are frozen. No query or source access occurred; staged execution awaits digest-bound owner authorization. |
| G2 prospective successor execution authority | The sole owner approved Option A against merged commit `79a5e06` and the exact decision, preparation, query and exposure digests. Metadata registration is authorized; later source access and analysis remain mechanically conditional and no publication, release or G2 passage is authorized. |
| G2 prospective successor terminal stop | All 16 frozen metadata calls completed in order with zero retries and no result or source access, yielding 280 observations. The registrar failed to retain their complete locator tuples, so cumulative exposure cannot reproduce; the lineage stopped terminally before selection and all 280 observations are exposed but unenumerated. A machine-enforced coarse quarantine blocks later search-based unseen claims. |
| G2 prospective future-edition route | The owner has authorized one non-search campaign over six frozen official publication roots. Eligibility requires official first-publication evidence strictly after `2026-08-29T05:17:40Z`; manifest registration is the next active stage and all later stages remain interlock-bound. |
| G2 future-edition manifest registration | Six exact official roots returned 1,251 registered locators with zero search or candidate-document access. Two roots were sitemap indexes; the first permitted GOV.UK child exceeded the frozen per-response limit, so complete enumeration stopped terminally before eligibility or selection. |
| G2 streaming manifest successor | A bounded-memory sitemap parser and fail-closed child-request policy remove the predecessor per-response-size defect. Precise unchanged child manifests may be skipped; missing, date-only or post-cutoff timestamps require streaming enumeration. |
| G2 streaming manifest execution | The first timestamp-uncertain New Zealand child returned a prohibited 301 trailing-slash redirect and terminated the lineage. Two later requests are quarantined execution-order defects; no redirect was followed or body parsed. |
| G2 canonical sitemap successor | A distinct prospective lineage freezes the three observed canonical trailing-slash New Zealand child endpoints. Requests are strictly sequential, zero-retry and fail-closed; only endpoint 1 is initially eligible and no candidate-document access is permitted. |
| G2 canonical sitemap execution | All three canonical child manifests passed sequential request and streaming-parse controls, exposing 2,302 observations. None had a timestamp after the frozen cutoff, so the lineage stopped terminally with zero eligible editions and no candidate-document access. |
| G2 prospective official-manifest monitoring | A daily, zero-retry monitor now enumerates only the three exact canonical sitemap endpoints, persists every observation as exposure and stops before returned-locator access. No-candidate observations create receipts without approval churn; two or more post-cutoff hypotheses trigger preparation of one grouped source-access decision. |
| G2 prospective multi-jurisdiction monitoring | Four additional previously frozen direct official URL sets now share the fail-closed monitor contract. Their 1,213 prior observations form an immutable exposure baseline; novel or post-cutoff hypotheses become action-required without opening returned locators. |
| G2 three-root monitor successor | The first four-root hosted run sealed 1,212 exposures then stopped on an FCFCOA timeout. A distinct successor retains California, CNJ and British Columbia, removes the one-homepage low-yield endpoint, and binds the failed partial ledger into cumulative exposure. |
| G2 official publication-index monitor | A publisher-controlled GOV.UK family-justice research/statistics index is frozen as a metadata-only route with explicit publication timestamps, complete single-page enumeration, cumulative-exposure checking and no returned-locator access. First hosted run `33242193951` passed with zero observations or candidates; the scheduled monitor remains active and cannot itself accept C04/C07, promote M06 or pass G2. |

## Current programme state

### G2 historical-edition alternative proposal — 2026-08-30

Continuation `7d70b7d` implements a versioned offline persisted-exposure audit
and historical metadata evaluator. The `a26ae08` review fix anchors membership
to the source manifest and brings focused coverage to 32 tests. The audit binds
234 files, checks 194 references and normalizes 4,622 locator identities. Three unresolved
exposure gaps remain explicit; the official-index mechanism cannot establish
that historical material is disjoint from 280 unenumerated prior observations.
See `docs/methods/g2-historical-controls-evidence-2026-08-30.md` for the evidence,
limitations and concise methods decision. No live runner, source/extraction
authority or G2 promotion is created. Complete historical exposure remains
blocked even though the persisted-file audit is reproducible.

The role-separated panel recommends preparing a separately frozen historical
official-index route, with future-edition monitoring retained as redundancy.
The exact inactive metadata request, fixed window, limits, unchanged concordance
rules, advisory dissent and execution prerequisites are bound in
`data/methods/g2/G2HISTORICAL-PROPOSAL-20260830-01/design/reference-manifest.sha256`.
See `docs/methods/g2-historical-route-plan-2026-08-30.md` and
`docs/governance/g2-historical-route-options-2026-08-30.md`.
No candidate or complete current exposure freeze is established. Persisted
JSON/JSONL normalization and the offline evaluator are implemented; complete
exposure and source-role interlocks remain unresolved. No execution approval is requested against
missing bindings; no publisher request, extraction, rights clearance or G2
promotion occurred. Existing failed lineages and monitor contracts are unchanged.

### Autonomous continuation guard — 2026-08-30

The resume queue now requires an explicit repository-only execution scope;
planned publication work is no longer classified as safe merely from status.
Unknown work and acceptance states fail closed. The standing-owner policy and
ordered continuation plan are bound into resume packets. See
`docs/engineering/medallion-autonomous-continuation-2026-08-30.md`.
Twenty-three focused autonomy tests cover the guard. This does not create a
background implementation schedule or alter monitor, source-access, publication,
rights or gate authority. Correction history remains the next engineering slice.

### Bounded medallion replay continuation — 2026-08-30

WI-G4-MED-02 now has an offline exact-string JSON projection API, per-field
JSON-pointer lineage, explicit nullable source-valid time, recorded time and
digest-bound deterministic replay verification. Thirty synthetic tests exercise
the kernel. See `docs/engineering/medallion-projection-replay-plan-2026-08-30.md`.
This is an unpromoted candidate mechanism, not a completed medallion layer:
public B0 custody integration, real partition replay, correction/supersession
history and complete bitemporal intervals remain open. No G2 criterion, maturity
rating, source right or publication permission changes.

- Active gate: **G2 — Reproducible pilot proven**.
- Track disposition: **T0–T9 implementation slices complete; later acceptance
  remains evidence-gated**. Role-separated agents advise and verify; the sole
  owner decides. Real source, build, archive, restore, publication and resource
  facts remain mandatory where the current gate contracts require them.
- Passed gates: **G1** through the digest-bound sole-owner decision dated
  2026-08-15. G2–G6 have not passed.
- G2 factual-evidence route: **nine of thirteen requirements complete**.
  C01/C02/C05/C06 are accepted only within their bounded scopes. The latest
  executed calibration lineage is terminal failed evidence after its first
  metadata query exceeded the frozen result cap. A hardened successor is
  prepared but has performed no external access; C04/C07 and M06 of the L2
  floor still block G2. M07 and M10 factual components await accountable review.
- Gold empirical observations: **none**.
- Synthetic fixtures: explicitly fictional and excluded from empirical release claims.
- Canonical GitHub owner: **`edithatogo`**, verified from authenticated GitHub state.
- Canonical GitHub repository visibility: **public by owner decision**; the
  aggregate-only boundary and fail-closed empirical publication controls remain
  in force.
- Canonical Hugging Face namespace: **`edithatogo`**; the public-only target
  topology is configured, while populated B0/medallion custody and remote
  verification remain planned evidence rather than a completion claim.
- Publication identity, final licence, real CODEOWNERS, protected-environment reviewers and complete live repository-control conformance remain pending genuine decisions and evidence.

## Not supplied by code

Stable v1.0 still requires authentic evidence for real source editions and retrievals, source-rights facts and owner decisions, multilingual searches, jurisdiction-aware triangulation, real connectors and fixtures, blinded role-separated re-extraction, methods adjudication, outcomes-evidence appraisal, agent/tool accessibility review, production operations, two-location preservation, tested restore, publication state and the owner's dated 12-month resource commitment. Agent panels cannot manufacture those facts or create legal, independent-specialist, local-human or lived-experience claims.

A passing technical workflow cannot approve a programme gate or transform process speed into evidence of child or family outcomes.
