"""Fictional structural fixtures only; no publisher responses or requests."""

import ast
import hashlib
import json
from pathlib import Path

import pytest

from gfjd.metadata_shape import MAX_BYTES, inspect_shape


def _bytes(value):
    return json.dumps(value).encode()


def test_fictional_structure_never_emits_scalar_contents():
    raw = _bytes(
        {
            "total": 999123,
            "results": [
                {
                    "title": "FICTIONAL_SECRET_TITLE",
                    "link": "https://fictional.invalid/private",
                    "format": "FICTIONAL_FORMAT",
                    "public_timestamp": "2000-01-01",
                    "FICTIONAL_UNKNOWN_KEY": {"NESTED_SECRET": "DO_NOT_EMIT"},
                }
            ],
        }
    )
    result = inspect_shape(raw)
    assert result["status"] == "structural_diagnostics_only"
    assert result["inspection_complete"] is True
    assert result["enumeration_complete"] is None
    assert result["eligibility"] == "not_assessed"
    assert not any(result["authority"].values())
    serialized = json.dumps(result)
    for text in (
        "999123",
        "FICTIONAL_SECRET_TITLE",
        "fictional.invalid",
        "FICTIONAL_FORMAT",
        "2000-01-01",
        "FICTIONAL_UNKNOWN_KEY",
        "NESTED_SECRET",
        "DO_NOT_EMIT",
    ):
        assert text not in serialized
    assert result["result_count"] == 1
    assert result["missing_row_fields"] == {
        "format": 0,
        "link": 0,
        "public_timestamp": 0,
        "title": 0,
    }


@pytest.mark.parametrize(
    "raw",
    [
        b"{bad",
        b"{} {}",
        b"\xff",
        b'{"a":1,"a":2}',
        b'{"nested":{"x":1,"x":2}}',
        b'{"a":NaN}',
        b'{"a":Infinity}',
        b'{"a":1e9999}',
    ],
)
def test_invalid_json_has_safe_fixed_failure(raw):
    result = inspect_shape(raw)
    assert result["status"] == "invalid_input"
    assert result["inspection_complete"] is False
    assert "fields" not in result


@pytest.mark.parametrize(
    "value",
    [
        None,
        [],
        True,
        42,
        "FICTIONAL",
        {},
        {"results": False},
        {"results": [None, {}, True]},
        {"results": []},
    ],
)
def test_structure_is_not_publication_or_eligibility_acceptance(value):
    result = inspect_shape(_bytes(value))
    assert result["inspection_complete"] is True
    assert result["eligibility"] == "not_assessed"
    assert result["enumeration_complete"] is None
    assert "hypotheses" not in result


def test_boolean_integer_and_number_types_distinct():
    result = inspect_shape(b'{"a":true,"b":1,"c":1.5,"d":null}')
    assert result["types"] == {"boolean": 1, "integer": 1, "null": 1, "number": 1, "object": 1}


@pytest.mark.parametrize("name", ["\ud800", "秘密", "https://fictional.invalid/key", "X" * 2000])
def test_unknown_names_never_emitted(name):
    result = inspect_shape(_bytes({name: {name: "FICTIONAL_SECRET"}}))
    assert "FICTIONAL_SECRET" not in json.dumps(result)
    assert all("name_sha256" in field for field in result["fields"])


@pytest.mark.parametrize(
    "value", [{str(i): i for i in range(129)}, [0] * 1001, [[0] * 1000 for _ in range(11)]]
)
def test_resource_failure_never_reports_partial_success(value):
    result = inspect_shape(_bytes(value))
    assert result["status"] == "limit_stop"
    assert result["inspection_complete"] is False
    assert "fields" not in result


def test_depth_boundary():
    assert inspect_shape(b"[" * 16 + b"0" + b"]" * 16)["inspection_complete"] is True
    assert inspect_shape(b"[" * 17 + b"0" + b"]" * 17)["status"] == "limit_stop"


def test_exact_byte_boundary():
    assert inspect_shape(b"0" + b" " * (MAX_BYTES - 1))["inspection_complete"] is True
    over = inspect_shape(b"0" + b" " * MAX_BYTES)
    assert over["status"] == "limit_stop"
    assert over["input_sha256"] is None


def test_key_order_does_not_change_structural_summary():
    left = inspect_shape(b'{"x":1,"y":true}')
    right = inspect_shape(b'{"y":true,"x":1}')
    left.pop("input_sha256")
    right.pop("input_sha256")
    assert left == right


def test_exact_container_limits():
    assert inspect_shape(_bytes([0] * 1000))["inspection_complete"] is True
    assert inspect_shape(_bytes({str(i): 0 for i in range(128)}))["inspection_complete"] is True


def test_exact_node_limit():
    assert inspect_shape(_bytes([[0] * 1000] * 9 + [[0] * 989]))["inspection_complete"] is True
    assert inspect_shape(_bytes([[0] * 1000] * 9 + [[0] * 990]))["status"] == "limit_stop"


def test_no_transport_filesystem_or_execution_imports():
    source = Path(__file__).resolve().parents[1] / "src/gfjd/metadata_shape.py"
    tree = ast.parse(source.read_text())
    imports = {
        node.module if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imports == {"__future__", "hashlib", "json", "math", "collections", "typing"}
    assert not any(
        isinstance(node, ast.Name) and node.id in {"open", "exec", "eval", "__import__"}
        for node in ast.walk(tree)
    )


def test_missing_fields_and_wrong_types_remain_diagnostics():
    result = inspect_shape(_bytes({"results": [None, {}, {"title": False}]}))
    assert result["missing_root_fields"] == ["total"]
    assert result["nonobject_rows"] == 1
    assert result["missing_row_fields"]["title"] == 1
    assert next(field for field in result["fields"] if field.get("name") == "title")["types"] == {
        "boolean": 1
    }


def test_domain_separated_unknown_field_fingerprint():
    raw = b'{"FICTIONAL_unknown":0}'
    result = inspect_shape(raw)
    assert result["input_sha256"] == hashlib.sha256(raw).hexdigest()
    assert result["fields"] == [
        {
            "name_sha256": hashlib.sha256(b"gfjd-metadata-field-v1\0FICTIONAL_unknown").hexdigest(),
            "types": {"integer": 1},
        }
    ]


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b'{"x":0,"x":1}', "duplicate_key"),
        (b'{"x":NaN}', "nonfinite_number"),
        (b'{"x":1e9999}', "nonfinite_number"),
    ],
)
def test_fixed_error_codes(raw, code):
    assert inspect_shape(raw)["code"] == code


def test_deep_parser_input_is_safe_incomplete():
    result = inspect_shape(b"[" * 5000 + b"0" + b"]" * 5000)
    assert result["inspection_complete"] is False
    assert result["status"] in {"invalid_input", "limit_stop"}


def test_pooled_known_and_unknown_names():
    result = inspect_shape(b'{"title":1,"x":{"title":false,"x":null}}')
    assert result["field_scope"] == "pooled_all_object_levels_not_semantic_paths"
    assert next(field for field in result["fields"] if field.get("name") == "title")["types"] == {
        "boolean": 1,
        "integer": 1,
    }
    assert next(field for field in result["fields"] if "name_sha256" in field)["types"] == {
        "null": 1,
        "object": 1,
    }
