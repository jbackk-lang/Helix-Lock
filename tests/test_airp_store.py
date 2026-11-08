import pytest

from helix_pro.airp_store import AIRPStore
from helix_pro.cipher import HelixProError


def test_store_persists_state_and_events_across_instances(tmp_path):
    db = tmp_path / "airp.sqlite3"
    store = AIRPStore(db)
    state = store.register("file-1", b"ciphertext-v1", key_id="key-v1")
    assert state.version == 1
    assert store.verify("file-1", b"ciphertext-v1", version=1, key_id="key-v1")
    assert not store.verify("file-1", b"old-copy", version=0, key_id="key-v1")

    reopened = AIRPStore(db)
    assert reopened.get("file-1") == state
    assert [e["outcome"] for e in reopened.events("file-1")] == ["granted", "granted", "denied"]


def test_store_rotation_compare_and_swap_and_rollback_rejection(tmp_path):
    store = AIRPStore(tmp_path / "airp.sqlite3")
    first = store.register("file-2", b"v1", key_id="key-v1")
    second = store.commit_rotation(
        "file-2", b"v2", expected_version=first.version,
        expected_blob_sha256=first.blob_sha256, new_key_id="key-v2",
    )
    assert second.version == 2
    assert second.key_id == "key-v2"
    assert store.verify("file-2", b"v2", version=2, key_id="key-v2")
    with pytest.raises(HelixProError, match="stale"):
        store.commit_rotation(
            "file-2", b"rollback", expected_version=1,
            expected_blob_sha256=first.blob_sha256, new_key_id="key-v3",
        )


def test_store_rejects_duplicate_registration_and_unknown_event(tmp_path):
    store = AIRPStore(tmp_path / "airp.sqlite3")
    store.register("file-3", b"v1", key_id="key-v1")
    with pytest.raises(Exception):
        store.register("file-3", b"v1", key_id="key-v1")
    with pytest.raises(HelixProError):
        store.record_event("missing", outcome="denied")
