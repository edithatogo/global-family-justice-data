"""Compatibility entry point for ``python -m gfjd.validate``."""
from __future__ import annotations

import sys

from .validation import validate, validate_project

__all__ = ["validate", "validate_project"]


def main() -> int:
    report = validate_project()
    print(report.render_text(max_issues=200))
    return 0 if report.error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
