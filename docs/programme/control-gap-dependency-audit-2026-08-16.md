# Control-gap and dependency audit — 2026-08-16

## Scope and authority boundary

This is a network-disabled audit of tracked repository evidence. It does not
access candidate URLs or source content, alter a programme register, accept an
evidence item, close a risk, authorize contact, or authorize publication. The
sole owner remains the accountable decision-maker; role-separated analyst-agent
panels provide advisory findings, options, trade-offs, contingencies and
recommendations only.

The audit baseline is:

| Artifact | SHA-256 | Material fact used |
|---|---|---|
| `programme/risk_register.csv` | `3f17d960b861bf409078c7b959b202e347cdb1a620458a2d8c30050803b70fa8` | 20 risks; 19 retain critical/high residual severity |
| `programme/evidence_register.csv` | `554828703d51f449b16272627b89b4fa60cfa647db2edc439247e773632f2e9d` | evidence state and exact evidence paths |
| `programme/work_items.csv` | `3dce2d5d6b115d3d158248cb1b12798e0665e08b1fd2dfd76f12fc237347a325` | dependency-ready and downstream work states |
| `config/stage_gates.toml` | `87b0d89d5197d3bc54fefeeb4e902c2620963ea7661a7318068707d5d5999245` | mandatory G2–G6 criteria and gate dependencies |
| `docs/programme/generated/status.md` | `f6f3b168c561d7ba49e71fd3c1a1859fdd423c97257f1cb904d6df6151c28418` | G1 passed; G2 blocked; G3–G6 dependency-blocked |
| `data/seed/source_register.csv` | `16023b6b560c141bb81be13b23f061481aa5b598ead7a24db4cff1f327c9fa4e` | seven high-priority rights notices on rows 2–8 |

## Executive finding

The repository has implemented every T0–T9 work item, but implementation is not
evidence acceptance. G2 is the sole dependency-ready gate and remains blocked;
G3, G4, G5 and G6 must remain dependency-blocked in that order. The current 19
critical/high count consists of six owner-adjudicated risks that deliberately
retain critical residual severity (`R02`, `R10`, `R11`, `R15`, `R16`, `R20`)
and thirteen high risks still marked `mitigating`. An `accepted` risk row is an
accepted adjudication, not a closed or low-residual risk.

The immediate repository-owned action is to finish the signed freeze and exact
owner-authority record for the separately identified G2 metadata-search
successor, then execute only the separately authorized, provider-isolated search
stage. That successor is preparation toward fresh blind-holdout evidence; it is
not itself G2 evidence acceptance. See
`docs/methods/g2-metadata-search-successor-design-evidence-2026-08-16.md`
(`E-PILOT-METADATA-SEARCH-SUCCESSOR-DESIGN-20260816`, SHA-256
`1c9b0d144b321f8351a72abc98b65c42d762718a17949e37dd579dcf8d535491`).

## Critical/high risk control gaps

| Risks | Current evidence-supported state | Repository-owned or sourceable next work | Future factual input | Panel and owner decision point | Recommended register update after evidence exists |
|---|---|---|---|---|---|
| `R01`, `R14`, `R19` — scope overclaim, product-first displacement, simplistic ranking | `mitigating/high`; product boundaries, stage gates, no-index controls and responsible-use material exist, but no live-product misuse evidence exists. | Re-run product-label, gap-display, ranking-prohibition and release-interlock tests against each candidate build; generate a digest-bound product/misuse panel report. | Actual published-product observations or a bounded pre-release misuse rehearsal. | Product, methods and misuse agents advise; owner adjudicates residual risk before G4/G5 and again before G6. | Append dated evidence paths and SHA-256 values; retain `high` until candidate-specific rehearsal passes; never close merely because controls exist. |
| `R02`, `R09`, `R13`, `R17` — comparability, outcomes interpretation, pilot scalability, contract churn | `R02` is `accepted/critical`; the others are `mitigating/high`. Packet 05 failed at 167/168 critical facts and was terminated; no reproducibility or generalisation pass exists (`docs/methods/g2-real-pilot-packet05-evidence-index-2026-08-15.md`, SHA-256 `651475...e0c7d`). | Complete the prospectively frozen unseen-edition holdout; produce dual extraction, exact comparator, quarantine, sensitivity and compatibility receipts without changing thresholds. | Unseen official editions and the resulting independently produced extraction outputs. | Separate methods, extraction-boundary, comparability and contract agents advise; owner accepts, rejects, quarantines or terminates. | For `R02`, retain `accepted/critical` until a later risk-specific owner decision changes residual severity. For `R09/R13/R17`, update controls/review dates only after holdout and contract-freeze evidence; do not infer closure from a pass on one frame. |
| `R03`, `R04`, `R08` — federal/devolved, multilingual and translation error | `mitigating/high`; 23-jurisdiction structures and agent-review routes exist, while complete reviewed institutional maps, negative-finding review and authoritative triangulation remain pending (`E-GLOBAL-COVERAGE-REPORT`, `E-NEGATIVE-FINDINGS-AUDIT`, `E-LOCAL-VERIFICATION-REPORT`). | Generate jurisdiction-by-jurisdiction contradiction queues, original-language citations, government-structure cross-checks and second-agent review receipts from permitted source metadata. | Current authoritative source-language material for every material ambiguity; inaccessible or absent evidence must remain an explicit gap. | Jurisdiction-structure, source-language and search-quality agents advise; owner adjudicates each unresolved ambiguity and the final G3 cohort. | Update each risk with coverage counts and evidence IDs, not a global closure. Retain high for unresolved jurisdictions and record quarantine/exclusion decisions explicitly. |
| `R05`, `R06` — source drift and redistribution rights | `mitigating/high`; preservation machinery exists, but exact-edition terms and operational drift evidence remain incomplete. Seven current rights notices are itemized below. | Run repository source-health, checksum, preservation and terms-screening workflows only on separately authorized artifacts; maintain metadata/citation-only routing where terms are unclear. | Exact-edition terms, licences or signed permissions; repeated monitoring observations showing drift detection and recovery. | Rights/terms, preservation and security agents advise on each exact edition; owner chooses redistribution, metadata-only, quarantine or exclusion. | Never convert a general site policy into edition clearance. Add edition ID, captured terms hash, permitted uses, attribution, expiry/recheck trigger and owner decision reference before changing `R06` or a source licence state. |
| `R07` — manual extraction error | `mitigating/high`; immutable failed calibration demonstrates the risk is real, not closed. | Use frozen contracts, two fresh artifact-isolated extraction paths, exact digests, comparator recomputation and fail-closed stopping rules. | Successful unseen-edition dual extraction at the approved 100% critical and at least 99% overall thresholds. | Extraction, source-boundary and comparator agents advise; owner adjudicates discrepancies without repair or waiver. | Add holdout receipt and decision bindings; reduce residual severity only through a new risk-specific owner adjudication. |
| `R10` — disclosure/context harm | `accepted/critical`; aggregate-only, suppression, metadata-only and quarantine controls are accepted, but this is not a release clearance. | Re-run disclosure and contextual-harm tests against every candidate dataset/product and generate a panel report with small-cell and inference cases. | Candidate-specific observations and any actual incident/correction evidence. | Privacy, safeguarding, misuse and product agents advise; owner adjudicates each candidate. | Preserve `critical` until candidate-specific evidence supports an explicit dated decision; reopen on greater granularity or a disclosure event. |
| `R11` — credentials and supply chain | `accepted/critical`; locked workflows and scans exist, but current candidate signing, custody and incident evidence do not. | Capture current CI/security receipts, dependency/Action locks, SBOM/provenance, secret-scan, signed commit/tag and restore rehearsal for the exact candidate. | Live repository-settings evidence, owner-held key/custody facts and any incident outcome. | Security, privacy, supply-chain and provenance agents advise; owner accepts candidate-specific residual risk. | Bind exact commit/run/artifact hashes and expiry. Retain critical until G5/G6 candidate evidence is current. |
| `R12` — single-maintainer continuity | `mitigating/high`; the accepted model intentionally has no human deputy and pauses governed decisions when the owner is unavailable. Existing “deputy roles” control text is stale for this model. | Test unattended monitoring, documented recovery, owner-unavailable pause and agent continuity workflows; remove deputy-dependent recommendations in a later reviewed register change. | Owner’s actual custody, support availability and resource commitment. | Operations, governance and recovery agents advise; owner confirms the single-owner pause/continuity posture. | Replace `Deputy roles` with `owner-unavailable pause; agent operational continuity; no substitute approval`; retain high unless a risk-specific decision supports otherwise. |
| `R15` — influence | `accepted/critical`; owner conflict/suppression policy is accepted, with no independent governance claim. | Generate conflict, attempted-influence and provenance logs; test that product generation cannot hide adverse findings or gaps. | Any real funding, host, institution or suppression request. | Governance, provenance and misuse agents advise; owner records conflict-specific disposition. | Retain critical; append actual conflicts and dated decisions. Never infer independence from an agent panel. |
| `R16` — maintenance funding | `accepted/critical`; it remains an open planning risk and no funding commitment is established. | Cost the 12-month sole-owner operating plan, enumerate minimum/low/base contingencies and bind an unavailable-owner pause. | Owner’s dated funding/resource commitment and actual operating staff/capacity facts. | Finance, operations and sustainability agents advise; owner selects and commits a bounded plan. | Add amount/capacity, covered period, expiry and reopen trigger only after a real commitment; do not treat a budget model as funding. |
| `R20` — premature v1.0 | `accepted/critical` hard no-go. G3–G6 are dependency-blocked and publication remains unauthorized. | Keep release, signing and publication workflows fail-closed; rehearse but do not publish. | Accepted G2–G5 evidence, exact G6 candidate, two-location custody, restore, service ownership and 12-month commitment. | Cross-role release panel advises; owner alone records the final signed release decision. | Preserve critical/no-go until every G6 criterion has accepted evidence and the owner records the exact immutable release decision. |

## Seven source-rights informational notices

Validation reports `SOURCE_RIGHTS_REVIEW_NEEDED` for rows 2–8 of
`data/seed/source_register.csv`. These are informational validation notices but
remain material to `R06`, G2-C06, G3-C06, G4-C07, G5-C05 and G6-C03.

| Source | Present licence state | What can be done now without source access | Future factual input and contingency | Recommended later update |
|---|---|---|---|---|
| `INT-CEPEJ-STAT` | `unknown` | Bind existing site-policy review and keep metadata/citation-only. | Exact database/export terms or written permission. If absent, retain metadata and locators only. | Record exact edition/export, terms capture hash, use class and owner decision. |
| `SWE-DOMSTOLSVERKET` | `unknown` | Preserve the recorded metadata-attribution route; keep workbook/report bytes uncleared. | Exact workbook/report terms. If ambiguous, quarantine bytes and publish only original metadata. | Split portal metadata rights from each edition’s bytes/artwork/third-party content. |
| `USA-MN-MJB` | `restricted_or_unknown` | Preserve the known 2024 report digest and 403/browser-fallback provenance without promoting reuse. | Exact dashboard/report terms or signed bulk-data agreement. If unavailable, metadata/citation-only. | Record agreement scope, fees, edition, expiry and redistribution conditions separately. |
| `INT-CEPEJ-2024` | `restricted_or_unknown` | Use citation and bounded metadata only. | Edition-specific permission or an applicable express exception. Otherwise exclude source bytes from public artifacts. | Record third-party exclusions and permitted extract limits. |
| `INT-NCSC-COURTOOLS` | `restricted_or_unknown` | Retain original GFJD definitions and source metadata, not NCSC content. | Copyright permission for the exact materials. If absent, link/cite only. | Bind permission or refusal/no-response outcome to the exact edition. |
| `INT-NCSC-FAMILY` | `restricted_or_unknown` | Retain source metadata and independently authored mappings only. | Exact page/material permission. If absent, link/cite only. | Separate factual metadata from protected explanatory text and measures wording. |
| `INT-HCCH-CA` | `restricted_or_unknown` | Apply attributed non-commercial metadata routing only. | Edition/content-class terms for portal, publication and database components. If mixed or ambiguous, route each component separately or quarantine. | Record component-level rights rather than one portal-wide status. |

The controlling reviews are
`docs/methods/high-priority-source-rights-review-2026-08-01.md` (SHA-256
`1d9a7a37e18fd3db33176262f2f4ecb1c90b6b5843df0969b529e3bb5f95b0d5`)
and `docs/methods/exact-edition-rights-screening-2026-08-03.md` (SHA-256
`3f1011855467ec386c7b6e1c64935668d12038e0332f89ef731f9fffc3101e1b`).

## G3–G6 dependency backlog

### Dependency sequence

1. **G2 first:** obtain a successful prospective blind-holdout result and owner
   adjudication for G2-C01–C08. Current technical readiness cannot substitute
   for the failed calibration or unseen-edition evidence.
2. **G3 after G2:** finish `WI-G3-01` through `WI-G3-08`, then build and owner-
   adjudicate `WI-G3-CLOSE`. The factual core is current coverage, second review,
   authoritative triangulation, enquiry closure, exact-edition rights and
   operational monitoring.
3. **G4 after G3:** use only approved G3 inputs to build the beta core, outcomes
   catalogue, context library and products; run quality, security, accessibility
   and operations panels; then owner-adjudicate `WI-G4-CLOSE`.
4. **G5 after G4:** freeze contracts and the exact release candidate; perform a
   clean rebuild, candidate-specific agent assurance, accessibility review,
   operations/restore rehearsals, provenance preparation and the 12-month
   operating plan; then owner-adjudicate `WI-G5-CLOSE`.
5. **G6 after G5:** require zero unresolved P0/P1 and no unaccepted critical/high
   assurance finding, exact artifact verification, two provider-separated
   custody locations with tested restore, live owner-held service controls,
   version-linked public materials, a dated resource commitment and the final
   signed owner decision. Publication occurs only after that decision.

The exact downstream work-item backlog is:

| Gate | Current non-accepted work items |
|---|---|
| G3 | `WI-G3-01`–`WI-G3-08`; `WI-G3-CLOSE` |
| G4 | `WI-G4-01`–`WI-G4-09`; `WI-G4-CLOSE` |
| G5 | `WI-G5-01`–`WI-G5-10`; `WI-G5-CLOSE` |
| G6 | `WI-G6-01`–`WI-G6-09`; `WI-G6-CLOSE` |

### Repository-owned work versus future facts

| Gate | Repository-owned/sourceable now | Facts that cannot be inferred from implementation | Advisory panel before owner decision |
|---|---|---|---|
| G3 | Generate coverage/contradiction queues; validate maps/logs; run second-agent reviews on already permitted evidence; build rights/preservation/monitoring receipts; prepare a closure pack. | Current authoritative evidence for unresolved jurisdictions, actual access failures, exact-edition terms, response outcomes and complete monitoring observations. | Coverage, source-language, institutional-structure, negative-findings, rights and preservation agents. |
| G4 | Build beta artifacts from accepted inputs; run lineage, comparability, disclosure, product, accessibility automation and operations rehearsals. | Complete approved G3 cohort, real outcomes studies, actual candidate behavior and any human-participant claim (which remains absent unless genuinely supplied). | Data quality, methods, product, accessibility/localisation, privacy/security and operations agents. |
| G5 | Freeze contracts; clean-build exact candidate; generate SBOM/provenance; run security/accessibility/operations panels; cost the operating plan. | Current live settings, actual key/custody facts, exact release-candidate inputs and owner resource commitment. | Methods, data assurance, security/privacy/rights, accessibility, provenance and release-operations agents. |
| G6 | Verify the immutable candidate, prepare custody/restore evidence, service runbooks, publication pack and decision packet without publishing. | Two actual custody locations, tested restore outcome, live support/monitoring state, dated 12-month resource commitment and final owner signature. | Cross-role final-release panel with explicit dissent and unresolved findings. |

## Precise recommended register updates

No register update is justified by this audit alone. Apply the following only in
a later coherent change after the named evidence exists:

1. Add the signed successor freeze, structured owner decision and authority
   receipt as a new G2 evidence record; keep it `in_review` until execution
   produces a verified bundle. Do not overwrite or promote
   `E-PILOT-METADATA-SEARCH-STOP-20260816`.
2. Add the completed successor execution as a distinct record with exact query,
   exposure, non-overlap and allowlist receipts. Its status remains `in_review`;
   metadata discovery does not satisfy G2-C07.
3. Add the later structural-preflight, selection, dual-extraction, comparator and
   owner-adjudication artifacts as separate immutable records. Only then update
   `E-PILOT-INDEPENDENT-ASSURANCE`, `E-PILOT-REVIEW` and related G2 work items.
4. For `R12`, replace the stale deputy control at the next risk-register review
   with the accepted single-owner unavailable-owner pause and non-approving
   agent continuity model.
5. For the seven rights notices, create edition/component-specific decisions;
   update `licence_status` only when the exact terms/permission artifact and
   owner decision are both bound. Otherwise retain the notice and metadata-only
   contingency.
6. Refresh every risk’s `reviewed_on`, `next_review_on`, evidence references and
   residual severity only through a risk-specific owner adjudication. Do not
   bulk-close the 19 risks or reinterpret `accepted` as low residual severity.
7. Keep all G3–G6 work items `in_review` and all downstream gates dependency-
   blocked until the immediately preceding gate has an accepted digest-bound
   owner decision.

## Recommended immediate action

Freeze and bind the clean G2 successor design, obtain the exact prospective
owner authority record, and then execute the bounded search stage under its
208-call, zero-retry, no-result-access contract. Stop on any contract or provider
failure. After execution, convene network-disabled identity/access/methods
panels and return the exact candidate and allowlist evidence to the owner. Do
not access any result URL or alter G2 acceptance state as part of that step.
