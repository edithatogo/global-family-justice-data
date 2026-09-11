from __future__ import annotations

import json
from hashlib import sha256

import pytest

from gfjd import medallion_api


def response() -> bytes:
    return json.dumps(
        {
            "took": 7,
            "timed_out": False,
            "_shards": {"total": 20, "successful": 20, "skipped": 0, "failed": 0},
            "hits": {"hits": [], "max_score": None},
            "aggregations": {
                "case_classes": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [{"key": 1389, "key_as_string": "1389", "doc_count": 42}],
                }
            },
        },
        separators=(",", ":"),
    ).encode()


def contract(source: bytes) -> dict[str, object]:
    request = {
        "size": 0,
        "track_total_hits": False,
        "query": {"bool": {"must": [{"match": {"classe.codigo": 1389}}]}},
        "aggs": {"case_classes": {"terms": {"field": "classe.codigo", "size": 20}}},
    }
    return {
        "extraction_version": medallion_api.VERSION,
        "source_sha256": sha256(source).hexdigest(),
        "request": request,
        "class_code": 1389,
        "class_name": "Ação de Alimentos",
    }


def test_aggregate_contract_is_digest_bound_and_recomputable() -> None:
    source = response()
    receipt = medallion_api.extract_aggregate(source, contract(source))
    assert receipt["value"] == 42
    medallion_api.verify_aggregate(source, contract(source), receipt)
    with pytest.raises(medallion_api.MedallionApiError):
        medallion_api.extract_aggregate(source + b"x", contract(source))


def test_aggregate_rejects_case_level_or_ambiguous_buckets() -> None:
    payload = json.loads(response())
    payload["hits"]["hits"] = [{"_source": {"cpf": "x"}}]
    source = json.dumps(payload, separators=(",", ":")).encode()
    with pytest.raises(medallion_api.MedallionApiError):
        medallion_api.extract_aggregate(source, contract(source))


def test_aggregate_rejects_scope_drift_and_contradictory_bucket() -> None:
    source = response()
    wrong_class = contract(source)
    wrong_class["class_code"] = 9999
    with pytest.raises(medallion_api.MedallionApiError):
        medallion_api.extract_aggregate(source, wrong_class)
    contradictory = json.loads(source)
    contradictory["aggregations"]["case_classes"]["buckets"][0]["key_as_string"] = "9999"
    changed = json.dumps(contradictory, separators=(",", ":")).encode()
    with pytest.raises(medallion_api.MedallionApiError):
        medallion_api.extract_aggregate(changed, contract(changed))
