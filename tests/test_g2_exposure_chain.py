from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from gfjd.g2_exposure_chain import collect_bound_exposure_chain


def _write(root: Path, name: str, payload: Any) -> dict[str, str]:
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


def test_fails_closed_on_malformed_ledger_content(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{bad", encoding="utf-8")
    descriptor = {
        "path": invalid_json.name,
        "sha256": hashlib.sha256(invalid_json.read_bytes()).hexdigest(),
    }
    _, _, errors = collect_bound_exposure_chain(tmp_path, descriptor)
    assert errors == ["exposure predecessor ledger is invalid JSON"]

    cases = [
        ([], "exposure predecessor ledger must be an object"),
        ({"denied_urls": [1]}, "exposure denied_urls must contain strings"),
        ({"entries": ["bad"]}, "exposure entries must contain objects"),
        ({"entries": [{"url": 1}]}, "exposure entry URL must be a string"),
        ({"entries": [{"urls": [1]}]}, "exposure entry urls must contain strings"),
    ]
    for index, (payload, expected) in enumerate(cases):
        current = _write(tmp_path, f"case-{index}.json", payload)
        _, _, errors = collect_bound_exposure_chain(tmp_path, current)
        assert errors == [expected]


def test_rejects_nonpositive_depth(tmp_path: Path) -> None:
    _, ledgers, errors = collect_bound_exposure_chain(
        tmp_path, {"path": "unused.json", "sha256": "0" * 64}, max_depth=0
    )
    assert ledgers == []
    assert errors == ["exposure predecessor max_depth must be positive"]


def test_fails_closed_on_malformed_url_strings(tmp_path: Path) -> None:
    cases = [
        {"denied_urls": ["http://["]},
        {"entries": [{"url": "http://["}]},
        {"entries": [{"urls": ["http://["]}]},
    ]
    for index, payload in enumerate(cases):
        current = _write(tmp_path, f"url-case-{index}.json", payload)
        _, _, errors = collect_bound_exposure_chain(tmp_path, current)
        assert errors == ["exposure URL is invalid"]
