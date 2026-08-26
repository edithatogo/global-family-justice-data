from __future__ import annotations

import json
from pathlib import Path

import pytest

from gfjd import bootstrap
from gfjd.bootstrap import BootstrapError, LocalRepository
from gfjd.project import load_project


def test_normalise_remote_url_equates_https_and_ssh() -> None:
    assert bootstrap.normalise_remote_url("https://github.com/example/repo.git") == (
        bootstrap.normalise_remote_url("git@github.com:example/repo.git")
    )


def test_duplicate_remote_groups_detects_clones() -> None:
    first = LocalRepository(
        path="/a/repo",
        name="repo",
        branch="main",
        head="a" * 40,
        last_commit_at="2026-07-27T00:00:00Z",
        dirty=False,
        remotes={"origin": ("https://github.com/example/repo.git",)},
        canonical_remote="https://github.com/example/repo.git",
        github_slug="example/repo",
        huggingface_slug="",
        platform="github",
        relevance_score=1,
        relevance_reasons=("test",),
        product_manifest="",
        product_id="",
    )
    second = LocalRepository(
        **{
            **first.__dict__,
            "path": "/b/repo",
            "remotes": {"origin": ("git@github.com:example/repo.git",)},
            "canonical_remote": "git@github.com:example/repo.git",
        }
    )
    assert bootstrap.duplicate_remote_groups([first, second]) == [
        {"remote": "github:example/repo", "paths": ["/a/repo", "/b/repo"]}
    ]


def test_build_plan_is_schema_valid(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    project = load_project(Path(__file__).resolve().parents[1])
    context = bootstrap.create_context(project, tmp_path / "receipts")
    monkeypatch.setattr(
        bootstrap,
        "discover_github_account",
        lambda _context: {
            "available": True,
            "authenticated": True,
            "login": "example",
            "organizations": [],
        },
    )
    monkeypatch.setattr(
        bootstrap,
        "discover_huggingface_account",
        lambda _context: {
            "available": True,
            "authenticated": True,
            "username": "example",
            "organizations": [],
        },
    )
    monkeypatch.setattr(bootstrap, "discover_local_repositories", lambda _context, roots=None: [])
    monkeypatch.setattr(bootstrap, "list_github_repositories", lambda _context, owner: [])
    monkeypatch.setattr(bootstrap, "list_huggingface_repositories", lambda _context, namespace: [])

    plan = bootstrap.build_plan(context, github_repository="global-family-justice-data")
    bootstrap.validate_bootstrap_plan(context, plan)
    outputs = bootstrap.write_plan(context, plan)
    assert Path(outputs["plan_json"]).is_file()
    assert (
        json.loads(Path(outputs["plan_json"]).read_text(encoding="utf-8"))["schema_version"]
        == "1.0"
    )


def test_apply_requires_explicit_confirmation(tmp_path: Path) -> None:
    project = load_project(Path(__file__).resolve().parents[1])
    context = bootstrap.create_context(project, tmp_path / "receipts")
    with pytest.raises(BootstrapError, match="explicit confirmation"):
        bootstrap.apply_bootstrap(
            context,
            github_owner="example",
            github_repository="global-family-justice-data",
            github_visibility="private",
            author_name="Example",
            author_email="example@example.invalid",
            push=False,
            apply_github_controls=False,
            create_huggingface=False,
            huggingface_namespace="",
            confirmation=False,
        )


def test_huggingface_space_uses_current_sdk_option(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    project = load_project(Path(__file__).resolve().parents[1])
    context = bootstrap.create_context(project, tmp_path / "receipts")
    commands: list[list[str]] = []

    monkeypatch.setattr(bootstrap.shutil, "which", lambda _name: "/usr/bin/hf")
    monkeypatch.setattr(
        bootstrap,
        "discover_huggingface_account",
        lambda _context: {"authenticated": True},
    )

    def fake_run_command(
        _context: bootstrap.BootstrapContext,
        command: list[str],
        **_kwargs: object,
    ) -> bootstrap.CommandResult:
        commands.append(command)
        repo_id = command[3] if command[:3] == ["hf", "repos", "create"] else command[3]
        return bootstrap.CommandResult(
            command=tuple(command),
            cwd=str(project.root),
            returncode=0,
            stdout=json.dumps({"id": repo_id, "private": False, "sha": None}),
            stderr="",
            started_at="2026-07-27T00:00:00Z",
            finished_at="2026-07-27T00:00:00Z",
        )

    monkeypatch.setattr(bootstrap, "run_command", fake_run_command)
    bootstrap.create_huggingface_repositories(context, namespace="example")

    space_create = next(
        command
        for command in commands
        if command[:3] == ["hf", "repos", "create"] and command[3].endswith("gfjd-explorer")
    )
    assert "--space-sdk" in space_create
    assert "--sdk" not in space_create


def test_gfjd_remote_estate_is_public_and_includes_source_archive(tmp_path: Path) -> None:
    project = load_project(Path(__file__).resolve().parents[1])
    context = bootstrap.create_context(project, tmp_path / "receipts")

    assert context.config["bootstrap"]["default_visibility"] == "public"
    assert context.config["github"]["visibility"] == "public"
    huggingface = context.config["huggingface"]
    assert huggingface["private_by_default"] is False
    repositories = huggingface["repositories"]
    assert all(entry["visibility"] == "public" for entry in repositories)
    assert any(
        entry["id"] == "source-archive"
        and entry["name"] == "gfjd-source-archive"
        and entry["publication_mode"] == "public_source_archive"
        for entry in repositories
    )
