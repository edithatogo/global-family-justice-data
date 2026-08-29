import importlib.util
import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def _load_monitor():  # noqa: ANN202
    script = Path(__file__).parents[1] / "scripts/g2_official_publication_feed_monitor.py"
    spec = importlib.util.spec_from_file_location("g2_official_publication_feed_monitor", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


monitor = _load_monitor()


def test_frozen_contract_is_a_single_page_official_index(project_root: Path) -> None:
    contract = json.loads(
        (project_root / "config/g2_official_publication_feed_monitor.json").read_text(
            encoding="utf-8"
        )
    )
    parsed = urlparse(contract["endpoint"])
    query = parse_qs(parsed.query)
    assert (parsed.scheme, parsed.netloc, parsed.path) == (
        "https",
        "www.gov.uk",
        "/api/search.json",
    )
    assert "q" not in query
    assert query["count"] == [str(contract["endpoint_count"])]
    assert query["start"] == ["0"]
    assert query["order"] == ["public_timestamp"]
    assert set(query["filter_format"]) == set(contract["eligible_formats"])
    assert query["filter_part_of_taxonomy_tree"] == ["fae66b20-eacd-4a41-a417-81cae5fa4b8c"]


class _Response:
    status = 200

    def __init__(self, body: bytes, endpoint: str) -> None:
        self._body = body
        self._endpoint = endpoint
        self.headers = self

    def __enter__(self):
        return self

    def __exit__(self, *args):  # noqa: ANN002
        return None

    def read(self, _limit: int) -> bytes:
        return self._body

    def geturl(self) -> str:
        return self._endpoint

    def get_content_type(self) -> str:
        return "application/json"


class _Opener:
    def __init__(self, response: _Response) -> None:
        self.response = response
        self.calls = 0

    def open(self, _request, *, timeout: int):  # noqa: ANN001, ANN201, ARG002
        self.calls += 1
        return self.response


def test_monitor_writes_complete_no_candidate_receipt(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    endpoint = "https://www.gov.uk/api/search.json?count=100&start=0"
    exposure = tmp_path / "exposure.json"
    exposure.write_text('{"exposure":{"urls":[]}}\n', encoding="utf-8")
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "campaign_id": "TEST",
                "exposure_cutoff": "2026-08-29T05:17:40Z",
                "endpoint": endpoint,
                "allowed_endpoint_host": "www.gov.uk",
                "allowed_endpoint_path": "/api/search.json",
                "endpoint_count": 100,
                "request_timeout_seconds": 10,
                "maximum_response_bytes": 1024,
                "allowed_locator_hosts": ["www.gov.uk"],
                "allowed_link_prefixes": ["/government/statistics/"],
                "eligible_formats": ["official_statistics"],
                "minimum_candidate_count": 2,
                "cumulative_exposure_sources": [str(exposure)],
            }
        ),
        encoding="utf-8",
    )
    response = _Response(b'{"total":0,"results":[]}', endpoint)
    opener = _Opener(response)
    monkeypatch.setattr(monitor.urllib.request, "build_opener", lambda *_args: opener)
    output = tmp_path / "output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "monitor",
            "--contract",
            str(contract),
            "--output",
            str(output),
            "--checked-at",
            "2026-08-29T08:00:00Z",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "test-1",
        ],
    )

    assert monitor.main() == 0
    assert opener.calls == 1
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "complete"
    assert receipt["summary"]["outcome"] == "monitor_no_candidates"
    assert receipt["boundary"]["result_url_access"] is False


def test_monitor_stops_on_incomplete_single_page(tmp_path: Path, monkeypatch) -> None:  # noqa: ANN001
    endpoint = "https://www.gov.uk/api/search.json?count=1&start=0"
    exposure = tmp_path / "exposure.json"
    exposure.write_text('{"exposure":{"urls":[]}}\n', encoding="utf-8")
    contract = tmp_path / "contract.json"
    contract.write_text(
        json.dumps(
            {
                "campaign_id": "TEST",
                "exposure_cutoff": "2026-08-29T05:17:40Z",
                "endpoint": endpoint,
                "allowed_endpoint_host": "www.gov.uk",
                "allowed_endpoint_path": "/api/search.json",
                "endpoint_count": 1,
                "request_timeout_seconds": 10,
                "maximum_response_bytes": 1024,
                "allowed_locator_hosts": ["www.gov.uk"],
                "allowed_link_prefixes": ["/government/statistics/"],
                "eligible_formats": ["official_statistics"],
                "minimum_candidate_count": 2,
                "cumulative_exposure_sources": [str(exposure)],
            }
        ),
        encoding="utf-8",
    )
    response = _Response(b'{"total":2,"results":[]}', endpoint)
    monkeypatch.setattr(monitor.urllib.request, "build_opener", lambda *_args: _Opener(response))
    output = tmp_path / "output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "monitor",
            "--contract",
            str(contract),
            "--output",
            str(output),
            "--checked-at",
            "2026-08-29T08:00:00Z",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "test-2",
        ],
    )

    assert monitor.main() == 2
    receipt = json.loads((output / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "terminal_failure"
    assert receipt["error"] == "incomplete single-page enumeration"
