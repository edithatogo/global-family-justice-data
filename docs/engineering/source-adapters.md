# Controlled source adapters

International court reporting appears as APIs, structured files, HTML pages, dashboards, spreadsheets, and PDFs. The adapter layer converts reviewed local inputs to source-native bronze tables without allowing source-specific executable code in configuration.

## Supported paths

| Adapter | Intended source | Locator |
|---|---|---|
| `csv` | Delimited official export | Source row number |
| `json_records` | JSON array at a reviewed record path | JSON path and array index |
| `html_table` | Static HTML table | Table index and row number |
| `xlsx` | Workbook table | Sheet and row number |
| `manual_transcription` | PDF or other report requiring human transcription | Mandatory reviewer-entered page/table/row or equivalent locator |

A connector TOML fixes source identity, edition identity, adapter, local input, expected columns, output location, and receipt location. All paths are confined to the repository; remote material must first pass through the rights-aware acquisition layer.

## Manual transcription

The manual path treats the report and transcription as distinct evidence objects. It requires:

- an original report file;
- a UTF-8 CSV transcription;
- a locator column with a nonblank source locator for every row;
- an exact expected-column contract;
- subsequent declarative mapping and ordinary observation validation.

The connector receipt hashes the connector specification, report, transcription, and resulting bronze table. Editing any object after extraction makes verification fail. Independent review should compare sampled or complete transcription rows against the cited report locations; the checksum proves integrity, not transcription accuracy.

## Receipt contract

Each run writes a receipt containing source and edition identifiers, adapter, execution time, paths, SHA-256 digests, row count, source columns, reserved provenance columns, and a canonical content hash. Verification recalculates all available digests and detects missing, modified, or path-escaping objects.

## Deliberate constraints

The adapters do not execute JavaScript, macros, formulas, arbitrary Python, or source-provided code. XLSX values are read in data-only, read-only mode. HTML parsing is table-only. Remote retrieval applies separate URL, redirect, size, protocol, and private-network controls.

Complex dashboards and APIs should be acquired as reviewed exports or represented by a bounded extraction recipe with query/filter provenance. A new adapter should be added only when it can preserve source meaning, locators, deterministic behaviour, and test fixtures.
