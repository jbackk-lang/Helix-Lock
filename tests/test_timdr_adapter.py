from datetime import datetime, timedelta, timezone

import pytest

from helix_pro.timdr_adapter import project_airp_events


def sample_events(count=8):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "sequence": i + 1,
            "timestamp_utc": (start + timedelta(seconds=i * 10)).isoformat(),
            "event_type": "access_denied" if i == 2 else "counter_observed",
            # These fields must be ignored by the projection.
            "payload": {"secret": "must-not-be-read"},
            "object_id": "opaque-id",
            "event_hash": "f" * 64,
        }
        for i in range(count)
    ]


def test_projection_is_deterministic_and_secret_free():
    events = sample_events()
    result = project_airp_events(events, window_size=4)
    assert len(result) == 2
    assert result[0].event_count == 4
    assert result[0].denied_count == 1
    assert "secret" not in repr(result)


def test_empty_input_returns_empty():
    assert project_airp_events([]) == ()


def test_rejects_non_monotonic_sequence():
    events = sample_events()
    events[3]["sequence"] = 2
    with pytest.raises(ValueError, match="increasing"):
        project_airp_events(events)


def test_rejects_naive_timestamps():
    events = sample_events()
    events[0]["timestamp_utc"] = "2026-01-01T00:00:00"
    with pytest.raises(ValueError, match="timezone"):
        project_airp_events(events)


def test_minimum_window_size():
    with pytest.raises(ValueError):
        project_airp_events(sample_events(), window_size=2)



def test_projects_real_airp_ledger_without_mutating_it(tmp_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from helix_pro.airp_ledger import AIRPIntegrityLedger
    from helix_pro.timdr_adapter import project_ledger

    ledger = AIRPIntegrityLedger(
        tmp_path / "airp.sqlite3",
        Ed25519PrivateKey.generate(),
    )
    for index in range(6):
        ledger.append(
            "access_denied" if index == 2 else "counter_observed",
            "object-A",
            {"counter": index, "secret": "must-not-leak"},
        )

    before_head = ledger.head()
    before_count = len(ledger.events())
    observations = project_ledger(ledger, object_id="object-A", window_size=3)

    assert len(observations) == 2
    assert observations[0].event_count == 3
    assert observations[0].denied_count == 1
    assert "secret" not in repr(observations)
    assert ledger.head() == before_head
    assert len(ledger.events()) == before_count


def test_project_ledger_requires_events_method():
    from helix_pro.timdr_adapter import project_ledger

    with pytest.raises(TypeError, match="events"):
        project_ledger(object())
