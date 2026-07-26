"""Structured reports shared by validation, programme and release commands."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Iterable


class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Issue:
    severity: Severity
    code: str
    message: str
    path: str | None = None
    row: int | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
        }
        if self.path is not None:
            result["path"] = self.path
        if self.row is not None:
            result["row"] = self.row
        if self.context:
            result["context"] = self.context
        return result

    def render(self) -> str:
        location = ""
        if self.path:
            location = self.path
            if self.row is not None:
                location += f":{self.row}"
            location += ": "
        return f"[{self.severity.value.upper()} {self.code}] {location}{self.message}"

    def __str__(self) -> str:
        return self.render()


@dataclass
class Report:
    """A deterministic, serialisable validation or assurance report."""

    name: str
    issues: list[Issue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    checks_run: int = 0

    def add(
        self,
        severity: Severity | str,
        code: str,
        message: str,
        *,
        path: str | Path | None = None,
        row: int | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        normalised = severity if isinstance(severity, Severity) else Severity(severity)
        self.issues.append(
            Issue(
                severity=normalised,
                code=code,
                message=message,
                path=str(path) if path is not None else None,
                row=row,
                context=context or {},
            )
        )

    def error(self, code: str, message: str, **kwargs: Any) -> None:
        self.add(Severity.ERROR, code, message, **kwargs)

    def warning(self, code: str, message: str, **kwargs: Any) -> None:
        self.add(Severity.WARNING, code, message, **kwargs)

    def info(self, code: str, message: str, **kwargs: Any) -> None:
        self.add(Severity.INFO, code, message, **kwargs)

    def extend(self, issues: Iterable[Issue]) -> None:
        self.issues.extend(issues)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity is Severity.WARNING]

    @property
    def infos(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity is Severity.INFO]

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def info_count(self) -> int:
        return len(self.infos)

    def ok(self, *, strict: bool = False) -> bool:
        return self.error_count == 0 and (not strict or self.warning_count == 0)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ok": self.ok(),
            "checks_run": self.checks_run,
            "counts": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
            },
            # Compatibility fields for simple clients.
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "metrics": self.metrics,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def as_dict(self) -> dict[str, Any]:
        return self.to_dict()

    def render_text(self, *, max_issues: int | None = None) -> str:
        status = "PASS" if self.error_count == 0 else "FAIL"
        lines = [
            f"{self.name}: {status}",
            f"Checks: {self.checks_run}; errors: {self.error_count}; "
            f"warnings: {self.warning_count}; info: {self.info_count}",
        ]
        shown = self.issues if max_issues is None else self.issues[:max_issues]
        lines.extend(issue.render() for issue in shown)
        if max_issues is not None and len(self.issues) > max_issues:
            lines.append(f"... {len(self.issues) - max_issues} additional issue(s) omitted")
        return "\n".join(lines)
