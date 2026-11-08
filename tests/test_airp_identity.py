import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_identity import AIRPIdentityManager
from helix_pro.airp_ledger import AIRPIntegrityLedger
from helix_pro.airp_quorum import QuorumTrustAnchor
from helix_pro.cipher import HelixProError


class Anchor:
    def __init__(self, fail=False):
        self.value = None
        self.fail = fail

    def publish_checkpoint(self, checkpoint):
        if self.fail:
            raise OSError("witness unavailable")
        parsed = json.loads(checkpoint)
        if self.value is not None:
            old = json.loads(self.value)
            if parsed["sequence"] < old["sequence"]:
                raise ValueError("rollback")
            if parsed["sequence"] == old["sequence"] and parsed["head_hash"] != old["head_hash"]:
                raise ValueError("fork")
        self.value = checkpoint

    def latest_checkpoint(self):
        if self.fail:
            raise OSError("witness unavailable")
        return self.value


def make_manager(tmp_path, *, failing=False):
    signer = Ed25519PrivateKey.generate()
    anchors = [Anchor(fail=failing), Anchor(fail=failing), Anchor()]
    quorum = QuorumTrustAnchor(anchors)
    ledger = AIRPIntegrityLedger(tmp_path / "identity.sqlite3", signer, trust_anchor=quorum)
    return AIRPIdentityManager(ledger), signer, anchors


def test_register_key_is_fingerprinted_and_quorum_anchored(tmp_path):
    manager, _, anchors = make_manager(tmp_path)
    result = manager.register_key(b"a" * 32, object_id="doc-1", key_id="key-1")
    assert result.anchored is True
    assert result.anchor_status == "fully_anchored"
    assert all(anchor.value is not None for anchor in anchors[:2])
    assert manager.status().status == "fully_anchored"


def test_rotation_creates_signed_link_and_anchors_event(tmp_path):
    manager, signer, anchors = make_manager(tmp_path)
    manager.register_key(b"a" * 32, object_id="doc-1", key_id="key-1")
    result = manager.rotate_key(
        b"a" * 32, b"b" * 32, object_id="doc-1",
        old_key_id="key-1", new_key_id="key-2", signer=signer,
    )
    assert result.anchored is True
    assert manager.ledger.events("doc-1")[-1]["event_type"] == "key_fingerprint_rotated"
    link = manager.ledger.events("doc-1")[-1]["payload"]["rotation_link"].encode()
    assert json.loads(link)["new_key_id"] == "key-2"


def test_rotation_refuses_a_signer_different_from_ledger_signer(tmp_path):
    manager, _, _ = make_manager(tmp_path)
    with pytest.raises(HelixProError, match="must match"):
        manager.rotate_key(
            b"a" * 32, b"b" * 32, object_id="doc",
            old_key_id="old", new_key_id="new",
            signer=Ed25519PrivateKey.generate(),
        )


def test_quorum_outage_is_reported_as_pending_not_success(tmp_path):
    manager, _, _ = make_manager(tmp_path, failing=True)
    result = manager.register_key(b"a" * 32, object_id="doc", key_id="key-1")
    assert result.anchored is False
    assert result.anchor_status.startswith("pending_anchor:")
    assert manager.status().status == "anchor_unavailable_or_no_quorum"


def test_retry_anchor_anchors_pending_local_event(tmp_path):
    manager, _, anchors = make_manager(tmp_path, failing=True)
    manager.register_key(b"a" * 32, object_id="doc", key_id="key-1")
    anchors[0].fail = False
    anchors[1].fail = False
    result = manager.retry_anchor()
    assert result.valid is True
    assert result.status == "fully_anchored"


def test_registration_refuses_corrupted_local_chain(tmp_path):
    manager, _, _ = make_manager(tmp_path)
    manager.ledger.append("initial", "doc", {"n": 1})
    import sqlite3
    with sqlite3.connect(manager.ledger.database_path) as db:
        db.execute("UPDATE airp_ledger_events SET payload_json='{}' WHERE sequence=1")
    with pytest.raises(HelixProError, match="hash chain"):
        manager.register_key(b"a" * 32, object_id="doc", key_id="key-1")
