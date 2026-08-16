from __future__ import annotations

import hashlib
import json
from pathlib import Path

from gfjd.g2_overlap_successor import DESIGN, verify_overlap_successor_design

ROOT = Path(__file__).resolve().parents[1]


def test_overlap_successor_design_verifies() -> None:
    assert verify_overlap_successor_design(ROOT) == []


def test_overlap_successor_requires_all_observed_urls(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    target.mkdir()
    for relative in (
        "scripts/build_g2_overlap_successor_design.py",
        "src/gfjd/g2_exposure_chain.py",
        "src/gfjd/g2_metadata_search_successor.py",
        "src/gfjd/g2_overlap_successor.py",
        "docs/governance/g2-successor-overlap-stop-owner-decision-2026-08-16.md",
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/design/successor-query-manifest.json",
        "data/methods/g2/G2HOLDOUT-METADATA-EXPANSION-20260816-02/registrar/execution-bundle.json",
        "data/methods/g2/G2HOLDOUT-STRUCTURAL-PREFLIGHT-20260815-01/url-resolution/exposure-ledger.json",
        "data/methods/g2/G2HOLDOUT-PROSPECTIVE-20260815-01/intake/exposure-ledger.json",
    ):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    design = target / DESIGN
    design.mkdir(parents=True)
    for name in ("plan.json", "ledger.json", "query-manifest.json"):
        (design / name).write_bytes((ROOT / DESIGN / name).read_bytes())
    ledger_path = design / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    ledger["denied_urls"] = ledger["denied_urls"][:-1]
    ledger_path.write_text(json.dumps(ledger) + "\n")
    files = [design / "plan.json", ledger_path, design / "query-manifest.json"]
    (design / "SUCCESSOR_DESIGN_MANIFEST.sha256").write_text(
        "\n".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  "
            f"{path.relative_to(target).as_posix()}"
            for path in files
        )
        + "\n"
    )
    assert "all 609 observed URLs are not denied" in verify_overlap_successor_design(target)


def test_overlap_successor_has_no_network_authority() -> None:
    plan = json.loads((ROOT / DESIGN / "plan.json").read_text())
    assert plan["authorization_flags"] == {
        "design_preparation_authorized": True,
        "network_access_authorized": False,
        "source_access_authorized": False,
        "extraction_authorized": False,
        "contact_authorized": False,
        "publication_authorized": False,
        "release_authorized": False,
        "g2_passage_authorized": False,
    }
