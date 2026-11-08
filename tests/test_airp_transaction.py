import json
import os

import pytest

from helix_pro.airp_store import AIRPStore
from helix_pro.airp_transaction import AIRPFileTransaction, AIRPRecoveryError
from helix_pro.cipher import HelixProError


def _registered(tmp_path):
    target = tmp_path / "record.helixpro"
    target.write_bytes(b"encrypted-representation-v1")
    store = AIRPStore(tmp_path / "airp.sqlite3")
    state = store.register("record-1", target.read_bytes(), key_id="key-v1")
    return target, store, state


def test_transaction_commits_file_and_registry(tmp_path):
    target, store, state = _registered(tmp_path)
    result = AIRPFileTransaction(store).commit(
        target, b"encrypted-representation-v2",
        object_id="record-1", expected_version=state.version,
        expected_blob_sha256=state.blob_sha256, new_key_id="key-v2",
    )
    assert target.read_bytes() == b"encrypted-representation-v2"
    assert result.version == 2
    assert result.key_id == "key-v2"
    assert not (tmp_path / "record.helixpro.airp-transaction.json").exists()


def test_recovery_finishes_when_registry_committed_but_replace_failed(tmp_path, monkeypatch):
    target, store, state = _registered(tmp_path)
    transaction = AIRPFileTransaction(store)
    real_replace = os.replace

    def fail_final_stage_replace(source, destination):
        if str(source).endswith(".stage") and os.path.abspath(destination) == os.path.abspath(target):
            raise OSError("simulated power loss before final replace")
        return real_replace(source, destination)

    monkeypatch.setattr("helix_pro.airp_transaction.os.replace", fail_final_stage_replace)
    with pytest.raises(OSError, match="simulated power loss"):
        transaction.commit(
            target, b"encrypted-representation-v2",
            object_id="record-1", expected_version=state.version,
            expected_blob_sha256=state.blob_sha256, new_key_id="key-v2",
        )

    monkeypatch.setattr("helix_pro.airp_transaction.os.replace", real_replace)
    assert target.read_bytes() == b"encrypted-representation-v1"
    assert store.get("record-1").version == 2
    assert transaction.recover(target) == "completed_committed"
    assert target.read_bytes() == b"encrypted-representation-v2"
    assert transaction.recover(target) == "clean"


def test_recovery_discards_uncommitted_stage(tmp_path):
    target, store, state = _registered(tmp_path)
    staged = tmp_path / ".record.helixpro.airp-test.stage"
    staged.write_bytes(b"not-yet-committed")
    journal = tmp_path / "record.helixpro.airp-transaction.json"
    journal.write_text(json.dumps({
        "schema": 1,
        "object_id": "record-1",
        "target": str(target.resolve()),
        "staged": str(staged.resolve()),
        "old_version": state.version,
        "old_hash": state.blob_sha256,
        "new_version": state.version + 1,
        "new_hash": AIRPStore.fingerprint(b"not-yet-committed"),
        "new_key_id": "key-v2",
    }), encoding="utf-8")

    assert AIRPFileTransaction(store).recover(target) == "discarded_uncommitted"
    assert target.read_bytes() == b"encrypted-representation-v1"
    assert not staged.exists()
    assert not journal.exists()


def test_transaction_rejects_stale_or_modified_target(tmp_path):
    target, store, state = _registered(tmp_path)
    target.write_bytes(b"modified")
    with pytest.raises(HelixProError, match="target file"):
        AIRPFileTransaction(store).commit(
            target, b"new",
            object_id="record-1", expected_version=state.version,
            expected_blob_sha256=state.blob_sha256, new_key_id="key-v2",
        )


def test_recovery_refuses_unknown_registry_state(tmp_path):
    target, store, state = _registered(tmp_path)
    staged = tmp_path / ".record.helixpro.airp-test.stage"
    staged.write_bytes(b"next")
    journal = tmp_path / "record.helixpro.airp-transaction.json"
    journal.write_text(json.dumps({
        "schema": 1,
        "object_id": "record-1",
        "target": str(target.resolve()),
        "staged": str(staged.resolve()),
        "old_version": state.version,
        "old_hash": state.blob_sha256,
        "new_version": state.version + 1,
        "new_hash": AIRPStore.fingerprint(b"next"),
        "new_key_id": "key-v2",
    }), encoding="utf-8")
    store.commit_rotation(
        "record-1", b"some-other-blob", expected_version=state.version,
        expected_blob_sha256=state.blob_sha256, new_key_id="key-v3",
    )
    with pytest.raises(AIRPRecoveryError, match="neither"):
        AIRPFileTransaction(store).recover(target)
