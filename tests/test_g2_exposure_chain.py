from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_exposure_chain import collect_bound_exposure_chain


def _write(root: Path, name: str, payload: dict[str, Any]) -> dict[str, str]:
    path = root / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def test_collects_complete_bound_predecessor_chain(tmp_path: Path) -> None:
    oldest = _write(
        tmp_path,
        "oldest.json",
        {"denied_urls": ["https://EXAMPLE.test/old#fragment"], "entries": []},
    )
    current = _write(
        tmp_path,
        "current.json",
        {
            "entries": [{"landing_page_url": "https://example.test/current"}],
            "predecessor": oldest,
        },
    )

    urls, ledgers, errors = collect_bound_exposure_chain(tmp_path, current)

    assert errors == []
    assert urls == {"https://example.test/current", "https://example.test/old"}
    assert ledgers == [current, oldest]


def test_fails_closed_on_tampered_or_unsafe_predecessor(tmp_path: Path) -> None:
    tampered = _write(
        tmp_path,
        "current.json",
        {"entries": [], "predecessor": {"path": "missing.json", "sha256": "0" * 64}},
    )
    _, _, errors = collect_bound_exposure_chain(tmp_path, tampered)
    assert errors == ["exposure predecessor binding mismatch"]

    _, _, errors = collect_bound_exposure_chain(
        tmp_path, {"path": "../outside.json", "sha256": "0" * 64}
    )
    assert errors == ["exposure predecessor binding mismatch"]


def test_fails_closed_at_depth_limit(tmp_path: Path) -> None:
    oldest = _write(tmp_path, "oldest.json", {"entries": []})
    current = _write(
        tmp_path,
        "current.json",
        {"entries": [], "predecessor": oldest},
    )

    _, ledgers, errors = collect_bound_exposure_chain(tmp_path, current, max_depth=1)

    assert ledgers == [current]
    assert errors == ["exposure predecessor chain exceeds maximum depth"]
