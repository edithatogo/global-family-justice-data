# Evidence operations calendar

Status date: 2026-08-01  
Operating model: single repository owner with analyst-agent execution

This calendar governs the remaining response-timing, rights, and coverage work. It is an execution control, not an authorization to contact an institution.

## Response timing

The authoritative enquiry records are in `data/census/direct_enquiry_register.csv`. The analyst-agent may inspect the controlled mailbox and record replies without sending anything. For entries sent on 2026-07-31, the recorded follow-up review date is 2026-08-15 and the earliest transparent no-response closure date is 2026-08-30.

At each review date, record one of: substantive response, acknowledgement only, delivery failure, or no response. Acknowledgements do not resolve coverage or rights. A no-response closure must include delivery evidence, the unanswered questions, and the applicable waiting-period date.

Any follow-up, reroute, phone call, postal submission, authenticated-form submission, or CAPTCHA completion requires explicit owner approval immediately before the action. Drafting is permitted; sending is not implied.

## Rights decisions

For every pilot source edition, maintain a rights classification in the source register and evidence note:

1. cleared for the intended use;
2. metadata/citation-only;
3. permission required; or
4. unresolved and excluded from acquisition or redistribution.

The analyst-agent may document publisher terms, attribution requirements, access dates, hashes, and intended-use boundaries. It may not infer a redistribution licence from a general copyright page. Permission requests require a separate owner decision and must identify the exact source, proposed use, and requested rights.

## Coverage packets

The five-candidate pilot packets (INT, AUS, USA-MN, BRA, and ZAF) must contain an institution map, multilingual search log, official source and edition references, scope and period coverage, family-law taxonomy, missingness/access limitations, rights classification, and review-ledger evidence.

Use `complete`, `partial`, `not_started`, `inaccessible`, or `not_applicable` for each coverage dimension. A jurisdiction cannot advance to readiness while any required dimension is unsupported or unresolved. Fail-closed dispositions are descriptive-only, quarantined, or excluded; they are not evidence of comparability.

## Review cycle

1. Before 2026-08-15: analyst-agent performs read-only mailbox checks and closes documentation gaps in the five packets.
2. On 2026-08-15: reassess responses and present any follow-up decisions to the owner; do not send automatically.
3. On 2026-08-30: close eligible non-responses transparently, or present exceptional escalation decisions to the owner.
4. After each evidence change: run strict validation, rebuild and verify the census, regenerate and verify `MANIFEST.sha256`, and record the review ledger entry.

Readiness remains fail-closed until source-backed coverage, rights classification, and review evidence are complete.
