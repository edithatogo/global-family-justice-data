# G2 prospective successor hardening design — 2026-08-29

Evidence ID: `E-G2-PROSPECTIVE-SUCCESSOR-HARDENING-20260829`

The repository-owned successor design addresses every material finding raised
against the terminal `G2PROSPECTIVE-CALIBRATION-20260829-01` lineage without
repairing, retrying or promoting that failed evidence.

## Implemented controls

1. Provider over-return is no longer confused with incomplete recording. Every
   observed result up to a separately frozen absolute safety cap is recorded as
   exposure; only the requested prefix can enter registration. Truncation and
   automatic retries remain prohibited. The recorder accepts locator-only
   metadata and rejects snippets or arbitrary provider fields.
2. A pre-source interlock must use the exact owner-authorization and preparation
   descriptors frozen in its execution contract. A self-declared replacement
   authorization cannot pass.
3. Exposure collection includes both `content_sha256` and `source_sha256`, the
   repository's established endpoint/definition fields, and generic `*_url`
   locators.
4. Role isolation is an exact matrix. Inputs, prohibited classes, network mode,
   URL allowlists and distinct output prefixes are recomputed for the registrar,
   orchestrator, both extractors, comparator and advisory reviewer.
5. A connected peer must be public and a member of the address set validated
   for the requested hostname. Any DNS rebinding or peer mismatch stops before
   a response body is read; hostname-based TLS verification remains mandatory.

## Options and trade-offs

- **Recommended — bounded complete recording:** retain a requested selection
  limit of 10 and an absolute safety cap of 50. This preserves complete exposure
  evidence for ordinary provider over-return without allowing unbounded memory
  use.
- **Provider-enforced pagination:** preferable where an API contract proves the
  limit, but unavailable as a universal search-provider assumption.
- **Stop on any over-return:** simplest but repeats the predecessor's avoidable
  failure and produces no additional assurance.

Contingency: if a provider returns more than the absolute cap, or cannot expose
the connected peer, stop without truncation, retry or source access and select a
different prospectively frozen provider contract in a new lineage.

## Current boundary

This is design and executable-control evidence only. No query, result URL,
landing page, file, source content or source byte was accessed. No candidate was
registered or selected, and no extraction, comparison, rights decision,
publication, release, maturity promotion or G2 decision occurred.

Before execution, one grouped digest-bound packet must freeze the query
manifest, rebuilt cumulative exposure snapshot, exact role bundles, concrete
peer-reporting transport adapter, resource estimate and terminal rules. External
execution then requires one explicit owner authorization.
