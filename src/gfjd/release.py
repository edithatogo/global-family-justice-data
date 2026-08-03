"""Deterministic release construction, verification and change reporting."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
import zipfile
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .conductor import Conductor
from .io import read_csv, read_json, sha256_file, write_csv, write_json
from .project import Project
from .validation import validate_project

SEMVER = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?P<suffix>[-+][0-9A-Za-z.-]+)?$"
)


class ReleaseError(RuntimeError):
    """Raised when a release fails a contract, gate or integrity condition."""


def build_release(
    project: Project,
    *,
    version: str,
    output_root: Path,
    source_date_epoch: int | None = None,
    allow_version_override: bool = False,
) -> dict[str, Any]:
    match = SEMVER.fullmatch(version)
    if not match:
        raise ReleaseError(f"Invalid semantic version: {version}")
    configured_version = str(project.project_config["version"])
    if version != configured_version and not allow_version_override:
        raise ReleaseError(
            f"Requested version {version} does not match config/project.toml version "
            f"{configured_version}; "
            "update the repository version or use an explicit controlled override"
        )
    epoch = _source_date_epoch(source_date_epoch)
    created_at = datetime.fromtimestamp(epoch, UTC).replace(microsecond=0)
    release_status, required_gate = _release_status_and_gate(version)

    validation = validate_project(project.root, as_of=created_at.date(), include_security=True)
    if validation.error_count:
        raise ReleaseError(
            f"Release validation failed with {validation.error_count} error(s):\n"
            + "\n".join(issue.render() for issue in validation.issues[:30])
        )
    if (
        release_status == "stable"
        and validation.warning_count
        and bool(project.config.get("validation", {}).get("fail_stable_release_on_warnings", True))
    ):
        raise ReleaseError(
            f"Stable release is blocked by {validation.warning_count} validation warning(s)"
        )

    conductor = Conductor.load(project)
    if required_gate and not conductor.gate_result(required_gate).passed:
        result = conductor.gate_result(required_gate)
        raise ReleaseError(
            f"{release_status.replace('_', ' ').title()} release requires {required_gate}, "
            f"which is {result.state} ({result.passed_count}/{result.total_count} criteria passed)"
        )

    output_root = output_root.expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    final_dir = output_root / f"gfjd-{version}"
    final_zip = output_root / f"gfjd-{version}.zip"
    if final_dir.exists() or final_zip.exists():
        raise ReleaseError(f"Release output already exists for version {version} in {output_root}")

    with tempfile.TemporaryDirectory(prefix=".gfjd-release-", dir=output_root) as temp_dir_name:
        temp_dir = Path(temp_dir_name) / f"gfjd-{version}"
        temp_dir.mkdir(parents=True)
        _copy_release_inputs(project, temp_dir)

        status_dir = temp_dir / "programme"
        conductor.render(status_dir, generated_at=created_at)
        _build_lineage_from_release(temp_dir)

        counts = _release_counts(temp_dir)
        release_metadata = {
            "schema_version": "1.0",
            "project_id": "GFJD",
            "version": version,
            "status": release_status,
            "created_at": created_at.isoformat(),
            "source_date_epoch": epoch,
            "contract_version": str(project.project_config["contract_version"]),
            "ontology_version": str(project.project_config["ontology_version"]),
            "programme_gate": required_gate or str(project.project_config.get("current_gate", "")),
            "counts": counts,
            "validation": {
                "errors": validation.error_count,
                "warnings": validation.warning_count,
                "info": validation.info_count,
            },
            "archive": {
                "format": "zip",
                "manifest_algorithm": "sha256",
                "deterministic_timestamp": created_at.isoformat(),
            },
            "source_revision": _source_revision(project.root),
            "known_limitations": _known_limitations(release_status),
            # Publication authority is deliberately explicit.  Draft and RC
            # artifacts must remain private; only a signed G6 decision may set
            # this true in a separately authorised release process.
            "publication": {
                "authorized": False,
                "authority_reference": None,
            },
        }
        _validate_release_metadata(project, release_metadata)
        write_json(temp_dir / "RELEASE.json", release_metadata)
        write_json(temp_dir / "SBOM.spdx.json", _build_spdx_sbom(project, version, created_at))

        manifest_entries = _manifest_entries(temp_dir)
        _write_manifest(temp_dir / "MANIFEST.sha256", manifest_entries)
        _normalise_file_timestamps(temp_dir, epoch)
        _deterministic_zip(temp_dir, final_zip, epoch)
        os.replace(temp_dir, final_dir)

    verification = verify_release(final_dir)
    if verification:
        shutil.rmtree(final_dir, ignore_errors=True)
        final_zip.unlink(missing_ok=True)
        raise ReleaseError("Built release failed verification: " + "; ".join(verification))

    return {
        "version": version,
        "status": release_status,
        "release_dir": str(final_dir),
        "archive_path": str(final_zip),
        "archive_sha256": sha256_file(final_zip),
        "counts": counts,
        "validation": release_metadata["validation"],
    }


def verify_release(release_dir: Path) -> list[str]:
    release_dir = release_dir.expanduser().resolve()
    errors: list[str] = []
    manifest_path = release_dir / "MANIFEST.sha256"
    metadata_path = release_dir / "RELEASE.json"
    sbom_path = release_dir / "SBOM.spdx.json"
    if not manifest_path.exists():
        return [f"Missing MANIFEST.sha256 in {release_dir}"]
    if not metadata_path.exists():
        errors.append(f"Missing RELEASE.json in {release_dir}")
    if not sbom_path.exists():
        errors.append("Missing SBOM.spdx.json")
    else:
        try:
            sbom = read_json(sbom_path)
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid SBOM.spdx.json: {exc}")
        else:
            # This is a structural integrity check, not a substitute for
            # independent supply-chain assurance or vulnerability review.
            required = {"spdxVersion", "SPDXID", "creationInfo", "packages"}
            missing_sbom = (
                sorted(required - set(sbom)) if isinstance(sbom, dict) else sorted(required)
            )
            if missing_sbom:
                errors.append("SBOM missing required SPDX fields: " + ", ".join(missing_sbom))

    if metadata_path.exists():
        try:
            metadata = read_json(metadata_path)
        except (OSError, ValueError):
            metadata = None
        if isinstance(metadata, dict):
            publication = metadata.get("publication")
            if not isinstance(publication, dict):
                errors.append("RELEASE.json missing explicit publication authority boundary")
            else:
                authorized = publication.get("authorized")
                reference = publication.get("authority_reference")
                if metadata.get("status") != "stable" and authorized is not False:
                    errors.append("Non-stable release must remain publication unauthorized")
                if metadata.get("status") == "stable" and (
                    authorized is not True
                    or not isinstance(reference, str)
                    or not reference.strip()
                ):
                    errors.append(
                        "Stable release requires a signed publication authority reference"
                    )

    expected: dict[str, str] = {}
    for line_number, line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            checksum, relative = line.split("  ", 1)
        except ValueError:
            errors.append(f"Malformed manifest line {line_number}")
            continue
        expected[relative] = checksum
    actual_files = {
        path.relative_to(release_dir).as_posix()
        for path in release_dir.rglob("*")
        if path.is_file() and path.name != "MANIFEST.sha256"
    }
    missing = sorted(set(expected) - actual_files)
    extra = sorted(actual_files - set(expected))
    errors.extend(f"Manifest file missing: {path}" for path in missing)
    errors.extend(f"Unmanifested file present: {path}" for path in extra)
    for relative, checksum in sorted(expected.items()):
        path = release_dir / relative
        if path.exists():
            actual = sha256_file(path)
            if actual != checksum:
                errors.append(f"Checksum mismatch: {relative}")
    return errors


def diff_releases(old_dir: Path, new_dir: Path) -> dict[str, Any]:
    old_dir = old_dir.expanduser().resolve()
    new_dir = new_dir.expanduser().resolve()
    errors = [*verify_release(old_dir), *verify_release(new_dir)]
    if errors:
        raise ReleaseError("Cannot diff invalid release(s): " + "; ".join(errors))

    files = {
        "jurisdictions": ("data/seed/jurisdiction_register.csv", "jurisdiction_id"),
        "sources": ("data/seed/source_register.csv", "source_id"),
        "indicators": ("data/seed/indicator_dictionary.csv", "indicator_id"),
        "matter_types": ("data/seed/matter_type_dictionary.csv", "matter_type_id"),
    }
    result: dict[str, Any] = {
        "old_version": read_json(old_dir / "RELEASE.json")["version"],
        "new_version": read_json(new_dir / "RELEASE.json")["version"],
        "tables": {},
    }
    for name, (relative, key) in files.items():
        old_rows = _keyed_csv(old_dir / relative, key)
        new_rows = _keyed_csv(new_dir / relative, key)
        common = set(old_rows) & set(new_rows)
        result["tables"][name] = {
            "added": sorted(set(new_rows) - set(old_rows)),
            "removed": sorted(set(old_rows) - set(new_rows)),
            "changed": sorted(
                identifier for identifier in common if old_rows[identifier] != new_rows[identifier]
            ),
            "unchanged_count": sum(
                old_rows[identifier] == new_rows[identifier] for identifier in common
            ),
        }

    old_observations = _release_observations(old_dir)
    new_observations = _release_observations(new_dir)
    common_obs = set(old_observations) & set(new_observations)
    result["tables"]["observations"] = {
        "added": sorted(set(new_observations) - set(old_observations)),
        "removed": sorted(set(old_observations) - set(new_observations)),
        "changed": sorted(
            identifier
            for identifier in common_obs
            if old_observations[identifier] != new_observations[identifier]
        ),
        "unchanged_count": sum(
            old_observations[identifier] == new_observations[identifier]
            for identifier in common_obs
        ),
    }
    return result


def _copy_release_inputs(project: Project, destination: Path) -> None:
    explicit = [
        "README.md",
        "LICENSE-NOTICE.md",
        "CITATION.cff",
        "V1_0_RELEASE_CRITERIA.md",
        "MATURITY_MODEL.md",
    ]
    for relative in explicit:
        source = project.root / relative
        if source.exists():
            _copy_file(source, destination / relative)
    for pattern in (
        "data/seed/*.csv",
        "data/gold/**/*.csv",
        "schemas/*.json",
        "docs/methods/**/*.md",
        "docs/templates/**/*.md",
        "docs/standards/**/*.md",
        "docs/quality/**/*.md",
    ):
        for source in sorted(project.root.glob(pattern)):
            if source.is_file():
                _copy_file(source, destination / source.relative_to(project.root))
    _copy_file(
        project.root / "config" / "data_contracts.toml",
        destination / "config" / "data_contracts.toml",
    )


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _build_lineage_from_release(release_dir: Path) -> None:
    observation_files = (
        sorted((release_dir / "data" / "gold").rglob("*.csv"))
        if (release_dir / "data" / "gold").exists()
        else []
    )
    headers = [
        "observation_id",
        "source_id",
        "source_edition_id",
        "extraction_id",
        "transformation_rule_id",
        "review_id",
        "provenance_locator",
    ]
    rows: list[dict[str, str]] = []
    for path in observation_files:
        file_headers, file_rows = read_csv(path)
        if "observation_id" not in file_headers:
            continue
        for row in file_rows:
            rows.append({key: row.get(key, "") for key in headers})
    rows.sort(key=lambda row: row["observation_id"])
    write_csv(release_dir / "provenance" / "lineage.csv", headers, rows)


def _release_counts(release_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    table_map = {
        "jurisdictions": release_dir / "data" / "seed" / "jurisdiction_register.csv",
        "sources": release_dir / "data" / "seed" / "source_register.csv",
        "indicators": release_dir / "data" / "seed" / "indicator_dictionary.csv",
        "matter_types": release_dir / "data" / "seed" / "matter_type_dictionary.csv",
    }
    for name, path in table_map.items():
        counts[name] = len(read_csv(path)[1]) if path.exists() else 0
    counts["gold_observations"] = (
        sum(len(read_csv(path)[1]) for path in (release_dir / "data" / "gold").rglob("*.csv"))
        if (release_dir / "data" / "gold").exists()
        else 0
    )
    return counts


def _validate_release_metadata(project: Project, metadata: dict[str, Any]) -> None:
    schema = read_json(project.root / "schemas" / "release.schema.json")
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(metadata),
        key=lambda error: list(error.path),
    )
    if errors:
        raise ReleaseError(
            "RELEASE.json failed schema validation: " + "; ".join(error.message for error in errors)
        )


def _build_spdx_sbom(project: Project, version: str, created_at: datetime) -> dict[str, Any]:
    with (project.root / "pyproject.toml").open("rb") as handle:
        pyproject = tomllib.load(handle)
    dependencies = list(pyproject.get("project", {}).get("dependencies", []))
    packages = [
        {
            "SPDXID": "SPDXRef-Package-GFJD",
            "name": "global-family-justice-data",
            "versionInfo": version,
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
        }
    ]
    relationships = []
    for index, dependency in enumerate(dependencies, start=1):
        name = re.split(r"[<>=!~\[ ]", dependency, maxsplit=1)[0]
        spdx_id = f"SPDXRef-Dependency-{index}"
        packages.append(
            {
                "SPDXID": spdx_id,
                "name": name,
                "versionInfo": dependency[len(name) :] or "NOASSERTION",
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": "NOASSERTION",
                "licenseDeclared": "NOASSERTION",
                "copyrightText": "NOASSERTION",
            }
        )
        relationships.append(
            {
                "spdxElementId": "SPDXRef-Package-GFJD",
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": spdx_id,
            }
        )
    namespace_stamp = created_at.strftime("%Y%m%dT%H%M%SZ")
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"GFJD-{version}-declared-dependencies",
        "documentNamespace": f"https://global-family-justice-data.example/spdx/{version}/{namespace_stamp}",
        "creationInfo": {
            "created": created_at.isoformat(),
            "creators": ["Tool: gfjd-release-builder"],
        },
        "packages": packages,
        "relationships": relationships,
        "comment": (
            "This SBOM records declared project dependencies, not the full host environment."
        ),
    }


def _manifest_entries(root: Path) -> list[tuple[str, str]]:
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.sha256":
            entries.append((sha256_file(path), path.relative_to(root).as_posix()))
    return entries


def _write_manifest(path: Path, entries: Iterable[tuple[str, str]]) -> None:
    lines = [f"{checksum}  {relative}" for checksum, relative in entries]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalise_file_timestamps(root: Path, epoch: int) -> None:
    for path in root.rglob("*"):
        os.utime(path, (epoch, epoch), follow_symlinks=False)
    os.utime(root, (epoch, epoch), follow_symlinks=False)


def _deterministic_zip(source_dir: Path, destination: Path, epoch: int) -> None:
    timestamp = time.gmtime(max(epoch, 315532800))[:6]  # ZIP timestamps begin in 1980.
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            relative = Path(source_dir.name) / path.relative_to(source_dir)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            info.create_system = 3
            archive.writestr(
                info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )


def _source_date_epoch(value: int | None) -> int:
    if value is not None:
        return int(value)
    env = os.getenv("SOURCE_DATE_EPOCH")
    if env:
        return int(env)
    return int(datetime.now(UTC).timestamp())


def _release_status_and_gate(version: str) -> tuple[str, str | None]:
    match = SEMVER.fullmatch(version)
    assert match is not None
    major = int(match.group("major"))
    suffix = match.group("suffix") or ""
    if major == 0:
        return "draft", None
    if suffix.startswith("-rc"):
        return "release_candidate", "G5"
    return "stable", "G6"


def _source_revision(root: Path) -> str | None:
    if os.getenv("GITHUB_SHA"):
        return os.getenv("GITHUB_SHA")
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return None


def _known_limitations(status: str) -> list[str]:
    if status == "stable":
        return []
    return [
        "This is a pre-v1 engineering or programme release and is not a stable "
        "comparative data product.",
        "Programme evidence may be draft or missing; consult programme/programme-status.json.",
        "The source census and outcomes evidence catalogue are incomplete.",
    ]


def _keyed_csv(path: Path, key: str) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    _, rows = read_csv(path)
    return {row[key]: row for row in rows if row.get(key)}


def _release_observations(root: Path) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    gold = root / "data" / "gold"
    if not gold.exists():
        return result
    for path in sorted(gold.rglob("*.csv")):
        _, rows = read_csv(path)
        for row in rows:
            if row.get("observation_id"):
                result[row["observation_id"]] = row
    return result
