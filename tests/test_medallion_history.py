"""Fictional string-only correction journals; no external source access."""

import copy
import hashlib
import json

import pytest

from gfjd.medallion_history import (
    build_event,
    replay_history,
    replay_partition,
    verify_append_only,
)
from gfjd.medallion_replay import VERSION


def revision(
    value: str,
    recorded: str,
    *,
    partition: str = "fictional",
    parent: str | None = None,
    valid_from: str | None = "2026-01-01T00:00:00Z",
    valid_until: str | None = None,
) -> tuple[dict, dict[str, bytes]]:
    source = json.dumps([{"fictional_source": value}]).encode()
    digest = hashlib.sha256(source).hexdigest()
    contract = {
        "contract_version": VERSION,
        "source_sha256": digest,
        "projection": {"fictional_output": "fictional_source"},
        "valid_from": valid_from,
        "recorded_at": recorded,
    }
    event = build_event(
        source, contract, partition=partition, supersedes=parent, valid_until=valid_until
    )
    return event, {digest: source}


def chain() -> tuple[list[dict], dict[str, bytes]]:
    first, sources = revision("fictional old", "2026-02-01T00:00:00Z")
    second, more = revision(
        "fictional correction", "2026-03-01T00:00:00Z", parent=first["event_id"]
    )
    return [first, second], {**sources, **more}


def test_deterministic_source_replay_and_derived_clock() -> None:
    events, sources = chain()
    original = copy.deepcopy(events)
    receipt = replay_history(events, sources)
    assert receipt == replay_history(events, sources)
    assert receipt["revisions"][0]["recorded_until"] == "2026-03-01T00:00:00Z"
    assert receipt["revisions"][1]["recorded_until"] is None
    assert receipt["promotion_authorized"] is False
    assert events == original
    assert "recorded_until" not in events[0]


@pytest.mark.parametrize(
    "at,value",
    [("2026-02-01T00:00:00Z", "fictional old"), ("2026-03-01T00:00:00Z", "fictional correction")],
)
def test_recorded_half_open_query(at: str, value: str) -> None:
    events, sources = chain()
    result = replay_partition(events, sources, partition="fictional", recorded_as_of=at)
    assert result["status"] == "replayed"
    assert result["rows"] == [{"fictional_output": value}]
    assert result["promotion_authorized"] is False


def test_no_fallback_to_superseded_valid_period() -> None:
    first, sources = revision("fictional old", "2026-02-01T00:00:00Z")
    second, more = revision(
        "fictional new",
        "2026-03-01T00:00:00Z",
        parent=first["event_id"],
        valid_from="2026-03-01T00:00:00Z",
        valid_until="2026-04-01T00:00:00Z",
    )
    for at in ("2026-02-01T00:00:00Z", "2026-04-01T00:00:00Z"):
        result = replay_partition(
            [first, second],
            {**sources, **more},
            partition="fictional",
            recorded_as_of="2026-03-15T00:00:00Z",
            valid_as_of=at,
        )
        assert result["status"] == "outside_valid_interval"
        assert result["rows"] == []


def test_unknown_valid_clock_and_not_yet_recorded() -> None:
    event, sources = revision("fictional", "2026-02-01T00:00:00Z", valid_from=None)
    result = replay_partition(
        [event],
        sources,
        partition="fictional",
        recorded_as_of="2026-03-01T00:00:00Z",
        valid_as_of="2026-01-01T00:00:00Z",
    )
    assert result["status"] == "valid_time_unknown"
    assert result["rows"] == []
    assert (
        replay_partition(
            [event], sources, partition="fictional", recorded_as_of="2026-01-01T00:00:00Z"
        )["status"]
        == "not_recorded"
    )


@pytest.mark.parametrize("target", ["rows", "field_lineage", "promotion_authorized"])
def test_forged_projection_even_after_rehash_fails(target: str) -> None:
    events, sources = chain()
    events[0]["projection_receipt"][target] = [] if target != "promotion_authorized" else True
    body = {key: value for key, value in events[0].items() if key != "event_id"}
    events[0]["event_id"] = hashlib.sha256(
        json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    with pytest.raises(ValueError):
        replay_history(events[:1], sources)


def test_missing_and_changed_source_fail() -> None:
    events, sources = chain()
    with pytest.raises(ValueError):
        replay_history(events, {})
    sources[events[0]["source_sha256"]] = b'[{"fictional_source":"changed"}]'
    with pytest.raises(ValueError):
        replay_history(events, sources)


def test_append_prefix_is_exact_and_both_sides_recomputed() -> None:
    events, sources = chain()
    verify_append_only(events[:1], events, sources)
    with pytest.raises(ValueError):
        verify_append_only(events, events[:1], sources)
    different, more = revision("fictional different", "2026-02-01T00:00:00Z")
    with pytest.raises(ValueError):
        verify_append_only(events[:1], [different], {**sources, **more})


def test_invalid_parent_and_fork() -> None:
    events, sources = chain()
    fork, more = revision("fictional fork", "2026-04-01T00:00:00Z", parent=events[0]["event_id"])
    with pytest.raises(ValueError):
        replay_history([*events, fork], {**sources, **more})
    with pytest.raises(ValueError):
        replay_history(events[1:], sources)
    with pytest.raises(ValueError):
        replay_history([events[0], events[0]], sources)


def test_distinct_partitions_may_share_recorded_instant() -> None:
    first, sources = revision("fictional one", "2026-02-01T00:00:00Z", partition="one")
    second, more = revision("fictional two", "2026-02-01T00:00:00Z", partition="two")
    assert len(replay_history([first, second], {**sources, **more})["revisions"]) == 2
    crossing, extra = revision(
        "fictional bad", "2026-03-01T00:00:00Z", partition="two", parent=first["event_id"]
    )
    with pytest.raises(ValueError):
        replay_history([first, crossing], {**sources, **extra})


@pytest.mark.parametrize("clock", ["2026-02-01T00:00:00Z", "2026-01-01T00:00:00Z"])
def test_same_partition_clock_strict(clock: str) -> None:
    first, sources = revision("fictional one", "2026-02-01T00:00:00Z")
    second, more = revision("fictional two", clock, parent=first["event_id"])
    with pytest.raises(ValueError):
        replay_history([first, second], {**sources, **more})


@pytest.mark.parametrize(
    "start,end",
    [
        (None, "2026-02-01T00:00:00Z"),
        ("2026-02-01T00:00:00Z", "2026-02-01T00:00:00Z"),
        ("2026-03-01T00:00:00Z", "2026-02-01T00:00:00Z"),
    ],
)
def test_invalid_valid_interval(start: str | None, end: str | None) -> None:
    with pytest.raises(ValueError):
        revision("fictional", "2026-02-01T00:00:00Z", valid_from=start, valid_until=end)


@pytest.mark.parametrize("partition", ["../unsafe", "", "a" * 129, "with space"])
def test_partition_name_bound(partition: str) -> None:
    with pytest.raises(ValueError):
        revision("fictional", "2026-02-01T00:00:00Z", partition=partition)


def test_event_and_source_budget() -> None:
    events, sources = chain()
    with pytest.raises(ValueError):
        replay_history(events[:1] * 101, sources)
    with pytest.raises(ValueError):
        replay_history([], {"a" * 64: b"x" * (8 * 1024 * 1024 + 1)})


@pytest.mark.parametrize(
    "field,value",
    [
        ("implementation_sha256", "0" * 64),
        ("event_id", "0" * 64),
        ("valid_from", None),
        ("history_version", "changed"),
        ("unexpected", False),
    ],
)
def test_event_envelope_tampering(field: str, value: object) -> None:
    events, sources = chain()
    events[0][field] = value
    with pytest.raises(ValueError):
        replay_history(events[:1], sources)


def test_global_clock_cannot_go_back_across_partitions() -> None:
    first, sources = revision("fictional one", "2026-03-01T00:00:00Z", partition="one")
    second, more = revision("fictional two", "2026-02-01T00:00:00Z", partition="two")
    with pytest.raises(ValueError):
        replay_history([first, second], {**sources, **more})


def test_recorded_only_unknown_valid_clock_is_explicit() -> None:
    event, sources = revision("fictional", "2026-02-01T00:00:00Z", valid_from=None)
    result = replay_partition(
        [event], sources, partition="fictional", recorded_as_of="2026-02-01T00:00:00Z"
    )
    assert result["status"] == "replayed"
    assert result["valid_time_known"] is False
    assert result["valid_as_of"] is None


def test_valid_interval_start_is_included() -> None:
    event, sources = revision(
        "fictional", "2026-02-01T00:00:00Z", valid_until="2026-02-01T00:00:00Z"
    )
    result = replay_partition(
        [event],
        sources,
        partition="fictional",
        recorded_as_of="2026-02-01T00:00:00Z",
        valid_as_of="2026-01-01T00:00:00Z",
    )
    assert result["status"] == "replayed"


@pytest.mark.parametrize(
    "clock", [None, "2026-01-01", "2026-01-01T00:00:00+00:00", "2026-02-30T00:00:00Z"]
)
def test_recorded_clock_must_be_explicit_valid_utc(clock: str) -> None:
    with pytest.raises(ValueError):
        revision("fictional", clock)


def test_build_event_does_not_alias_input_contract() -> None:
    source = b'[{"fictional":"value"}]'
    contract = {
        "contract_version": VERSION,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "projection": {"output": "fictional"},
        "valid_from": None,
        "recorded_at": "2026-01-01T00:00:00Z",
    }
    first = build_event(source, contract, partition="fictional", valid_until=None, supersedes=None)
    second = build_event(source, contract, partition="fictional", valid_until=None, supersedes=None)
    assert first == second
    contract["projection"]["output"] = "changed"
    assert first["projection_contract"]["projection"]["output"] == "fictional"


def test_invalid_later_event_blocks_earlier_asof_query() -> None:
    events, sources = chain()
    events[-1]["projection_receipt"]["rows"] = []
    with pytest.raises(ValueError):
        replay_partition(
            events, sources, partition="fictional", recorded_as_of="2026-02-01T00:00:00Z"
        )
