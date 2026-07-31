#!/usr/bin/env python3
"""Plan, apply and verify the GFJD local/GitHub/Hugging Face bootstrap.

The script runs directly from a source checkout without requiring package installation.
It is deliberately plan-first and requires ``--yes`` before any remote mutation.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gfjd.bootstrap import (  # noqa: E402
    BootstrapError,
    apply_bootstrap,
    build_plan,
    create_context,
    preflight,
    validate_bootstrap_plan,
    verify_audit_log,
    verify_bootstrap_receipt,
    write_plan,
)
from gfjd.project import load_project  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("preflight", help="inspect tools and repository state without mutation")

    plan = commands.add_parser("plan", help="discover local clones and write a dry-run plan")
    _add_discovery_arguments(plan)
    plan.add_argument("--output", type=Path, default=Path("build/bootstrap"))

    apply = commands.add_parser("apply", help="initialise Git and create/wire remote repositories")
    apply.add_argument("--output", type=Path, default=Path("build/bootstrap"))
    apply.add_argument("--github-owner", default="")
    apply.add_argument("--github-repository", default="")
    apply.add_argument(
        "--github-visibility", choices=("private", "public", "internal"), default="private"
    )
    apply.add_argument("--author-name", default="")
    apply.add_argument("--author-email", default="")
    apply.add_argument("--no-push", action="store_true")
    apply.add_argument("--apply-github-controls", action="store_true")
    apply.add_argument("--create-huggingface", action="store_true")
    apply.add_argument("--huggingface-namespace", default="")
    apply.add_argument("--yes", action="store_true", help="confirm remote-changing operations")

    verify = commands.add_parser("verify", help="verify bootstrap receipt and audit chain")
    verify.add_argument(
        "--receipt", type=Path, default=Path("build/bootstrap/bootstrap-receipt.json")
    )
    verify.add_argument(
        "--audit-log", type=Path, default=Path("build/bootstrap/bootstrap-audit.jsonl")
    )
    return parser


def _add_discovery_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scan-root", action="append", type=Path, default=[])
    parser.add_argument("--github-owner", default="")
    parser.add_argument("--github-repository", default="")
    parser.add_argument("--huggingface-namespace", default="")


def _resolve(root: Path, value: Path) -> Path:
    return value.expanduser().resolve() if value.is_absolute() else (root / value).resolve()


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        project = load_project(args.root)
        if args.command == "preflight":
            context = create_context(project)
            print(json.dumps(preflight(context), indent=2, ensure_ascii=False, sort_keys=True))
            return 0

        if args.command == "plan":
            output = _resolve(project.root, args.output)
            context = create_context(project, output)
            roots = [_resolve(project.root, value) for value in args.scan_root] or None
            plan = build_plan(
                context,
                scan_roots=roots,
                github_owner=args.github_owner,
                github_repository=args.github_repository,
                huggingface_namespace=args.huggingface_namespace,
            )
            validate_bootstrap_plan(context, plan)
            paths = write_plan(context, plan)
            print(json.dumps({"plan": plan, "outputs": paths}, indent=2, ensure_ascii=False))
            return 0

        if args.command == "apply":
            output = _resolve(project.root, args.output)
            context = create_context(project, output)
            receipt = apply_bootstrap(
                context,
                github_owner=args.github_owner,
                github_repository=args.github_repository,
                github_visibility=args.github_visibility,
                author_name=args.author_name,
                author_email=args.author_email,
                push=not args.no_push,
                apply_github_controls=args.apply_github_controls,
                create_huggingface=args.create_huggingface,
                huggingface_namespace=args.huggingface_namespace,
                confirmation=args.yes,
            )
            print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))
            return 0

        receipt_path = _resolve(project.root, args.receipt)
        audit_path = _resolve(project.root, args.audit_log)
        errors = verify_bootstrap_receipt(receipt_path) + verify_audit_log(audit_path)
        if errors:
            print("Bootstrap verification failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print("Bootstrap receipt and audit chain verified.")
        return 0
    except (BootstrapError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
