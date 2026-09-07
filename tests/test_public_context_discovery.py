"""Fictional HTML only; never execute network requests."""

import json
import runpy

import pytest


@pytest.fixture
def stage(project_root):
    return runpy.run_path(str(project_root / "scripts/discover_g2_public_context.py"))


@pytest.mark.parametrize(
    "url",
    [
        "http://app.powerbi.com/view?r=x",
        "https://user@app.powerbi.com/view?r=x",
        "https://app.powerbi.com:443/view?r=x",
        "https://app.powerbi.com.evil.invalid/view?r=x",
        "https://app.powerbi.com/reportEmbed?r=x",
        "https://app.powerbi.com/view?r=x&r=y",
        "https://app.powerbi.com/view?r=",
        "https://app.powerbi.com/view?r=x#fragment",
    ],
)
def test_reject_unsafe_view(stage, url):
    with pytest.raises(ValueError):
        stage["validate_url"](url, "view")


@pytest.mark.parametrize(
    "html",
    [
        b'<base href="https://example.invalid/">',
        b'<a href="a" href="b">x</a>',
        b'<a href="a">unfinished',
    ],
)
def test_ambiguous_html(stage, html):
    with pytest.raises(ValueError):
        stage["parse_links"](html, stage["ENTRY"])


def test_release_ranking_and_ambiguity(stage):
    prefix = "https://www.gov.uk/government/statistics/family-court-statistics-quarterly-"
    a, b = prefix + "january-to-march-2020", prefix + "april-to-june-2020"
    assert stage["choose_release"]([(a, ""), (b, ""), (b, "duplicate")]) == b
    with pytest.raises(ValueError):
        stage["choose_release"]([(b + "?x=1", "")])


def test_two_view_identities_stop(stage):
    with pytest.raises(ValueError):
        stage["choose_next"](
            [("https://app.powerbi.com/view?r=a", ""), ("https://app.powerbi.com/view?r=b", "")],
            stage["ENTRY"],
            True,
        )


@pytest.mark.parametrize("failure", ["redirect", "mime", "encoding", "size"])
def test_transport_failure_has_no_followup(stage, monkeypatch, failure):
    calls = []

    class Response:
        status = 302 if failure == "redirect" else 200

        def getheader(self, name, default=None):
            return {
                "Content-Type": "application/json" if failure == "mime" else "text/html",
                "Content-Encoding": "gzip" if failure == "encoding" else "identity",
            }.get(name, default)

        def read(self, limit):
            assert limit == 2000001
            return b"x" * limit if failure == "size" else b"<html></html>"

    class Connection:
        def __init__(self, *args, **kwargs):
            assert kwargs["timeout"] == 30

        def request(self, method, path, headers):
            calls.append((method, path))
            assert set(headers) == {"User-Agent", "Accept-Encoding"}

        def getresponse(self):
            return Response()

        def close(self):
            pass

    namespace = stage["fetch_html"].__globals__
    monkeypatch.setitem(namespace, "PeerBoundHTTPSConnection", Connection)
    monkeypatch.setitem(namespace, "resolve_public_addresses", lambda host: ("8.8.8.8",))
    with pytest.raises(ValueError):
        stage["fetch_html"](stage["ENTRY"], "entry")
    assert len(calls) == 1


def test_checkpoint_refuses_existing_pending_file(stage, tmp_path):
    path = tmp_path / "receipt.json"
    pending = path.with_suffix(".pending")
    pending.write_text("preserve")
    with pytest.raises(FileExistsError):
        stage["checkpoint"](path, {})
    assert pending.read_text() == "preserve"
    assert not path.exists()


@pytest.mark.parametrize("fail", [False, True])
def test_one_shot_receipt_redacts_source_and_stops(stage, tmp_path, fail):
    plan = tmp_path / stage["PLAN"]
    plan.parent.mkdir(parents=True)
    plan.write_text(json.dumps(stage["CONTRACT"]))
    receipt_path = tmp_path / stage["RECEIPT"]
    receipt_path.parent.mkdir(parents=True)
    (tmp_path / "data/raw/files").mkdir(parents=True)
    release = "https://www.gov.uk/government/statistics/family-court-statistics-quarterly-january-to-march-2020"
    view = "https://app.powerbi.com/view?r=FICTIONAL_PRIVATE_RESOURCE"
    responses = [
        f'<a href="{release}">Quarter</a>'.encode(),
        f'<a href="{view}">Dashboard</a>'.encode(),
        b"<html>Fictional private text not to retain</html>",
    ]
    calls = []

    def fetch(url, kind):
        assert json.loads(receipt_path.read_text())["requests"][-1]["state"] == "attempted"
        calls.append((url, kind))
        if fail:
            raise RuntimeError(view)
        return responses[len(calls) - 1]

    result = stage["execute"](tmp_path, "fictional-freeze", fetch)
    assert len(calls) == (1 if fail else 3)
    assert result["request_contract_qualified"] is False
    assert "FICTIONAL_PRIVATE_RESOURCE" not in receipt_path.read_text()
    assert "Fictional private text" not in receipt_path.read_text()
    assert result["state"] == (
        "terminal_stop" if fail else "public_entry_observed_contract_pending"
    )
    with pytest.raises(ValueError, match="already attempted"):
        stage["execute"](tmp_path, "fictional-freeze", fetch)
