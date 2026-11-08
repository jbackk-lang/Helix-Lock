import json
import threading
from http.server import ThreadingHTTPServer

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_anchor_service import AnchorRepository, make_handler
from helix_pro.airp_http_anchor import HTTPTrustAnchor
from helix_pro.airp_ledger import AIRPIntegrityLedger
from helix_pro.cipher import HelixProError


def _key_bytes(key):
    from cryptography.hazmat.primitives import serialization
    return key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


def test_anchor_accepts_signed_checkpoint_and_rejects_rollback(tmp_path):
    key = Ed25519PrivateKey.generate()
    repository = AnchorRepository(tmp_path / "anchor.sqlite3", _key_bytes(key))
    ledger = AIRPIntegrityLedger(tmp_path / "ledger.sqlite3", key)
    ledger.append("registered", "object-1", {"version": 1})
    first = ledger.create_checkpoint()
    assert repository.publish(first)["sequence"] == 1

    ledger.append("rotated", "object-1", {"version": 2})
    second = ledger.create_checkpoint()
    assert repository.publish(second)["sequence"] == 2
    with pytest.raises(HelixProError, match="rollback"):
        repository.publish(first)
    assert repository.latest() == second


def test_anchor_rejects_fork_at_same_sequence(tmp_path):
    key = Ed25519PrivateKey.generate()
    repository = AnchorRepository(tmp_path / "anchor.sqlite3", _key_bytes(key))
    ledger_a = AIRPIntegrityLedger(tmp_path / "a.sqlite3", key)
    ledger_b = AIRPIntegrityLedger(tmp_path / "b.sqlite3", key)
    ledger_a.append("registered", "object-1", {"version": 1})
    ledger_b.append("registered", "object-1", {"version": 99})
    checkpoint_a = ledger_a.create_checkpoint()
    checkpoint_b = ledger_b.create_checkpoint()
    repository.publish(checkpoint_a)
    with pytest.raises(HelixProError, match="fork"):
        repository.publish(checkpoint_b)


def test_anchor_rejects_untrusted_signer(tmp_path):
    trusted = Ed25519PrivateKey.generate()
    attacker = Ed25519PrivateKey.generate()
    repository = AnchorRepository(tmp_path / "anchor.sqlite3", _key_bytes(trusted))
    ledger = AIRPIntegrityLedger(tmp_path / "ledger.sqlite3", attacker)
    ledger.append("registered", "object-1", {"version": 1})
    with pytest.raises(HelixProError, match="invalid AIRP checkpoint"):
        repository.publish(ledger.create_checkpoint())


def test_http_client_and_service_round_trip(tmp_path):
    key = Ed25519PrivateKey.generate()
    repository = AnchorRepository(tmp_path / "anchor.sqlite3", _key_bytes(key))
    token = "t" * 48
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(repository, token))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        anchor = HTTPTrustAnchor(f"http://127.0.0.1:{server.server_port}", token)
        ledger = AIRPIntegrityLedger(
            tmp_path / "ledger.sqlite3", key, trust_anchor=anchor,
            trusted_public_key=_key_bytes(key),
        )
        ledger.append("registered", "object-1", {"version": 1})
        ledger.publish_checkpoint()
        assert ledger.verify().status == "fully_anchored"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_http_client_requires_https_off_loopback():
    with pytest.raises(HelixProError, match="HTTPS"):
        HTTPTrustAnchor("http://anchor.example", "x" * 48)
    with pytest.raises(HelixProError, match="HTTPS"):
        HTTPTrustAnchor("http://127.0.0.1.attacker.example", "x" * 48)
    with pytest.raises(HelixProError, match="HTTPS"):
        HTTPTrustAnchor("https://anchor.example@attacker.example", "x" * 48)
    with pytest.raises(HelixProError, match="32 characters"):
        HTTPTrustAnchor("https://anchor.example", "short")
