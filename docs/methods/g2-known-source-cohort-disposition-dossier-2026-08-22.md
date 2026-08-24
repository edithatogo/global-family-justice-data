# G2 known-source cohort and disposition dossier — 2026-08-22

This dossier implements the repository-owned preparation in the G2
blocker-resolution plan. It is an evidence map and proposed disposition, not a
gate decision, legal opinion, rights clearance, publication authorisation, or
G2 passage.

## Bound cohort and coverage state

| Route | Exact edition / artifact | Institutional provenance | Coverage state | G2 use now |
| --- | --- | --- | --- | --- |
| API | `G2-API-BRA-TJSP-2026`, original aggregate response SHA-256 `f475ae52b31f0e9a509de1be1d312bb946f4f57944717d0bda5d68d1f59df2fe`; later class-1389 aggregate response SHA-256 `626d18292c23ffe5e369b3c82c5477f9265686dca86f195021bc8f100c903da3` | DataJud public TJSP endpoint | The later bounded request selects official CNJ TPU class `1389` (`Ação de Alimentos`), retains zero hits and returns an aggregate bucket count of `2`; no time basis or denominator is bound. | Private aggregate-only supporting evidence; not part of formal concordance. |
| Spreadsheet | `GBR_EAW_MOJ_FAMILY_Q_2026Q1`, ODS SHA-256 `3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2` | England and Wales Ministry of Justice family-court tables | Extracted and role-separated re-extracted in final two-row known-source recalibration. | Quarantine-only, descriptive source record. |
| Dashboard | `GBR_EAW_MOJ_FAMILY_DASH_2026Q1`, Power BI entry HTML SHA-256 `52d356701a10ac6519da61d82ecf3f0cb0e04921597f19a4df6fe721687ac63f`; quarterly response SHA-256 `4009c22c5e0bf115205d8488838b8c9b0f224ec627a6f9bc2f2e7be02b36fae1` | England and Wales Ministry of Justice visualisation tool | Digest-bound semantic query evidence explicitly returns `2026-Q1`, `Orders applied for`, value `4,917`; denominator and reporting-universe equivalence remain unresolved. | Same-series cross-format reconciliation evidence only; not independent corroboration or formal concordance. |
| PDF/manual | `AUS_FCFCOA_AR_2024_25`, PDF SHA-256 `e251da7a9424aeba5e8c9e53a7f33fc5901769b10e6e0ea27f5b446bc5fd2ee9` | Federal Circuit and Family Court of Australia annual report | Extracted and role-separated re-extracted in final two-row known-source recalibration. | Quarantine-only, descriptive source record. |

The four-route acquisition record is
[`g2-four-edition-acquisition-evidence-2026-08-21.md`](./g2-four-edition-acquisition-evidence-2026-08-21.md).
This is a bounded known-source cohort, not a coverage claim or an unseen
holdout.

## Method disposition matrix

| Record | Source-faithful interpretation | Material incompatibility | Proposed disposition |
| --- | --- | --- | --- |
| England and Wales ODS | `4,917` public-law **orders applied for**; national scope; source period `2026 Q1`; ISO dates remain null under the explicit-only rule. | Counts orders, not applications; period endpoints are not explicitly established in the bound row. | Retain as quarantined descriptive evidence. Do not pool, rank or compare with the PDF. |
| Australia PDF | `2,555` **applications/filings** in Table 3.3.1(a); court scope; source period `2024–25`; ISO dates remain null. | Counts applications/filings, not orders; court rather than national scope; a different source-defined period. | Retain as quarantined descriptive evidence. Do not pool, rank or compare with the ODS. |
| DataJud API | No substantive measure selected. | Missing family-justice filter, denominator and target definition. | Keep acquisition-only; a fresh scoped request definition is required before any extraction. |
| England and Wales dashboard | `4,917` `Orders applied for`; the same visual now returns an explicit `2026-Q1` row under `Period = Quarterly`. | Reporting universe/denominator semantics and rights/security remain unadjudicated. | Same-series cross-format reconciliation evidence only; retain quarantine and do not treat as independent corroboration. |

This matrix is the prepared input for G2-C05. It does not adjudicate methods:
the sole owner must decide whether these quarantine-only dispositions are
accepted for the bounded cohort after the route gaps are resolved or formally
excluded by a separate scope decision.

## Edition assessment envelope

| Edition | Current factual handling | Assessment state | Required completion evidence |
| --- | --- | --- | --- |
| DataJud API responses | Aggregate-only and locally hash-bound; no hit records acquired. | Handling decided: private aggregate-only; edition-specific assessment remains incomplete. | Complete rights/privacy/security/disclosure finding; retain private and require a separate decision before reuse. |
| England and Wales ODS | Locally hash-bound and used only for quarantined extraction. | Handling decided: private quarantine and conditional bounded-reuse candidate; assessment remains incomplete. | Complete edition-specific assessment and recheck OGL applicability, attribution, exclusions, third-party content and prohibited material at the point of reuse. |
| England and Wales dashboard entry and responses | Locally hash-bound HTML shell plus digest-bound semantic queries and explicit quarterly confirmation. | Handling decided: metadata/citation and private-response evidence; assessment remains incomplete. | Complete edition/visual assessment; keep raw model/query responses outside Git and public publication; no redistribution. |
| Australia PDF | Locally hash-bound and used only for quarantined extraction. | Handling decided: private quarantine; edition-specific assessment remains incomplete. | Complete rights/privacy/security/disclosure finding; do not extract or redistribute unrelated pages. |

The owner handling decision is recorded in
[`g2-rights-privacy-security-disclosure-owner-decision-2026-08-24.md`](../governance/g2-rights-privacy-security-disclosure-owner-decision-2026-08-24.md).
It establishes controlled private quarantine and a metadata-only public/Git
boundary, with retention review by `2027-08-24`. It is not rights clearance or
specialist assurance and does not close `G2-C06`; the criterion remains
`in_review`.

## Evidence already produced

- Final two-row exact concordance: 36/36 critical and 40/40 populated-field
  matches; both rows remain quarantined.
- Quarantine-only clean build: two bronze, two silver, two quarantine and zero
  gold records; receipt SHA-256
  `b317a4f5fa79e317af9843470bf1d91f4cf5d1b9d4bbec33a4f58cf258a6a4ba`.
- Failed packets, dashboard secondary stop and search/exposure lineages remain
  immutable supporting evidence; none is repaired or promoted.

## Next bounded execution

The remaining work can be performed as one real-pilot completion packet:

1. bind a substantive API request definition and a dashboard visual/export
   value, each with source hash and locator;
2. complete the four edition assessments above; and
3. refresh the cohort evidence, methods matrix and review/re-extraction record.

If either API or dashboard route cannot yield those facts, stop and return a
single scope decision: retain the route as acquisition-only or amend the pilot
criterion. Do not silently substitute the ODS value, re-run a terminated
lineage, or promote the two-row result.
