# Remaining evidence gates

This is the bounded handoff for the single-analyst repository. Agents may
prepare searches, receipts, and draft rows; they must not promote observations
or assert institutional coverage without source and review evidence.

## Queue

1. **Rights review (five high-priority sources).** Record the publisher's
   licence or redistribution terms, retrieval date, and permitted use for each
   source in `data/seed/source_register.csv`.

   Initial official leads (not clearance): Council of Europe requires prior
   permission for reproduction beyond citation/excerpts ([copyright and
   permissions](https://www.coe.int/en/web/portal/copyright-licensing-permissions));
   HCCH publishes separate digital-publication sales terms ([HCCH terms](https://www.hcch.net/en/publications-and-studies/publications2/general-terms-conditions-sale)).
   These links are leads for review, not a licence grant.

   NCSC states that its library materials are copyright-protected and directs
   permission requests to its library ([NCSC permissions guidance](https://www.ncsc.org/ncsc-library-collection-research-hub)).
   WJP publishes a copyright policy and separate terms ([copyright policy](https://worldjusticeproject.org/copyright-policy),
   [terms of service](https://worldjusticeproject.org/terms-service)); these do
   not by themselves establish redistribution rights for the dataset.
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
and traceable. Current baseline: 23 jurisdictions, 0 ready, 23 gaps, all
`DIRECT_ENQUIRY_UNRESOLVED` (the generated census summary is authoritative;
regenerate it after any data change). Twelve enquiries were sent on
2026-07-31; Minnesota awaits CAPTCHA completion and Brazil awaits authenticated
CNJ portal access. Nine other packets await submission through their documented
form-, phone-, postal-, or routing-only official channels.
