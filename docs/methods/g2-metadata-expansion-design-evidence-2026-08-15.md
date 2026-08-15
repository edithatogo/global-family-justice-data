# G2 metadata-expansion design evidence — 2026-08-15

Status: prepared and source-disabled; sole-owner search-stage decision pending

The repository has prepared a prospectively frozen design for the predeclared
44-to-96 candidate metadata expansion. It preserves the 44-record baseline and
requires exactly 52 non-overlapping additions across four 13-record search
streams. It binds 32 jurisdiction-specific official names, local search terms
and official domains; four query templates; a deterministic 208-query
materialization order; exact language, jurisdiction and year ordering;
preliminary title-only plausibility rules; role separation; budgets; exposure
controls; fail-closed stopping rules and the next owner checkpoint.

The proposed first execution stage is search-index-only. It prohibits opening
or requesting any result URL, visiting official landing pages, requesting a PDF
or file endpoint, issuing `HEAD`, following redirects, persisting verbatim
snippets or source excerpts, extracting target facts, contacting anyone, or
claiming rights, publication, release or G2 passage. The access boundary is a
procedural agent/tool control and is not represented as OS/proxy attestation.

Digest bindings:

- Signed freeze commit: `fd18ca981053e828055f6ca338a94a4050f1fea1`.
- Machine plan:
  `95aee30f7c285b5d32950e87dcb2de56880a24e6d96d5241b1563d24068fdcfa`.
- Query registry:
  `005123dcf521f2c12b7f87f2ad6c3b3792cc262579b9a51bd7b2b1d1b3e5cf8c`.
- Plan schema:
  `0c21b82781d7483882a909bdf0ee124dd349acce9e44363e908ebca8448c70a2`.
- Exact 208-row query manifest:
  `d7419c0bc281ac9e940819d01005a922e2e6612e40ab1b573ba941eee3b8dddc`.
- Search execution-bundle schema:
  `fa179ab2b8409fc6a28aa8043889a35bd7c0cff13d1804628a93801493821edd`.
- Detached expansion-design manifest:
  `68f853669b0700aa17d2e1825b5f4afb062f4e01ca1abdc1ac4beda7376a3a8c`.

This evidence proves only that a source-disabled plan exists and is
machine-validated. It does not authorize metadata execution, landing-page or
source access, establish a 96-candidate frame, or satisfy G2.
