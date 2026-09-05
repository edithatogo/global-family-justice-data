"""Render non-destructive active and recorded-completion views of Conductor work."""

import argparse
from pathlib import Path

from gfjd.conductor import Conductor

ROOT = Path(__file__).resolve().parents[1]


def cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def render(conductor: Conductor, *, completed: bool) -> str:
    items = sorted(conductor.work_items.values(), key=lambda item: item.id)
    selected = [item for item in items if (item.status == "accepted") == completed]
    title = "Recorded completed work" if completed else "Active work"
    counterpart = "active-work.md" if completed else "completed-work.md"
    lines = [
        f"# {title}",
        "",
        "Generated from [the canonical register](../../../programme/work_items.csv). "
        "No record, dependency or historical evidence is removed.",
        "",
        f"{len(selected)} of {len(items)} work items. [Other view]({counterpart}).",
        "",
        "Recorded acceptance is not renewed assurance, gate passage or track archival. "
        "Items in review stay active even when implementation tests pass.",
        "",
        "| Track | Recorded accepted | Total | Whole-track archive eligible |",
        "|---|---:|---:|---|",
    ]
    for track in sorted({item.track_id for item in items}):
        group = [item for item in items if item.track_id == track]
        accepted = sum(item.status == "accepted" for item in group)
        # Acceptance counts alone cannot establish current whole-track closure.
        eligibility = "needs current closure review" if accepted == len(group) else "no"
        lines.append(f"| {track} | {accepted} | {len(group)} | {eligibility} |")
    lines += [
        "",
        "| Work item | Track/gate | Status | Title | Evidence IDs | Dependencies |",
        "|---|---|---|---|---|---|",
    ]
    for item in selected:
        dependencies = "; ".join(
            f"{dependency} ({conductor.work_items[dependency].status})"
            for dependency in item.dependency_ids
        )
        lines.append(
            f"| {item.id} | {item.track_id}/{item.gate_id} | {item.status} | "
            f"{cell(item.title)} | {cell('; '.join(item.evidence_ids))} | "
            f"{cell(dependencies)} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    conductor = Conductor.load(ROOT)
    errors = conductor.validate().errors
    if errors:
        raise ValueError(f"Invalid canonical programme: {errors}")
    for name, completed in (("active-work.md", False), ("completed-work.md", True)):
        path = ROOT / "docs/programme/generated" / name
        content = render(conductor, completed=completed)
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Stale or missing work index: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print("Conductor work indexes verified." if args.check else "Conductor work indexes written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
