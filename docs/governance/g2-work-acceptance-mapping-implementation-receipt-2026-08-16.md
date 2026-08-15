# G2 work acceptance and mapping — implementation receipt — 2026-08-16

Receipt ID: `R-G2-WORK-ACCEPTANCE-MAPPING-20260816`

Authority decision:
`docs/governance/g2-work-acceptance-mapping-owner-decision-2026-08-16.md`.

Authority-decision SHA-256:
`ff8c27dbc2bfc7ba08c018addc40cf26f9bb5dcb427531365f151283f396ad4a`.

Signed authority-decision commit:
`c5fbc4922e6f7ceb983cd5b16771b4f2268d54e5`.

## Applied changes

1. `WI-G2-08` moved through the controlled transitions `done -> in_review ->
   accepted` using the Conductor CLI. Both events are retained in
   `programme/audit-log.jsonl`.
2. `WI-G2-07.evidence_ids` now contains only
   `E-PILOT-INDEPENDENT-ASSURANCE`, matching `G2-C07`.
3. The `WI-G2-07` note preserves the identifiers of every historical failed,
   expired, design, stop and successor-preparation record as immutable
   supporting lineage.
4. `WI-G2-07` and `E-PILOT-INDEPENDENT-ASSURANCE` remain `in_review`.
5. `D-G2-WORK-ACCEPTANCE-MAPPING-20260816` is recorded in
   `programme/decision_log.csv`.
6. The transition exposed pre-existing unquoted comma fields in the programme
   CSVs. The affected notes were restored without changing their meaning, and
   the shared CSV reader now rejects surplus fields before any governed rewrite.

The WI-G2-07 mapping change is an owner-authorized administrative correction
recorded by the repository diff and this receipt. It does not alter any
evidence record or evidence status.

## Post-change bindings

- `programme/work_items.csv` SHA-256:
  `d2b927f028f8c1941c437c80f45a24972f7df4869e3902501b0a781cafb2fe86`
- `programme/evidence_register.csv` SHA-256:
  `12b094df687832366631e0cc287561a465b0b32f6258d6c0c6034a32c93dc72d`
- `programme/decision_log.csv` SHA-256:
  `8b0da8ce7214fe68d56daa0485977bf63b18f465410841a4b17995519e72103b`
- `programme/audit-log.jsonl` SHA-256:
  `e5cb228ef36f45503f635f6e93d5ab2633d4a1a09a384a3b5ddae1aa04484a98`
- Generated status SHA-256:
  `09f52c47c58a9b34d5a2c1b1480a9b0ac1464ac4315211077a721db668588e6d`
- Generated programme graph SHA-256:
  `6bdd1bfd7f904ae06f5ddfe8248962a24dfc5a1426108ce2c0ddfa15aa3346db`

## Validation result

- Project validation: `PASS`, 22 checks, 0 errors, 0 warnings and 7 existing
  informational source-rights notices.
- `WI-G2-08` is no longer a G2 work failure.
- G2 remains `blocked_by_maturity`, not ready and not passed.
- Remaining G2 work failures: `WI-G2-01` through `WI-G2-07`.
- G2 remains at 4 of 13 completed requirements because `G2-C08` already passed
  before the work-item acceptance transition.
- Evidence-assured maturity remains L1, below the required L2.

## Boundaries preserved

No network or source access, extraction, rights acceptance, live operations,
publication, deployment, release, G2 decision or G2 passage was performed.
