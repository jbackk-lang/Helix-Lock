import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_ledger import AIRPIntegrityLedger
from helix_pro.airp_quorum import QuorumTrustAnchor
from helix_pro.cipher import HelixProError


class Anchor:
    def __init__(self, value=None, fail_publish=False, fail_read=False):
        self.value = value
        self.fail_publish = fail_publish
        self.fail_read = fail_read

    def publish_checkpoint(self, checkpoint):
        if self.fail_publish:
            raise RuntimeError("offline")
        self.value = checkpoint

    def latest_checkpoint(self):
        if self.fail_read:
            raise RuntimeError("offline")
        return self.value


def _checkpoint(tmp_path):
    key = Ed25519PrivateKey.generate()
    ledger = AIRPIntegrityLedger(tmp_path / "ledger.sqlite3", key)
    ledger.append("registered", "object", {"version": 1})
    return ledger.create_checkpoint()


def test_quorum_publish_and_read_require_majority(tmp_path):
    checkpoint = _checkpoint(tmp_path)
    a, b, c = Anchor(), Anchor(), Anchor(fail_publish=True)
    quorum = QuorumTrustAnchor([a, b, c])
    quorum.publish_checkpoint(checkpoint)
    assert quorum.latest_checkpoint() == checkpoint


def test_quorum_fails_when_publish_reaches_too_few_anchors(tmp_path):
    checkpoint = _checkpoint(tmp_path)
    anchors = [Anchor(fail_publish=True), Anchor(), Anchor(fail_publish=True)]
    quorum = QuorumTrustAnchor(anchors)
    with pytest.raises(HelixProError, match="2 required"):
        quorum.publish_checkpoint(checkpoint)


def test_quorum_rejects_disagreeing_latest_checkpoints(tmp_path):
    one = _checkpoint(tmp_path / "one")
    two = _checkpoint(tmp_path / "two")
    quorum = QuorumTrustAnchor([Anchor(one), Anchor(two), Anchor()])
    with pytest.raises(HelixProError, match="matching checkpoint quorum"):
        quorum.latest_checkpoint()


def test_quorum_uses_matching_majority_and_ignores_single_fork(tmp_path):
    checkpoint = _checkpoint(tmp_path)
    quorum = QuorumTrustAnchor([Anchor(checkpoint), Anchor(checkpoint), Anchor(b'{"sequence":99,"head_hash":"x"}')])
    assert quorum.latest_checkpoint() == checkpoint


def test_quorum_must_be_strict_majority():
    with pytest.raises(HelixProError, match="strict majority"):
        QuorumTrustAnchor([Anchor(), Anchor(), Anchor()], quorum=1)
