"""Peer-bound HTTPS transport for the prospective G2 successor."""

from __future__ import annotations

import http.client
import socket
import ssl
from collections.abc import Sequence

from .g2_successor_controls import verify_connected_peer


def resolve_public_addresses(hostname: str, *, port: int = 443) -> tuple[str, ...]:
    """Resolve a hostname once and reject empty, invalid or non-public answers."""

    addresses = sorted(
        {str(item[4][0]) for item in socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)}
    )
    for address in addresses:
        verify_connected_peer(
            validated_addresses=addresses,
            connected_peer_address=address,
        )
    return tuple(addresses)


class PeerBoundHTTPSConnection(http.client.HTTPSConnection):
    """Connect to a validated address while retaining hostname TLS checks."""

    def __init__(
        self,
        hostname: str,
        *,
        validated_addresses: Sequence[str],
        port: int = 443,
        timeout: float = 30.0,
        context: ssl.SSLContext | None = None,
    ) -> None:
        if not validated_addresses:
            raise ValueError("validated address set is empty")
        super().__init__(
            hostname,
            port=port,
            timeout=timeout,
            context=context or ssl.create_default_context(),
        )
        self._validated_addresses = tuple(validated_addresses)

    def connect(self) -> None:
        """Pin the socket, verify its peer, then perform hostname-bound TLS."""

        raw = socket.create_connection(
            (self._validated_addresses[0], self.port),
            self.timeout,
            self.source_address,
        )
        try:
            verify_connected_peer(
                validated_addresses=self._validated_addresses,
                connected_peer_address=str(raw.getpeername()[0]),
            )
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
            verify_connected_peer(
                validated_addresses=self._validated_addresses,
                connected_peer_address=str(self.sock.getpeername()[0]),
            )
        except Exception:
            raw.close()
            raise


def bounded_read(response: http.client.HTTPResponse, *, maximum_bytes: int) -> bytes:
    """Read at most the frozen byte limit and fail on overrun."""

    if maximum_bytes < 1:
        raise ValueError("maximum_bytes must be positive")
    body = response.read(maximum_bytes + 1)
    if len(body) > maximum_bytes:
        raise ValueError("response exceeds frozen byte limit")
    return body
