"""Bounded supplied-byte DCAT-AP shape checks, without factual authority."""

import hashlib
import logging
from collections import Counter
from typing import Any

import pyshacl
import rdflib
from pyshacl import Validator
from pyshacl.graph_abstraction import DataGraph
from rdflib import DCAT, RDF, SH, Graph, URIRef

from gfjd.federation_rdf_input import parse_metadata

VERSION = "gfjd-dcat-base-range-v1"
SHAPE_SHA256 = {
    "shapes.ttl": "7fe9815e0f32b10f5cbce74fa6ccd0290aae3ef9e5080fb84e2d8093eb984d1d",
    "range.ttl": "24d3bfd0fa17a3d0e877c9ebb91c8174124e5038538e1bf081b2cb679ad0f1b2",
}
MAX_SHAPE_BYTES = 1024 * 1024
ENGINE_VERSIONS = {"pyshacl": "0.40.1", "rdflib": "7.6.0"}
_CONSTRAINTS = frozenset(
    name + "ConstraintComponent"
    for name in (
        "Class",
        "Datatype",
        "NodeKind",
        "MinCount",
        "MaxCount",
        "MinExclusive",
        "MinInclusive",
        "MaxExclusive",
        "MaxInclusive",
        "MinLength",
        "MaxLength",
        "Pattern",
        "LanguageIn",
        "UniqueLang",
        "Equals",
        "Disjoint",
        "LessThan",
        "LessThanOrEquals",
        "Not",
        "And",
        "Or",
        "Xone",
        "Node",
        "Property",
        "QualifiedMinCount",
        "QualifiedMaxCount",
        "Closed",
        "HasValue",
        "In",
    )
)


class DCATError(ValueError):
    """Invalid bounded DCAT preparation input."""


def _require(condition: bool) -> None:
    if not condition:
        raise DCATError("DCAT preparation contract violation")


def _counts(report: Graph) -> tuple[dict[str, int], dict[str, int], int]:
    severity: Counter[str] = Counter()
    constraints: Counter[str] = Counter()
    results = set(report.subjects(RDF.type, SH.ValidationResult))
    for result in results:
        levels = list(report.objects(result, SH.resultSeverity))
        components = list(report.objects(result, SH.sourceConstraintComponent))
        _require(len(levels) == len(components) == 1)
        level = next(
            (name for name in ("Violation", "Warning", "Info") if levels[0] == SH[name]), None
        )
        component = next((name for name in _CONSTRAINTS if components[0] == SH[name]), None)
        _require(level is not None and component is not None)
        assert level is not None and component is not None
        severity[level] += 1
        constraints[component] += 1
    return dict(sorted(severity.items())), dict(sorted(constraints.items())), len(results)


def validate_catalogue(data_bytes: bytes, shape_bytes: dict[str, bytes]) -> dict[str, Any]:
    """Execute only bound base/range shapes; never attest full or factual conformance.

    Inputs, shapes and engine options are closed and bounded. Neither source
    loading nor the convenience entrypoint is used. Dependency imports are
    ordinary Python startup, not an operating-system isolation guarantee.
    """
    try:
        _require(type(shape_bytes) is dict and set(shape_bytes) == set(SHAPE_SHA256))
        for name, digest in SHAPE_SHA256.items():
            raw = shape_bytes[name]
            _require(type(raw) is bytes and 0 < len(raw) <= MAX_SHAPE_BYTES)
            _require(hashlib.sha256(raw).hexdigest() == digest)
        _require(pyshacl.__version__ == ENGINE_VERSIONS["pyshacl"])
        _require(rdflib.__version__ == ENGINE_VERSIONS["rdflib"])
        data, statements = parse_metadata(data_bytes)
        catalogues = set(data.subjects(RDF.type, DCAT.Catalog))
        _require(len(catalogues) == 1)
        catalogue = next(iter(catalogues))
        linked = set(data.objects(catalogue, DCAT.dataset))
        typed_datasets = set(data.subjects(RDF.type, DCAT.Dataset))
        _require(bool(linked & typed_datasets))
        shapes = Graph(identifier=URIRef("urn:gfjd:dcat:bound-shapes"))
        for name in sorted(SHAPE_SHA256):
            shapes.parse(data=shape_bytes[name], format="turtle", publicID="urn:gfjd:dcat:" + name)
        logger = logging.Logger("gfjd-dcat-isolated")
        logger.propagate = False
        logger.addHandler(logging.NullHandler())
        validator = Validator(
            DataGraph.from_rdflib(data),
            shacl_graph=shapes,
            ont_graph=None,
            options={
                "logger": logger,
                "debug": False,
                "advanced": False,
                "inference": "none",
                "use_js": False,
                "iterate_rules": False,
                "sparql_mode": False,
                "inplace": False,
                "abort_on_first": False,
                "allow_infos": False,
                "allow_warnings": False,
                "max_validation_depth": 15,
                "focus_nodes": None,
                "use_shapes": None,
            },
        )
        conforms, report, _text = validator.run()  # type: ignore[no-untyped-call]
        _require(type(conforms) is bool and isinstance(report, Graph))
        severity, constraints, count = _counts(report)
        _require(conforms == (count == 0))
        return {
            "contract_version": VERSION,
            "status": "shape_checks_passed" if conforms else "shape_checks_failed",
            "data_sha256": hashlib.sha256(data_bytes).hexdigest(),
            "shape_sha256": dict(sorted(SHAPE_SHA256.items())),
            "engine_versions": dict(ENGINE_VERSIONS),
            "statement_count": statements,
            "triple_count": len(data),
            "catalogue_count": len(catalogues),
            "linked_typed_dataset_count": len(linked & typed_datasets),
            "result_count": count,
            "severity_counts": severity,
            "constraint_counts": constraints,
            "coverage": "DCAT-AP-3.0.1-base-and-range-shapes-only",
            "controlled_vocabularies": "unverified",
            "full_conformance": "unverified",
            "factual_evidence": "unverified",
            "authority": dict.fromkeys(
                (
                    "network",
                    "source_access",
                    "publication",
                    "release",
                    "rights_clearance",
                    "custody",
                    "gold_promotion",
                    "maturity",
                    "gate_acceptance",
                    "partner_registration",
                ),
                False,
            ),
        }
    except DCATError:
        raise
    except Exception:
        # RDF/SHACL exceptions can contain whole supplied terms and reports.
        raise DCATError("DCAT preparation contract violation") from None
