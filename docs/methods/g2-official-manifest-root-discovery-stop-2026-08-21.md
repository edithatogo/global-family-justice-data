# G2 official-manifest-root discovery stop — 2026-08-21

## Scope and authority

This bounded metadata-only discovery was run under the owner's 2026-08-21
direction to proceed with the recommended official publication-manifest route.
The endpoint set was derived deterministically from official hosts in the
checked-in source register: each distinct host received at most two requests,
`/robots.txt` and `/sitemap.xml`.

No registered source URL, result URL, landing page, source file or other
locator was requested. Redirects were disabled; response bodies were neither
persisted nor interpreted. No contact, extraction, rights acceptance,
publication, release or G2 decision occurred.

## Receipt

- Receipt:
  `data/methods/g2/G2OFFICIAL-MANIFEST-ROOT-DISCOVERY-20260821-01/discovery-receipt.json`
- SHA-256:
  `9f583a5888b1af7739a7c8e871efbc81582d596a9b849633e8687120f7de033a`
- Bounded endpoints: **30** across distinct official hosts.
- Source register SHA-256:
  `16023b6b560c141bb81be13b23f061481aa5b598ead7a24db4cff1f327c9fa4e`.

## Terminal result

The discovery stopped fail-closed. Four endpoints breached the frozen
metadata boundary:

| Endpoint class | Count | Outcome |
| --- | ---: | --- |
| Oversized sitemap response | 2 | No parsing, storage or follow-up |
| Redirect response | 2 | Redirect not followed |

The remaining receipt entries are endpoint metadata only. No candidate,
manifest root, source edition or factual evidence is promoted from this run.
The result does not demonstrate source exhaustion; it only closes this exact
30-endpoint attempt.

## Next boundary

No retry, redirect follow, size-limit relaxation, endpoint substitution or
candidate filtering is authorized. A materially changed discovery method would
need a new bounded owner decision before any external activity.
