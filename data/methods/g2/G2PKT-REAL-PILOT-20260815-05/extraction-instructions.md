# Frozen G2 packet-05 final domain-calibration extraction instructions

Packet ID: `G2PKT-REAL-PILOT-20260815-05`

This is the final calibration rerun for the frozen four-row exercise. Each
assigned analyst agent must independently inspect the four exact source
editions and produce exactly four rows satisfying the atomic row schema, base
semantic contract, packet-03 boundary corrections, packet-04 methods amendment
and packet-05 domain amendment.

Do not inspect any packet 01–04 extraction output, receipt, difference,
comparison or panel report. Do not inspect the other packet-05 extraction
role's output or receipt. Procedural role separation is advisory and does not
create human or institutional independence.

## Exact-source normalization

For every field ending `_source` or `_quote`, transcribe only the bounded source
text; normalize Unicode to NFC; collapse every whitespace run to one ASCII
space; trim outer whitespace; and preserve source case, punctuation, spelling
and Unicode punctuation. Do not paraphrase, translate, repair or infer.

## Final domain rule

`domain_label_source` is the complete lexical text of the nearest enclosing
broader-domain heading not assigned as locator, matter or measure. Exclude
structural section-number tokens and layout-only line breaks. Preserve
subtitles, dashes and every other lexical component.

The mandatory values are:

- AUS: `Court Performance and Statistics – Original Jurisdiction`
- USA-MN: `Timeliness`
- BRA: `Violência contra a Mulher`
- ZAF: `District Courts Court Performance Overview`

If a required value cannot be reproduced, fail the run. Do not substitute,
waive, repair or reinterpret it.

## Prior frozen mappings and uncertainty

All packet-03 corrected mappings and all packet-04 mappings remain mandatory.
In particular, the packet-04 deterministic uncertainty rule permits only:

- `none` when all required source occurrences are legible and no ambiguity code
  is required;
- `unresolved` when a required ambiguity code preserves a source conflict the
  packet does not resolve.

Required uncertainty is AUS `unresolved`, USA-MN `none`, BRA `none`, and ZAF
`unresolved`. Values `low` and `material` are unavailable.

## Dates, values and quarantine

Dates are explicit-only: populate an ISO date only when the exact edition
states it; otherwise preserve the source period label and use `null` with
`not_stated`. Transcribe headline and component values exactly; do not
recalculate or repair source contradictions. Preserve all canonical codes,
denominators, cohort/population bases and ambiguity evidence frozen by the
contracts. AUS and ZAF remain `hard_quarantine`; BRA and USA-MN remain
`quarantine`.

## Frozen source targets

- AUS `ED-AUS-FCFCOA-ANNUAL-2024-25`: PDF p.101–102 / printed p.83–84,
  enclosing section 3.3 and Figure 3.3.2(a).
- USA-MN `ED-USA-MN-MJB-PERF-2024`: PDF/printed p.12 enclosing section 3.2;
  p.14 subsection 3.2.2 and Table 4.
- BRA `ED-BRA-CNJ-JUSTICA-2026`: PDF/printed p.588, Figure 528.
- ZAF `ED-ZAF-JUDICIARY-ANNUAL-2024-25`: PDF p.49–52 / printed p.47–50,
  enclosing court heading and Table 20; PDF p.90 / printed p.88 Annexure C.

The exact byte paths and content digests are packet-bound. No other editions or
pages may supply a fact.

## Output boundary

Write only a four-row JSON array and a digest-bound extraction-run receipt.
Bind the packet, instructions, row schema, source manifests and output digest;
record UTC timestamps, role/session, warnings, limitations and procedural
blinding. Do not make a methods, rights, gate, publication or release decision.

Any packet-05 critical discrepancy terminates this calibration route. No packet
06 is authorized. A pass proves reproducibility only for this frozen exercise;
generalisation requires a prospectively frozen blind holdout on unseen
editions. Public handling remains metadata/citation only.
