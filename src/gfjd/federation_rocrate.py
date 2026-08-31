"""Restricted flattened RO-Crate 1.3 declarations; not JSON-LD expansion.

Only a root Dataset, descriptor, relative Files, Organizations and licence
CreativeWorks are supported. No payloads or identifiers are accessed. Calendar
dates only, no inferred publication. Complete declarations are not factual proof.
Absent factual keys produce incomplete issues; supplied blank date or licence
values are malformed. Every File must be linked from the root's hasPart.
"""

import hashlib
import json
import re
from typing import Any

from gfjd.federation_metadata import (
    MetadataError,
    date_label,
    make_report,
    parse_json,
    require,
    safe_url,
)

CONTEXT_SHA256 = "5a3df1a43185501db4d45cdde5a478c57eeb1d673eedfe400488fc4c4b21dd91"
CONTEXT_URI = "https://w3id.org/ro/crate/1.3/context"
VERSION_URI = "https://w3id.org/ro/crate/1.3"
PROFILE = "gfjd-rocrate-declarations-v1"


def _path(value: str) -> None:
    require(re.fullmatch(r"[A-Za-z0-9_-][A-Za-z0-9._/-]*", value) is not None)
    require(all(part not in {"", ".", ".."} for part in value.split("/")))
    require(value != "ro-crate-metadata.json")


def _identifier(value: Any) -> str:
    require(isinstance(value, str) and bool(value))
    if value.startswith("https://"):
        safe_url(value)
    elif value.startswith("#"):
        require(re.fullmatch(r"#[A-Za-z0-9_-][A-Za-z0-9._-]*", value) is not None)
    elif value not in {"./", "ro-crate-metadata.json"}:
        _path(value)
    return str(value)


def _refs(value: Any) -> list[str]:
    values = value if isinstance(value, list) else [value]
    require(bool(values))
    result = []
    for ref in values:
        require(isinstance(ref, dict) and set(ref) == {"@id"})
        result.append(_identifier(ref["@id"]))
    require(len(result) == len(set(result)))
    return result


def _assess(metadata_raw: bytes, context_raw: bytes) -> dict[str, Any]:
    require(type(context_raw) is bytes and 0 < len(context_raw) <= 256 * 1024)
    require(hashlib.sha256(context_raw).hexdigest() == CONTEXT_SHA256)
    # The exact context is a bound artifact, not input to a JSON-LD processor.
    metadata = parse_json(metadata_raw)
    require(isinstance(metadata, dict) and set(metadata) == {"@context", "@graph"})
    require(metadata["@context"] == CONTEXT_URI)
    graph = metadata["@graph"]
    require(isinstance(graph, list) and 2 <= len(graph) <= 1000)
    nodes: dict[str, dict[str, Any]] = {}
    issues: list[str] = []
    for node in graph:
        require(isinstance(node, dict) and "@id" in node and "@type" in node)
        identifier = _identifier(node["@id"])
        require(identifier not in nodes)
        nodes[identifier] = node
    require("./" in nodes and "ro-crate-metadata.json" in nodes)
    descriptor = nodes["ro-crate-metadata.json"]
    require(set(descriptor) == {"@id", "@type", "about", "conformsTo"})
    require(descriptor["@type"] == "CreativeWork")
    require(descriptor["about"] == {"@id": "./"})
    require(descriptor["conformsTo"] == {"@id": VERSION_URI})
    require(nodes["./"]["@type"] == "Dataset")
    file_ids = {key for key, node in nodes.items() if node["@type"] == "File"}
    root_parts = set(_refs(nodes["./"]["hasPart"])) if "hasPart" in nodes["./"] else set()
    require(root_parts == file_ids)
    for identifier, node in nodes.items():
        if identifier == "ro-crate-metadata.json":
            continue
        kind = node["@type"]
        require(
            isinstance(kind, str) and kind in {"Dataset", "File", "Organization", "CreativeWork"}
        )
        allowed = {"@id", "@type", "name", "description"}
        if kind == "Dataset":
            require(identifier == "./")
            allowed |= {"datePublished", "license", "creator", "hasPart"}
        elif kind == "File":
            _path(identifier)
            allowed |= {"encodingFormat", "sha256"}
        else:
            require(identifier.startswith(("#", "https://")))
        require(set(node) <= allowed)
        for field in ("name", "description", "encodingFormat"):
            if field in node:
                require(isinstance(node[field], str))
        for field in (
            ("name", "description", "license", "datePublished")
            if kind == "Dataset"
            else ("name",)
            if kind in {"Organization", "CreativeWork"}
            else ()
        ):
            if field not in node or (isinstance(node[field], str) and not node[field].strip()):
                issues.append(f"{kind.lower()}_{field}_missing")
        if "datePublished" in node:
            require(date_label(node["datePublished"]))
        if "sha256" in node:
            require(
                isinstance(node["sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", node["sha256"]) is not None
            )
        for field, target_kind in (
            ("hasPart", "File"),
            ("creator", "Organization"),
            ("license", "CreativeWork"),
        ):
            if field not in node:
                continue
            for target in _refs(node[field]):
                if target in nodes:
                    require(nodes[target]["@type"] == target_kind)
                else:
                    require(field != "hasPart" and target.startswith("https://"))
                    safe_url(target)
    return make_report(PROFILE, metadata_raw, {"context_sha256": CONTEXT_SHA256}, issues)


def assess_rocrate(metadata_raw: bytes, context_raw: bytes) -> dict[str, Any]:
    """Assess only the closed representation profile with supplied exact context bytes."""
    try:
        return _assess(metadata_raw, context_raw)
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None


def verify_rocrate(metadata_raw: bytes, context_raw: bytes, report: dict[str, Any]) -> None:
    """Recompute the complete report; caller claims never substitute for checks."""
    try:
        expected = assess_rocrate(metadata_raw, context_raw)
        require(type(report) is dict and report == expected)
        # Python equality alone treats bool and integer as equal.
        require(
            json.dumps(report, sort_keys=True, allow_nan=False)
            == json.dumps(expected, sort_keys=True)
        )
    except Exception:
        raise MetadataError("Metadata profile contract violation") from None
