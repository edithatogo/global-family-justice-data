"""Fictional supplied metadata input boundaries."""

import json
import traceback

import pytest

from gfjd.federation_metadata import MetadataError, date_label, make_report, parse_json, safe_url


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"\xff",
        b"{",
        b'{"x":1,"x":2}',
        b"NaN",
        b"Infinity",
        b"-Infinity",
        b'"\\u0000"',
        b'"\\ud800"',
        b'"\\u007f"',
        b"[" * 20 + b"0" + b"]" * 20,
        b" " * (1024 * 1024 + 1),
        json.dumps([0] * 1001).encode(),
        json.dumps("a" * 4097).encode(),
        json.dumps([[0] * 1000] * 11).encode(),
    ],
)
def test_strict_json_rejects(raw: bytes) -> None:
    with pytest.raises(MetadataError):
        parse_json(raw)


def test_json_is_supplied_only(monkeypatch) -> None:
    import builtins
    import socket

    def forbidden(*args, **kwargs):
        raise AssertionError("unexpected I/O")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    assert parse_json(b'{"fictional":[null,true,1,1.5,"x"]}') == {
        "fictional": [None, True, 1, 1.5, "x"]
    }


@pytest.mark.parametrize(
    "value",
    [
        "http://example.invalid",
        "https://user@example.invalid",
        "https://example.invalid:99999",
        "https://bad..host/x",
        "https://example.invalid/%xy",
        "https://example.invalid/\x7f",
        "https://example.invalid/a#b#c",
        "https://example.invalid/" + "x" * 4096,
    ],
)
def test_invalid_reference(value: str) -> None:
    with pytest.raises(MetadataError):
        safe_url(value)


def test_safe_reference_and_date() -> None:
    assert safe_url("https://example.invalid:443/path#x") == "https://example.invalid:443/path#x"
    assert date_label("2024-02-29")
    assert not date_label("2026-02-29")
    assert not date_label("20260831")
    assert not date_label(None)


@pytest.mark.parametrize("suffix", ["a[b]", "a?x=[b]"])
def test_raw_brackets_rejected(suffix: str) -> None:
    with pytest.raises(MetadataError):
        safe_url("https://example.invalid/" + suffix)
    assert safe_url("https://example.invalid/a%5Bb%5D")


def test_fixed_traceback() -> None:
    try:
        parse_json(b"FICTIONAL_SECRET_SENTINEL")
    except MetadataError as error:
        rendered = "".join(traceback.format_exception(error))
        assert "JSONDecodeError" not in rendered
        assert rendered.endswith("MetadataError: Metadata profile contract violation\n")


def test_report_is_deterministic_and_has_no_authority() -> None:
    report = make_report("fictional-v1", b"{}", {"b": "2", "a": "1"}, ["b", "a", "b"])
    assert report["issues"] == ["a", "b"]
    assert report["status"] == "profile_incomplete"
    assert not any(report["authority"].values())
    assert make_report("fictional-v1", b"{}", {}, [])["status"] == "profile_complete"
