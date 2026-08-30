# GOV.UK API interface qualification

Repository preparation; not an execution contract or G2 acceptance. Plan commit:
`358046a`. Primary evidence is the official `alphagov/search-api` repository at
commit `a6b92bc1dc36b1081835f44a10eaecf18f651a32`, read on 2026-08-31 Brisbane time.
Exact document fingerprints are recorded in
`data/methods/g2-repro/api-interface-evidence-2026-08-31.json`.
Only technical documentation/code was read; documentation example queries were
not executed. No court metadata query, candidate page or statistical source file
was opened.

## Established interface facts

1. Repeated `fields=x&fields=y` is explicitly supported, as is array-style
   syntax. Repeated filter values are alternatives within a field, while
   different filter fields combine conjunctively. The predecessor's repeated
   parameters must not be called malformed on the basis of the failed receipt.
   [Official usage documentation](https://github.com/alphagov/search-api/blob/a6b92bc1dc36b1081835f44a10eaecf18f651a32/docs/using-the-search-api.md).
2. The result presenter filters requested content fields, then adds `index`,
   `es_score`, `_id`, `elasticsearch_type` and `document_type`. The set presenter
   returns `results`, `total`, `start`, an aggregate-name member (normally
   `aggregates`), `suggested_queries`, `suggested_autocomplete` and `es_cluster`.
   Query/debug options can add further fields. These facts establish that an
   exact three-key root and exact four-key row are incompatible with this
   implementation. They do not establish actual historical response keys.
   [Result presenter](https://github.com/alphagov/search-api/blob/a6b92bc1dc36b1081835f44a10eaecf18f651a32/lib/search/presenters/result_presenter.rb),
   [set presenter](https://github.com/alphagov/search-api/blob/a6b92bc1dc36b1081835f44a10eaecf18f651a32/lib/search/presenters/result_set_presenter.rb).
3. `public_timestamp` denotes an update time; `first_published_at` denotes
   first publication. Neither a last-update date nor chronological ordering
   proves first publication of an exact edition. The field catalogue's meaning
   is not evidence that a particular result supplies a reliable non-null date.
   `format` is a broad classification, not an edition-identity guarantee;
   `link` is not universally guaranteed to be a GOV.UK-relative path.
   [Field definitions](https://github.com/alphagov/search-api/blob/a6b92bc1dc36b1081835f44a10eaecf18f651a32/config/schema/field_definitions.json).
4. `count` bounds returned rows (documented maximum 1500); `start` is a
   zero-based offset. The presenter obtains `total` from search hit counts.
   Therefore a single page is not complete just because it respects `count`:
   retain `start=0`, exact total/row-count equality, duplicate checks and the
   separately frozen cap. These checks concern the API result set, not proof
   that all court publications exist in its index. Do not increase the project's 100-row cap merely
   because the API allows more. Date filtering is inclusive and assumes UTC
   without a timezone; freeze explicit boundaries rather than infer them.
   [Parameter parser](https://github.com/alphagov/search-api/blob/a6b92bc1dc36b1081835f44a10eaecf18f651a32/lib/parameter_parser/search_parameter_parser.rb)
   and usage documentation above.

## Limits and preserved evidence

This is version-pinned publisher code, not proof of the deployed version at
the failed request or a live response conformance test. No failed raw response
was retained. Its actual extra keys and precise rejection causes remain unknown.
The terminal receipt, consumed attempt, frozen evaluator, original bundle and
all exposure records are unchanged. No historical run is repaired or promoted.

Any future-edition route using `public_timestamp` must treat it as update-time
screening only. It must not confer post-cutoff first-publication eligibility
without separate explicit first-publication and edition-identity evidence.
Existing frozen monitor artifacts are not rewritten by this finding; their
outputs cannot satisfy that missing evidence. Existing bounded historical
reproducibility remains distinct from a project-unseen or future-edition claim.

## Options, recommendation and contingencies

- Documentation-only qualification (this slice): establishes interface facts
  without spending another metadata request, but cannot produce candidates.
- **Recommended next:** implement a separate versioned, synthetic-tested
  successor contract. Separate semantic fields from documented incidental
  presenter fields; bound but never retain or select on incidental values.
  Unknown fields stop with structural diagnostics only. Do not infer types or
  non-null guarantees just because a presenter assigns a key.
- Reject widening/reusing the failed evaluator or substituting the monitor:
  neither provides a prospective contract or resolves publication semantics.

The successor must explicitly declare whether its date window is update-time
or first-publication-time. For first publication, require explicit evidence;
missing or ambiguous evidence must not fall back to `public_timestamp`.
Freeze the exact endpoint, request fields, schema, caps, cumulative exposure,
safe retention, diagnostic policy, fresh roles and terminal stops before one
grouped metadata-only execution approval. No request is authorized here.
If deployed schema differs, stop; no retry, arbitrary-key acceptance, broader
logging, pagination, selection or returned-link access follows automatically.

Resource estimate for next repository-only slice: one small pure evaluator,
synthetic contract/boundary tests and a separate advisory review; no source
storage or external execution budget. Any request packet must state its own
exact limits. G2-C04/C07, M06 and all publication/release gates remain blocked.

## Role-separated advisory review

`api_contract_advice` reviewed local controls and the primary-source facts
supplied by the orchestrator without network or source access. It recommends
the distinct contract, agrees that repeated parameters are valid, and requires
update/first-publication separation. It cautions that assigned keys do not
guarantee non-null values and source code is not deployed-version evidence.
No dissent from the recommended direction; deployed shape and actual date
evidence remain unknown. This is agent advice, not independent assurance.
