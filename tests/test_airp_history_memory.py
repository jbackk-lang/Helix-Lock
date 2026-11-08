from datetime import datetime, timedelta, timezone

import pytest

from helix_pro.airp_history_memory import AIRPHistoryMemory
from helix_pro.cipher import HelixProError


def make_events(count=12):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    events = []
    for index in range(count):
        kind = "access" if index % 4 == 0 else ("rotated" if index % 5 == 0 else "counter_observed")
        payload = {"outcome": "denied" if index % 8 == 0 else "granted"} if kind == "access" else {"secret": "NEVER-RETAIN"}
        events.append({
            "sequence": index + 1,
            "timestamp_utc": (start + timedelta(seconds=index * (2 if index < 6 else 3))).isoformat(),
            "event_type": kind,
            "payload": payload,
            "object_id": "sensitive-object-id",
        })
    return events


def test_fixed_window_summaries_are_batch_independent():
    events = make_events()
    checkpoint = "a" * 64
    whole = AIRPHistoryMemory(window_size=3)
    whole_out = whole.consume(events, source_checkpoint_sha256=checkpoint)
    chunked = AIRPHistoryMemory(window_size=3)
    chunked_out = []
    for batch in (events[:2], events[2:7], events[7:]):
        chunked_out.extend(chunked.consume(batch, source_checkpoint_sha256=checkpoint))
    assert whole_out == tuple(chunked_out)
    assert len(whole_out) == 4


def test_memory_retains_at_most_one_incomplete_window_and_no_summaries():
    memory = AIRPHistoryMemory(window_size=4)
    emitted = memory.consume(make_events(100), source_checkpoint_sha256="b" * 64)
    assert len(emitted) == 25
    assert memory.retained_event_count == 0
    assert memory.pending_events == 0
    # The caller owns persistence of emitted summaries; this object does not accumulate them.
    assert not hasattr(memory, "summaries")


def test_partial_window_is_bounded_and_not_emitted():
    memory = AIRPHistoryMemory(window_size=5)
    emitted = memory.consume(make_events(4), source_checkpoint_sha256="c" * 64)
    assert emitted == ()
    assert memory.pending_events == 4
    assert memory.retained_event_count <= memory.window_size


def test_rejects_sequence_gap_and_replay():
    memory = AIRPHistoryMemory(window_size=3)
    events = make_events(3)
    events[1]["sequence"] = 9
    with pytest.raises(HelixProError, match="sequence gap or replay"):
        memory.consume(events, source_checkpoint_sha256="d" * 64)


def test_rejects_naive_timestamp_and_bad_checkpoint_hash():
    event = make_events(1)[0]
    event["timestamp_utc"] = "2026-01-01T00:00:00"
    memory = AIRPHistoryMemory(window_size=3)
    with pytest.raises(HelixProError, match="timezone"):
        memory.consume([event], source_checkpoint_sha256="e" * 64)
    with pytest.raises(HelixProError, match="SHA-256"):
        AIRPHistoryMemory(window_size=3).consume([], source_checkpoint_sha256="not-a-hash")


def test_summary_is_secret_free_and_bound_to_source_checkpoint():
    memory = AIRPHistoryMemory(window_size=3)
    result = memory.consume(make_events(3), source_checkpoint_sha256="f" * 64)
    summary = result[0]
    assert summary.source_checkpoint_sha256 == "f" * 64
    assert summary.first_sequence == 1 and summary.last_sequence == 3
    assert summary.event_count == 3
    assert summary.denied_count == 1
    assert "NEVER-RETAIN" not in repr(summary)
    assert "sensitive-object-id" not in repr(summary)
    assert len(summary.summary_sha256) == 64