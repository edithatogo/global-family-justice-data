"""Restricted metadata syntax, using fictional identifiers only."""

import pytest
from rdflib import Literal, URIRef

from gfjd.federation_rdf_input import RDFInputError, parse_metadata

TRIPLE = b'<https://example.invalid/s> <urn:fictional:predicate> "safe" .\n'


def test_literal_and_duplicate_count() -> None:
    graph, count = parse_metadata(TRIPLE * 2)
    assert count == 2 and len(graph) == 1
    assert (
        URIRef("https://example.invalid/s"),
        URIRef("urn:fictional:predicate"),
        Literal("safe"),
    ) in graph


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"{}",
        b'_:b <urn:x:p> "x" .',
        b'<file:///secret> <urn:x:p> "x" .',
        b'<https://bad host> <urn:x:p> "x" .',
        b'<urn:x:s> <urn:x:p> "x"^^<http://www.w3.org/2001/XMLSchema#integer> .',
        b"<urn:x:s> <http://www.w3.org/2002/07/owl#imports> <https://example.invalid/> .",
        b"<urn:x:s> <http://www.w3.org/ns/shacl#targetClass> <urn:x:t> .",
        b'<urn:x:s> <urn:x:p> "\\q" .',
        b'<urn:x:s> <urn:x:p> "\\u0000" .',
        b'<urn:x:s> <urn:x:p> "\\ud800" .',
        b"\xff",
        TRIPLE * 2001,
    ],
    ids=[
        "empty",
        "json",
        "blank",
        "file",
        "space",
        "datatype",
        "import",
        "shape",
        "escape",
        "control",
        "surrogate",
        "utf8",
        "statements",
    ],
)
def test_rejected(
    raw: bytes, caplog: pytest.LogCaptureFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(RDFInputError, match="^RDF metadata input rejected$") as exc:
        parse_metadata(raw)
    assert exc.value.__suppress_context__
    assert not caplog.records
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize(
    "obj",
    [
        "<urn:x:o>",
        '"quoted \\"value\\""',
        '"bonjour"@fr',
        '"text"^^<http://www.w3.org/2001/XMLSchema#string>',
        '"Unicode café"',
    ],
)
def test_supported_objects(obj: str) -> None:
    graph, count = parse_metadata(f"<urn:x:s> <urn:x:p> {obj} .\n".encode())
    assert len(graph) == count == 1


def test_bounds() -> None:
    graph, count = parse_metadata(TRIPLE * 2000)
    assert len(graph) == 1 and count == 2000
    for value in [
        b" " * (1024 * 1024 + 1),
        b"#" + b"a" * 8192,
        b'<urn:x:s> <urn:x:p> "' + b"a" * 4097 + b'" .',
    ]:
        with pytest.raises(RDFInputError):
            parse_metadata(value)


@pytest.mark.parametrize("raw", [None, "text", bytearray(TRIPLE), 1])
def test_wrong_input_type(raw: object) -> None:
    with pytest.raises(RDFInputError):
        parse_metadata(raw)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "iri",
    [
        "relative",
        "urn:missing",
        "http://",
        "https://host/%xx",
        "https://bad..host/x",
        "https://host:99999/x",
        "https://user@host/x",
        "https://host/x#one#two",
        "https://host/\\u0061",
        "https://host/é",
        "https://host/[bad]",
        "https://host/{bad}",
    ],
)
def test_bad_iri_silent(iri: str, caplog: pytest.LogCaptureFixture) -> None:
    with pytest.raises(RDFInputError):
        parse_metadata(f'<{iri}> <urn:x:p> "private-sentinel" .'.encode())
    assert not caplog.records


def test_whole_input_preflight(monkeypatch: pytest.MonkeyPatch) -> None:
    import gfjd.federation_rdf_input as parser

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("term constructed before complete preflight")

    monkeypatch.setattr(parser, "URIRef", forbidden)
    with pytest.raises(RDFInputError):
        parser.parse_metadata(TRIPLE + b'<https://bad host> <urn:x:p> "private" .')


def test_no_io(monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins
    import socket

    from rdflib import Graph

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("I/O or RDF parser called")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    monkeypatch.setattr(Graph, "parse", forbidden)
    graph, count = parse_metadata(TRIPLE)
    assert len(graph) == count == 1


def test_comments_and_lexical_values() -> None:
    value = b"# fictional comment\r\n" + TRIPLE + b"\n"
    graph, count = parse_metadata(value)
    assert len(graph) == count == 1
    graph, _ = parse_metadata(b'<urn:x:s> <urn:x:p> "  exact  " .')
    assert str(next(graph.objects())) == "  exact  "


def test_traceback_no_raw_value() -> None:
    import traceback

    try:
        parse_metadata(b'<urn:x:s> <urn:x:p> "private-sentinel\\q" .')
    except RDFInputError:
        rendered = traceback.format_exc()
        # The source line itself is shown normally; exception diagnostics must
        # contain no intermediate JSON/RDF errors or echoed values.
        assert rendered.rstrip().endswith("RDFInputError: RDF metadata input rejected")
        assert "JSONDecodeError" not in rendered


def test_surrogate_pair_not_legal_ntriples_escape() -> None:
    with pytest.raises(RDFInputError):
        parse_metadata(b'<urn:x:s> <urn:x:p> "\\ud83d\\ude00" .')
    graph, _ = parse_metadata(b'<urn:x:s> <urn:x:p> "\\\\ud800" .')
    assert str(next(graph.objects())) == "\\ud800"
