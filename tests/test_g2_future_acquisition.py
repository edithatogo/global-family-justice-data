from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from gfjd.g2_future_acquisition import G2FutureAcquisitionError, acquire_exact_url


class FakeResponse:
    def __init__(self, status: int, headers: Mapping[str, str], body: bytes = b"") -> None:
        self.status = status
        self.headers = headers
        self._body = body
        self._offset = 0

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = len(self._body) - self._offset
        result = self._body[self._offset : self._offset + size]
        self._offset += len(result)
        return result

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeTransport:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, object]]] = []

    def __call__(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


def public_resolver(host: str, port: int) -> list[str]:
    assert host in {"official.example", "files.example"}
    assert port == 443
    return ["93.184.216.34"]


def test_acquires_with_manually_validated_redirect_and_deterministic_receipt(
    tmp_path: Path,
) -> None:
    start = "https://official.example/edition"
    final = "https://files.example/edition.json"
    body = b'{"aggregate": 7}\n'
    transport = FakeTransport(
        [
            FakeResponse(302, {"Location": final}),
            FakeResponse(
                200,
                {
                    "Content-Type": "application/json; charset=utf-8",
                    "Content-Length": str(len(body)),
                },
                body,
            ),
        ]
    )

    receipt, payload, receipt_path = acquire_exact_url(
        url=start,
        exact_url_allowlist=[start, final],
        destination_root=tmp_path / "controlled",
        output_name="edition.json",
        transport=transport,
        resolver=public_resolver,
    )

    assert payload.read_bytes() == body
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt
    assert receipt["final"] == {
        "url": final,
        "content_type": "application/json",
        "byte_count": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    assert [call[0] for call in transport.calls] == [start, final]
    assert all(call[1]["method"] == "GET" for call in transport.calls)
    assert all(call[1]["follow_redirects"] is False for call in transport.calls)
    assert len(receipt["hops"]) == 2  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "url,match",
    [
        ("http://official.example/a", "HTTPS"),
        ("https://user:secret@official.example/a", "userinfo"),
        ("https://official.example/a#fragment", "fragments"),
        ("https://OFFICIAL.example/a", "canonical"),
    ],
)
def test_invalid_initial_target_fails_before_request_or_write(
    tmp_path: Path, url: str, match: str
) -> None:
    transport = FakeTransport([])
    with pytest.raises(G2FutureAcquisitionError, match=match):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path / "does-not-exist",
            output_name="out.bin",
            transport=transport,
            resolver=public_resolver,
        )
    assert transport.calls == []
    assert not (tmp_path / "does-not-exist").exists()


def test_private_address_fails_before_request(tmp_path: Path) -> None:
    url = "https://official.example/a"
    transport = FakeTransport([])
    with pytest.raises(G2FutureAcquisitionError, match="not public"):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path / "out",
            output_name="a.json",
            transport=transport,
            resolver=lambda _host, _port: ["127.0.0.1"],
        )
    assert transport.calls == []


def test_redirect_outside_allowlist_stops_without_second_request(tmp_path: Path) -> None:
    start = "https://official.example/a"
    transport = FakeTransport([FakeResponse(302, {"Location": "https://files.example/b"})])
    with pytest.raises(G2FutureAcquisitionError, match="outside exact allowlist"):
        acquire_exact_url(
            url=start,
            exact_url_allowlist=[start],
            destination_root=tmp_path,
            output_name="a.json",
            transport=transport,
            resolver=public_resolver,
        )
    assert len(transport.calls) == 1
    assert not (tmp_path / "a.json").exists()


def test_rejects_content_type_and_declared_or_streamed_oversize(tmp_path: Path) -> None:
    url = "https://official.example/a"
    cases = [
        (FakeResponse(200, {"Content-Type": "image/png"}, b"x"), "content type"),
        (
            FakeResponse(200, {"Content-Type": "application/json", "Content-Length": "9"}),
            "declared content length",
        ),
        (FakeResponse(200, {"Content-Type": "application/json"}, b"123456789"), "byte limit"),
    ]
    for index, (response, match) in enumerate(cases):
        with pytest.raises(G2FutureAcquisitionError, match=match):
            acquire_exact_url(
                url=url,
                exact_url_allowlist=[url],
                destination_root=tmp_path,
                output_name=f"out-{index}.json",
                transport=FakeTransport([response]),
                resolver=public_resolver,
                max_bytes=8,
            )
        assert not (tmp_path / f"out-{index}.json").exists()


def test_output_path_escape_and_bad_limits_fail_before_request(tmp_path: Path) -> None:
    url = "https://official.example/a"
    transport = FakeTransport([])
    with pytest.raises(G2FutureAcquisitionError, match="plain filename"):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path,
            output_name="../escape.json",
            transport=transport,
            resolver=public_resolver,
        )
    with pytest.raises(G2FutureAcquisitionError, match="max_redirects"):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path,
            output_name="safe.json",
            transport=transport,
            resolver=public_resolver,
            max_redirects=11,
        )
    assert transport.calls == []


def test_existing_output_fails_before_request_and_is_not_overwritten(tmp_path: Path) -> None:
    url = "https://official.example/a"
    payload = tmp_path / "a.json"
    payload.write_bytes(b"preserve")
    transport = FakeTransport([])
    with pytest.raises(G2FutureAcquisitionError, match="already exists"):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path,
            output_name="a.json",
            transport=transport,
            resolver=public_resolver,
        )
    assert payload.read_bytes() == b"preserve"
    assert transport.calls == []


def test_receipt_write_failure_removes_unbound_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    url = "https://official.example/a"
    transport = FakeTransport([FakeResponse(200, {"Content-Type": "application/json"}, b"{}")])

    def fail_write(_path: Path, _value: object) -> None:
        raise OSError("fictional receipt failure")

    monkeypatch.setattr("gfjd.g2_future_acquisition.write_json", fail_write)
    with pytest.raises(OSError, match="fictional receipt failure"):
        acquire_exact_url(
            url=url,
            exact_url_allowlist=[url],
            destination_root=tmp_path,
            output_name="a.json",
            transport=transport,
            resolver=public_resolver,
        )
    assert not (tmp_path / "a.json").exists()
    assert not (tmp_path / "a.json.receipt.json").exists()
