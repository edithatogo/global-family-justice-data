# Fresh M07/M10 local observations — 2026-09-05

Actual execution produced two byte-identical candidate product manifests and
verified both builds plus a fresh local copy without errors. Existing static
accessibility checks passed. The fresh receipt is
`g2-l2-fresh-local-checks-2026-09-05.json`; it does not recreate the missing
August receipts or accept a maturity level.

The input source commit is `f0ccb5e63ce5c48ef793b5e1f861f70c38191d32`.
The generated catalogue records SHA-256 for all 25 input CSVs. Both builds
use the repository-native product builder, its fixed epoch of zero, and
different new output directories. They share an interpreter and source tree;
this is a determinism observation, not independent execution assurance.
The third check copies the first bundle locally and re-verifies it; it does
not establish hosted availability or provider-separated retrieval.

## Executed operations

From the repository root with the locked environment, `uv run python` invoked:

```python
from pathlib import Path
import shutil
from gfjd.products import build_products, verify_products

root = Path.cwd()
base = root / "build/fresh-l2-20260905-agent"
assert not base.exists()
a = build_products(root, base / "a")
b = build_products(root, base / "b")
assert a.manifest.read_bytes() == b.manifest.read_bytes()
shutil.copytree(base / "a", base / "retrieved")
assert all(not verify_products(root, base / name)
           for name in ("a", "b", "retrieved"))
```

This exact output directory already exists following execution. A later
repeat must use a new directory and record its actual source commit; do not
overwrite the retained observation.

The metadata check read the existing jurisdiction register and census search
log using `csv.DictReader`. It counted rows by `review_status` and
`result_state`, tested empty `search_languages` and `language` fields, and
compared the two sets of jurisdiction IDs. No network requests or source
document access were used. All 23 jurisdictions have declared languages and
at least one logged search; all 245 search rows have a language label and a
registered jurisdiction. However, 171 rows remain draft, 168 record
inaccessible sources, and two record incomplete searches. Labels such as
"Multiple" and "regional languages" do not identify a completed review.

## Requirements against actual evidence

| Dimension requirement | Observation | Remaining work |
| --- | --- | --- |
| M07 reproducible candidate product | Two equal manifests; six bound artifacts plus manifest; three successful verifications | Review this scoped observation; obtain separate execution evidence if required by acceptance contract |
| M07 accessible product | Seven existing static markers checked | Browser, keyboard, reflow and assistive-technology or user evidence is not supplied by these checks |
| M07 available public product | Fresh local copy verified | Hosted publication and anonymous/provider-separated retrieval receipts |
| M10 language and jurisdiction metadata | 23 jurisdiction records and 245 search rows checked | Resolve incomplete/inaccessible searches; exact source-language review and authoritative triangulation |
| M10 sustainability | Existing owner commitment remains separate evidence | Review the exact commitment and scope alongside factual language evidence; this run creates no funding or service commitment |

Recommendation: retain this current evidence as bounded support, continue
automated browser testing where a local runtime is available, and use the
existing authorized editions for an actual language review when their bytes
are available. Keep unresolved requirements explicit in the maturity matrix.
This report is agent advice and automation evidence; it is not native,
specialist, human-participant or independent assurance.
