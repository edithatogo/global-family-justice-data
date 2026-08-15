# G2 work acceptance and mapping — owner decision — 2026-08-16

Decision ID: `D-G2-WORK-ACCEPTANCE-MAPPING-20260816`

Decision-maker: repository owner, founder and sole accountable decision-maker.

Recorded at: `2026-08-16T09:42:40+10:00`.

Status: `accepted` for Options A1 and B1 only.

## Immutable input bindings

- Decision packet:
  `docs/governance/g2-work-acceptance-mapping-owner-decision-packet-2026-08-16.md`
- Decision-packet SHA-256:
  `5df122f50d08279e63d633baa0cbe453dac720358d3e4fc90fcb8df9ae12d79c`
- Evidence-acceptance audit:
  `docs/programme/audits/g2-evidence-acceptance-audit-2026-08-16.md`
- Evidence-acceptance audit SHA-256:
  `9980a8ec3532655f3e3886f8d6fe5f70068c28f5e058098ebc25a8a03eda4344`
- Pre-decision work-item register SHA-256:
  `3dce2d5d6b115d3d158248cb1b12798e0665e08b1fd2dfd76f12fc237347a325`
- Evidence register SHA-256:
  `554828703d51f449b16272627b89b4fa60cfa647db2edc439247e773632f2e9d`
- Stage-gate contract SHA-256:
  `87b0d89d5197d3bc54fefeeb4e902c2620963ea7661a7318068707d5d5999245`

The repository verified these bindings and confirmed that G2 was fail-closed
before recording this decision.

## Owner decision

> I approve Options A1 and B1 in the G2 work acceptance and mapping owner
> decision packet dated 2026-08-16.
>
> For WI-G2-08, I accept the completed private synthetic pilot release,
> correction and artifact-restoration rehearsal and authorize the controlled
> transitions done → in_review → accepted. This does not establish live
> operations, publication, release readiness or G2 passage.
>
> For WI-G2-07, I approve correction of its acceptance-bearing evidence mapping
> to E-PILOT-INDEPENDENT-ASSURANCE. Historical failed, expired, design, stop and
> successor-preparation evidence remains unchanged as supporting lineage.
> WI-G2-07 remains in_review pending a successful blind holdout and separate
> owner adjudication.
>
> This decision authorizes no network or source access, extraction,
> publication, release or G2 passage.

## Authorized implementation

1. Transition `WI-G2-08` from `done` to `in_review`, then from `in_review` to
   `accepted`, using the Conductor state machine.
2. Set the acceptance-bearing `evidence_ids` for `WI-G2-07` to
   `E-PILOT-INDEPENDENT-ASSURANCE`, matching criterion `G2-C07`.
3. Preserve all historical failed, expired, design, stop and successor records
   unchanged as supporting lineage in the work-item note.
4. Keep `WI-G2-07` and `E-PILOT-INDEPENDENT-ASSURANCE` `in_review`.
5. Recompute generated views and confirm that G2 remains fail-closed.

## Explicit exclusions

This decision is not G2 passage and does not authorize network access, source
access, extraction, rights acceptance, live operations, publication,
deployment or release.

Immutable reference: the signed Git commit containing this decision. The
implementation commit must bind that signed commit and this file's SHA-256.
