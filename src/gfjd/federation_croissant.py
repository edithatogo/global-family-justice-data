"""Closed Croissant declaration preparation; no dataset or JSON-LD loader."""

import hashlib
import json
import re
from typing import Any, cast

from gfjd.federation_metadata import (
    MetadataError,
    date_label,
    make_report,
    parse_json,
    require,
    safe_url,
)

PROFILE_SHA256 = "e0bcf9bbfcba4101cb7bf53b8b883b137e8ba74db6aa0a2fb0ba21ca89b4ed60"


def _object(value: Any, allowed: list[str]) -> dict[str, Any]:
    require(type(value) is dict and set(value) <= set(allowed))
    return cast(dict[str, Any], value)


def _text(value: Any) -> None:
    require(isinstance(value, str) and bool(value.strip()))


def _identity(item: dict[str, Any], seen: set[str]) -> str:
    value = item.get("@id")
    require(isinstance(value, str))
    value = cast(str, value)
    require(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*)*", value)
        is not None
    )
    require(value not in seen)
    seen.add(value)
    return value


def _optional_text(item: dict[str, Any]) -> None:
    for key in ("name", "description"):
        if key in item:
            _text(item[key])


def _facts(item: dict[str, Any], fields: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for key in fields:
        if key not in item:
            issues.append(prefix + "_missing_" + key)
        else:
            _text(item[key])


def assess_croissant(metadata_raw: bytes, profile_raw: bytes) -> dict[str, Any]:
    """Check only declared shape/reference integrity, never actual files or rights.

    The sole inline context is compared as JSON, not expanded. Local identifiers
    remain local declarations, not resolved absolute identities. Missing factual
    declarations produce incomplete issues; unsupported syntax fails closed.
    Content-size, recommended properties, complex creators/licences and broader
    JSON-LD representations are outside coverage, not silently validated.
    """
    try:
        require(type(profile_raw) is bytes and 0 < len(profile_raw) <= 1024 * 1024)
        require(hashlib.sha256(profile_raw).hexdigest() == PROFILE_SHA256)
        profile = parse_json(profile_raw)
        metadata = _object(parse_json(metadata_raw), profile["dataset_keys"])
        require(metadata.get("@context") == profile["context"])
        require(metadata.get("@type") == "sc:Dataset")
        require(metadata.get("conformsTo") == profile["conformsTo"])
        issues: list[str] = []
        _facts(
            metadata, ("name", "description", "license", "datePublished", "url"), "dataset", issues
        )
        for key in ("license", "url", "@id"):
            if key in metadata:
                safe_url(metadata[key])
        if "datePublished" in metadata:
            require(date_label(metadata["datePublished"]))
        if "creator" not in metadata:
            issues.append("dataset_missing_creator")
        else:
            creator = _object(metadata["creator"], ["@type", "name", "url"])
            require(creator.get("@type") == "sc:Organization")
            _facts(creator, ("name",), "creator", issues)
            if "url" in creator:
                safe_url(creator["url"])
        seen: set[str] = set()
        if "@id" in metadata:
            seen.add(metadata["@id"])
        distributions = metadata.get("distribution", [])
        require(type(distributions) is list)
        if not distributions:
            issues.append("dataset_missing_distribution")
        files: set[str] = set()
        for value in distributions:
            item = _object(value, profile["file_keys"])
            require(item.get("@type") == "cr:FileObject")
            files.add(_identity(item, seen))
            _optional_text(item)
            _facts(item, ("name", "contentUrl", "encodingFormat", "sha256"), "file", issues)
            if "contentUrl" in item:
                safe_url(item["contentUrl"])
            if "encodingFormat" in item:
                require(
                    re.fullmatch(
                        r"[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]*",
                        item["encodingFormat"],
                    )
                    is not None
                )
            if "sha256" in item:
                require(re.fullmatch(r"[a-f0-9]{64}", item["sha256"]) is not None)
        records = metadata.get("recordSet", [])
        require(type(records) is list)
        for value in records:
            record = _object(value, profile["recordset_keys"])
            require(record.get("@type") == "cr:RecordSet")
            _identity(record, seen)
            _optional_text(record)
            fields = record.get("field", [])
            require(type(fields) is list)
            if not fields:
                issues.append("recordset_missing_fields")
            field_names: set[str] = set()
            for value in fields:
                field = _object(value, profile["field_keys"])
                require(field.get("@type") == "cr:Field")
                _identity(field, seen)
                _optional_text(field)
                _facts(field, ("name",), "field", issues)
                if "name" in field:
                    require(field["name"] not in field_names)
                    field_names.add(field["name"])
                if "dataType" not in field:
                    issues.append("field_missing_datatype")
                else:
                    require(field["dataType"] in profile["datatypes"])
                if "source" not in field:
                    issues.append("field_missing_source")
                    continue
                source = _object(field["source"], ["fileObject", "extract"])
                require(set(source) == {"fileObject", "extract"})
                reference = _object(source["fileObject"], ["@id"])
                require(set(reference) == {"@id"} and isinstance(reference["@id"], str))
                require(reference["@id"] in files)
                extraction = _object(source["extract"], ["column"])
                require(set(extraction) == {"column"})
                _text(extraction["column"])
                require(
                    re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ .-]*", extraction["column"]) is not None
                )
        return make_report(
            profile["profile"], metadata_raw, {"profile_sha256": PROFILE_SHA256}, issues
        )
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None


def verify_croissant(metadata_raw: bytes, profile_raw: bytes, report: dict[str, Any]) -> None:
    """Recompute every report field; no caller hash or pass assertion is trusted."""
    try:
        expected = assess_croissant(metadata_raw, profile_raw)
        require(type(report) is dict)
        rendered = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
        require(
            rendered == json.dumps(expected, sort_keys=True, separators=(",", ":"), allow_nan=False)
        )
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None
