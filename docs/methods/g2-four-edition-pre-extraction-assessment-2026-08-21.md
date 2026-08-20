# G2 four-edition pre-extraction assessment — 2026-08-21

This assessment turns the locally acquired four-route pilot into a bounded
formal-extraction scope. It is a preparation record, not an extraction result,
methods decision, or G2 acceptance.

## Frozen input set

The source bytes and aggregate API response are locally held under
`build/g2-real-pilot-20260821-01/sources/`; their source hashes are recorded in
the [acquisition evidence](./g2-four-edition-acquisition-evidence-2026-08-21.md).
The acquisition metadata has SHA-256
`a272bcaaa9cc0d605d103c67769fddc22aba2f0362f72f1b146db1d74d1f5375`.

## Candidate targets

| Route | Proposed target | Exact locator | Readiness |
| --- | --- | --- | --- |
| England and Wales ODS | Public-law orders applied, Q1 2026, England and Wales: **4,917** | `Table_2`, row for `2026 / Q1`, public-law `Total orders applied for` column | Ready for formal extraction. |
| England and Wales dashboard | The same public-law orders-applied Q1 2026 total: **4,917** | Volumes page; Type `Orders applied for`; Period `Annually`; all regions; 2026 column in the aggregate total row | Ready as a same-series cross-format reconciliation target, provided each extraction records visible filters and access time. |
| Australia PDF | Original-jurisdiction total filings, 2024–25: **2,555** | PDF page 102 / printed page 83, `Table 3.3.1(a): total filings by application type, 2024–25` | Ready for formal extraction. |
| DataJud TJSP API | No indicator target selected | Aggregate-only snapshot has 20 unfiltered class-code buckets and zero hits | Acquisition-only. A future extraction must bind a documented family-justice class or other aggregate filter before requesting a new response. |

## Formal extraction rules

1. Use the ODS, dashboard and PDF rows above as a three-row known-source
   calibration packet. Treat the ODS/dashboard pair as cross-format
   reconciliation, not independent corroboration.
2. Preserve the exact source labels, locators, time basis, counted entity and
   any ambiguity in the atomic row contract. Keep each row quarantined.
3. Produce two separately digest-bound extraction outputs before running the
   existing strict concordance comparator. No value or source is promoted if a
   critical field differs.
4. Do not include the DataJud snapshot in that packet. It is valid
   aggregate-only acquisition evidence but lacks a packet-bound substantive
   scope.

## Limits

This three-row packet would demonstrate a bounded known-source calibration
only. It cannot establish global coverage, a project-unseen holdout, source
rights, release readiness or G2 passage.
