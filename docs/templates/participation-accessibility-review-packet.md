# Participation, accessibility and independent-review packet

This packet is a structured handoff for the subagent panel and accountable
reviewers. It is not a consent record, accessibility certificate, localisation
approval, ethics approval or publication decision.

## Frozen identity

- Packet digest (SHA-256):
- Review ID:
- Review type: accessibility / localisation / usability / responsible-use / participation / independent_assurance
- Candidate release:
- Evidence freeze date:

## Evidence register

| Reference | Kind | Status | Notes |
|---|---|---|---|
| | automated_check / human_review / participant_feedback / consent_record / independent_report | present / missing / unresolved | |

Automated checks may establish structural controls only. Human review,
participant feedback and consent records must identify their accountable source
without placing personal data in this repository.

## Findings and disposition

| Finding ID | Severity | Finding | Disposition | Residual risk |
|---|---|---|---|---|
| | P0/P1/P2/P3 | | open/fix/defer/accept/reject | |

Open P0/P1 findings, missing reports, unresolved consent, or disagreement keep
the gate blocked. Owner adjudication does not substitute for independent
assurance or participant consent.

## Authority boundary (mandatory)

- Human accessibility/localisation/usability review required: **yes**
- Consent and safeguarding approval required before participant engagement: **yes**
- Independent assurance required where claimed: **yes**
- Publication/release authority required: **yes**
- Subagent panel can grant any of the above: **no**

## Contingencies

- Missing reviewer or participant evidence: retain `blocked`; do not infer approval.
- No consent or safeguarding approval: synthetic rehearsal only; collect no participant data.
- Accessibility defect: remediate and rerun checks; no publication claim.
- Unresolved language coverage: preserve source language and label the gap.
- Unresolved rights: metadata-only or exclude the affected artefact.
- No independent report: draft/unsigned candidate only.

## Sign-off (external)

- Accountable owner:
- Independent reviewer/assurer:
- Consent/safeguarding authority:
- Publication authority:
- Decision and date:
