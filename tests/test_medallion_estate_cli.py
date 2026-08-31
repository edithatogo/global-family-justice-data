"""CLI filesystem tests use fictional config metadata and a bounded fake compiler."""

import os
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

FILES = (
    "estate-manifest.json",
    "datasets/gfjd-source-archive/README.md",
    "datasets/gfjd-source-catalogue/README.md",
    "datasets/gfjd-observations/README.md",
    "datasets/gfjd-outcomes-evidence/README.md",
    "datasets/gfjd-extraction-benchmark/README.md",
    "explorer/README.md",
    "explorer/index.html",
)


@pytest.fixture
def cli(project_root: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    if os.name != "posix" or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        pytest.skip("POSIX descriptor-relative filesystem capability is unavailable; not verified")
    module = ModuleType("gfjd.medallion_estate")

    class EstateError(ValueError):
        pass

    def prepare(configs: dict) -> dict:
        assert set(configs) == {
            "config/bootstrap.toml",
            "config/archive_targets.toml",
            "portfolio/products.toml",
            ".gfjd/product.toml",
            "docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md",
        }
        assert all(raw == b"fictional = true\n" for raw in configs.values())
        return {name: b"FICTIONAL OFFLINE DRAFT\n" for name in FILES}

    def verify(configs: dict, artifacts: dict) -> None:
        if artifacts != prepare(configs):
            raise EstateError("fictional mismatch")

    module.EstateError = EstateError  # type: ignore[attr-defined]
    module.POLICY_REFERENCE = (  # type: ignore[attr-defined]
        "docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md"
    )
    module.prepare_estate = prepare  # type: ignore[attr-defined]
    module.verify_estate = verify  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "gfjd.medallion_estate", module)
    script = runpy.run_path(str(project_root / "scripts/prepare_medallion_estate.py"))
    root = tmp_path / "fixture-project"
    root.mkdir()
    for name in script["INPUTFILES"]:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"fictional = true\n")
    script["main"].__globals__["ROOT"] = root
    script["fixture_root"] = root
    return script


def test_fresh_bundle_and_exact_verification(cli: dict, tmp_path: Path) -> None:
    destination = tmp_path / "draft"
    assert cli["main"](["--output", str(destination)]) == 0
    assert {
        str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file()
    } == set(FILES)
    assert cli["main"](["--verify", str(destination)]) == 0
    assert cli["main"](["--output", str(destination)]) == 1
    assert cli["main"](["--verify", str(destination)]) == 0


@pytest.mark.parametrize(
    "mode", ["missing", "extra", "changed", "extra_directory", "oversized", "symlink", "hardlink"]
)
def test_bundle_tampering_fails(cli: dict, tmp_path: Path, mode: str) -> None:
    destination = tmp_path / "draft"
    assert cli["main"](["--output", str(destination)]) == 0
    manifest = destination / "estate-manifest.json"
    if mode == "missing":
        manifest.unlink()
    elif mode == "extra":
        (destination / "unlisted.txt").write_text("fictional")
    elif mode == "changed":
        manifest.write_text("altered fictional bytes")
    elif mode == "extra_directory":
        (destination / "unlisted-directory").mkdir()
    elif mode == "oversized":
        manifest.write_bytes(b"x" * (1024 * 1024 + 1))
    else:
        external = tmp_path / "external"
        external.write_bytes(manifest.read_bytes())
        manifest.unlink()
        if mode == "symlink":
            manifest.symlink_to(external)
        else:
            manifest.hardlink_to(external)
    assert cli["main"](["--verify", str(destination)]) == 1


def test_symlink_root_and_parent_paths_fail(cli: dict, tmp_path: Path) -> None:
    directory = tmp_path / "real"
    directory.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(directory, target_is_directory=True)
    assert cli["main"](["--output", str(alias / "draft")]) == 1
    assert not (directory / "draft").exists()
    assert cli["main"](["--verify", str(alias)]) == 1


@pytest.mark.parametrize("mode", ["missing", "symlink", "oversized", "directory"])
@pytest.mark.parametrize(
    "relative",
    [
        "config/bootstrap.toml",
        "docs/programme/maximal-public-medallion-federation-plan-2026-08-26.md",
    ],
)
def test_config_metadata_inputs_are_regular_and_bounded(
    cli: dict, tmp_path: Path, mode: str, relative: str
) -> None:
    target = cli["fixture_root"] / relative
    target.unlink()
    if mode == "symlink":
        external = tmp_path / "external.toml"
        external.write_bytes(b"fictional = true\n")
        target.symlink_to(external)
    elif mode == "oversized":
        target.write_bytes(b"x" * (1024 * 1024 + 1))
    elif mode == "directory":
        target.mkdir()
    output = tmp_path / "never-created"
    assert cli["main"](["--output", str(output)]) == 1
    assert not output.exists()


def test_compiler_extra_or_unsafe_output_is_rejected(cli: dict, tmp_path: Path) -> None:
    globals_ = cli["main"].__globals__
    prepare = globals_["prepare_estate"]
    globals_["prepare_estate"] = lambda configs: {**prepare(configs), "../outside": b"bad"}
    assert cli["main"](["--output", str(tmp_path / "draft")]) == 1
    assert not (tmp_path / "outside").exists()


def test_existing_empty_output_directory_is_not_reused(cli: dict, tmp_path: Path) -> None:
    output = tmp_path / "already-present"
    output.mkdir()
    assert cli["main"](["--output", str(output)]) == 1
    assert list(output.iterdir()) == []


def test_missing_bundle_and_unknown_nested_entries_stop(cli: dict, tmp_path: Path) -> None:
    output = tmp_path / "draft"
    assert cli["main"](["--verify", str(output)]) == 1
    assert cli["main"](["--output", str(output)]) == 0
    (output / "datasets/unknown-empty-directory").mkdir()
    assert cli["main"](["--verify", str(output)]) == 1


def test_known_directory_replaced_with_symlink(cli: dict, tmp_path: Path) -> None:
    output = tmp_path / "draft"
    assert cli["main"](["--output", str(output)]) == 0
    explorer = output / "explorer"
    moved = tmp_path / "moved-explorer"
    explorer.rename(moved)
    explorer.symlink_to(moved, target_is_directory=True)
    assert cli["main"](["--verify", str(output)]) == 1


def test_real_compiler_current_config_metadata_roundtrip(
    project_root: Path, tmp_path: Path
) -> None:
    if os.name != "posix" or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        pytest.skip("POSIX descriptor-relative filesystem capability is unavailable; not verified")
    # Real declared configuration metadata, not a synthetic empirical dataset.
    script = runpy.run_path(str(project_root / "scripts/prepare_medallion_estate.py"))
    output = tmp_path / "configured-estate-draft"
    assert script["main"](["--output", str(output)]) == 0
    assert script["main"](["--verify", str(output)]) == 0
    assert {str(path.relative_to(output)) for path in output.rglob("*") if path.is_file()} == set(
        FILES
    )


def test_unsupported_filesystem_capability_fails_explicitly(
    project_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    script = runpy.run_path(str(project_root / "scripts/prepare_medallion_estate.py"))
    monkeypatch.delattr(os, "O_NOFOLLOW", raising=False)
    output = tmp_path / "not-created"
    assert script["main"](["--output", str(output)]) == 1
    assert not output.exists()
    message = capsys.readouterr().out
    assert "POSIX filesystem capability missing" in message
    assert "verified" not in message


def test_partial_write_is_preserved_but_never_verified(
    cli: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    real_open = os.open
    writes = 0

    def fail_second_write(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal writes
        if flags & os.O_WRONLY and flags & os.O_CREAT:
            writes += 1
            if writes == 2:
                raise OSError("injected fictional write failure")
        return real_open(path, flags, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(os, "open", fail_second_write)
    output = tmp_path / "partial"
    assert cli["main"](["--output", str(output)]) == 1
    files = [path for path in output.rglob("*") if path.is_file()]
    assert len(files) == 1
    assert files[0].read_bytes() == b"FICTIONAL OFFLINE DRAFT\n"
    assert "verified" not in capsys.readouterr().out
    assert cli["main"](["--verify", str(output)]) == 1
    assert cli["main"](["--output", str(output)]) == 1
    assert files[0].exists()
