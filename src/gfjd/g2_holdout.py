"""Fail-closed metadata-only selection for the G2 blind holdout."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import posixpath
import subprocess
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker

from .io import sha256_file, write_json

DESIGN_COMMIT = "42b89486b7d71a60ed01eb7e7b1d862e6a736820"
DESIGN_SHA256 = "ab78bb8a609cda84931b1a441c91205a10db28793e0f9f2aabf5371df412a83e"
DESIGN_SCHEMA_SHA256 = "88d477d5231f00234c9b7fa41cb07e9f1d56626324010a73cc97c05edcfc63c2"
OWNER_DECISION_COMMIT = "d9ee23769122d2f912b5d86b5c7cf8df1f9169e4"
OWNER_DECISION_SHA256 = "f3b12478c7c17bfcbd9bc84f7bdb50b050ed522b65ae61679d04f586d06c3340"
OWNER_DECISION_PATH = Path("docs/governance/g2-blind-holdout-design-owner-decision-2026-08-15.md")


class G2HoldoutError(ValueError):
    """Raised when a holdout intake is invalid or cannot satisfy the frozen design."""


@dataclass(frozen=True, slots=True)
class G2HoldoutSelection:
    manifest_path: Path
    receipt_path: Path
    scope_complete: bool


def verify_g2_holdout_selection(root: Path, output_dir: Path) -> list[str]:
    """Independently verify a selection receipt and recompute the frozen selection."""

    resolved_root = root.expanduser().resolve()
    destination = _confined(resolved_root, output_dir, require_exists=False)
    try:
        receipt = _load_object(destination / "selection-receipt.json")
        manifest = _load_object(destination / "candidate-manifest.json")
        _validate(resolved_root, "g2_holdout_selection_receipt.schema.json", receipt)
        _validate(resolved_root, "g2_holdout_candidate_manifest.schema.json", manifest)
        artifacts: dict[str, Path] = {}
        for name in (
            "design",
            "design_schema",
            "owner_decision",
            "candidate_universe",
            "exposure_ledger",
            "candidate_manifest",
        ):
            artifact = receipt[name]
            path = _confined(resolved_root, Path(artifact["path"]))
            if sha256_file(path) != artifact["sha256"]:
                raise G2HoldoutError(f"receipt digest mismatch: {name}")
            artifacts[name] = path
        _verify_frozen_bindings(
            resolved_root,
            artifacts["design"],
            artifacts["design_schema"],
            artifacts["owner_decision"],
        )
        plan = _load_object(artifacts["design"])
        universe = _load_object(artifacts["candidate_universe"])
        ledger = _load_object(artifacts["exposure_ledger"])
        denied = _verified_denylists(resolved_root, ledger)
        candidates = universe["candidates"]
        _verify_candidate_universe(candidates)
        eligible: list[dict[str, Any]] = []
        rejected: list[dict[str, str]] = []
        for candidate in candidates:
            reasons = _rejection_reasons(candidate, *denied)
            if reasons:
                rejected.append(
                    {"candidate_id": candidate["candidate_id"], "reason": "; ".join(reasons)}
                )
                continue
            item = dict(candidate)
            item["proposed_stratum"] = _computed_stratum(candidate, plan["design"])
            item["selection_score"] = _score(manifest["selection_seed"], candidate["candidate_id"])
            eligible.append(item)
        ranked = sorted(eligible, key=lambda item: (item["selection_score"], item["candidate_id"]))
        design = plan["design"]
        allocation = _reserve_allocation(
            ranked, strata=design["strata"], reserve_count=int(design["reserve_count"])
        )
        chosen = _choose_assignments(
            ranked,
            strata=design["strata"],
            per_stratum=int(design["editions_per_stratum"]),
            reserve_allocation=allocation,
            jurisdiction_cap=int(design["maximum_editions_per_jurisdiction"]),
        )
        expected_primary, expected_reserves = chosen if chosen is not None else ([], [])
        failure_reasons = (
            [] if chosen is not None else ["eligible metadata cannot satisfy the frozen 24+6 scope"]
        )
        expected_manifest = {
            "schema_version": "1.0",
            "manifest_id": "G2HOLDOUT-MANIFEST-PROSPECTIVE-20260815-01",
            "design_id": plan["plan_id"],
            "design_commit": DESIGN_COMMIT,
            "selection_seed": manifest["selection_seed"],
            "selection_algorithm": "sha256_seed_nul_candidate_id_ascending_backtracking_v2",
            "metadata_only": True,
            "source_content_accessed": False,
            "scope_complete": chosen is not None,
            "primary": [
                _manifest_entry(item, "primary", index + 1)
                for index, item in enumerate(expected_primary)
            ],
            "reserves": [
                _manifest_entry(item, "reserve", index + 1)
                for index, item in enumerate(expected_reserves)
            ],
            "reserve_allocation": allocation,
            "generated_at": manifest["generated_at"],
            "limitations": failure_reasons,
        }
        if expected_manifest != manifest:
            raise G2HoldoutError("manifest does not reproduce from bound metadata")
        expected_receipt_claims = {
            "eligible_candidate_count": len(eligible),
            "rejected_candidates": rejected,
            "scope_complete": chosen is not None,
            "failure_reasons": failure_reasons,
            "generated_at": manifest["generated_at"],
        }
        if any(receipt[key] != value for key, value in expected_receipt_claims.items()):
            raise G2HoldoutError("receipt claims do not reproduce from bound metadata")
        _verify_manifest_semantics(manifest, design)
    except (G2HoldoutError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as exc:
        return [str(exc)]
    return []


def select_g2_holdout(
    root: Path,
    *,
    candidate_universe_path: Path,
    exposure_ledger_path: Path,
    output_dir: Path,
    seed: str,
    generated_at: str,
    design_path: Path = Path("config/g2_blind_holdout_plan.json"),
) -> G2HoldoutSelection:
    """Select the exact primary and reserve scope without accessing source content."""

    resolved_root = root.expanduser().resolve()
    universe_path = _confined(resolved_root, candidate_universe_path)
    ledger_path = _confined(resolved_root, exposure_ledger_path)
    plan_path = _confined(resolved_root, design_path)
    schema_path = _confined(resolved_root, Path("schemas/g2_blind_holdout_plan.schema.json"))
    decision_path = _confined(resolved_root, OWNER_DECISION_PATH)
    destination = _confined(resolved_root, output_dir, require_exists=False)
    universe = _load_object(universe_path)
    ledger = _load_object(ledger_path)
    plan = _load_object(plan_path)
    _validate(resolved_root, "g2_holdout_candidate_universe.schema.json", universe)
    _validate(resolved_root, "g2_holdout_exposure_ledger.schema.json", ledger)
    _validate(resolved_root, "g2_blind_holdout_plan.schema.json", plan)
    _verify_frozen_bindings(resolved_root, plan_path, schema_path, decision_path)
    if len(seed) < 16:
        raise G2HoldoutError("selection seed must contain at least 16 characters")

    design = plan["design"]
    strata = tuple(design["strata"])
    per_stratum = int(design["editions_per_stratum"])
    jurisdiction_cap = int(design["maximum_editions_per_jurisdiction"])
    target = int(design["recommended_sample_size"])
    reserve_count = int(design["reserve_count"])
    if target != per_stratum * len(strata):
        raise G2HoldoutError("frozen sample size does not equal the stratum allocation")
    if int(design["maximum_editions_per_source_series"]) != 1:
        raise G2HoldoutError("selector requires the frozen one-edition-per-series rule")

    denied_editions, denied_series, denied_urls = _verified_denylists(resolved_root, ledger)
    candidates = universe["candidates"]
    _verify_candidate_universe(candidates)
    eligible: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for candidate in candidates:
        reasons = _rejection_reasons(candidate, denied_editions, denied_series, denied_urls)
        if reasons:
            rejected.append(
                {"candidate_id": candidate["candidate_id"], "reason": "; ".join(reasons)}
            )
            continue
        enriched = dict(candidate)
        enriched["proposed_stratum"] = _computed_stratum(candidate, design)
        enriched["selection_score"] = _score(seed, candidate["candidate_id"])
        eligible.append(enriched)

    ranked = sorted(eligible, key=lambda item: (item["selection_score"], item["candidate_id"]))
    allocation = _reserve_allocation(ranked, strata=strata, reserve_count=reserve_count)
    chosen = _choose_assignments(
        ranked,
        strata=strata,
        per_stratum=per_stratum,
        reserve_allocation=allocation,
        jurisdiction_cap=jurisdiction_cap,
    )
    failure_reasons: list[str] = []
    if chosen is None:
        primary: list[dict[str, Any]] = []
        reserves: list[dict[str, Any]] = []
        failure_reasons.append("eligible metadata cannot satisfy the frozen 24+6 scope")
    else:
        primary, reserves = chosen
        if len({item["jurisdiction_id"] for item in primary}) < int(
            design["minimum_jurisdictions"]
        ):
            failure_reasons.append("selected primary scope does not meet minimum jurisdictions")
    scope_complete = not failure_reasons
    manifest = {
        "schema_version": "1.0",
        "manifest_id": "G2HOLDOUT-MANIFEST-PROSPECTIVE-20260815-01",
        "design_id": plan["plan_id"],
        "design_commit": DESIGN_COMMIT,
        "selection_seed": seed,
        "selection_algorithm": "sha256_seed_nul_candidate_id_ascending_backtracking_v2",
        "metadata_only": True,
        "source_content_accessed": False,
        "scope_complete": scope_complete,
        "primary": [_manifest_entry(item, "primary", i + 1) for i, item in enumerate(primary)],
        "reserves": [_manifest_entry(item, "reserve", i + 1) for i, item in enumerate(reserves)],
        "reserve_allocation": allocation,
        "generated_at": generated_at,
        "limitations": failure_reasons,
    }
    _verify_manifest_semantics(manifest, design)
    destination.mkdir(parents=True, exist_ok=True)
    manifest_path = destination / "candidate-manifest.json"
    write_json(manifest_path, manifest)
    receipt = {
        "schema_version": "1.0",
        "receipt_id": "G2HOLDOUT-SELECTION-PROSPECTIVE-20260815-01",
        "design": _artifact(resolved_root, plan_path),
        "design_schema": _artifact(resolved_root, schema_path),
        "owner_decision": _artifact(resolved_root, decision_path),
        "design_commit": DESIGN_COMMIT,
        "owner_decision_commit": OWNER_DECISION_COMMIT,
        "candidate_universe": _artifact(resolved_root, universe_path),
        "exposure_ledger": _artifact(resolved_root, ledger_path),
        "candidate_manifest": _artifact(resolved_root, manifest_path),
        "metadata_only": True,
        "source_content_accessed": False,
        "eligible_candidate_count": len(eligible),
        "rejected_candidates": rejected,
        "scope_complete": scope_complete,
        "failure_reasons": failure_reasons,
        "generated_at": generated_at,
    }
    receipt_path = destination / "selection-receipt.json"
    write_json(receipt_path, receipt)
    _validate(resolved_root, "g2_holdout_candidate_manifest.schema.json", manifest)
    _validate(resolved_root, "g2_holdout_selection_receipt.schema.json", receipt)
    if not scope_complete:
        raise G2HoldoutError("; ".join(failure_reasons))
    return G2HoldoutSelection(manifest_path, receipt_path, True)


def _rejection_reasons(
    item: Mapping[str, Any],
    denied_editions: set[str],
    denied_series: set[str],
    denied_urls: set[str],
) -> list[str]:
    reasons: list[str] = []
    if item["eligibility"] != "eligible_metadata_only":
        reasons.append(f"eligibility={item['eligibility']}")
    if item["source_content_accessed"]:
        reasons.append("source content accessed")
    if not item["exact_edition_identity_established"]:
        reasons.append("exact edition identity not established")
    if not item["official_publisher"]:
        reasons.append("publisher is not official")
    if item["format"] != "pdf":
        reasons.append("format is not PDF")
    if item.get("source_url") is None:
        reasons.append("exact source URL is not established from public metadata")
    if item["stratum_support"] != "supported_by_public_metadata":
        reasons.append("stratum is not supported by public metadata")
    for key in (
        "terms_screen",
        "rights_screen",
        "privacy_screen",
        "security_screen",
        "prohibited_data_screen",
    ):
        if item[key] != "no_known_metadata_blocker":
            reasons.append(f"{key}={item[key]}")
    if item["edition_id"] in denied_editions:
        reasons.append("edition appears in exposure ledger")
    if item["source_series_id"] in denied_series:
        reasons.append("source series appears in exposure ledger")
    locators = {_canonical_public_url(item["landing_page_url"])}
    if item.get("source_url"):
        locators.add(_canonical_public_url(item["source_url"]))
    if locators & denied_urls:
        reasons.append("URL appears in exposure ledger")
    return reasons


def _choose_assignments(
    ranked: Sequence[dict[str, Any]],
    *,
    strata: Sequence[str],
    per_stratum: int,
    reserve_allocation: Mapping[str, int],
    jurisdiction_cap: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]] | None:
    by_stratum = {
        stratum: [candidate for candidate in ranked if candidate["proposed_stratum"] == stratum]
        for stratum in strata
    }
    slots = [
        *[("primary", stratum) for stratum in strata for _ in range(per_stratum)],
        *[
            ("reserve", stratum)
            for stratum in strata
            for _ in range(int(reserve_allocation[stratum]))
        ],
    ]
    counts: Counter[str] = Counter()
    used_series: set[str] = set()
    used_editions: set[str] = set()
    used_urls: set[str] = set()
    selected: list[dict[str, Any]] = []

    def visit(position: int, offsets: dict[str, int]) -> bool:
        if position == len(slots):
            return True
        _, stratum = slots[position]
        start = offsets.get(stratum, 0)
        for index in range(start, len(by_stratum[stratum])):
            candidate = by_stratum[stratum][index]
            jurisdiction = candidate["jurisdiction_id"]
            series = candidate["source_series_id"]
            edition = candidate["edition_id"]
            source_url = _canonical_public_url(candidate["source_url"])
            if (
                counts[jurisdiction] >= jurisdiction_cap
                or series in used_series
                or edition in used_editions
                or source_url in used_urls
            ):
                continue
            selected.append(candidate)
            counts[jurisdiction] += 1
            used_series.add(series)
            used_editions.add(edition)
            used_urls.add(source_url)
            next_offsets = dict(offsets)
            next_offsets[stratum] = index + 1
            if visit(position + 1, next_offsets):
                return True
            selected.pop()
            counts[jurisdiction] -= 1
            used_series.remove(series)
            used_editions.remove(edition)
            used_urls.remove(source_url)
        return False

    if not visit(0, {}):
        return None
    primary_count = per_stratum * len(strata)
    return list(selected[:primary_count]), list(selected[primary_count:])


def _reserve_allocation(
    eligible: Sequence[Mapping[str, Any]], *, strata: Sequence[str], reserve_count: int
) -> dict[str, int]:
    if reserve_count < len(strata):
        raise G2HoldoutError("reserve count is smaller than the number of strata")
    allocation = {stratum: 1 for stratum in strata}
    counts = Counter(item["proposed_stratum"] for item in eligible)
    extras = reserve_count - len(strata)
    for stratum in sorted(strata, key=lambda value: (-counts[value], value))[:extras]:
        allocation[stratum] += 1
    return allocation


def _computed_stratum(item: Mapping[str, Any], design: Mapping[str, Any]) -> str:
    supported = set(item["supported_strata"])
    for value in design["stratum_assignment_precedence"]:
        stratum = str(value)
        if stratum in supported:
            if item["proposed_stratum"] != stratum:
                raise G2HoldoutError(
                    f"candidate {item['candidate_id']} conflicts with frozen stratum precedence"
                )
            return stratum
    raise G2HoldoutError(f"candidate {item['candidate_id']} has no supported stratum")


def _verified_denylists(
    root: Path, ledger: Mapping[str, Any]
) -> tuple[set[str], set[str], set[str]]:
    if not ledger["limitations"]:
        raise G2HoldoutError("exposure ledger must state its limitations")
    editions = {str(item["edition_id"]) for item in ledger["entries"] if item["edition_id"]}
    series = {
        str(item["source_series_id"]) for item in ledger["entries"] if item["source_series_id"]
    }
    urls = {_deny_url(url) for item in ledger["entries"] for url in item["urls"]}
    if editions != set(ledger["denied_edition_ids"]):
        raise G2HoldoutError("denied edition summary does not match exposure entries")
    if series != set(ledger["denied_source_series_ids"]):
        raise G2HoldoutError("denied source-series summary does not match exposure entries")
    if urls != {_deny_url(url) for url in ledger["denied_urls"]}:
        raise G2HoldoutError("denied URL summary does not match exposure entries")
    for artifact in ledger["evidence_artifacts"]:
        path = _confined(root, Path(artifact["path"]))
        if not _matches_current_or_frozen_design_blob(root, path, str(artifact["sha256"])):
            raise G2HoldoutError(f"exposure evidence digest mismatch: {artifact['path']}")
    referenced_paths = {
        str(path) for entry in ledger["entries"] for path in entry["evidence_paths"]
    }
    artifact_paths = {str(artifact["path"]) for artifact in ledger["evidence_artifacts"]}
    if not referenced_paths <= artifact_paths:
        missing = ", ".join(sorted(referenced_paths - artifact_paths))
        raise G2HoldoutError(f"exposure entry lacks verified evidence artifact: {missing}")
    return editions, series, urls


def _matches_current_or_frozen_design_blob(root: Path, path: Path, expected_sha256: str) -> bool:
    """Verify mutable evidence against current bytes or its frozen design blob."""

    if sha256_file(path) == expected_sha256:
        return True
    repository_path = path.relative_to(root).as_posix()
    try:
        subprocess.run(
            ["git", "verify-commit", DESIGN_COMMIT],
            cwd=root,
            check=True,
            capture_output=True,
        )
        committed = subprocess.run(
            ["git", "show", f"{DESIGN_COMMIT}:{repository_path}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return False
    return hashlib.sha256(committed).hexdigest() == expected_sha256


def _verify_candidate_universe(candidates: Sequence[Mapping[str, Any]]) -> None:
    for field in ("candidate_id", "edition_id"):
        values = [str(candidate[field]) for candidate in candidates]
        if len(values) != len(set(values)):
            raise G2HoldoutError(f"candidate universe contains duplicate {field}")
    for candidate in candidates:
        _canonical_public_url(candidate["landing_page_url"])
        if candidate.get("source_url"):
            _canonical_public_url(candidate["source_url"])


def _verify_frozen_bindings(root: Path, plan: Path, schema: Path, decision: Path) -> None:
    expected = (
        (plan, DESIGN_SHA256, DESIGN_COMMIT, plan.relative_to(root).as_posix()),
        (schema, DESIGN_SCHEMA_SHA256, DESIGN_COMMIT, schema.relative_to(root).as_posix()),
        (
            decision,
            OWNER_DECISION_SHA256,
            OWNER_DECISION_COMMIT,
            decision.relative_to(root).as_posix(),
        ),
    )
    for path, digest, commit, repository_path in expected:
        if sha256_file(path) != digest:
            raise G2HoldoutError(f"frozen binding drift: {repository_path}")
        subprocess.run(["git", "verify-commit", commit], cwd=root, check=True, capture_output=True)
        committed = subprocess.run(
            ["git", "show", f"{commit}:{repository_path}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        if hashlib.sha256(committed).hexdigest() != digest:
            raise G2HoldoutError(f"commit does not contain bound bytes: {repository_path}")


def _verify_manifest_semantics(manifest: Mapping[str, Any], design: Mapping[str, Any]) -> None:
    selected = [*manifest["primary"], *manifest["reserves"]]
    if not manifest["scope_complete"]:
        if selected or not manifest["limitations"]:
            raise G2HoldoutError("failed manifest must be empty and state limitations")
        return
    if len(manifest["primary"]) != 24 or len(manifest["reserves"]) != 6:
        raise G2HoldoutError("complete manifest must contain exactly 24+6 editions")
    for field in ("candidate_id", "edition_id", "source_series_id", "source_url"):
        values = [str(item[field]) for item in selected]
        if len(values) != len(set(values)):
            raise G2HoldoutError(f"complete manifest repeats {field}")
    counts = Counter(item["jurisdiction_id"] for item in selected)
    if max(counts.values(), default=0) > int(design["maximum_editions_per_jurisdiction"]):
        raise G2HoldoutError("complete manifest exceeds jurisdiction cap")
    primary_strata = Counter(item["proposed_stratum"] for item in manifest["primary"])
    if any(primary_strata[stratum] != 6 for stratum in design["strata"]):
        raise G2HoldoutError("complete manifest violates primary stratum quotas")
    reserve_strata = Counter(item["proposed_stratum"] for item in manifest["reserves"])
    allocation = manifest["reserve_allocation"]
    if set(allocation) != set(design["strata"]) or sum(allocation.values()) != 6:
        raise G2HoldoutError("complete manifest has invalid reserve allocation")
    if any(reserve_strata[stratum] != allocation[stratum] for stratum in design["strata"]):
        raise G2HoldoutError("complete manifest violates reserve stratum allocation")


def _canonical_public_url(value: object) -> str:
    parsed = urlsplit(str(value))
    if (
        parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        raise G2HoldoutError(f"candidate locator is not canonical public HTTPS: {value}")
    if parsed.fragment:
        raise G2HoldoutError(f"candidate locator contains a fragment: {value}")
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".local"):
        raise G2HoldoutError(f"candidate locator is not public: {value}")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        try:
            canonical_host = host.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise G2HoldoutError(f"candidate locator has invalid host: {value}") from exc
    else:
        if not address.is_global:
            raise G2HoldoutError(f"candidate locator is not public: {value}")
        canonical_host = f"[{address.compressed}]" if address.version == 6 else address.compressed
    port = "" if parsed.port in (None, 443) else f":{parsed.port}"
    decoded = unquote(parsed.path) or "/"
    path = posixpath.normpath(decoded)
    if decoded.endswith("/") and not path.endswith("/"):
        path += "/"
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunsplit(("https", f"{canonical_host}{port}", path, query, ""))


def _deny_url(value: object) -> str:
    text = str(value)
    parsed = urlsplit(text)
    if parsed.scheme.lower() == "https":
        return _canonical_public_url(text)
    if parsed.scheme.lower() == "file" and not parsed.query and not parsed.fragment:
        return urlunsplit(("file", parsed.netloc, unquote(parsed.path), "", ""))
    raise G2HoldoutError(f"exposure ledger contains unsupported URL: {value}")


def _manifest_entry(item: Mapping[str, Any], assignment: str, rank: int) -> dict[str, Any]:
    return {
        "assignment": assignment,
        "rank": rank,
        "candidate_id": item["candidate_id"],
        "edition_id": item["edition_id"],
        "jurisdiction_id": item["jurisdiction_id"],
        "source_series_id": item["source_series_id"],
        "proposed_stratum": item["proposed_stratum"],
        "landing_page_url": item["landing_page_url"],
        "source_url": item["source_url"],
        "selection_score": item["selection_score"],
    }


def _score(seed: str, candidate_id: str) -> str:
    return hashlib.sha256(f"{seed}\0{candidate_id}".encode()).hexdigest()


def _artifact(root: Path, path: Path) -> dict[str, str]:
    return {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}


def _load_object(path: Path) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise G2HoldoutError(f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicates)
    except json.JSONDecodeError as exc:
        raise G2HoldoutError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise G2HoldoutError(f"expected JSON object: {path}")
    return value


def _validate(root: Path, schema_name: str, instance: object) -> None:
    schema = _load_object(root / "schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        raise G2HoldoutError(f"{schema_name}: {errors[0].message}")


def _confined(root: Path, path: Path, *, require_exists: bool = True) -> Path:
    candidate = path.expanduser()
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise G2HoldoutError(f"path escapes repository: {path}") from exc
    if require_exists and not resolved.is_file():
        raise G2HoldoutError(f"required file does not exist: {path}")
    return resolved
