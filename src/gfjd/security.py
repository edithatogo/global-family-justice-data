"""Repository-level safety checks for a public aggregate-data project."""
from __future__ import annotations

import csv
from pathlib import Path
import re
from typing import Iterable

from .reporting import Report

FORBIDDEN_SUFFIXES = {".pem", ".p12", ".pfx", ".key", ".keystore"}
FORBIDDEN_FILENAMES = {".env", "credentials.json", "service-account.json", "id_rsa", "id_ed25519"}
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GITHUB_TOKEN", re.compile(r"\bgh[opsu]_[A-Za-z0-9]{30,255}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
)
PROHIBITED_PUBLIC_DATA_HEADERS = {
    "person_name",
    "full_name",
    "date_of_birth",
    "street_address",
    "case_number",
    "email_address",
    "phone_number",
    "national_identifier",
}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".toml",
    ".yml",
    ".yaml",
    ".json",
    ".csv",
    ".txt",
    ".cff",
}


def scan_repository(root: Path) -> Report:
    report = Report("Repository security and public-data scan")
    scanned_files = 0
    for path in _iter_files(root):
        relative = str(path.relative_to(root))
        if path.name in FORBIDDEN_FILENAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            report.error(
                "SECURITY_FORBIDDEN_FILE",
                f"Potential credential or private-key file must not be committed: {relative}",
                path=relative,
            )
        if path.suffix.lower() == ".csv" and _is_public_data_path(path, root):
            _scan_csv_headers(path, root, report)
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 5_000_000:
            scanned_files += 1
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for code, pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    report.error(
                        f"SECURITY_SECRET_{code}",
                        f"Potential secret detected in {relative}",
                        path=relative,
                    )
    report.metrics["text_files_scanned"] = scanned_files
    return report


def _iter_files(root: Path) -> Iterable[Path]:
    excluded_parts = {".git", ".venv", "__pycache__", ".pytest_cache", "build", "dist"}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded_parts for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() in {".zip", ".gz", ".parquet", ".duckdb"}:
            continue
        yield path


def _is_public_data_path(path: Path, root: Path) -> bool:
    parts = path.relative_to(root).parts
    return bool(parts and parts[0] == "data")


def _scan_csv_headers(path: Path, root: Path, report: Report) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            headers = next(reader, [])
    except (OSError, UnicodeError, csv.Error):
        return
    dangerous = sorted({header.strip().lower() for header in headers} & PROHIBITED_PUBLIC_DATA_HEADERS)
    if dangerous:
        report.error(
            "PUBLIC_DATA_PROHIBITED_HEADER",
            "Public data file contains prohibited person-level field(s): " + ", ".join(dangerous),
            path=str(path.relative_to(root)),
        )
