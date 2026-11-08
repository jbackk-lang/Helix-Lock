import hashlib
import pytest

from helix_pro.cipher import HelixProError, encrypt_bytes, decrypt_bytes, generate_key
from helix_pro.adaptive_rotation import rotate_encrypted_blob


def test_rotation_preserves_plaintext_and_changes_representation():
    plaintext = b"TIMDR AIRP\x00" * 100
    old_key, new_key = generate_key(), generate_key()
    aad = b"record-id:42"
    old_blob = encrypt_bytes(plaintext, old_key, aad=aad)

    result = rotate_encrypted_blob(old_blob, old_key, new_key, aad=aad)

    assert result.blob != old_blob
    assert decrypt_bytes(result.blob, new_key, aad=aad) == plaintext
    assert result.plaintext_sha256 == hashlib.sha256(plaintext).hexdigest()
    assert result.old_blob_sha256 == hashlib.sha256(old_blob).hexdigest()
    assert result.new_blob_sha256 == hashlib.sha256(result.blob).hexdigest()
    with pytest.raises(HelixProError):
        decrypt_bytes(result.blob, old_key, aad=aad)


def test_rotation_rejects_wrong_old_key():
    blob = encrypt_bytes(b"secret", generate_key())
    with pytest.raises(HelixProError):
        rotate_encrypted_blob(blob, generate_key(), generate_key())


def test_rotation_rejects_same_key():
    key = generate_key()
    blob = encrypt_bytes(b"secret", key)
    with pytest.raises(HelixProError, match="must differ"):
        rotate_encrypted_blob(blob, key, key)


def test_rotation_rejects_wrong_aad():
    old_key, new_key = generate_key(), generate_key()
    blob = encrypt_bytes(b"secret", old_key, aad=b"correct")
    with pytest.raises(HelixProError):
        rotate_encrypted_blob(blob, old_key, new_key, aad=b"wrong")
