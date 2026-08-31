"""Fictional, in-memory ZIP fixtures for metadata-only artifact selection."""

import io
import stat
import struct
import warnings
import zipfile
from unittest.mock import MagicMock, patch

import pytest

from gfjd.monitor_artifact import MonitorArtifactError, read_monitor_artifact

ROUTE = frozenset({"receipt.json", "exposure-ledger.jsonl", "novel-exposure-ledger.jsonl"})
FICTIONAL = {
    "receipt.json": b'{"fixture": "fictional"}\n',
    "exposure-ledger.jsonl": b'{"fixture": "fictional"}\n',
    "novel-exposure-ledger.jsonl": b"",
}


def archive(members: list[tuple[str | zipfile.ZipInfo, bytes]]) -> bytes:
    stream = io.BytesIO()
    with (
        zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as output,
        warnings.catch_warnings(),
    ):
        warnings.simplefilter("ignore", UserWarning)
        for name, payload in members:
            output.writestr(name, payload)
    return stream.getvalue()


def central_patch(payload: bytes, offset: int, value: int, fmt: str = "<I") -> bytes:
    result = bytearray(payload)
    position = result.index(b"PK\x01\x02")
    struct.pack_into(fmt, result, position + offset, value)
    return bytes(result)


def test_exact_original_bytes_and_empty_ledger_without_log_read() -> None:
    payload = archive([*FICTIONAL.items(), ("execution.log", b"fictional unread log")])
    original = zipfile.ZipFile.open
    opened = []

    def guarded(self: zipfile.ZipFile, name: zipfile.ZipInfo, *args: object, **kwargs: object):
        assert name.filename != "execution.log"
        opened.append(name.filename)
        return original(self, name, *args, **kwargs)

    with patch.object(zipfile.ZipFile, "open", guarded):
        assert read_monitor_artifact(payload, required_members=ROUTE) == FICTIONAL
    assert set(opened) == ROUTE


@pytest.mark.parametrize("names", [[], ["receipt.json"], [*ROUTE, "observations.json"]])
def test_route_requires_exact_metadata_set(names: list[str]) -> None:
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(archive([(name, b"{}") for name in names]), required_members=ROUTE)


@pytest.mark.parametrize(
    "route",
    [
        frozenset(),
        frozenset({"observations.json"}),
        frozenset({"receipt.json", "execution.log"}),
        frozenset({"receipt.json", "unknown.json"}),
        {"receipt.json"},
    ],
)
def test_invalid_route_fails_before_zip_parse(route: frozenset[str]) -> None:
    with (
        patch("gfjd.monitor_artifact.zipfile.ZipFile", side_effect=AssertionError("parsed ZIP")),
        pytest.raises(MonitorArtifactError),
    ):
        read_monitor_artifact(b"", required_members=route)


@pytest.mark.parametrize(
    "name",
    [
        "../receipt.json",
        "./receipt.json",
        "/receipt.json",
        "folder/receipt.json",
        "folder\\receipt.json",
        ".",
        "..",
        "folder/",
        "unknown.json",
        "Receipt.json",
        "receipt.json",
    ],
)
def test_disallowed_names_duplicates_and_case_collisions(name: str) -> None:
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(archive([*FICTIONAL.items(), (name, b"{}")]), required_members=ROUTE)


@pytest.mark.parametrize(
    "mode", [stat.S_IFLNK, stat.S_IFIFO, stat.S_IFSOCK, stat.S_IFCHR, stat.S_IFBLK, stat.S_IFDIR]
)
def test_special_files_rejected_even_for_unread_log(mode: int) -> None:
    info = zipfile.ZipInfo("execution.log")
    info.create_system = 3
    info.external_attr = (mode | 0o600) << 16
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(archive([*FICTIONAL.items(), (info, b"x")]), required_members=ROUTE)


@pytest.mark.parametrize("payload", [b"", b"fictional not a ZIP", b"PK\x03\x04"])
def test_malformed_zip(payload: bytes) -> None:
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(payload, required_members=ROUTE)


def test_input_bound_checked_before_zip_parse() -> None:
    with (
        patch("gfjd.monitor_artifact.zipfile.ZipFile", side_effect=AssertionError("parsed ZIP")),
        pytest.raises(MonitorArtifactError, match="archive byte"),
    ):
        read_monitor_artifact(b"x" * (8 * 1024 * 1024 + 1), required_members=ROUTE)


def test_member_count_bound() -> None:
    with pytest.raises(MonitorArtifactError, match="member count"):
        read_monitor_artifact(archive([("receipt.json", b"{}")] * 33), required_members=ROUTE)


@pytest.mark.parametrize(
    "offset,value,fmt",
    [(24, 8 * 1024 * 1024 + 1, "<I"), (8, 1, "<H"), (10, 99, "<H"), (20, 0, "<I")],
)
def test_untrusted_directory_bounds_and_flags(offset: int, value: int, fmt: str) -> None:
    payload = central_patch(archive(list(FICTIONAL.items())), offset, value, fmt)
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(payload, required_members=ROUTE)


def test_compression_ratio_bound() -> None:
    payload = archive([("receipt.json", b"x" * (2 * 1024 * 1024))])
    with pytest.raises(MonitorArtifactError, match="compression ratio"):
        read_monitor_artifact(payload, required_members=frozenset({"receipt.json"}))


def test_total_expanded_bound_including_unread_log() -> None:
    payload = archive([*FICTIONAL.items(), ("execution.log", b"x")])
    changed = bytearray(payload)
    position = 0
    while (position := changed.find(b"PK\x01\x02", position)) != -1:
        struct.pack_into("<I", changed, position + 20, 9000)
        struct.pack_into("<I", changed, position + 24, 8 * 1024 * 1024)
        position += 4
    with pytest.raises(MonitorArtifactError, match="expanded byte"):
        read_monitor_artifact(bytes(changed), required_members=ROUTE)


def test_selected_crc_failure() -> None:
    payload = central_patch(archive(list(FICTIONAL.items())), 16, 0)
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(payload, required_members=ROUTE)


def test_corrupt_log_crc_is_not_read() -> None:
    payload = archive([("execution.log", b"fictional log"), *FICTIONAL.items()])
    payload = central_patch(payload, 16, 0)
    assert read_monitor_artifact(payload, required_members=ROUTE) == FICTIONAL


def test_observations_route() -> None:
    members = {"receipt.json": b"{}", "observations.json": b"[]\n"}
    assert (
        read_monitor_artifact(archive(list(members.items())), required_members=frozenset(members))
        == members
    )


def test_embedded_nul_is_rejected() -> None:
    payload = archive(list(FICTIONAL.items())).replace(b"receipt.json", b"receipt.jso\x00")
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(payload, required_members=ROUTE)


def test_dos_directory_flag_is_rejected() -> None:
    payload = central_patch(archive(list(FICTIONAL.items())), 38, 0x10)
    with pytest.raises(MonitorArtifactError):
        read_monitor_artifact(payload, required_members=ROUTE)


@pytest.mark.parametrize("returned", [b"", b"xxxx"])
def test_selected_read_is_bounded_and_size_verified(returned: bytes) -> None:
    payload = archive([("receipt.json", b"{}")])
    stream = MagicMock()
    stream.__enter__.return_value = stream
    stream.read.return_value = returned
    with (
        patch.object(zipfile.ZipFile, "open", return_value=stream),
        pytest.raises(MonitorArtifactError, match="size mismatch"),
    ):
        read_monitor_artifact(payload, required_members=frozenset({"receipt.json"}))
    stream.read.assert_called_once_with(3)
