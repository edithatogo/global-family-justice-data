"""Fictional, in-memory OOXML fixtures; never acquire source workbooks."""

import copy
import hashlib
import io
import struct
import zipfile

import pytest

from gfjd.medallion_xlsx import VERSION, MedallionXlsxError, extract_xlsx, verify_xlsx

S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"


def parts() -> dict[str, str]:
    return {
        "[Content_Types].xml": (
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" '
            'ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>"
        ),
        "_rels/.rels": (
            f'<Relationships xmlns="{P}"><Relationship Id="r1" Type="{R}/officeDocument" '
            'Target="xl/workbook.xml"/></Relationships>'
        ),
        "xl/workbook.xml": (
            f'<workbook xmlns="{S}" xmlns:r="{R}"><sheets>'
            '<sheet name="Fictional" sheetId="1" r:id="r1"/></sheets></workbook>'
        ),
        "xl/_rels/workbook.xml.rels": (
            f'<Relationships xmlns="{P}"><Relationship Id="r1" Type="{R}/worksheet" '
            'Target="worksheets/sheet1.xml"/></Relationships>'
        ),
        "xl/worksheets/sheet1.xml": (
            f'<worksheet xmlns="{S}"><sheetData><row r="1">'
            '<c r="A1" t="inlineStr"><is>'
            '<t xml:space="preserve"> Fictional label </t></is></c>'
            '<c r="B1" t="inlineStr"><is><t>Fictional amount</t></is></c></row>'
            '<row r="2"><c r="A2" t="inlineStr"><is>'
            '<t xml:space="preserve"> exact  text </t></is></c>'
            '<c r="B2"><v>001.2300</v></c></row></sheetData></worksheet>'
        ),
    }


def source(entries: dict[str, str] | None = None) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, text in (entries if entries is not None else parts()).items():
            archive.writestr(name, text)
    return stream.getvalue()


def contract(raw: bytes) -> dict:
    return {
        "extraction_version": VERSION,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "sheet_name": "Fictional",
        "header_row": 1,
        "columns": ["A", "B"],
        "data_rows": [2],
    }


def test_exact_lexical_rows_and_replay() -> None:
    raw = source()
    receipt = extract_xlsx(raw, contract(raw))
    assert receipt["rows"] == [
        {" Fictional label ": " exact  text ", "Fictional amount": "001.2300"}
    ]
    assert receipt["fields"][0]["Fictional amount"] == {
        "cell": "B2",
        "header_cell": "B1",
        "cell_type": "n",
        "header_type": "inlineStr",
    }
    assert receipt["worksheet_part"] == "xl/worksheets/sheet1.xml"
    assert all(value is False for value in receipt["authority"].values())
    assert extract_xlsx(raw, contract(raw)) == receipt
    assert verify_xlsx(raw, contract(raw), receipt) is None


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_sha256", "0" * 64),
        ("extraction_version", "unknown"),
        ("sheet_name", "absent"),
        ("header_row", True),
        ("header_row", 0),
        ("columns", ["B", "A"]),
        ("columns", ["A", "A"]),
        ("columns", ["BM"]),
        ("columns", []),
        ("data_rows", [2, 2]),
        ("data_rows", [3, 2]),
        ("data_rows", [1]),
        ("data_rows", [True]),
        ("data_rows", [10001]),
        ("data_rows", list(range(2, 1003))),
    ],
)
def test_exact_contract(field: str, value: object) -> None:
    raw = source()
    selection = contract(raw)
    selection[field] = value
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, selection)


@pytest.mark.parametrize(
    "old,new",
    [
        ('<c r="B2"><v>001.2300</v></c>', '<c r="B2"><f>1+1</f><v>2</v></c>'),
        ('<c r="B2"><v>001.2300</v></c>', ""),
        ('<c r="B2">', '<c r="B2" t="e">'),
        ('<c r="B2">', '<c r="B2" t="unknown">'),
        ('<c r="B2">', '<c r="B2" t="b">'),
        ('<c r="B2">', '<c r="B2" t="s">'),
        ('<row r="2">', '<row r="2" hidden="1">'),
        ('<row r="1">', '<row r="1" hidden="true">'),
        ("<sheetData>", '<cols><col min="2" max="2" hidden="1"/></cols><sheetData>'),
        ("</sheetData>", '</sheetData><mergeCells><mergeCell ref="A2:B2"/></mergeCells>'),
        ("<t>Fictional amount</t>", "<r><t>Fictional amount</t></r>"),
        ("<t>Fictional amount</t>", "<t> Fictional label </t>"),
        ("<t>Fictional amount</t>", "<t/>"),
        ("<v>001.2300</v>", "<v>001.2300</v><v>2</v>"),
        ('r="B2"', 'r="B3"'),
        ("</row></sheetData>", '<c r="B2"><v>1</v></c></row></sheetData>'),
    ],
)
def test_ambiguous_or_hidden_cells_stop(old: str, new: str) -> None:
    entries = parts()
    entries["xl/worksheets/sheet1.xml"] = entries["xl/worksheets/sheet1.xml"].replace(old, new)
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


@pytest.mark.parametrize(
    "name", ["../bad", "/bad", "xl//bad", "xl/./bad", "xl/../bad", "xl\\bad", "XL/WORKBOOK.XML"]
)
def test_bad_zip_paths(name: str) -> None:
    entries = parts()
    entries[name] = "fictional"
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


def test_bomb_and_link_and_duplicate_members() -> None:
    entries = parts()
    entries["bomb.xml"] = "x" * 1_000_000
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = 0o120777 << 16
        archive.writestr(link, "target")
    raw = stream.getvalue()
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("duplicate", "a")
        with pytest.warns(UserWarning):
            archive.writestr("duplicate", "b")
    raw = stream.getvalue()
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


@pytest.mark.parametrize(
    "mutation", ["external", "traversal", "hidden", "macro", "dtd", "utf16dtd"]
)
def test_package_rejections(mutation: str) -> None:
    entries = parts()
    if mutation == "external":
        entries["xl/_rels/workbook.xml.rels"] = entries["xl/_rels/workbook.xml.rels"].replace(
            'Target="worksheets/sheet1.xml"',
            'Target="https://example.invalid/a" TargetMode="External"',
        )
    elif mutation == "traversal":
        entries["xl/_rels/workbook.xml.rels"] = entries["xl/_rels/workbook.xml.rels"].replace(
            "worksheets/sheet1.xml", "../sheet.xml"
        )
    elif mutation == "hidden":
        entries["xl/workbook.xml"] = entries["xl/workbook.xml"].replace(
            'sheetId="1"', 'sheetId="1" state="hidden"'
        )
    elif mutation == "macro":
        entries["xl/vbaProject.bin"] = "fictional macro bytes"
    else:
        entries["xl/workbook.xml"] = (
            '<!DOCTYPE x [<!ENTITY y "fictional">]>' + entries["xl/workbook.xml"]
        )
        if mutation == "utf16dtd":
            entries["xl/workbook.xml"] = entries["xl/workbook.xml"].encode("utf-16")  # type: ignore[assignment]
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


def test_plain_shared_strings_boolean_and_date() -> None:
    entries = parts()
    entries["xl/sharedStrings.xml"] = (
        f'<sst xmlns="{S}"><si><t xml:space="preserve"> shared  text </t></si></sst>'
    )
    entries["xl/_rels/workbook.xml.rels"] = entries["xl/_rels/workbook.xml.rels"].replace(
        "</Relationships>",
        f'<Relationship Id="r2" Type="{R}/sharedStrings" '
        'Target="sharedStrings.xml"/></Relationships>',
    )
    entries["xl/worksheets/sheet1.xml"] = (
        entries["xl/worksheets/sheet1.xml"]
        .replace(
            '<c r="A2" t="inlineStr"><is><t xml:space="preserve"> exact  text </t></is></c>',
            '<c r="A2" t="s"><v>0</v></c>',
        )
        .replace('<c r="B2"><v>001.2300</v></c>', '<c r="B2" t="b"><v>1</v></c>')
    )
    raw = source(entries)
    assert extract_xlsx(raw, contract(raw))["rows"][0] == {
        " Fictional label ": " shared  text ",
        "Fictional amount": "1",
    }
    entries["xl/worksheets/sheet1.xml"] = entries["xl/worksheets/sheet1.xml"].replace(
        '<c r="B2" t="b"><v>1</v></c>', '<c r="B2" t="d"><v>2026-08-31T00:00:00Z</v></c>'
    )
    raw = source(entries)
    assert extract_xlsx(raw, contract(raw))["fields"][0]["Fictional amount"]["cell_type"] == "d"
    entries["xl/sharedStrings.xml"] = f'<sst xmlns="{S}"><si><r><t>rich</t></r></si></sst>'
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


def test_receipt_tamper() -> None:
    raw = source()
    receipt = extract_xlsx(raw, contract(raw))
    for key in ("rows", "fields", "source_sha256", "authority"):
        changed = copy.deepcopy(receipt)
        changed[key] = None
        with pytest.raises(MedallionXlsxError):
            verify_xlsx(raw, contract(raw), changed)
    receipt["fields"][0]["Fictional amount"]["cell"] = "B3"
    with pytest.raises(MedallionXlsxError):
        verify_xlsx(raw, contract(raw), receipt)


@pytest.mark.parametrize("mode", ["encrypted", "crc", "member_limit", "input_limit", "xml_depth"])
def test_additional_archive_and_xml_limits(mode: str) -> None:
    entries = parts()
    if mode == "member_limit":
        entries.update({f"extra{i}.xml": "<fictional/>" for i in range(129)})
    if mode == "xml_depth":
        entries["extra.xml"] = "<fictional>" * 65 + "</fictional>" * 65
    raw = source(entries)
    if mode == "input_limit":
        raw = b"x" * (8 * 1024 * 1024 + 1)
    if mode in {"encrypted", "crc"}:
        mutable = bytearray(raw)
        central = raw.index(b"PK\x01\x02")
        if mode == "encrypted":
            struct.pack_into("<H", mutable, central + 8, 1)
        else:
            struct.pack_into("<I", mutable, central + 16, 0)
        raw = bytes(mutable)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


def test_array_formula_anchor_outside_selected_cells() -> None:
    entries = parts()
    entries["xl/worksheets/sheet1.xml"] = entries["xl/worksheets/sheet1.xml"].replace(
        "</row></sheetData>",
        '<c r="C2"><f t="array" ref="B2:C2">1+1</f><v>2</v></c></row></sheetData>',
    )
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))


def test_explicit_sparse_selection_and_outside_merge() -> None:
    entries = parts()
    entries["xl/worksheets/sheet1.xml"] = entries["xl/worksheets/sheet1.xml"].replace(
        "</sheetData>", '</sheetData><mergeCells><mergeCell ref="C3:D4"/></mergeCells>'
    )
    raw = source(entries)
    selected = contract(raw)
    selected["columns"] = ["B"]
    assert extract_xlsx(raw, selected)["rows"] == [{"Fictional amount": "001.2300"}]
    selected["extra"] = "not permitted"
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, selected)


def test_missing_contract_fields_and_nonbytes_fail_fixed() -> None:
    raw = source()
    selected = contract(raw)
    del selected["sheet_name"]
    with pytest.raises(MedallionXlsxError, match="medallion XLSX extraction failed"):
        extract_xlsx(raw, selected)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx("not bytes", contract(raw))  # type: ignore[arg-type]


def test_package_root_relationships_resolve_only_inside_archive() -> None:
    original = source()
    expected = extract_xlsx(original, contract(original))
    entries = parts()
    entries["_rels/.rels"] = entries["_rels/.rels"].replace(
        'Target="xl/workbook.xml"', 'Target="/xl/workbook.xml"'
    )
    entries["xl/_rels/workbook.xml.rels"] = entries["xl/_rels/workbook.xml.rels"].replace(
        'Target="worksheets/sheet1.xml"', 'Target="/xl/worksheets/sheet1.xml"'
    )
    raw = source(entries)
    result = extract_xlsx(raw, contract(raw))
    assert result["worksheet_part"] == "xl/worksheets/sheet1.xml"
    assert result["rows"] == expected["rows"]
    assert result["fields"] == expected["fields"]
    verify_xlsx(raw, contract(raw), result)


@pytest.mark.parametrize(
    "target",
    [
        "//xl/worksheets/sheet1.xml",
        "/../xl/worksheets/sheet1.xml",
        "/xl/../xl/worksheets/sheet1.xml",
        "/xl//worksheets/sheet1.xml",
        "/xl/%77orksheets/sheet1.xml",
        "/xl\\worksheets/sheet1.xml",
        "/xl/worksheets/sheet1.xml#fragment",
        "/xl/worksheets/missing.xml",
    ],
)
def test_package_root_relationship_escape_and_absence_stop(target: str) -> None:
    entries = parts()
    entries["xl/_rels/workbook.xml.rels"] = entries["xl/_rels/workbook.xml.rels"].replace(
        'Target="worksheets/sheet1.xml"', f'Target="{target}"'
    )
    raw = source(entries)
    with pytest.raises(MedallionXlsxError):
        extract_xlsx(raw, contract(raw))
