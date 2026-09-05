# Bounded source-accuracy review and owner acceptance

The repository owner directed acceptance within the approved qualifying scope,
then approved the recommendation to accept only the bounded source-accuracy
review. This record transcribes that conversational owner decision; the agent
performed the review and is not the accountable decision-maker.

## Exact evidence binding

- Contract: `data/methods/g2-swe-aus-freeze-20260905.json`, SHA-256
  `808318acb41fe055b3ff2c7b8e9bc352fa64bae1f40a1b0485bbe3c3f07d5398`.
- Retained Agent A output: SHA-256
  `1dbca17e12dec0c1c10900b20669ff13c76ab7120c54367d77d0e971637ebaa4`.
- Swedish source: SHA-256
  `47a751d419ffc4861eda29580654cc1a5053a2852f05052e5c387b61c6dceceb`.
- AUS source: SHA-256
  `e251da7a9424aeba5e8c9e53a7f33fc5901769b10e6e0ea27f5b446bc5fd2ee9`.

## Accepted review findings

The reviewing orchestrator independently read Swedish OOXML selected cells
using ZIP/XML parsing and compared them to the retained output: 30 of 30
lexical values matched. Component filings and determinations reconcile to the
respective total rows. The AUS table was read with pdftotext on PDF page 102:
four of four table rows matched, including source labels, counts and percentages.
This is an orchestrator source check, not blinded dual-extractor concordance
or an independent assurance claim. PDF checking used text extraction rather
than a separate visual rendering review.

Swedish context explicitly identifies 2025, district courts and the source
category Övr familjemål. This does not establish all-family-case coverage.
Total rows must remain distinguished from components. AUS context identifies
Division 1 and transfers from Division 2 for final-order receipts; it does not
establish new national case filings. Clearance-rate prose reverses the ratio
consistent with its percentage; that derived measure remains excluded.

## Scope and Conductor disposition

Owner-accepted scope: preliminary source accuracy and descriptive interpretation
of these selected cells/table rows only. Preserve source labels, category,
division and source period context. No standardised date bounds, denominator
equivalence, ontology equivalence or cross-jurisdiction comparability is accepted.
All extracted rows retain quarantine and comparison-ineligible flags.

The terminated two-agent lineage remains immutable failed evidence, with no
Agent B output and no concordance score. Its stop is neither repaired nor
waived. WI-G2-04 and WI-G2-07 acceptance-bearing evidence mappings remain
unchanged; G2 remains blocked. This acceptance grants no Gold, maturity,
rights, publication, release or programme-gate acceptance.

Reopen this scoped acceptance if source/output digests change, transcription
errors are found or authoritative source context contradicts these findings.
It is limited to these exact editions and superseded only by an explicit
decision. The Git commit containing this record supplies its immutable
repository reference; it does not imply a separate personal owner signature.
