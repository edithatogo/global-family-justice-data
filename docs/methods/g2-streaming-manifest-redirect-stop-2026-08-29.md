# G2 streaming manifest redirect stop — 2026-08-29

Evidence ID: `E-G2-STREAMING-MANIFEST-REDIRECT-STOP-20260829`

The successor skipped the 35 precisely pre-cutoff GOV.UK child manifests and
requested the first timestamp-uncertain New Zealand child. It returned a 301
redirect to a trailing-slash URL, terminating the lineage. Two later requests
were execution-order defects and are quarantined as out-of-lineage observations;
none of the redirects was followed and no response body, locator or candidate
document was opened. The lineage stopped before eligibility. This establishes
the exact canonical endpoint correction needed by a future lineage; it does
not authorize or perform a retry.
