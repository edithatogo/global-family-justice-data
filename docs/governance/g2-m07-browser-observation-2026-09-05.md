# M07 local browser observation — 2026-09-05

Role-separated analyst-agent execution used Playwright CLI 0.1.19 and Chrome
152.0.7977.76 against a newly built candidate product served only on loopback.
This narrows the browser-evidence gap. It is neither a WCAG conformance audit
nor assistive-technology, lived-experience, hosted-availability or G2 acceptance.

The base Git commit was `af75e03e1a3a6175c8b37f67a40de72a474e363c`.
The post-fix `src/gfjd/products.py` SHA-256 was
`c8c934fe7991ec679c9cc9a2d001283b92768aaa7c75512c31432ffd32cd77bf`.
Pre-fix generated HTML SHA-256 was
`b4d147e810822d1f0c2eb72e635f2c315bc1f3332c9b32502a30bad6a64fe69c`;
post-fix HTML SHA-256 was
`1f106ae65dbcc5615e0c21f9e4f21462341f19f282705ea8d69c91518fed9061`.
The fresh post-fix product manifest SHA-256 was
`f4b35f32f21f2da083faa3811e777e95b6bc37489a58a774e888baa9dff559ab`.
This binds a working-tree change explicitly rather than representing the base
commit as containing that change.

## Executed findings

| Check | Actual observation | Disposition |
| --- | --- | --- |
| Keyboard focus | All four links were reachable in document order; each had `:focus-visible` and native `rgb(0, 95, 204) auto 1px` outline | Passed in this Chrome configuration |
| Skip link before fix | Enter set `#main`, but active element remained BODY; next Tab reached `catalogue.json` | Corrected explicit focus transfer |
| Skip link after fix | Adding `tabindex='-1'` to main made Enter focus MAIN with id `main`; next Tab reached `catalogue.json` | Passed on fresh build |
| Narrow reflow | At 1280, 640 and 320 CSS-pixel viewport widths, document scroll width equalled client width | No horizontal page overflow observed |
| Structure and names | One main; H1 then H2; named support/corrections navigation; English language; no unnamed links | Passed bounded structure check |
| Reduced motion | Emulated reduce preference was true and active animation count was zero | No motion to disable |
| Local destinations | Catalogue, definitions and corrections returned HTTP 200 with JSON/Markdown media types | Resources available locally |
| Active dependencies | No script, iframe, object, embed or linked stylesheet in document | No active third-party dependency observed |
| CSP | No CSP meta policy in the generated page; loopback server supplied no policy | Hosted CSP enforcement remains untested |

No forms or data tables exist in this landing page, so form errors and table
semantics were not exercised. Width reduction is a reflow check, not an actual
200%/400% browser-zoom measurement. Screen-reader announcements, colour/contrast
conformance, forced colours, other browsers and user task success remain
unassessed. Definitions and corrections are raw Markdown resources, not a
rendered support interface. The only browser console error observed was the
local server's missing favicon (404).

## Reproduction

Build into a fresh output directory rather than overwriting this observation:

```sh
uv run python -m gfjd products build --output build/m07-browser-repeat
uv run python -m gfjd products verify --output build/m07-browser-repeat
uv run python -m http.server 8874 --bind 127.0.0.1 --directory build/m07-browser-repeat
```

In another terminal, use the installed Playwright CLI or its skill wrapper to
open `http://127.0.0.1:8874/`, then capture a snapshot. Press Tab, Enter and Tab;
inspect `document.activeElement` after each operation. Resize to widths 1280,
640 and 320 (height 800) and compare `document.documentElement.scrollWidth`
with `document.documentElement.clientWidth`. Emulate reduced motion and inspect
`document.getAnimations().length`. Only request the three relative destinations
named above. Retain new build hashes and browser/tool versions on each repeat.

The regression test parses the generated HTML and requires the first link to
target the single main landmark with negative tabindex, allowing fragment focus
without adding main to the ordinary tab sequence. The product verifier requires
the same focusable main marker. All three product tests passed, and the newly
built bundle verified. Existing static checks remain complementary evidence.

## Advice

Recommended: use this as bounded M07 automation support and retain broader
accessibility qualification in review. Next test the actual hosted Explorer
when its deployment is available, because the portable landing page cannot
establish that application's behaviour. A full accessibility assertion would
require substantially broader assessment. If that product remains unavailable,
keep the current evidence scoped to the local portable catalogue.
