import io
from unittest.mock import Mock, patch

import pytest

from gfjd.g2_successor_transport import (
    PeerBoundHTTPSConnection,
    bounded_read,
    resolve_public_addresses,
)


def test_resolver_returns_only_verified_public_addresses() -> None:
    answers = [
        (2, 1, 6, "", ("93.184.216.34", 443)),
        (2, 1, 6, "", ("93.184.216.34", 443)),
    ]
    with patch("socket.getaddrinfo", return_value=answers):
        assert resolve_public_addresses("example.test") == ("93.184.216.34",)


def test_resolver_rejects_private_answer() -> None:
    answers = [(2, 1, 6, "", ("127.0.0.1", 443))]
    with (
        patch("socket.getaddrinfo", return_value=answers),
        pytest.raises(ValueError, match="not public"),
    ):
        resolve_public_addresses("example.test")


def test_peer_bound_connection_verifies_socket_before_tls() -> None:
    raw = Mock()
    raw.getpeername.return_value = ("93.184.216.34", 443)
    tls = Mock()
    tls.getpeername.return_value = ("93.184.216.34", 443)
    context = Mock()
    context.wrap_socket.return_value = tls
    connection = PeerBoundHTTPSConnection(
        "example.test",
        validated_addresses=["93.184.216.34"],
        context=context,
    )
    with patch("socket.create_connection", return_value=raw):
        connection.connect()
    context.wrap_socket.assert_called_once_with(raw, server_hostname="example.test")
    assert connection.sock is tls


def test_peer_mismatch_closes_before_tls() -> None:
    raw = Mock()
    raw.getpeername.return_value = ("8.8.8.8", 443)
    context = Mock()
    connection = PeerBoundHTTPSConnection(
        "example.test",
        validated_addresses=["93.184.216.34"],
        context=context,
    )
    with (
        patch("socket.create_connection", return_value=raw),
        pytest.raises(ValueError, match="connected peer differs"),
    ):
        connection.connect()
    context.wrap_socket.assert_not_called()
    raw.close.assert_called_once()


def test_bounded_read_rejects_overrun() -> None:
    assert bounded_read(io.BytesIO(b"abc"), maximum_bytes=3) == b"abc"  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="exceeds"):
        bounded_read(io.BytesIO(b"abcd"), maximum_bytes=3)  # type: ignore[arg-type]
