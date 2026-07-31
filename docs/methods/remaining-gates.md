# Remaining evidence gates

This is the bounded handoff for the single-analyst repository. Agents may
prepare searches, receipts, and draft rows; they must not promote observations
or assert institutional coverage without source and review evidence.

## Queue

1. **Rights review (five high-priority sources).** The analyst-agent reviewed
   and recorded public publisher terms on 2026-08-01 in
   `docs/methods/high-priority-source-rights-review-2026-08-01.md` and
   `data/seed/source_register.csv`. The review establishes restricted metadata,
   citation, excerpt, and non-commercial website-use routes, but does not clear
   general redistribution. Edition-level classification and any required
   permission or owner rights adjudication remain open.

   Initial official leads (not clearance): Council of Europe requires prior
   permission for reproduction beyond citation/excerpts ([copyright and
   permissions](https://www.coe.int/en/web/portal/copyright-licensing-permissions));
   HCCH publishes separate digital-publication sales terms ([HCCH terms](https://www.hcch.net/en/publications-and-studies/publications2/general-terms-conditions-sale)).
   These links are evidence of the reviewed restrictions, not a blanket licence
   grant. No permission request was sent; explicit owner approval is required
   immediately before any future outbound request.

   NCSC states that its library materials are copyright-protected and directs
   permission requests to its library ([NCSC permissions guidance](https://www.ncsc.org/ncsc-library-collection-research-hub)).
   WJP publishes a copyright policy and separate terms ([copyright policy](https://worldjusticeproject.org/copyright-policy),
   [terms of service](https://worldjusticeproject.org/terms-service)); these do
   not by themselves establish redistribution rights for the dataset.
   Separately, the exact England and Wales 2026 Q1 Family Court Statistics CSV
   archive has been acquired and bound to an OGL v3 source-edition record. That
   closes acquisition and edition-level rights for this one archive only; it
   does not close taxonomy, missingness, continuity, validation, adjudication,
   or jurisdiction-readiness gates.
2. **Pilot universe.** Populate `data/census/jurisdiction_universe.csv` only
   from approved pilot scope; attach a reviewed coverage assessment for every
   included jurisdiction.
3. **Institution discovery.** Add source-backed rows to
   `data/census/institution_map.csv`; retain the URL, access date, language,
   and evidence reference for every mapping.
4. **Search audit.** Add multilingual searches to
   `data/census/search_log.csv`, including zero-result searches and blocked
   pages.
5. **Direct enquiries.** For each priority enquiry, record sent/answered,
   closed-no-response, or not-required status in
   `data/census/direct_enquiry_register.csv`.
6. **Independent review.** Record the analyst-agent review and any owner
   adjudication in `data/census/review_ledger.csv` before a jurisdiction can
   become ready.

The census harness remains fail-closed until these rows are real, validated,
and traceable. Current baseline: 23 jurisdictions, 0 ready, 45 gaps: 23
`COVERAGE_INCOMPLETE` and 22 `DIRECT_ENQUIRY_UNRESOLVED` (the generated census
summary is authoritative; regenerate it after any data change). Eighteen
enquiries were sent or submitted on 2026-07-31, including the completed
Minnesota and India form routes; Sweden has one substantive answer. Brazil
still requires owner-supplied contact data plus CAPTCHA or authenticated portal
access. Japan, France, and the Netherlands await action through their documented
phone-, postal-, authenticated-form-, or messaging-only official channels. No
new outbound action may occur without explicit owner approval immediately
before sending or submission.
