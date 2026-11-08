import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from helix_pro.airp_key_fingerprint import (
    KeyFingerprint,
    create_key_fingerprint,
    create_rotation_link,
    public_key_fingerprint,
    representation_fingerprint,
    representation_fingerprint_file,
    verify_key_fingerprint,
    verify_rotation_link,
)
from helix_pro.cipher import HelixProError


def test_key_fingerprint_is_context_bound_and_verifiable():
    key = b"k" * 32
    fp = create_key_fingerprint(key, object_id="document-1", key_id="key-v1")
    assert verify_key_fingerprint(key, fp)
    assert verify_key_fingerprint(key, fp, object_id="document-2") is False
    assert verify_key_fingerprint(key, fp, key_id="key-v2") is False
    assert verify_key_fingerprint(b"x" * 32, fp) is False


def test_key_fingerprint_does_not_equal_plain_sha256_key_hash():
    import hashlib
    key = b"k" * 32
    fp = create_key_fingerprint(key, object_id="doc", key_id="v1")
    assert fp.value != hashlib.sha256(key).hexdigest()


def test_fingerprint_manifest_round_trip_and_validation():
    fp = create_key_fingerprint(b"k" * 32, object_id="doc", key_id="v1")
    restored = KeyFingerprint.from_dict(json.loads(json.dumps(fp.to_dict())))
    assert restored == fp
    with pytest.raises(HelixProError, match="invalid key fingerprint document"):
        KeyFingerprint.from_dict({"value": fp.value})


def test_representation_fingerprint_changes_when_blob_changes():
    assert representation_fingerprint(b"ciphertext-a") != representation_fingerprint(b"ciphertext-b")
    assert representation_fingerprint(b"ciphertext-a") == representation_fingerprint(b"ciphertext-a")


def test_public_key_fingerprint_is_stable():
    signer = Ed25519PrivateKey.generate()
    assert public_key_fingerprint(signer.public_key()) == public_key_fingerprint(signer.public_key())


def test_signed_rotation_link_binds_old_and_new_key():
    signer = Ed25519PrivateKey.generate()
    link = create_rotation_link(
        b"a" * 32, b"b" * 32,
        object_id="doc", old_key_id="key-v1", new_key_id="key-v2",
        signer=signer,
    )
    parsed = verify_rotation_link(link, signer.public_key())
    assert parsed["old_key_id"] == "key-v1"
    assert parsed["new_key_id"] == "key-v2"
    with pytest.raises(HelixProError, match="invalid AIRP key rotation link"):
        verify_rotation_link(link, Ed25519PrivateKey.generate().public_key())


def test_rotation_link_rejects_reused_key_identifier():
    with pytest.raises(HelixProError, match="new key_id"):
        create_rotation_link(
            b"a" * 32, b"b" * 32,
            object_id="doc", old_key_id="same", new_key_id="same",
            signer=Ed25519PrivateKey.generate(),
        )


def test_streaming_representation_fingerprint_matches_bytes(tmp_path):
    path = tmp_path / 'ciphertext.bin'
    data = b'ciphertext' * 10000
    path.write_bytes(data)
    assert representation_fingerprint_file(str(path), chunk_size=4096) == representation_fingerprint(data)
