# Blocker resolution plan

This plan addresses every current Conductor blocker while preserving the
separation between repository implementation and external evidence or
authority.

## Recommended route: autonomous fail-closed preparation

The analyst continues all safe repository work: deterministic evidence packs,
search and review queues, rights routing, source manifests, reproducibility
checks, release rehearsals, and exact-head pull requests. No gate is accepted
from a local test, owner assertion, checksum, or generated report alone.

## Dependency sequence

`T9 -> T0 -> T1 -> (T2, T7) -> T3 -> (T4, T5) -> (T6, T8) -> G1..G6`

Each downstream track remains blocked until its predecessor gate and required
evidence are accepted.

## Blocker classes and actions

| Blocker | Repository action | External boundary | Contingency |
|---|---|---|---|
| Governance and decision rights | Maintain charter, RACI, gate packs and stale-approval checks | Formal authority acceptance | Keep G1 `blocked_by_assurance` |
| Methods and pilot adjudication | Maintain v0.3 manifest, adjudication register and review packet | Independent methods review and pilot evidence | Quarantine unresolved questions |
| Census coverage | Maintain search logs, maps, coverage matrix and remediation queues | Reviewed source findings and local verification | Preserve explicit incomplete states |
| Direct enquiries | Maintain templates, register and transparent-closure controls | Approved contact and response outcome | Close as no-response only with dated evidence |
| Source rights and preservation | Maintain manifests, checksums and rights queue | Authoritative rights decision | Metadata/citation-only routing |
| Engineering and release | Run clean builds, pipeline, warehouse, backup and reproducibility rehearsals | Release authority and independent verification | Keep release draft-only |
| Product, security and operations | Maintain accessibility, disclosure, security, incident and restore checks | External assurance, host and operating commitment | Keep publication disabled |

## Stop conditions

The autonomous loop stops only for a destructive action, credential use,
outbound contact, rights decision, independent review, formal gate decision,
publication, signing, funding or host commitment. These conditions are
recorded as blockers rather than silently waived.

## T6 execution plan (2026-08-01)

### Options

1. **Recommended — fail-closed candidate release:** keep the portable product
   bundle reproducible and inspectable, but leave publication disabled until
   rights, accessibility, localisation and independent assurance evidence is
   attached to the exact release digest.
2. **Conditional beta:** publish only metadata, schemas and synthetic examples
   under a clearly labelled technical preview. This improves discoverability
   but still requires host, accessibility and disclosure review.
3. **Full publication:** wait for all source, methods, rights, coverage and
   operational gates, then publish an approved immutable release.

The recommendation is option 1. It maximises autonomous progress without
turning generated products into authority or empirical evidence.

### Dependency sequence and contingencies

| Step | Repository-owned action | Required external evidence | Fallback |
|---|---|---|---|
| T6-1 | Build and verify `gfjd products` candidate bundle and digest inventory | None | Rebuild deterministically from the same inputs |
| T6-2 | Maintain source, methods, limitations, citation and responsible-use links | Rights and methods decisions | Metadata/synthetic-only bundle |
| T6-3 | Run automated HTML, schema, checksum and low-bandwidth checks | Independent accessibility/localisation review | Publish an accessibility exception register, keep release disabled |
| T6-4 | Attach coverage and provenance summaries to the candidate manifest | Reviewed jurisdiction/source coverage | Keep unresolved dimensions explicit and exclude from comparison |
| T6-5 | Re-run strict validation, release rehearsal and hosted CI | Publication authority and host commitment | Retain draft artefact; do not sign or deploy |

No outbound enquiry, rights decision, publication, signing or external review
is performed by the analyst without explicit authority and evidence.

## T7 execution plan (2026-08-01)

### Options

1. **Recommended — assurance baseline plus fail-closed release:** continuously
   run repository security/public-data scans, rights-queue validation, supply-
   chain checks and release-blocker evaluation; retain unresolved findings as
   explicit blockers.
2. **Technical-preview assurance:** expose only synthetic fixtures and metadata
   after the baseline passes, with no empirical or rights-sensitive material.
3. **Production assurance:** wait for independent security/legal review,
   rights determinations, threat-model acceptance and accountable gate approval.

Option 1 is adopted. It improves detection and produces review-ready evidence
without treating an agent-generated scan as independent assurance.

| Step | Repository-owned action | External dependency | Contingency |
|---|---|---|---|
| T7-1 | Run `gfjd security`, strict validation and contract/lock audits | None | Quarantine the affected artefact and retain the report |
| T7-2 | Validate rights queue, prohibited-data headers and release blockers | Rights/legal determination | Metadata-only or synthetic-only routing |
| T7-3 | Rehearse clean release/backup and preserve digests | Independent security and supply-chain review | Keep release candidate unsigned and undeployed |
| T7-4 | Attach scan outputs to the candidate evidence packet | Accountable owner acceptance | Leave G1/G2/G4/G5/G6 evidence in draft/missing state |

## T8 execution plan (2026-08-01)

### Options

1. **Recommended — rehearse locally and keep operations draft-only:** exercise
   deterministic release, backup/restore, correction and monitoring workflows;
   preserve receipts and hashes without deploying or signing.
2. **Controlled technical service:** run the synthetic candidate in a managed
   preview with an explicit operator and rollback path; requires host and
   incident-contact approval.
3. **Production operation:** require two-location custody, signed provenance,
   support rota, incident readiness and a committed maintenance budget.

Option 1 is adopted because it reduces operational risk without implying a live
service or creating an unapproved external commitment.

| Step | Repository-owned action | External dependency | Contingency |
|---|---|---|---|
| T8-1 | Run release, backup/restore and manifest verification | None | Keep the reproducible draft artefact |
| T8-2 | Exercise correction, rollback and incident runbooks against synthetic data | Operator/host approval | Record a rehearsal-only receipt |
| T8-3 | Preserve provenance and archive/restore instructions | Independent custody and signing | Keep unsigned, single-location draft |
| T8-4 | Maintain support, monitoring and release-calendar templates | Named service owner, deputy and budget | Keep handover evidence missing |

## T9 execution plan (2026-08-01)

### Options

1. **Recommended — prepare participation and sustainability evidence without
   claiming participation:** maintain translation/glossary controls, local
   verification templates, feedback-disposition records and a costed operating
   plan template; keep all human acceptance and funding fields pending.
2. **Limited consultation:** run an approved, compensated synthetic usability
   exercise with no collection of sensitive lived-experience data.
3. **Full community programme:** engage regional experts and lived-experience
   contributors under approved safeguarding, remuneration, consent and funding
   arrangements.

Option 1 is adopted. It improves readiness while avoiding unapproved outreach,
personal-data collection or invented representation.

| Step | Repository-owned action | External dependency | Contingency |
|---|---|---|---|
| T9-1 | Maintain translation glossary, source-language retention and review templates | Local/regional verification | Mark ambiguity unresolved and exclude from comparison |
| T9-2 | Maintain beta feedback and disposition schema | Consent-based participant recruitment | Use synthetic feedback only; do not claim user research |
| T9-3 | Maintain costed 12-month operating/succession plan | Committed staffing, deputy and funding | Keep G5/G6 evidence draft/missing |
| T9-4 | Record coverage and participation gaps in the conductor | Regional network and lived-experience review | Publish limitations and defer readiness |
