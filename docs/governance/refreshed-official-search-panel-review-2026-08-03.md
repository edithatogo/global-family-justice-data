# Refreshed official-search panel review — 2026-08-03

## Scope and evidence boundary

The panel reviewed the refreshed candidate searches in
`build/pilot-official-searches.json` for INT, AUS, USA-MN, BRA and ZAF. These
records establish search leads and access observations only. They do not prove
local verification, completeness, rights, edition identity, or publication
permission.

## Panel synthesis

| Jurisdiction | Candidate lead | Language | Access observation | Recommended next evidence |
|---|---|---|---|---|
| INT | CEPEJ-STAT dynamic database | English | Browser landing page available; shell retrieval previously 403 | Capture exact table/export through an allowed browser route, record version/filters and hash; obtain independent second review |
| AUS | FCFCOA annual reports | English | Landing and annual-report links available | Capture exact report edition and relevant tables; cross-check with an independent official catalogue or archive; record terms |
| USA-MN | Minnesota Judicial Branch court statistics | English | Link available | Capture report/table and period; cross-check with district publication; obtain local interpretation of family-justice scope |
| BRA | CNJ Estatística / statistical panels | Portuguese | Link available | Capture Portuguese source and metadata; second-review translation and indicator definitions; cross-check CNJ panel/export |
| ZAF | South African Judiciary annual reports | English | Link available | Capture exact report and family-court sections; cross-check judiciary catalogue/archive; obtain local scope interpretation |

## Options

**A — dual-route evidence acquisition (recommended).** For each jurisdiction,
capture the official landing page and an exact report/table/export through a
permitted route, then have a separate agent perform a source-language/second
review. This gives resilient provenance while preserving the access boundary.

**B — official-link inventory only.** Record URLs and search receipts without
capturing bytes. Fast, but insufficient for edition-level rights, extraction or
coverage claims.

**C — broaden to secondary sources.** Use reputable mirrors/catalogues only as
discovery or cross-check evidence. They cannot replace the authoritative source
or local verification.

**D — defer inaccessible items.** Retain INT as `source_inaccessible` until an
allowed browser capture or authoritative export is available; keep all other
items candidate-only pending exact-edition review.

## Recommendation and rationale

Adopt **A + D**: proceed with dual-route capture for the four apparently
reachable jurisdictions, while treating INT's 403 as an explicit access issue.
This maximises redundancy without converting a URL into evidence and avoids
overclaiming from a dynamic database or translated indicator.

## Contingencies

- Browser route unavailable or blocked: preserve the 403/access receipt and use
  an official downloadable export, catalogue record, or transparent unresolved
  status; never infer absence.
- Exact edition cannot be identified: retain citation/metadata only and exclude
  derived publication claims.
- Translation or indicator disagreement: keep original-language text, record
  both interpretations, and set `adjudication_required`.
- Primary and redundant sources conflict: preserve both hashes and quarantine
  the affected measure until owner/methods adjudication.
- Rights terms unclear: metadata/citation-only or exclude; no redistribution.
- No local reviewer: keep the jurisdiction descriptive-only and do not promote
  T2/G3 readiness.

## Required receipt fields

Each follow-up must add a search-log row with query, result, language, date,
route, access issue, URL, exact edition/version, MIME, SHA-256 (or explicit
unavailable), extraction filters, reviewer role, second-review status and
limitations. A source lead is not a rights or coverage decision.

No outbound enquiry is authorised by this review; any future contact requires
an exact recipient/message/scope packet and explicit owner approval.
