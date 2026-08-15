# Sole-owner panel decision packet — G1 and later gates

Date: 2026-08-14

## Authority and panel boundary

The repository owner is the sole accountable decision-maker. Role-separated
analyst-agent panels provide advice, technical review and evidence preparation.
They do not exercise authority and must not be described as independent
specialists, legal advisers, local experts, human participants or people with
lived experience.

Each panel was instructed to provide options, trade-offs, limitations,
contingencies, rationale, recommendations, evidence references, dissent and
abstentions. This packet records their synthesis for owner decision.

## Material correction to the current G1 interpretation

G1-C03 requires acceptance of the aggregate-only boundary, ethics principles
and prohibited-data rules. G1-C04 requires approval of the target architecture,
contracts, environments and release-authority model. G1-C06 requires the
initial risk, threat, rights and disclosure baselines to be documented. None of
these three criterion texts expressly requires an external specialist or
independent human reviewer.

The panel therefore recommends that the owner may accept these foundation
criteria after the repository contradictions below are corrected. Stronger
methods, security, privacy, legal, accessibility, local-human, operational and
release evidence remains required only where a later gate retains such a
requirement.

## Decision 1 — G1-C03 ethics and security

### Options

1. Retain `in_review` pending external specialists. This gives conventional
   separation but creates an unnecessary dependency for a foundation-policy
   criterion.
2. Accept after correcting the reporting route and extending the scoped
   owner-decidable allowlist. **Recommended.** This accepts repository policy
   without claiming legal, specialist or release assurance.
3. Rewrite the criterion as documentation-only. This removes ambiguity but
   weakens the gate contract and creates avoidable migration work.

### Conditions and contingencies

- Replace the obsolete instruction to report through a host institution with
  an owner-controlled private route or a fail-closed instruction prohibiting
  sensitive reports in public issues.
- Add `E-ETHICS-BOUNDARY` and `E-SECURITY-POLICY` to the scoped G1
  owner-decidable allowlist.
- Continue the aggregate-only, metadata-first boundary and quarantine unclear
  privacy, disclosure or safeguarding states.
- Reopen on personal/case-level processing, increased granularity, disclosure
  incident, safeguarding concern, material boundary change or digest change.

### Recommendation

Accept G1-C03 for foundation purposes after the two repository changes. Do not
represent the acceptance as legal advice, specialist assurance or authority to
publish or operate a live service.

## Decision 2 — G1-C04 architecture

### Options

1. Retain `in_review` until an independent technical reviewer exists. This
   preserves the former multi-person model but conflicts with the declared
   single-owner structure.
2. Accept after reconciling architecture language with the single-owner model.
   **Recommended.** Role-separated agents prepare and verify; the owner alone
   authorizes signing, publication, deployment and release.
3. Remove production/release architecture from G1. This simplifies G1 but
   weakens early architectural control.

### Conditions and contingencies

- Replace the architecture's mandatory second-person production step with
  role-separated agent preparation/verification plus owner authorization.
- Never label agent verification as independent assurance.
- Add `E-ARCH-V1` to the scoped G1 owner-decidable allowlist.
- Leave hosting, archive custody, signing/key custody and monitoring as later
  operational decisions.
- Reopen on material architecture/contract changes, new data boundaries,
  manifest mismatch, supply-chain event, live-service proposal or custody
  change.

### Recommendation

Accept the target architecture for repository-owned implementation after the
contradictory language is repaired. Keep all release and live-operation
decisions separate.

## Decision 3 — G1-C06 risks, rights and disclosure

### Options

1. Preserve an external-specialist prerequisite. This provides conventional
   separation but exceeds the literal G1 baseline criterion.
2. Accept the documented baselines after agent-panel review. **Recommended.**
   Later source-specific and release assurance remains separately required.
3. Accept automatically because the files exist. This lacks accountable
   binding and is not recommended.

### Rights boundary

The recommended baseline distinguishes public facts, metadata and independently
generated aggregate observations from protected expressive material and exact
source bytes. Owner policy may govern repository handling, but it cannot erase
an express third-party restriction. Ambiguity continues to trigger
metadata-only handling, private preservation or quarantine unless the owner
records a source-specific decision.

### Recommendation

Accept `E-RISK-REGISTER`, `E-THREAT-BASELINE` and `E-RIGHTS-BASELINE` for the
limited G1 purpose, then accept WI-G1-06. This accepts documented fail-closed
baselines, not any particular source edition, legal conclusion, publication or
release.

## Decision 4 — risk-specific treatment

| Risk | Recommended G1 decision | Mandatory contingency |
|---|---|---|
| R02 | Accept residual risk for G1; do not close | Quarantine comparisons; reopen for any new clock, denominator, statistic or cross-jurisdiction comparison |
| R10 | Accept only under aggregate/suppression/metadata boundary | Reopen for small cells, personal data, increased granularity or contextual-harm concern |
| R11 | Accept for private repository preparation | No deployment/release; reopen for secret exposure, dependency alert or unexpected workflow/digest change |
| R15 | Accept while the owner retains sole control | Reopen for funding, institutional influence, suppression request, conflict or governance change |
| R16 | Accept for private development only | Reopen for publication/live-service/release proposal without a costed owner commitment |
| R20 | Accept for G1 accounting while retaining hard release no-go | Must be closed before release through actual support, monitoring, incident, custody, restore and rehearsal evidence |

`accepted` means the owner knowingly accepts the residual risk for the bounded
stage. It does not mean `closed`. No panel recommends closing these risks now.

## Decision 5 — later-gate evidence model

### Options

1. Preserve every independent/external/human/local requirement. This offers
   conventional assurance but leaves the project permanently externally
   dependent.
2. Amend applicable contracts to role-separated, digest-bound agent-panel
   advice plus sole-owner adjudication, with transparent limitations.
   **Recommended.** Actual source and operational facts remain mandatory.
3. Preserve the current contracts and stop at a private release candidate.
   This avoids overclaiming but prevents G4-G6 passage.

### Recommended gate changes and retained facts

- **G2:** use the bounded approved pilot cohort rather than an arbitrary
  twelve-system minimum; use blinded role-separated agent re-extraction and
  owner adjudication. Still require real source inputs, manifests, concordance,
  methods dispositions, rights decisions and restore receipts.
- **G3:** use source-language, jurisdiction-aware agent review with
  authoritative-source triangulation. Do not claim local-human verification.
  Ambiguity stays metadata-only/quarantined. No outbound enquiry without
  separate owner approval.
- **G4:** use non-participatory accessibility, localisation and usability
  testing by agents and automated tools. Disclose that no human-participant,
  lived-experience or regional-acceptance validation occurred.
- **G5:** replace external/independent review language with role-separated
  agent-panel review and owner disposition. Still require actual clean builds,
  checksums, archives, rehearsals, defect closure and a costed operating plan.
- **G6:** use two technically and provider-separated archive locations under
  owner custody; owner support with response targets and unavailable-owner
  pause; and agent reproducibility checks. Still require actual receipts,
  restore tests, signing/attestation, monitoring, publication records and a
  dated 12-month resource commitment.

### Limitations and dissent

- The security/privacy role rejects any claim of independent or specialist
  assurance from an agent panel.
- The rights role rejects blanket exact-byte reuse where express terms say
  otherwise and abstains from legal conclusions.
- The methods role rejects closing R02 before real-pilot adjudication.
- The accessibility/localisation role rejects lived-experience, local-cultural
  or participant-validation claims without actual people.
- The operations role rejects treating R16/R20 acceptance as service or
  release readiness.
- The release role recommends publication only after the exact immutable
  candidate and residual risks are accepted by the owner.

## Consolidated recommended owner decision

> I approve the role-separated analyst-agent panel recommendations recorded in
> the Sole-owner panel decision packet dated 2026-08-14.
>
> I accept G1-C03, G1-C04 and G1-C06 for their limited foundation purposes,
> subject to the repository corrections, conditions and reopen triggers in the
> packet. I authorize E-ETHICS-BOUNDARY, E-SECURITY-POLICY, E-ARCH-V1,
> E-RISK-REGISTER, E-THREAT-BASELINE and E-RIGHTS-BASELINE to be added to the
> scoped owner-decidable G1 evidence policy and accepted through a digest-bound
> owner record after those corrections pass validation.
>
> I accept R02, R10, R11, R15, R16 and R20 as residual risks for G1 foundation
> and private repository preparation only. None is closed. Their controls and
> reopen triggers remain mandatory. R20 remains a hard no-go for deployment,
> publication and release until actual operational evidence passes.
>
> For G2-G6, role-separated, digest-bound analyst-agent panels are the required
> advisory and technical-review mechanism. I remain the sole accountable
> decision-maker for methods, risk, rights policy, gates, publication, custody,
> signing and release. Requirements referring to independent, external,
> specialist, deputy, local-human or participant review must be amended rather
> than satisfied by relabelling agents, and public claims must disclose the
> resulting limitations.
>
> I approve the bounded pilot model, blinded role-separated agent
> re-extraction, source-language agent review with authoritative triangulation,
> non-participatory agent/tool accessibility testing, agent-panel release
> review, two provider-separated archives under my custody, and an
> unavailable-owner pause condition. No outbound enquiry is authorized by this
> decision.
>
> This decision does not manufacture source facts, permissions, correspondence,
> test results, archive receipts, restore results, publication states or
> resource commitments. Those must be evidenced. Any unresolved critical risk
> remains a blocker; every high risk requires my explicit digest-bound
> adjudication with conditions, expiry and reopen trigger.

## Implementation after owner approval

1. Correct `SECURITY.md` and the architecture's multi-person contradictions.
2. Extend the scoped owner-decidable G1 evidence allowlist.
3. Create the digest-bound owner decision and bind it to this packet and the
   current manifest.
4. Accept the six G1 evidence rows and WI-G1-03/04/06 without claiming
   specialist or independent assurance.
5. Record risk acceptance separately from closure and preserve R20's release
   hard stop.
6. Amend later-gate contracts and work-item language consistently.
7. Rebuild generated artefacts and the manifest; run strict validation and the
   G1 gate.

