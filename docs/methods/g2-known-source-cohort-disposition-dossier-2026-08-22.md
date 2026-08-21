# G2 known-source cohort and disposition dossier — 2026-08-22

This dossier implements the repository-owned preparation in the G2
blocker-resolution plan. It is an evidence map and proposed disposition, not a
gate decision, legal opinion, rights clearance, publication authorisation, or
G2 passage.

## Bound cohort and coverage state

| Route | Exact edition / artifact | Institutional provenance | Coverage state | G2 use now |
| --- | --- | --- | --- | --- |
| API | `G2-API-BRA-TJSP-2026`, aggregate API response SHA-256 `f475ae52b31f0e9a509de1be1d312bb946f4f57944717d0bda5d68d1f59df2fe` | DataJud public TJSP endpoint | Acquisition-only: zero document hits and 20 unfiltered class buckets; no family-justice measure is bound. | Cannot enter extraction or methods adjudication. |
| Spreadsheet | `GBR_EAW_MOJ_FAMILY_Q_2026Q1`, ODS SHA-256 `3d2018163db2e50c3ed2ce9206b1f1fc3145c5028de5fd7d7c63cde362ca6fd2` | England and Wales Ministry of Justice family-court tables | Extracted and role-separated re-extracted in final two-row known-source recalibration. | Quarantine-only, descriptive source record. |
| Dashboard | `GBR_EAW_MOJ_FAMILY_DASH_2026Q1`, Power BI entry HTML SHA-256 `52d356701a10ac6519da61d82ecf3f0cb0e04921597f19a4df6fe721687ac63f` | England and Wales Ministry of Justice visualisation tool | Aggregate visible view is evidenced, but the bound HTML shell does not establish the required numeric value or a frozen export. | Acquisition-only until a source-faithful visible/exported value is bound. |
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
| England and Wales dashboard | Required value is not established from the bound entry shell. | Missing source-faithful value and frozen visual/export locator. | Keep acquisition-only; do not infer the ODS value into the dashboard route. |

This matrix is the prepared input for G2-C05. It does not adjudicate methods:
the sole owner must decide whether these quarantine-only dispositions are
accepted for the bounded cohort after the route gaps are resolved or formally
excluded by a separate scope decision.

## Edition assessment envelope

| Edition | Current factual handling | Assessment state | Required completion evidence |
| --- | --- | --- | --- |
| DataJud API response | Aggregate-only response, locally hash-bound; no hit records acquired. | Rights/privacy/security/disclosure assessment incomplete. | Scoped query definition; endpoint/response review; rights and disclosure finding. |
| England and Wales ODS | Locally hash-bound and used only for quarantined extraction. | Rights/privacy/security/disclosure assessment incomplete. | Edition-specific conditions, aggregate/prohibited-data check, local handling and disclosure finding. |
| England and Wales dashboard entry | Locally hash-bound HTML shell; no value extracted. | Rights/privacy/security/disclosure assessment incomplete. | Source-faithful value/export evidence, edition/visual conditions, aggregate/disclosure finding. |
| Australia PDF | Locally hash-bound and used only for quarantined extraction. | Rights/privacy/security/disclosure assessment incomplete. | Edition-specific conditions, aggregate/prohibited-data check, local handling and disclosure finding. |

The owner has authorised local acquisition and processing of this bounded
cohort. That authorisation is recorded operationally; it is not a factual
finding about the editions and does not close G2-C06. Unknown conditions remain
quarantined or metadata-only.

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

