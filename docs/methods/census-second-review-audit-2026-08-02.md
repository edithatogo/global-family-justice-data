# Census second-review readiness audit (advisory)

**As of:** 2026-08-02  
**Scope:** 23 jurisdiction coverage assessments and institution mappings in
`data/census/`.  
**Purpose:** identify evidence required before a second review or readiness
promotion. This is an agent audit, not local verification, owner adjudication,
or a finding that any jurisdiction is complete.

## Panel verdict

**Blocked for second-review closure.** All 23 coverage rows are `partial` with
`negative_finding_state=not_assessed`. Each institution mapping is marked
`active` but its mapping review is either first-review `changes_required` or
otherwise lacks a completed second-review record. The records are useful draft
inputs and must remain fail-closed.

## Jurisdiction audit

| ID | Current coverage | Map evidence | Missing before second review | Safe disposition |
|---|---|---|---|---|
| INT | partial | official landing page; first review changes required | second mapping review; negative-finding review; completeness and rights evidence | unresolved/conditional |
| AUS | partial | official landing page and acquisition receipt | second mapping review; taxonomy/completeness; rights disposition | unresolved/conditional |
| GBR | partial | official collection/guide | second mapping review; edition completeness; negative-finding review | unresolved/conditional |
| CAN | partial | official downloadable table | second mapping review; participating-jurisdiction coverage; negative-finding review | unresolved/conditional |
| USA | partial | official project page | second mapping review; scope and jurisdiction-level coverage; local confirmation | unresolved/conditional |
| GBR-EAW | partial | official collection/guide | second mapping review; devolved/system boundary; completeness evidence | unresolved/conditional |
| NZL | partial | official justice source | second mapping review; local-language/negative search review; rights evidence | unresolved/conditional |
| SGP | partial | official judiciary source | second mapping review; source-period completeness; negative-finding review | unresolved/conditional |
| CAN-BC | partial | official statistical source | second mapping review; provincial scope and bilingual search evidence | unresolved/conditional |
| USA-CA | partial | official courts source | second mapping review; local coverage and negative-finding evidence | unresolved/conditional |
| USA-MN | partial | pilot-scope/official source evidence | second mapping review; independent re-check; rights and completeness | unresolved/conditional |
| ESP | partial | official judiciary source | second mapping review; Spanish search and period completeness evidence | unresolved/conditional |
| BRA | partial | official statistics source and receipt | second mapping review; Portuguese local verification; access/rights disposition | unresolved/conditional |
| IND | partial | official project/source evidence | second mapping review; state/union-territory scope; multilingual search evidence | unresolved/conditional |
| MEX | partial | official state judiciary source | second mapping review; Spanish local verification; completeness and rights | unresolved/conditional |
| ZAF | partial | official judiciary source and receipt | second mapping review; provincial coverage; local-language/negative-finding evidence | unresolved/conditional |
| JPN | partial | official courts source | second mapping review; Japanese search review; translation and completeness evidence | unresolved/conditional |
| FRA | partial | official justice source | second mapping review; French search review; edition completeness and rights | unresolved/conditional |
| NLD | partial | official data portal | second mapping review; Dutch search review; completeness and licensing evidence | unresolved/conditional |
| SWE | partial | official source plus response receipt | second mapping review; response-to-public-source reconciliation; completeness | unresolved/conditional |
| KEN | partial | official judiciary source | second mapping review; subnational coverage; local-language and access evidence | unresolved/conditional |
| CHL | partial | official judiciary source | second mapping review; Spanish search review; completeness and rights | unresolved/conditional |
| PHL | partial | official judiciary source | second mapping review; local-language search; scope, completeness and rights | unresolved/conditional |

## Cross-cutting blockers

1. **Second review:** the ledger contains first-review `changes_required`
   mapping records; no jurisdiction has a clean second-review disposition.
2. **Negative findings:** every coverage row is `not_assessed`; no inaccessible
   or zero-result search can be promoted without a second reviewer and receipt.
3. **Coverage:** all rows remain `partial`; no completeness or readiness claim
   is supported.
4. **Rights:** official URLs and acquisition receipts do not establish
   redistribution permission; keep restricted material metadata-only.
5. **Local verification:** browser/public-source evidence is not local or
   independent verification. No local verification is claimed here.
6. **Enquiries:** enquiry states and responses remain separate from coverage;
   no-response must use the documented dated closure rules.

## Recommended sequence and contingencies

1. Freeze this audit and the exact census digest.
2. A second panel agent independently re-checks each mapping and coverage row,
   recording evidence references, language and access state.
3. Resolve disagreements through owner adjudication; do not silently overwrite
   first-review findings.
4. Obtain local/regional verification where required. Until then, retain
   `partial`/`unresolved` and readiness zero.
5. Resolve rights per source edition. If unresolved, use metadata-only or
   exclude; never infer a licence from accessibility.
6. Rebuild the census summary and re-run strict validation after real evidence
   is added.

If a reviewer, source or local verifier is unavailable, record a missing report
and keep the row blocked. If an endpoint is inaccessible, record
`source_inaccessible`; it is not evidence of no source. This audit does not
create empirical evidence, local verification, owner adjudication or readiness.
