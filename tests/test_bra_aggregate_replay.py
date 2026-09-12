from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from gfjd import bra_aggregate_replay

PACKET = Path("data/federation/bra-aggregate-replay-execution-packet-20260911.json")


def owner_authorization(packet_sha: str) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "decision_id": "D-G2-BRA-REPLAY-TEST",
        "decided_at": "2026-09-11T19:20:00Z",
        "decision_status": "authorized",
        "owner_identity": "repository owner",
        "owner_role": "repository owner and sole accountable decision-maker",
        "packet_id": "G2-BRA-AGGREGATE-REPLAY-20260911-01",
        "packet_sha256": packet_sha,
        "network_access": True,
        "publication": False,
        "release": False,
        "rights_clearance": False,
        "immutable_reference": "test-owner-reference",
        "conditions": ["exact packet only"],
        "reopen_triggers": ["any stop condition"],
    }


def test_packet_verification_is_digest_and_contract_bound() -> None:
    packet, raw, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    assert packet_sha == hashlib.sha256(raw).hexdigest()
    bra_aggregate_replay.verify_packet(packet, packet_sha, packet_sha)
    with pytest.raises(bra_aggregate_replay.BraReplayError):
        bra_aggregate_replay.verify_packet(packet, packet_sha, "0" * 64)


def test_dry_run_has_no_network_and_reports_exact_bindings(
    capsys: pytest.CaptureFixture[str],
) -> None:
    packet, raw, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    with TemporaryDirectory() as directory:
        authorization_path = Path(directory) / "authorization.json"
        authorization_path.write_text(json.dumps(owner_authorization(packet_sha)))
        assert (
            bra_aggregate_replay.main(
                [
                    "--packet",
                    str(PACKET),
                    "--authorized-packet-sha256",
                    packet_sha,
                    "--authorization-record",
                    str(authorization_path),
                    "--output",
                    str(Path(directory) / "receipt.json"),
                    "--dry-run",
                ]
            )
            == 0
        )
    result = json.loads(capsys.readouterr().out)
    assert result == {
        "packet_sha256": packet_sha,
        "request_sha256": packet["request_sha256"],
        "network": False,
    }
    assert raw


def test_owner_authorization_must_bind_exact_packet() -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="bound to this packet"):
        bra_aggregate_replay.verify_owner_authorization(
            {**owner_authorization("0" * 64), "packet_sha256": "0" * 64},
            packet_sha,
        )


def test_packet_rejects_request_digest_drift() -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    packet["request_sha256"] = "0" * 64
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="request digest"):
        bra_aggregate_replay.verify_packet(packet, packet_sha, packet_sha)


def test_executor_success_uses_one_bound_post(monkeypatch: pytest.MonkeyPatch) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    response_body = json.dumps(
        {
            "took": 1,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {"hits": [], "max_score": None},
            "aggregations": {
                "case_classes": {
                    "doc_count_error_upper_bound": 0,
                    "sum_other_doc_count": 0,
                    "buckets": [{"key": 1389, "key_as_string": "1389", "doc_count": 7}],
                }
            },
        },
        separators=(",", ":"),
    ).encode()

    class Response:
        status = 200

        def getheader(self, name: str, default: str = "") -> str:
            return "application/json" if name == "Content-Type" else default

        def read(self, limit: int) -> bytes:
            return response_body[:limit]

    class Connection:
        requests = 0

        def __init__(self, *args: object, **kwargs: object) -> None:
            self.closed = False

        def request(self, *args: object, **kwargs: object) -> None:
            self.requests += 1

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(bra_aggregate_replay, "resolve_public_addresses", lambda _: ("1.1.1.1",))
    monkeypatch.setattr(bra_aggregate_replay, "PeerBoundHTTPSConnection", Connection)
    receipt = bra_aggregate_replay.execute(packet, packet_sha, "test-key")
    assert receipt["adapter"]["value"] == 7
    assert receipt["raw_response_retained"] is False


def test_executor_records_network_started_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)

    class Response:
        status = 503

        def getheader(self, name: str, default: str = "") -> str:
            return default

    class Connection:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def request(self, *args: object, **kwargs: object) -> None:
            pass

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            pass

    monkeypatch.setattr(bra_aggregate_replay, "resolve_public_addresses", lambda _: ("1.1.1.1",))
    monkeypatch.setattr(bra_aggregate_replay, "PeerBoundHTTPSConnection", Connection)
    with pytest.raises(bra_aggregate_replay.BraReplayError) as error:
        bra_aggregate_replay.execute(packet, packet_sha, "test-key")
    assert error.value.network_call_started is True
    failure = bra_aggregate_replay.terminal_failure(
        packet_sha, str(error.value), network_call_started=error.value.network_call_started
    )
    assert failure["terminal"] == "failed"
    assert failure["retry_authorized"] is False


def test_executor_converts_adapter_failure_to_terminal_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)

    class Response:
        status = 200

        def getheader(self, name: str, default: str = "") -> str:
            return "application/json" if name == "Content-Type" else default

        def read(self, limit: int) -> bytes:
            return b"{}"

    class Connection:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def request(self, *args: object, **kwargs: object) -> None:
            pass

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            pass

    monkeypatch.setattr(bra_aggregate_replay, "resolve_public_addresses", lambda _: ("1.1.1.1",))
    monkeypatch.setattr(bra_aggregate_replay, "PeerBoundHTTPSConnection", Connection)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="contract violation") as error:
        bra_aggregate_replay.execute(packet, packet_sha, "test-key")
    assert error.value.network_call_started is True


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda packet: packet.pop("source"), "packet sections"),
        (lambda packet: packet["source"].update(method="GET"), "endpoint"),
        (lambda packet: packet["source"].update(class_name="wrong"), "class label"),
        (lambda packet: packet["execution_controls"].update(provider_calls=2), "provider-call"),
        (lambda packet: packet["execution_controls"].update(redirects=True), "redirect"),
        (lambda packet: packet["execution_controls"].update(personal_data=True), "prohibited"),
        (lambda packet: packet["source"].update(endpoint="http://example.test"), "HTTPS"),
    ],
)
def test_packet_contract_failures_are_explicit(mutation, message: str) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    mutation(packet)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match=message):
        bra_aggregate_replay.verify_packet(packet, packet_sha, packet_sha)


def test_load_and_owner_authorization_failures_are_explicit() -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "bad.json"
        path.write_text("{")
        with pytest.raises(bra_aggregate_replay.BraReplayError, match="failed to load packet"):
            bra_aggregate_replay.load_packet(path)
        path.write_text("[]")
        with pytest.raises(bra_aggregate_replay.BraReplayError, match="root"):
            bra_aggregate_replay.load_packet(path)
        packet, raw, _ = bra_aggregate_replay.load_packet(PACKET)
        malformed = json.loads(raw)
        malformed["packet_id"] = "other"
        path.write_text(json.dumps(malformed))
        with pytest.raises(bra_aggregate_replay.BraReplayError, match="identity"):
            bra_aggregate_replay.load_packet(path)
        malformed["packet_id"] = packet["packet_id"]
        malformed["status"] = "done"
        path.write_text(json.dumps(malformed))
        with pytest.raises(bra_aggregate_replay.BraReplayError, match="awaiting"):
            bra_aggregate_replay.load_packet(path)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="not an object"):
        bra_aggregate_replay.verify_owner_authorization([], "0" * 64)  # type: ignore[arg-type]
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="schema validation"):
        bra_aggregate_replay.verify_owner_authorization({}, "0" * 64)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="schema validation"):
        bra_aggregate_replay.verify_owner_authorization(
            {
                **owner_authorization("0" * 64),
                "owner_identity": "",
                "owner_role": "wrong",
            },
            "0" * 64,
        )
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="schema validation"):
        bra_aggregate_replay.verify_owner_authorization(
            {**owner_authorization("0" * 64), "network_access": False},
            "0" * 64,
        )


def test_owner_authorization_schema_unavailability_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bra_aggregate_replay, "AUTHORIZATION_SCHEMA", Path("/missing/schema.json"))
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="schema unavailable"):
        bra_aggregate_replay.verify_owner_authorization(owner_authorization("0" * 64), "0" * 64)


def test_execute_rejects_missing_key_and_malformed_execution_packet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="API key"):
        bra_aggregate_replay.execute(packet, packet_sha, "")
    malformed = dict(packet)
    malformed.pop("source")
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="packet sections"):
        bra_aggregate_replay.execute(malformed, packet_sha, "key")
    malformed = dict(packet)
    malformed["source"] = dict(packet["source"])
    malformed["source"].pop("endpoint")
    monkeypatch.setattr(bra_aggregate_replay, "verify_packet", lambda *args: None)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="endpoint is missing"):
        bra_aggregate_replay.execute(malformed, packet_sha, "key")


def test_executor_rejects_wrong_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)

    class Response:
        status = 200

        def getheader(self, name: str, default: str = "") -> str:
            return "text/html" if name == "Content-Type" else default

    class Connection:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def request(self, *args: object, **kwargs: object) -> None:
            pass

        def getresponse(self) -> Response:
            return Response()

        def close(self) -> None:
            pass

    monkeypatch.setattr(bra_aggregate_replay, "resolve_public_addresses", lambda _: ("1.1.1.1",))
    monkeypatch.setattr(bra_aggregate_replay, "PeerBoundHTTPSConnection", Connection)
    with pytest.raises(bra_aggregate_replay.BraReplayError, match="content type"):
        bra_aggregate_replay.execute(packet, packet_sha, "key")


def test_main_success_writes_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    with TemporaryDirectory() as directory:
        auth = Path(directory) / "auth.json"
        out = Path(directory) / "receipt.json"
        auth.write_text(json.dumps(owner_authorization(packet_sha)))
        monkeypatch.setattr(
            bra_aggregate_replay,
            "execute",
            lambda packet, packet_sha256, api_key: {"terminal": "success"},
        )
        assert (
            bra_aggregate_replay.main(
                [
                    "--packet",
                    str(PACKET),
                    "--authorized-packet-sha256",
                    packet_sha,
                    "--authorization-record",
                    str(auth),
                    "--output",
                    str(out),
                ]
            )
            == 0
        )
        assert json.loads(out.read_text())["terminal"] == "success"


def test_main_writes_terminal_failure_without_api_key(capsys: pytest.CaptureFixture[str]) -> None:
    packet, _, packet_sha = bra_aggregate_replay.load_packet(PACKET)
    with TemporaryDirectory() as directory:
        auth = Path(directory) / "auth.json"
        out = Path(directory) / "receipt.json"
        auth.write_text(json.dumps(owner_authorization(packet_sha)))
        assert (
            bra_aggregate_replay.main(
                [
                    "--packet",
                    str(PACKET),
                    "--authorized-packet-sha256",
                    packet_sha,
                    "--authorization-record",
                    str(auth),
                    "--output",
                    str(out),
                ]
            )
            == 2
        )
        assert json.loads(out.read_text())["terminal"] == "failed"
