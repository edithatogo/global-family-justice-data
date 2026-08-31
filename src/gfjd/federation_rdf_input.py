"""Bounded restricted N-Triples metadata, not a complete N-Triples parser.

One statement per line; absolute ASCII HTTP(S)/URN IRIs, string literals and
language tags only. No blank nodes, escaped IRIs, imports or SHACL vocabulary.
All lexical validation precedes RDFLib term construction; no resource loaders
or parser diagnostics are used. Literal Unicode escapes are limited to JSON's
four-hex form; N-Triples eight-hex escapes and single-quote escapes are unsupported.
"""

import json
import re
from urllib.parse import urlsplit

from rdflib import Graph, Literal, URIRef

MAX_BYTES = 1024 * 1024
MAX_LINE = 8192
MAX_TERM = 4096
MAX_STATEMENTS = 2000
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
_IRI = r"<([^<>]*)>"
_STRING = r'"((?:[^"\\]|\\["\\nrtbf]|\\u[0-9A-Fa-f]{4})*)"'
_STATEMENT = re.compile(
    rf"^[ \t]*{_IRI}[ \t]+{_IRI}[ \t]+(?:{_IRI}|{_STRING}"
    rf"(?:@([A-Za-z]+(?:-[A-Za-z0-9]+)*)|\^\^{_IRI})?)[ \t]*\.[ \t]*(?:#.*)?$"
)


def _require(value: bool) -> None:
    if not value:
        raise RDFInputError("RDF metadata input rejected")


def _safe_text(value: str) -> None:
    _require(len(value) <= MAX_TERM)
    _require(
        all(
            ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF
            for c in value
        )
    )


def _iri(value: str) -> None:
    _safe_text(value)
    _require(value.isascii() and not re.search(r'[\s<>"{}|^`\\]', value))
    _require(re.search(r"%(?![0-9A-Fa-f]{2})", value) is None)
    _require(value.count("#") <= 1)
    _require(not value.startswith("http://www.w3.org/ns/shacl#"))
    _require(not value.startswith("https://www.w3.org/ns/shacl#"))
    _require(value != "http://www.w3.org/2002/07/owl#imports")
    if value.startswith(("http://", "https://")):
        parsed = urlsplit(value)
        _require(bool(parsed.hostname) and parsed.username is None and parsed.password is None)
        _require(parsed.port is None or 1 <= parsed.port <= 65535)
        _require(not any(c in value for c in "[]"))
        _require(
            all(
                re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in (parsed.hostname or "").split(".")
            )
        )
    else:
        _require(
            re.fullmatch(
                r"urn:[A-Za-z0-9][A-Za-z0-9-]{0,30}[A-Za-z0-9]?:"
                r"[A-Za-z0-9._~!$&'()*+,;=:@%/?#-]+",
                value,
            )
            is not None
        )


class RDFInputError(ValueError):
    """Rejected metadata input."""


def parse_metadata(raw: bytes) -> tuple[Graph, int]:
    """Parse supplied bytes only; return graph and pre-deduplication statement count."""
    try:
        _require(type(raw) is bytes and 0 < len(raw) <= MAX_BYTES)
        text = raw.decode("utf-8")
        _require(
            all(
                c in "\n\r\t"
                or (ord(c) >= 32 and not 127 <= ord(c) <= 159 and not 0xD800 <= ord(c) <= 0xDFFF)
                for c in text
            )
        )
        statements: list[tuple[str, str, str | None, str | None, str | None, str | None]] = []
        for line in text.split("\n"):
            if line.endswith("\r"):
                line = line[:-1]
            _require(len(line) <= MAX_LINE and "\r" not in line)
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = _STATEMENT.fullmatch(line)
            _require(match is not None)
            assert match is not None
            subject, predicate, obj, lexical, language, datatype = match.groups()
            for value in (subject, predicate, obj, datatype):
                if value is not None:
                    _iri(value)
            literal = None
            if lexical is not None:
                _require(len(lexical) <= MAX_TERM)
                for escape in re.findall(r'\\(?:["\\nrtbf]|u[0-9A-Fa-f]{4})', lexical):
                    if escape.startswith("\\u"):
                        _require(not 0xD800 <= int(escape[2:], 16) <= 0xDFFF)
                literal = json.loads('"' + lexical + '"')
                _safe_text(literal)
                _require(datatype is None or datatype == XSD_STRING)
                _require(language is None or len(language) <= MAX_TERM)
            statements.append((subject, predicate, obj, literal, language, datatype))
            _require(len(statements) <= MAX_STATEMENTS)
        _require(bool(statements))
        graph = Graph()
        for subject, predicate, obj, literal, language, datatype in statements:
            object_term = (
                URIRef(obj)
                if obj is not None
                else Literal(
                    literal,
                    lang=language,
                    datatype=URIRef(datatype) if datatype else None,
                    normalize=False,
                )
            )
            graph.add((URIRef(subject), URIRef(predicate), object_term))
        return graph, len(statements)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise RDFInputError("RDF metadata input rejected") from None
