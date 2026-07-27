# Remaining evidence gates

This is the bounded handoff for the single-analyst repository. Agents may
prepare searches, receipts, and draft rows; they must not promote observations
or assert institutional coverage without source and review evidence.

## Queue

1. **Rights review (five high-priority sources).** Record the publisher's
   licence or redistribution terms, retrieval date, and permitted use for each
   source in `data/seed/source_register.csv`.
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
and traceable. Current baseline: 23 jurisdictions, 0 ready, 138 gaps.
