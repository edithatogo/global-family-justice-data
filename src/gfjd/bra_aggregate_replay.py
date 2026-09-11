"""Fail-closed executor for the bound BRA aggregate replay packet.

This module deliberately performs no discovery.  It accepts only the exact
packet, requires an explicit matching packet hash and an API key supplied by
the caller, makes one HTTPS POST, and writes only a digest-bound receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .g2_successor_transport import (
    PeerBoundHTTPSConnection,
    bounded_read,
    resolve_public_addresses,
)
from .medallion_api import (
    FROZEN_CLASS_CODE,
    FROZEN_CLASS_NAME,
    VERSION,
    _canonical,
    extract_aggregate,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACKET = ROOT / "data/federation/bra-aggregate-replay-execution-packet-20260911.json"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024


class BraReplayError(ValueError):
    """A frozen BRA execution contract failed closed."""

    def __init__(self, message: str, *, network_call_started: bool = False) -> None:
        super().__init__(message)
        self.network_call_started = network_call_started


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load_packet(path: Path) -> tuple[dict[str, Any], bytes, str]:
    try:
        raw = path.read_bytes()
        packet = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise BraReplayError(f"failed to load packet: {exc}") from exc
    if not isinstance(packet, dict):
        raise BraReplayError("packet root is not an object")
    if packet.get("packet_id") != "G2-BRA-AGGREGATE-REPLAY-20260911-01":
        raise BraReplayError("unexpected packet identity")
    if packet.get("status") != "awaiting_owner_execution_authorization":
        raise BraReplayError("packet is not awaiting owner execution authorization")
    return packet, raw, _sha(raw)


def verify_packet(packet: dict[str, Any], packet_sha256: str, authorized_sha256: str) -> None:
    if packet_sha256 != authorized_sha256:
        raise BraReplayError("owner authorization does not match packet digest")
    source = packet.get("source")
    request = packet.get("request")
    controls = packet.get("execution_controls")
    if (
        not isinstance(source, dict)
        or not isinstance(request, dict)
        or not isinstance(controls, dict)
    ):
        raise BraReplayError("packet sections are invalid")
    if source.get("method") != "POST" or source.get("class_code") != FROZEN_CLASS_CODE:
        raise BraReplayError("endpoint or class contract drift")
    if source.get("class_name") != FROZEN_CLASS_NAME:
        raise BraReplayError("class label drift")
    if packet.get("request_sha256") != _sha(_canonical(request)):
        raise BraReplayError("request digest does not match adapter canonicalization")
    if controls.get("provider_calls") != 1 or controls.get("retries") != 0:
        raise BraReplayError("provider-call or retry budget drift")
    if (
        controls.get("redirects") is not False
        or controls.get("maximum_response_bytes") != MAX_RESPONSE_BYTES
    ):
        raise BraReplayError("redirect or response-size control drift")
    if (
        controls.get("case_level_records") is not False
        or controls.get("personal_data") is not False
    ):
        raise BraReplayError("prohibited-data boundary drift")
    endpoint = source.get("endpoint")
    parsed = urlsplit(endpoint) if isinstance(endpoint, str) else None
    if (
        not parsed
        or parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
    ):
        raise BraReplayError("endpoint must be credential-free HTTPS")


def verify_owner_authorization(record: dict[str, Any], packet_sha256: str) -> None:
    if not isinstance(record, dict):
        raise BraReplayError("owner authorization record is not an object")
    if record.get("decision_status") != "authorized":
        raise BraReplayError("owner authorization is not active")
    if record.get("packet_sha256") != packet_sha256:
        raise BraReplayError("owner authorization is not bound to this packet")
    if (
        not record.get("owner_identity")
        or record.get("owner_role") != "repository owner and sole accountable decision-maker"
    ):
        raise BraReplayError("owner identity or role is missing")
    if (
        record.get("network_access") is not True
        or record.get("publication") is not False
        or record.get("release") is not False
    ):
        raise BraReplayError("owner authorization boundary is invalid")


def execute(packet: dict[str, Any], packet_sha256: str, api_key: str) -> dict[str, Any]:
    verify_packet(packet, packet_sha256, packet_sha256)
    if not api_key or any(char.isspace() for char in api_key):
        raise BraReplayError("API key is missing or malformed")
    source = packet.get("source")
    request = packet.get("request")
    if not isinstance(source, dict) or not isinstance(request, dict):
        raise BraReplayError("packet structure invalid at execution")
    endpoint = source.get("endpoint")
    if not isinstance(endpoint, str):
        raise BraReplayError("endpoint is missing or invalid")
    parsed = urlsplit(endpoint)
    addresses = resolve_public_addresses(parsed.hostname or "")
    connection = PeerBoundHTTPSConnection(
        parsed.hostname or "", validated_addresses=addresses, timeout=30
    )
    wire_body = json.dumps(
        request, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    network_call_started = False
    try:
        connection.request(
            "POST",
            parsed.path + (("?" + parsed.query) if parsed.query else ""),
            body=wire_body,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "Authorization": f"APIKey {api_key}",
                "Content-Type": "application/json",
            },
        )
        network_call_started = True
        response = connection.getresponse()
        if response.status != 200:
            raise BraReplayError(f"unexpected HTTP status {response.status}")
        content_type = response.getheader("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise BraReplayError("unexpected response content type")
        raw_response = bounded_read(response, maximum_bytes=MAX_RESPONSE_BYTES)
    except BraReplayError as exc:
        exc.network_call_started = network_call_started
        raise
    except Exception as exc:
        raise BraReplayError(str(exc), network_call_started=network_call_started) from exc
    finally:
        connection.close()
    contract = {
        "extraction_version": VERSION,
        "source_sha256": _sha(raw_response),
        "request": request,
        "class_code": FROZEN_CLASS_CODE,
        "class_name": FROZEN_CLASS_NAME,
    }
    adapter_receipt = extract_aggregate(raw_response, contract)
    return {
        "schema_version": "1.0",
        "packet_id": packet["packet_id"],
        "packet_sha256": packet_sha256,
        "executed_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "endpoint": endpoint,
        "request_sha256": packet["request_sha256"],
        "response_sha256": _sha(raw_response),
        "response_bytes": len(raw_response),
        "http_status": 200,
        "content_type": "application/json",
        "adapter": adapter_receipt,
        "raw_response_retained": False,
        "promotion_authorized": False,
        "claim_limit": (
            "supporting reproducibility only; no semantic, rights, maturity, gate, "
            "publication or release acceptance"
        ),
    }


def terminal_failure(
    packet_sha256: str, message: str, *, network_call_started: bool
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "packet_sha256": packet_sha256,
        "terminal": "failed",
        "failed_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "error": message,
        "network_call_started": network_call_started,
        "raw_response_retained": False,
        "retry_authorized": False,
        "promotion_authorized": False,
        "claim_limit": (
            "terminal failure record only; no semantic, rights, maturity, gate, "
            "publication or release acceptance"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--authorized-packet-sha256", required=True)
    parser.add_argument("--authorization-record", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    packet, _, packet_sha256 = load_packet(args.packet)
    verify_packet(packet, packet_sha256, args.authorized_packet_sha256)
    try:
        authorization = json.loads(args.authorization_record.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise BraReplayError(f"failed to load owner authorization: {exc}") from exc
    verify_owner_authorization(authorization, packet_sha256)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "packet_sha256": packet_sha256,
                    "request_sha256": packet["request_sha256"],
                    "network": False,
                }
            )
        )
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        receipt = execute(packet, packet_sha256, os.environ.get("GFJD_BRA_API_KEY", ""))
    except BraReplayError as exc:
        args.output.write_text(
            json.dumps(
                terminal_failure(
                    packet_sha256, str(exc), network_call_started=exc.network_call_started
                ),
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
        return 2
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
