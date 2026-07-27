"""Quality-harness checks for locks, coverage, distributions and reproducibility."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import re
import stat
import tarfile
import tomllib
import zipfile
from dataclasses import asdict, dataclass
from email.parser import BytesParser
from email.policy import default as email_policy
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlparse

from .io import sha256_file

_URL = re.compile(r"https?://[^\s\"']+")
_ALLOWED_LOCK_HOSTS = {"pypi.org", "files.pythonhosted.org"}
_FORBIDDEN_HOST_FRAGMENTS = (".internal.", "localhost", "localdomain")


@dataclass(frozen=True, slots=True)
class HarnessIssue:
    severity: str
    code: str
    subject: str
    message: str

    def render(self) -> str:
        return f"[{self.severity.upper()}] {self.code} {self.subject} — {self.message}"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HarnessReport:
    check: str
    issues: tuple[HarnessIssue, ...]
    metrics: dict[str, Any]

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.check,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "metrics": self.metrics,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def render_text(self) -> str:
        header = f"{self.check}: {self.error_count} error(s), {self.warning_count} warning(s)."
        return "\n".join([header, *(issue.render() for issue in self.issues)])


def audit_lockfile(path: Path) -> HarnessReport:
    """Verify that a uv lock is parseable, complete and free of private registries."""

    issues: list[HarnessIssue] = []
    if not path.is_file():
        return HarnessReport(
            "dependency lock",
            (HarnessIssue("error", "LOCK_MISSING", str(path), "uv.lock is required"),),
            {},
        )
    text = path.read_text(encoding="utf-8")
    try:
        payload = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return HarnessReport(
            "dependency lock",
            (HarnessIssue("error", "LOCK_TOML_INVALID", str(path), str(exc)),),
            {},
        )
    packages = payload.get("package", [])
    if not isinstance(packages, list) or not packages:
        issues.append(HarnessIssue("error", "LOCK_EMPTY", str(path), "No packages are locked"))
        packages = []
    names: set[tuple[str, str]] = set()
    for index, package in enumerate(packages, start=1):
        if not isinstance(package, dict):
            issues.append(
                HarnessIssue(
                    "error", "LOCK_PACKAGE_INVALID", f"package[{index}]", "Entry is not a table"
                )
            )
            continue
        name = str(package.get("name", ""))
        version = str(package.get("version", ""))
        if not name or not version:
            issues.append(
                HarnessIssue(
                    "error", "LOCK_PACKAGE_ID", f"package[{index}]", "name and version are required"
                )
            )
        key = (name, version)
        if key in names:
            issues.append(
                HarnessIssue(
                    "error", "LOCK_DUPLICATE", f"{name}=={version}", "Duplicate package entry"
                )
            )
        names.add(key)
    for match in _URL.findall(text):
        cleaned = match.rstrip("],}")
        hostname = (urlparse(cleaned).hostname or "").lower()
        if hostname and hostname not in _ALLOWED_LOCK_HOSTS:
            issues.append(
                HarnessIssue(
                    "error",
                    "LOCK_PRIVATE_OR_UNREVIEWED_HOST",
                    hostname,
                    "Only canonical PyPI lock URLs may be committed",
                )
            )
    lower = text.lower()
    for fragment in _FORBIDDEN_HOST_FRAGMENTS:
        if fragment in lower:
            issues.append(
                HarnessIssue(
                    "error",
                    "LOCK_PRIVATE_FRAGMENT",
                    fragment,
                    "Private host fragment found in lock",
                )
            )
    return HarnessReport(
        "dependency lock",
        tuple(_dedupe_issues(issues)),
        {"package_entries": len(packages), "sha256": sha256_file(path)},
    )


def check_coverage_budget(coverage_json: Path, config_path: Path) -> HarnessReport:
    """Enforce overall and critical-module branch-aware coverage budgets."""

    issues: list[HarnessIssue] = []
    try:
        payload = json.loads(coverage_json.read_text(encoding="utf-8"))
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return HarnessReport(
            "coverage budget",
            (HarnessIssue("error", "COVERAGE_INPUT", str(coverage_json), str(exc)),),
            {},
        )
    section = config.get("coverage", {})
    minimum = float(section.get("overall_minimum", 0.0))
    total = payload.get("totals", {})
    overall = float(total.get("percent_covered", 0.0)) if isinstance(total, dict) else 0.0
    if overall + 1e-9 < minimum:
        issues.append(
            HarnessIssue(
                "error", "COVERAGE_OVERALL", "overall", f"{overall:.2f}% is below {minimum:.2f}%"
            )
        )
    files = payload.get("files", {})
    critical = section.get("critical_modules", {})
    if not isinstance(files, dict) or not isinstance(critical, dict):
        issues.append(
            HarnessIssue(
                "error", "COVERAGE_SHAPE", str(coverage_json), "files/critical_modules must be maps"
            )
        )
    else:
        for filename, required in critical.items():
            record = files.get(str(filename))
            if not isinstance(record, dict):
                issues.append(
                    HarnessIssue(
                        "error",
                        "COVERAGE_FILE_MISSING",
                        str(filename),
                        "Critical module absent from report",
                    )
                )
                continue
            summary = record.get("summary", {})
            percent = (
                float(summary.get("percent_covered", 0.0)) if isinstance(summary, dict) else 0.0
            )
            threshold = float(required)
            if percent + 1e-9 < threshold:
                issues.append(
                    HarnessIssue(
                        "error",
                        "COVERAGE_CRITICAL",
                        str(filename),
                        f"{percent:.2f}% is below {threshold:.2f}%",
                    )
                )
    baseline_path_value = section.get("baseline_file") if isinstance(section, dict) else None
    baseline_overall: float | None = None
    if baseline_path_value:
        baseline_path = (config_path.parent.parent / str(baseline_path_value)).resolve()
        try:
            baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(HarnessIssue("error", "COVERAGE_BASELINE", str(baseline_path), str(exc)))
        else:
            tolerance = float(section.get("ratchet_tolerance", 0.0))
            baseline_overall = float(baseline.get("overall_percent", 0.0))
            if overall + tolerance < baseline_overall:
                issues.append(
                    HarnessIssue(
                        "error",
                        "COVERAGE_RATCHET",
                        "overall",
                        (
                            f"{overall:.2f}% regressed below baseline "
                            f"{baseline_overall:.2f}% by more than {tolerance:.2f} points"
                        ),
                    )
                )
            baseline_files = baseline.get("critical_modules", {})
            if isinstance(files, dict) and isinstance(baseline_files, dict):
                for filename, baseline_value in baseline_files.items():
                    record = files.get(str(filename), {})
                    summary = record.get("summary", {}) if isinstance(record, dict) else {}
                    actual = (
                        float(summary.get("percent_covered", 0.0))
                        if isinstance(summary, dict)
                        else 0.0
                    )
                    expected = float(baseline_value)
                    if actual + tolerance < expected:
                        issues.append(
                            HarnessIssue(
                                "error",
                                "COVERAGE_CRITICAL_RATCHET",
                                str(filename),
                                (
                                    f"{actual:.2f}% regressed below baseline "
                                    f"{expected:.2f}% by more than {tolerance:.2f} points"
                                ),
                            )
                        )
    return HarnessReport(
        "coverage budget",
        tuple(issues),
        {
            "overall_percent": overall,
            "overall_minimum": minimum,
            "baseline_overall_percent": baseline_overall,
            "critical_count": len(critical) if isinstance(critical, dict) else 0,
        },
    )


def check_test_runtime(timing_paths: list[Path], config_path: Path, *, suite: str) -> HarnessReport:
    """Enforce suite and single-test runtime budgets from pytest timing receipts."""

    issues: list[HarnessIssue] = []
    try:
        with config_path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return HarnessReport(
            "test runtime",
            (HarnessIssue("error", "RUNTIME_CONFIG", str(config_path), str(exc)),),
            {},
        )
    budget = config.get("test_runtime", {})
    if not isinstance(budget, dict):
        budget = {}
    suite_key = f"{suite}_suite_seconds"
    suite_limit = float(budget.get(suite_key, 0.0))
    single_limit = float(budget.get("single_test_seconds", 0.0))
    total = 0.0
    tests: dict[str, float] = {}
    for path in timing_paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            issues.append(HarnessIssue("error", "RUNTIME_RECEIPT", str(path), str(exc)))
            continue
        raw_tests = payload.get("tests", {}) if isinstance(payload, dict) else {}
        if not isinstance(raw_tests, dict):
            issues.append(HarnessIssue("error", "RUNTIME_SHAPE", str(path), "tests must be a map"))
            continue
        for node_id, value in raw_tests.items():
            duration = float(value)
            tests[str(node_id)] = max(tests.get(str(node_id), 0.0), duration)
    total = sum(tests.values())
    if suite_limit and total > suite_limit:
        issues.append(
            HarnessIssue(
                "error",
                "RUNTIME_SUITE_BUDGET",
                suite,
                f"{total:.2f}s exceeds {suite_limit:.2f}s",
            )
        )
    for node_id, duration in sorted(tests.items()):
        if single_limit and duration > single_limit:
            issues.append(
                HarnessIssue(
                    "error",
                    "RUNTIME_TEST_BUDGET",
                    node_id,
                    f"{duration:.2f}s exceeds {single_limit:.2f}s",
                )
            )
    return HarnessReport(
        "test runtime",
        tuple(issues),
        {
            "suite": suite,
            "test_count": len(tests),
            "total_test_seconds": round(total, 6),
            "suite_limit_seconds": suite_limit,
            "single_test_limit_seconds": single_limit,
        },
    )


def verify_wheel(path: Path, quality_config: Path) -> HarnessReport:
    """Inspect a wheel as untrusted input, including archive and RECORD integrity."""

    issues: list[HarnessIssue] = []
    config, config_issue = _distribution_config(quality_config)
    if config_issue is not None:
        return HarnessReport("wheel policy", (config_issue,), {})
    limits = _archive_limits(config)
    required = {str(item) for item in config.get("required_files", [])}
    forbidden_paths = tuple(
        str(item).lower() for item in config.get("forbidden_path_fragments", [])
    )
    forbidden_content = tuple(
        str(item).lower() for item in config.get("forbidden_content_fragments", [])
    )
    names: list[str] = []
    total_uncompressed = 0
    total_compressed = 0
    if path.is_file() and path.stat().st_size > limits["max_archive_bytes"]:
        issues.append(
            HarnessIssue(
                "error",
                "WHEEL_ARCHIVE_SIZE",
                str(path),
                f"Archive exceeds {limits['max_archive_bytes']} bytes",
            )
        )
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            names = [item.filename for item in infos]
            if len(infos) > limits["max_members"]:
                issues.append(
                    HarnessIssue(
                        "error",
                        "WHEEL_MEMBER_LIMIT",
                        str(path),
                        f"Archive has {len(infos)} members; limit is {limits['max_members']}",
                    )
                )
            if archive.testzip() is not None:
                issues.append(
                    HarnessIssue("error", "WHEEL_CORRUPT", str(path), "CRC verification failed")
                )
            seen: set[str] = set()
            seen_casefold: dict[str, str] = {}
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                total_uncompressed += info.file_size
                total_compressed += info.compress_size
                if (
                    pure.is_absolute()
                    or "\\" in name
                    or len(name.encode("utf-8")) > limits["max_path_bytes"]
                    or any(part in {"", ".", ".."} for part in pure.parts)
                ):
                    issues.append(
                        HarnessIssue("error", "WHEEL_UNSAFE_PATH", name, "Unsafe archive member")
                    )
                if name in seen:
                    issues.append(
                        HarnessIssue("error", "WHEEL_DUPLICATE", name, "Duplicate archive member")
                    )
                seen.add(name)
                folded = name.casefold()
                if folded in seen_casefold and seen_casefold[folded] != name:
                    issues.append(
                        HarnessIssue(
                            "error",
                            "WHEEL_CASE_COLLISION",
                            name,
                            f"Case-insensitive collision with {seen_casefold[folded]}",
                        )
                    )
                seen_casefold[folded] = name
                if info.flag_bits & 0x1:
                    issues.append(
                        HarnessIssue(
                            "error", "WHEEL_ENCRYPTED", name, "Encrypted members are forbidden"
                        )
                    )
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_ISLNK(mode):
                    issues.append(
                        HarnessIssue("error", "WHEEL_SYMLINK", name, "Symbolic links are forbidden")
                    )
                if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    issues.append(
                        HarnessIssue(
                            "error",
                            "WHEEL_COMPRESSION_METHOD",
                            name,
                            "Only stored and deflated members are permitted",
                        )
                    )
                if info.file_size > limits["max_member_bytes"]:
                    issues.append(
                        HarnessIssue(
                            "error",
                            "WHEEL_MEMBER_SIZE",
                            name,
                            f"Member exceeds {limits['max_member_bytes']} bytes",
                        )
                    )
                if (
                    _compression_ratio(info.file_size, info.compress_size)
                    > limits["max_compression_ratio"]
                ):
                    issues.append(
                        HarnessIssue(
                            "error",
                            "WHEEL_COMPRESSION_RATIO",
                            name,
                            "Member compression ratio exceeds the configured limit",
                        )
                    )
                lower_name = name.lower()
                if any(fragment in lower_name for fragment in forbidden_paths):
                    issues.append(
                        HarnessIssue(
                            "error", "WHEEL_FORBIDDEN_PATH", name, "Forbidden path fragment"
                        )
                    )
                if name.endswith((".py", ".toml", ".json", ".md", ".txt", ".yml", ".yaml")):
                    if info.file_size > limits["max_text_scan_bytes"]:
                        issues.append(
                            HarnessIssue(
                                "error",
                                "WHEEL_TEXT_SCAN_LIMIT",
                                name,
                                "Text member is too large for complete policy scanning",
                            )
                        )
                    else:
                        content = archive.read(name).decode("utf-8", errors="ignore").lower()
                        if any(fragment in content for fragment in forbidden_content):
                            issues.append(
                                HarnessIssue(
                                    "error",
                                    "WHEEL_PRIVATE_CONTENT",
                                    name,
                                    "Private or local fragment",
                                )
                            )
            if total_uncompressed > limits["max_uncompressed_bytes"]:
                issues.append(
                    HarnessIssue(
                        "error",
                        "WHEEL_EXPANDED_SIZE",
                        str(path),
                        f"Expanded archive exceeds {limits['max_uncompressed_bytes']} bytes",
                    )
                )
            if (
                _compression_ratio(total_uncompressed, total_compressed)
                > limits["max_compression_ratio"]
            ):
                issues.append(
                    HarnessIssue(
                        "error",
                        "WHEEL_TOTAL_COMPRESSION_RATIO",
                        str(path),
                        "Overall compression ratio exceeds the configured limit",
                    )
                )
            for expected in sorted(required - set(names)):
                issues.append(
                    HarnessIssue(
                        "error",
                        "WHEEL_REQUIRED_MISSING",
                        expected,
                        "Required package member absent",
                    )
                )
            issues.extend(_verify_wheel_record(archive, names))
            issues.extend(_verify_wheel_metadata(archive, names, config))
    except (OSError, zipfile.BadZipFile, KeyError, csv.Error, RuntimeError) as exc:
        issues.append(HarnessIssue("error", "WHEEL_UNREADABLE", str(path), str(exc)))
    return HarnessReport(
        "wheel policy",
        tuple(_dedupe_issues(issues)),
        {
            "member_count": len(names),
            "compressed_bytes": path.stat().st_size if path.is_file() else 0,
            "uncompressed_bytes": total_uncompressed,
            "sha256": sha256_file(path) if path.is_file() else "",
        },
    )


def verify_sdist(path: Path, quality_config: Path) -> HarnessReport:
    """Inspect a source distribution without extracting it to the filesystem."""

    issues: list[HarnessIssue] = []
    config, config_issue = _distribution_config(quality_config)
    if config_issue is not None:
        return HarnessReport("sdist policy", (config_issue,), {})
    limits = _archive_limits(config)
    required = {str(item) for item in config.get("sdist_required_files", [])}
    forbidden_paths = tuple(
        str(item).lower() for item in config.get("forbidden_path_fragments", [])
    )
    forbidden_content = tuple(
        str(item).lower() for item in config.get("forbidden_content_fragments", [])
    )
    content_allowlist = {
        str(item).replace("\\", "/") for item in config.get("forbidden_content_allowlist_paths", [])
    }
    member_names: list[str] = []
    relative_names: set[str] = set()
    roots: set[str] = set()
    total_uncompressed = 0
    archive_size = path.stat().st_size if path.is_file() else 0
    if archive_size > limits["max_archive_bytes"]:
        issues.append(
            HarnessIssue(
                "error",
                "SDIST_ARCHIVE_SIZE",
                str(path),
                f"Archive exceeds {limits['max_archive_bytes']} bytes",
            )
        )
    try:
        with tarfile.open(path, mode="r:*") as archive:
            members = archive.getmembers()
            if len(members) > limits["max_members"]:
                issues.append(
                    HarnessIssue(
                        "error",
                        "SDIST_MEMBER_LIMIT",
                        str(path),
                        f"Archive has {len(members)} members; limit is {limits['max_members']}",
                    )
                )
            seen: set[str] = set()
            seen_casefold: dict[str, str] = {}
            for member in members:
                name = member.name
                member_names.append(name)
                pure = PurePosixPath(name)
                total_uncompressed += max(member.size, 0)
                if (
                    pure.is_absolute()
                    or "\\" in name
                    or len(name.encode("utf-8")) > limits["max_path_bytes"]
                    or any(part in {"", ".", ".."} for part in pure.parts)
                ):
                    issues.append(
                        HarnessIssue("error", "SDIST_UNSAFE_PATH", name, "Unsafe archive member")
                    )
                    continue
                if name in seen:
                    issues.append(
                        HarnessIssue("error", "SDIST_DUPLICATE", name, "Duplicate archive member")
                    )
                seen.add(name)
                folded = name.casefold()
                if folded in seen_casefold and seen_casefold[folded] != name:
                    issues.append(
                        HarnessIssue(
                            "error",
                            "SDIST_CASE_COLLISION",
                            name,
                            f"Case-insensitive collision with {seen_casefold[folded]}",
                        )
                    )
                seen_casefold[folded] = name
                roots.add(pure.parts[0])
                relative = PurePosixPath(*pure.parts[1:]).as_posix() if len(pure.parts) > 1 else ""
                if relative:
                    relative_names.add(relative)
                if member.issym() or member.islnk() or member.isdev():
                    issues.append(
                        HarnessIssue(
                            "error",
                            "SDIST_UNSAFE_MEMBER",
                            name,
                            "Links and device entries are forbidden",
                        )
                    )
                if any(str(key).startswith("GNU.sparse") for key in member.pax_headers):
                    issues.append(
                        HarnessIssue(
                            "error", "SDIST_SPARSE_MEMBER", name, "Sparse members are forbidden"
                        )
                    )
                if member.size > limits["max_member_bytes"]:
                    issues.append(
                        HarnessIssue(
                            "error",
                            "SDIST_MEMBER_SIZE",
                            name,
                            f"Member exceeds {limits['max_member_bytes']} bytes",
                        )
                    )
                lower_name = name.lower()
                if any(fragment in lower_name for fragment in forbidden_paths):
                    issues.append(
                        HarnessIssue(
                            "error", "SDIST_FORBIDDEN_PATH", name, "Forbidden path fragment"
                        )
                    )
                if (
                    member.isfile()
                    and relative not in content_allowlist
                    and name.endswith((".py", ".toml", ".json", ".md", ".txt", ".yml", ".yaml"))
                ):
                    if member.size > limits["max_text_scan_bytes"]:
                        issues.append(
                            HarnessIssue(
                                "error",
                                "SDIST_TEXT_SCAN_LIMIT",
                                name,
                                "Text member is too large for complete policy scanning",
                            )
                        )
                    else:
                        extracted = archive.extractfile(member)
                        if extracted is not None:
                            content = extracted.read().decode("utf-8", errors="ignore").lower()
                            if any(fragment in content for fragment in forbidden_content):
                                issues.append(
                                    HarnessIssue(
                                        "error",
                                        "SDIST_PRIVATE_CONTENT",
                                        name,
                                        "Private or local fragment",
                                    )
                                )
            if total_uncompressed > limits["max_uncompressed_bytes"]:
                issues.append(
                    HarnessIssue(
                        "error",
                        "SDIST_EXPANDED_SIZE",
                        str(path),
                        f"Expanded archive exceeds {limits['max_uncompressed_bytes']} bytes",
                    )
                )
            if (
                _compression_ratio(total_uncompressed, archive_size)
                > limits["max_compression_ratio"]
            ):
                issues.append(
                    HarnessIssue(
                        "error",
                        "SDIST_TOTAL_COMPRESSION_RATIO",
                        str(path),
                        "Overall compression ratio exceeds the configured limit",
                    )
                )
            if len(roots) != 1:
                issues.append(
                    HarnessIssue(
                        "error",
                        "SDIST_ROOTS",
                        str(path),
                        "Source distribution must have exactly one top-level directory",
                    )
                )
            for expected in sorted(required - relative_names):
                issues.append(
                    HarnessIssue(
                        "error",
                        "SDIST_REQUIRED_MISSING",
                        expected,
                        "Required source-distribution member absent",
                    )
                )
    except (OSError, tarfile.TarError, RuntimeError) as exc:
        issues.append(HarnessIssue("error", "SDIST_UNREADABLE", str(path), str(exc)))
    return HarnessReport(
        "sdist policy",
        tuple(_dedupe_issues(issues)),
        {
            "member_count": len(member_names),
            "compressed_bytes": archive_size,
            "uncompressed_bytes": total_uncompressed,
            "sha256": sha256_file(path) if path.is_file() else "",
        },
    )


def _archive_limits(config: dict[str, Any]) -> dict[str, int | float]:
    defaults: dict[str, int | float] = {
        "max_archive_bytes": 50_000_000,
        "max_members": 5_000,
        "max_uncompressed_bytes": 200_000_000,
        "max_member_bytes": 20_000_000,
        "max_text_scan_bytes": 4_000_000,
        "max_path_bytes": 240,
        "max_compression_ratio": 200.0,
    }
    result: dict[str, int | float] = {}
    for key, default in defaults.items():
        raw = config.get(key, default)
        if isinstance(default, float):
            value: int | float = float(raw)
        else:
            value = int(raw)
        result[key] = value if value > 0 else default
    return result


def _compression_ratio(uncompressed: int, compressed: int) -> float:
    if uncompressed <= 0:
        return 0.0
    if compressed <= 0:
        return float("inf")
    return uncompressed / compressed


def _distribution_config(path: Path) -> tuple[dict[str, Any], HarnessIssue | None]:
    try:
        with path.open("rb") as handle:
            config = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {}, HarnessIssue("error", "QUALITY_CONFIG", str(path), str(exc))
    distribution = config.get("distribution", {})
    if not isinstance(distribution, dict):
        return {}, HarnessIssue(
            "error", "QUALITY_CONFIG", str(path), "[distribution] must be a table"
        )
    return distribution, None


def _verify_wheel_record(archive: zipfile.ZipFile, names: list[str]) -> list[HarnessIssue]:
    issues: list[HarnessIssue] = []
    record_names = [name for name in names if name.endswith(".dist-info/RECORD")]
    if len(record_names) != 1:
        return [
            HarnessIssue(
                "error",
                "WHEEL_RECORD_COUNT",
                "RECORD",
                f"Expected exactly one RECORD file; found {len(record_names)}",
            )
        ]
    record_name = record_names[0]
    rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
    recorded: dict[str, tuple[str, str]] = {}
    for row in rows:
        if len(row) != 3:
            issues.append(
                HarnessIssue("error", "WHEEL_RECORD_ROW", record_name, "RECORD row is malformed")
            )
            continue
        member, digest, size = row
        if member in recorded:
            issues.append(
                HarnessIssue("error", "WHEEL_RECORD_DUPLICATE", member, "Duplicate RECORD row")
            )
        recorded[member] = (digest, size)
    files = {name for name in names if not name.endswith("/")}
    for missing in sorted(files - set(recorded)):
        issues.append(
            HarnessIssue(
                "error", "WHEEL_RECORD_MISSING", missing, "Archive member absent from RECORD"
            )
        )
    for extra in sorted(set(recorded) - files):
        issues.append(
            HarnessIssue("error", "WHEEL_RECORD_EXTRA", extra, "RECORD refers to absent member")
        )
    for member in sorted(files & set(recorded)):
        digest, size = recorded[member]
        if member == record_name:
            if digest or size:
                issues.append(
                    HarnessIssue(
                        "error",
                        "WHEEL_RECORD_SELF_HASH",
                        member,
                        "RECORD must not hash itself",
                    )
                )
            continue
        content = archive.read(member)
        expected = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        if digest != f"sha256={expected}":
            issues.append(
                HarnessIssue("error", "WHEEL_RECORD_HASH", member, "RECORD hash mismatch")
            )
        if size != str(len(content)):
            issues.append(
                HarnessIssue("error", "WHEEL_RECORD_SIZE", member, "RECORD size mismatch")
            )
    return issues


def _verify_wheel_metadata(
    archive: zipfile.ZipFile, names: list[str], config: dict[str, Any]
) -> list[HarnessIssue]:
    issues: list[HarnessIssue] = []
    metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
    wheel_names = [name for name in names if name.endswith(".dist-info/WHEEL")]
    if len(metadata_names) != 1 or len(wheel_names) != 1:
        issues.append(
            HarnessIssue(
                "error",
                "WHEEL_METADATA_COUNT",
                "dist-info",
                "Exactly one METADATA and WHEEL file are required",
            )
        )
        return issues
    metadata = BytesParser(policy=email_policy).parsebytes(archive.read(metadata_names[0]))
    expected_name = str(config.get("expected_project_name", ""))
    if expected_name and metadata.get("Name") != expected_name:
        issues.append(
            HarnessIssue(
                "error",
                "WHEEL_PROJECT_NAME",
                str(metadata.get("Name", "")),
                f"Expected {expected_name}",
            )
        )
    expected_python = str(config.get("requires_python", ""))
    if expected_python and metadata.get("Requires-Python") != expected_python:
        issues.append(
            HarnessIssue(
                "error",
                "WHEEL_REQUIRES_PYTHON",
                str(metadata.get("Requires-Python", "")),
                f"Expected {expected_python}",
            )
        )
    entry_points = [name for name in names if name.endswith(".dist-info/entry_points.txt")]
    if len(entry_points) != 1 or "gfjd = gfjd.cli:main" not in archive.read(entry_points[0]).decode(
        "utf-8"
    ):
        issues.append(
            HarnessIssue(
                "error",
                "WHEEL_ENTRY_POINT",
                "gfjd",
                "Console entry point gfjd = gfjd.cli:main is required",
            )
        )
    return issues


def compare_artifacts(first: Path, second: Path) -> HarnessReport:
    """Require byte-for-byte deterministic artefacts."""

    issues: list[HarnessIssue] = []
    if not first.is_file() or not second.is_file():
        issues.append(
            HarnessIssue(
                "error", "ARTIFACT_MISSING", f"{first} / {second}", "Both artefacts are required"
            )
        )
        return HarnessReport("reproducibility", tuple(issues), {})
    first_hash = sha256_file(first)
    second_hash = sha256_file(second)
    if first_hash != second_hash:
        issues.append(HarnessIssue("error", "ARTIFACT_DRIFT", first.name, "SHA-256 values differ"))
    return HarnessReport(
        "reproducibility",
        tuple(issues),
        {
            "first_sha256": first_hash,
            "second_sha256": second_hash,
            "identical": first_hash == second_hash,
        },
    )


def _dedupe_issues(issues: list[HarnessIssue]) -> list[HarnessIssue]:
    seen: set[tuple[str, str, str, str]] = set()
    result: list[HarnessIssue] = []
    for issue in issues:
        key = (issue.severity, issue.code, issue.subject, issue.message)
        if key not in seen:
            seen.add(key)
            result.append(issue)
    return result
