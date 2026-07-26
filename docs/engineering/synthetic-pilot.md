# Heterogeneous synthetic pilot

The synthetic pilot is a reference implementation, not a dataset. Its fictional records exercise five ingestion paths—CSV, JSON records, HTML table, XLSX, and controlled manual transcription from a rendered PDF—through bronze extraction, declarative mapping, combined silver output, eligibility assessment, quarantine, and gold promotion.

Run and verify it with:

```bash
gfjd demo run --output build/demo
gfjd demo verify --output build/demo
```

The expected result is ten accepted synthetic observations and zero quarantined observations. Connector receipts bind every input and output. The manual fixture additionally binds the PDF and companion transcription and preserves page/table/row locators.

A passing synthetic pilot demonstrates pipeline behaviour. It does not demonstrate that any real source has been found, correctly interpreted, legally retained, translated, independently re-extracted, or judged comparable.
