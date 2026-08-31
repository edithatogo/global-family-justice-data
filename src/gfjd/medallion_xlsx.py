"""Bounded explicit-cell OOXML extraction, never formatted-display/source truth.

Only implementation fingerprinting reads a file. Inputs are supplied bytes;
there is no transport, formula evaluation, disk extraction or promotion.
This deliberately narrow UTF-8 transitional-OOXML subset fails closed.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import stat
import zipfile
import zlib
from bisect import bisect_left
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree as ET

VERSION = "gfjd-medallion-xlsx-v1"
MAX_SOURCE_BYTES = 8 * 1024 * 1024
MAX_MEMBERS = 128
MAX_EXPANDED_BYTES = 16 * 1024 * 1024
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_RATIO = 200
MAX_ROWS = 1000
MAX_CELLS = 10000
MAX_XML_NODES = 100000
MAX_XML_DEPTH = 64
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
T = "http://schemas.openxmlformats.org/package/2006/content-types"
CONTRACT_KEYS = frozenset(
    {"extraction_version", "source_sha256", "sheet_name", "header_row", "columns", "data_rows"}
)


class MedallionXlsxError(ValueError):
    """Fail-closed extraction; no partial receipt or untrusted exception text."""


def _require(condition: bool) -> None:
    if not condition:
        raise MedallionXlsxError("medallion XLSX contract violation")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _column(value: str) -> int:
    _require(re.fullmatch(r"[A-Z]{1,3}", value) is not None)
    number = 0
    for char in value:
        number = number * 26 + ord(char) - ord("A") + 1
    _require(number <= 16384)
    return number


def _coordinate(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]{1,3})([1-9][0-9]{0,6})", value)
    _require(match is not None)
    assert match is not None
    row = int(match[2])
    _require(row <= 1048576)
    return _column(match[1]), row


def _contract(source: bytes, contract: dict[str, Any]) -> None:
    _require(isinstance(source, bytes) and 0 < len(source) <= MAX_SOURCE_BYTES)
    _require(isinstance(contract, dict) and set(contract) == CONTRACT_KEYS)
    _require(contract["extraction_version"] == VERSION)
    _require(contract["source_sha256"] == _sha(source))
    _require(isinstance(contract["sheet_name"], str) and 0 < len(contract["sheet_name"]) <= 31)
    header = contract["header_row"]
    _require(type(header) is int and 1 <= header <= 10000)
    columns = contract["columns"]
    _require(isinstance(columns, list) and 0 < len(columns) <= 64)
    _require(all(isinstance(item, str) for item in columns))
    indices = [_column(item) for item in columns]
    _require(indices == sorted(set(indices)) and max(indices) <= 64)
    rows = contract["data_rows"]
    _require(isinstance(rows, list) and 0 < len(rows) <= MAX_ROWS)
    _require(all(type(item) is int and 1 <= item <= 10000 for item in rows))
    _require(rows == sorted(set(rows)) and header not in rows)
    _require((len(rows) + 1) * len(columns) <= MAX_CELLS)


def _path(value: str) -> None:
    _require(isinstance(value, str) and 0 < len(value) <= 512)
    _require(re.fullmatch(r"[A-Za-z0-9_./\[\]-]+", value) is not None)
    _require(not value.startswith("/") and all(p not in {"", ".", ".."} for p in value.split("/")))


def _package(source: bytes) -> dict[str, bytes]:
    with zipfile.ZipFile(io.BytesIO(source)) as archive:
        infos = archive.infolist()
        _require(0 < len(infos) <= MAX_MEMBERS)
        names: set[str] = set()
        total = 0
        for info in infos:
            _path(info.filename)
            _require(info.orig_filename == info.filename)
            name = info.filename.casefold()
            _require(name not in names)
            names.add(name)
            mode = stat.S_IFMT(info.external_attr >> 16)
            _require(mode in {0, stat.S_IFREG} and not info.is_dir())
            _require(not info.flag_bits & (1 | 64))
            _require(info.compress_type in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED})
            _require(0 <= info.file_size <= MAX_MEMBER_BYTES)
            _require(info.file_size <= MAX_RATIO * max(info.compress_size, 1))
            total += info.file_size
            _require(total <= MAX_EXPANDED_BYTES)
            _require(
                not any(
                    token in name
                    for token in ("vbaproject", "externallink", "activex", "embeddings")
                )
            )
            _require(not name.endswith(".bin"))
        # Preflight every member before any member decompression; bounded reads
        # also verify actual length and CRC, including unselected members.
        members: dict[str, bytes] = {}
        for info in infos:
            with archive.open(info) as member:
                raw = member.read(MAX_MEMBER_BYTES + 1)
            _require(len(raw) == info.file_size and len(raw) <= MAX_MEMBER_BYTES)
            members[info.filename] = raw
        return members


def _xmls(members: dict[str, bytes]) -> dict[str, ET.Element]:
    trees = {}
    nodes = 0
    for name, raw in members.items():
        if not name.endswith((".xml", ".rels")):
            continue
        text = raw.decode("utf-8-sig")
        # UTF-8 only excludes UTF-16/32 bypasses; reject declarations before ET.
        _require(
            "\x00" not in text
            and "<!DOCTYPE" not in text.upper()
            and "<!ENTITY" not in text.upper()
        )
        declaration = re.match(r"\s*<\?xml\s+([^?]+)\?>", text)
        if declaration:
            encoding = re.search(r"encoding\s*=\s*['\"]([^'\"]+)['\"]", declaration[1])
            _require(encoding is None or encoding[1].lower() in {"utf-8", "utf8"})
        # Iteration checks bounds during parsing (with the parser's bounded
        # chunk lookahead), rather than after a whole oversized tree exists.
        parser = ET.iterparse(io.StringIO(text), events=("start", "end"))
        depth = 0
        root: ET.Element | None = None
        for event, element in parser:
            if event == "start":
                if root is None:
                    root = element
                depth += 1
                nodes += 1
                _require(nodes <= MAX_XML_NODES and depth <= MAX_XML_DEPTH)
            else:
                depth -= 1
        _require(root is not None)
        assert root is not None
        trees[name] = root
    return trees


def _relationships(
    trees: dict[str, ET.Element], members: dict[str, bytes]
) -> dict[str, dict[str, tuple[str, str]]]:
    result = {}
    for name, root in trees.items():
        if not name.endswith(".rels"):
            continue
        _require(root.tag == f"{{{P}}}Relationships")
        base = "" if name == "_rels/.rels" else str(PurePosixPath(name).parent.parent)
        mapping: dict[str, tuple[str, str]] = {}
        for rel in root:
            _require(rel.tag == f"{{{P}}}Relationship")
            _require(set(rel.attrib) <= {"Id", "Type", "Target", "TargetMode"})
            _require(rel.get("TargetMode", "Internal") == "Internal")
            identity, target, kind = rel.get("Id", ""), rel.get("Target", ""), rel.get("Type", "")
            _require(bool(identity) and identity not in mapping and bool(kind))
            _require(
                not any(
                    token in kind.lower() for token in ("external", "vba", "oleobject", "activex")
                )
            )
            # A single leading slash denotes the package root, never the host
            # filesystem. Validate the remaining canonical part before lookup;
            # double slashes, escapes and parent traversal remain forbidden.
            if target.startswith("/"):
                resolved = target[1:]
                _path(resolved)
            else:
                _path(target)
                resolved = f"{base}/{target}" if base else target
            _require(resolved in members)
            mapping[identity] = (kind, resolved)
        result[name] = mapping
    return result


def _sheet(
    trees: dict[str, ET.Element], rels: dict[str, dict[str, tuple[str, str]]], name: str
) -> str:
    content = trees["[Content_Types].xml"]
    _require(content.tag == f"{{{T}}}Types")
    for element in content:
        _require(
            not any(
                word in element.get("ContentType", "").lower()
                for word in ("macro", "vba", "ole", "activex")
            )
        )
    office = [
        target for kind, target in rels["_rels/.rels"].values() if kind == f"{R}/officeDocument"
    ]
    _require(office == ["xl/workbook.xml"])
    workbook = trees["xl/workbook.xml"]
    _require(workbook.tag == f"{{{S}}}workbook")
    containers = workbook.findall(f"{{{S}}}sheets")
    _require(len(containers) == 1)
    sheets = list(containers[0])
    _require(all(item.tag == f"{{{S}}}sheet" for item in sheets))
    _require(len({item.get("name", "").casefold() for item in sheets}) == len(sheets))
    chosen = [item for item in sheets if item.get("name") == name]
    _require(len(chosen) == 1 and chosen[0].get("state", "visible") == "visible")
    kind, target = rels["xl/_rels/workbook.xml.rels"][chosen[0].get(f"{{{R}}}id", "")]
    _require(kind == f"{R}/worksheet")
    _require(re.fullmatch(r"xl/worksheets/[A-Za-z0-9_-]+\.xml", target) is not None)
    return target


def _visible(value: str | None) -> None:
    _require(value in {None, "0", "false"})


def _overlap(reference: str, axes: tuple[list[int], list[int]]) -> bool:
    bounds = reference.split(":")
    _require(1 <= len(bounds) <= 2)
    left, top = _coordinate(bounds[0])
    right, bottom = _coordinate(bounds[-1])
    _require(left <= right and top <= bottom)
    columns, rows = axes
    column_index, row_index = bisect_left(columns, left), bisect_left(rows, top)
    return (
        column_index < len(columns)
        and columns[column_index] <= right
        and row_index < len(rows)
        and rows[row_index] <= bottom
    )


def _cells(sheet: ET.Element, selected: set[tuple[int, int]]) -> dict[str, ET.Element]:
    _require(sheet.tag == f"{{{S}}}worksheet")
    # Fail closed on extension/fallback payloads rather than guessing cell semantics.
    _require(all(element.tag.startswith(f"{{{S}}}") for element in sheet.iter()))
    selected_columns = {column for column, _ in selected}
    selected_rows = {row for _, row in selected}
    axes = (sorted(selected_columns), sorted(selected_rows))
    for defaults in sheet.findall(f"{{{S}}}sheetFormatPr"):
        _visible(defaults.get("zeroHeight"))
    for col in sheet.findall(f"{{{S}}}cols/{{{S}}}col"):
        first, last = col.get("min", ""), col.get("max", "")
        _require(first.isascii() and first.isdigit() and last.isascii() and last.isdigit())
        low, high = int(first), int(last)
        _require(1 <= low <= high <= 16384)
        if any(low <= column <= high for column in selected_columns):
            _visible(col.get("hidden"))
    for merged in sheet.findall(f"{{{S}}}mergeCells/{{{S}}}mergeCell"):
        _require(not _overlap(merged.get("ref", ""), axes))
    containers = sheet.findall(f"{{{S}}}sheetData")
    _require(len(containers) == 1)
    cells = {}
    rows: set[int] = set()
    for row in containers[0]:
        _require(row.tag == f"{{{S}}}row")
        label = row.get("r", "")
        _require(re.fullmatch(r"[1-9][0-9]{0,6}", label) is not None)
        number = int(label)
        _require(number <= 1048576 and number not in rows)
        rows.add(number)
        if number in selected_rows:
            _visible(row.get("hidden"))
        for cell in row:
            _require(cell.tag == f"{{{S}}}c")
            ref = cell.get("r", "")
            _, actual_row = _coordinate(ref)
            _require(actual_row == number and ref not in cells)
            cells[ref] = cell
            for formula in cell.findall(f"{{{S}}}f"):
                if formula.get("ref"):
                    _require(not _overlap(formula.get("ref", ""), axes))
    return cells


def _text(container: ET.Element) -> str:
    _require(not container.attrib and not (container.text or "").strip())
    _require(len(container) == 1 and container[0].tag == f"{{{S}}}t")
    text = container[0]
    _require(not (text.tail or "").strip())
    _require(len(text) == 0 and set(text.attrib) <= {"{http://www.w3.org/XML/1998/namespace}space"})
    _require(
        text.get("{http://www.w3.org/XML/1998/namespace}space") in {None, "default", "preserve"}
    )
    return text.text or ""


def _value(cell: ET.Element, strings: list[str]) -> tuple[str, str]:
    _require(not (cell.text or "").strip())
    _require(set(cell.attrib) <= {"r", "t", "s"})
    kind = cell.get("t", "n")
    _require(kind in {"n", "b", "d", "s", "inlineStr"})
    _require(len(cell) == 1)
    child = cell[0]
    _require(not (child.tail or "").strip())
    if kind == "inlineStr":
        _require(child.tag == f"{{{S}}}is")
        return _text(child), kind
    _require(child.tag == f"{{{S}}}v" and len(child) == 0 and not child.attrib)
    value = child.text or ""
    _require(bool(value))
    if kind == "s":
        _require(re.fullmatch(r"0|[1-9][0-9]*", value) is not None and len(value) <= 8)
        index = int(value)
        _require(index < len(strings))
        return strings[index], kind
    if kind == "b":
        _require(value in {"0", "1"})
    elif kind == "n":
        _require(
            re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value)
            is not None
        )
    elif kind == "d":
        # Validate the bounded date representation but preserve its exact text:
        # no date-system conversion, timezone normalization or source inference.
        _require(
            re.fullmatch(
                r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})?)?",
                value,
            )
            is not None
        )
        offset = re.search(r"[+-]([0-9]{2}):([0-9]{2})$", value)
        if offset:
            _require(int(offset[1]) <= 23 and int(offset[2]) <= 59)
        # fromisoformat alone normalizes offset minute overflow; the explicit
        # check above prevents that malformed lexical form from passing.
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value, kind


def _extract(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    _contract(source, contract)
    members = _package(source)
    trees = _xmls(members)
    rels = _relationships(trees, members)
    target = _sheet(trees, rels, contract["sheet_name"])
    selected = {
        (_column(col), row)
        for col in contract["columns"]
        for row in [contract["header_row"], *contract["data_rows"]]
    }
    cells = _cells(trees[target], selected)
    shared = [
        part
        for kind, part in rels["xl/_rels/workbook.xml.rels"].values()
        if kind == f"{R}/sharedStrings"
    ]
    _require(len(shared) <= 1)
    strings: list[str] = []
    if shared:
        root = trees[shared[0]]
        _require(root.tag == f"{{{S}}}sst")
        for item in root:
            _require(item.tag == f"{{{S}}}si")
            strings.append(_text(item))
    labels = []
    headers = []
    for col in contract["columns"]:
        ref = f"{col}{contract['header_row']}"
        label, kind = _value(cells[ref], strings)
        _require(kind in {"inlineStr", "s"} and bool(label.strip()) and label not in labels)
        labels.append(label)
        headers.append((ref, kind))
    rows = []
    fields = []
    for number in contract["data_rows"]:
        values = {}
        locators = {}
        for col, label, (header, header_type) in zip(
            contract["columns"], labels, headers, strict=True
        ):
            ref = f"{col}{number}"
            value, kind = _value(cells[ref], strings)
            values[label] = value
            locators[label] = {
                "cell": ref,
                "header_cell": header,
                "cell_type": kind,
                "header_type": header_type,
            }
        rows.append(values)
        fields.append(locators)
    return {
        "extraction_version": VERSION,
        "source_sha256": _sha(source),
        "contract_sha256": _sha(_canonical(contract)),
        "implementation_sha256": _sha(Path(__file__).read_bytes()),
        "sheet_name": contract["sheet_name"],
        "worksheet_part": target,
        "scope": json.loads(_canonical(contract)),
        "rows": rows,
        "fields": fields,
        "value_semantics": "OOXML lexical values; not formatted display or source truth",
        "authority": dict.fromkeys(
            [
                "network",
                "source_access",
                "rights_clearance",
                "public_safety",
                "b1_promotion",
                "silver_promotion",
                "publication",
                "release",
                "gate_acceptance",
            ],
            False,
        ),
    }


def extract_xlsx(source: bytes, contract: dict[str, Any]) -> dict[str, Any]:
    """Extract exact explicit cells or fail closed without returning partial rows."""
    try:
        return _extract(source, contract)
    except (
        ValueError,
        TypeError,
        KeyError,
        OSError,
        RuntimeError,
        RecursionError,
        OverflowError,
        zipfile.BadZipFile,
        ET.ParseError,
        zlib.error,
    ):
        raise MedallionXlsxError("medallion XLSX extraction failed") from None


def verify_xlsx(source: bytes, contract: dict[str, Any], receipt: dict[str, Any]) -> None:
    """Recompute exact receipt from source bytes and contract, never trust self-hashes."""
    try:
        _require(_canonical(receipt) == _canonical(extract_xlsx(source, contract)))
    except (ValueError, TypeError, RecursionError, OverflowError):
        raise MedallionXlsxError("medallion XLSX receipt mismatch") from None
