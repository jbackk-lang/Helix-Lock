"""Context-bound fingerprints for Helix-Lock keys and encrypted representations.

Secret-key fingerprints use HKDF-SHA256 + HMAC-SHA256 with explicit domain
separation. This avoids publishing a raw SHA-256(key) verifier. Fingerprints
are integrity identifiers, not encryption keys, authenticators, or proof that
a key is authorized; authorization comes from the signed AIRP ledger/anchor.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import asdict, dataclass
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from .cipher import KEY_SIZE, HelixProError

KEY_FP_DOMAIN = b"Helix-Lock/AIRP/key-fingerprint/v1"
REP_FP_DOMAIN = b"Helix-Lock/AIRP/representation-fingerprint/v1"
PUBLIC_FP_DOMAIN = b"Helix-Lock/AIRP/public-key-fingerprint/v1"


def _context(object_id: str, key_id: str) -> bytes:
    if not isinstance(object_id, str) or not object_id or len(object_id) > 512:
        raise HelixProError("object_id must contain 1..512 characters")
    if not isinstance(key_id, str) or not key_id or len(key_id) > 256:
        raise HelixProError("key_id must contain 1..256 characters")
    try:
        return object_id.encode("utf-8") + b"\0" + key_id.encode("utf-8")
    except UnicodeError as exc:
        raise HelixProError("fingerprint context must be valid UTF-8") from exc


@dataclass(frozen=True)
class KeyFingerprint:
    schema: int
    algorithm: str
    object_id: str
    key_id: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "KeyFingerprint":
        required = {"schema", "algorithm", "object_id", "key_id", "value"}
        if not isinstance(value, dict) or set(value) != required:
            raise HelixProError("invalid key fingerprint document")
        if value["schema"] != 1 or value["algorithm"] != "HKDF-SHA256+HMAC-SHA256":
            raise HelixProError("unsupported key fingerprint schema or algorithm")
        if not isinstance(value["value"], str) or len(value["value"]) != 64:
            raise HelixProError("invalid key fingerprint value")
        try:
            bytes.fromhex(value["value"])
        except ValueError as exc:
            raise HelixProError("invalid key fingerprint hex") from exc
        _context(value["object_id"], value["key_id"])
        return cls(**value)


def create_key_fingerprint(key: bytes, *, object_id: str, key_id: str) -> KeyFingerprint:
    """Create a context-bound keyed fingerprint without exposing raw key hash."""
    if not isinstance(key, bytes) or len(key) != KEY_SIZE:
        raise HelixProError("key must be exactly 32 bytes")
    context = _context(object_id, key_id)
    derived = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=hashlib.sha256(KEY_FP_DOMAIN + context).digest(),
        info=KEY_FP_DOMAIN + context,
    ).derive(key)
    value = hmac.new(derived, KEY_FP_DOMAIN + context, hashlib.sha256).hexdigest()
    return KeyFingerprint(1, "HKDF-SHA256+HMAC-SHA256", object_id, key_id, value)


def verify_key_fingerprint(
    key: bytes, fingerprint: KeyFingerprint | dict[str, Any], *,
    object_id: str | None = None, key_id: str | None = None,
) -> bool:
    """Constant-time comparison; context mismatches fail closed."""
    if isinstance(fingerprint, dict):
        fingerprint = KeyFingerprint.from_dict(fingerprint)
    if not isinstance(fingerprint, KeyFingerprint):
        raise HelixProError("fingerprint must be KeyFingerprint or its dictionary")
    expected_object = fingerprint.object_id if object_id is None else object_id
    expected_key = fingerprint.key_id if key_id is None else key_id
    if expected_object != fingerprint.object_id or expected_key != fingerprint.key_id:
        return False
    try:
        candidate = create_key_fingerprint(key, object_id=expected_object, key_id=expected_key)
    except HelixProError:
        return False
    return hmac.compare_digest(candidate.value, fingerprint.value)


def representation_fingerprint(blob: bytes) -> str:
    """Public SHA-256 identifier for one exact encrypted representation."""
    if not isinstance(blob, bytes):
        raise HelixProError("representation must be bytes")
    return hashlib.sha256(REP_FP_DOMAIN + blob).hexdigest()


def representation_fingerprint_file(path: str, *, chunk_size: int = 1024 * 1024) -> str:
    """Stream a file into the domain-separated representation fingerprint."""
    if type(chunk_size) is not int or chunk_size < 4096 or chunk_size > 16 * 1024 * 1024:
        raise HelixProError("chunk_size must be between 4096 and 16777216 bytes")
    digest = hashlib.sha256()
    digest.update(REP_FP_DOMAIN)
    try:
        with open(path, "rb") as stream:
            for chunk in iter(lambda: stream.read(chunk_size), b""):
                digest.update(chunk)
    except OSError as exc:
        raise HelixProError(f"cannot fingerprint representation file: {exc}") from exc
    return digest.hexdigest()


def public_key_fingerprint(public_key: Ed25519PublicKey | bytes) -> str:
    """Public identifier for an Ed25519 public key."""
    if isinstance(public_key, Ed25519PublicKey):
        raw = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    elif isinstance(public_key, bytes) and len(public_key) == 32:
        raw = public_key
        try:
            Ed25519PublicKey.from_public_bytes(raw)
        except ValueError as exc:
            raise HelixProError("invalid Ed25519 public key") from exc
    else:
        raise HelixProError("public_key must be Ed25519PublicKey or 32 raw bytes")
    return hashlib.sha256(PUBLIC_FP_DOMAIN + raw).hexdigest()


def create_rotation_link(
    old_key: bytes, new_key: bytes, *,
    object_id: str, old_key_id: str, new_key_id: str,
    signer: Ed25519PrivateKey,
) -> bytes:
    """Sign a transition between two context-bound fingerprints.

    The event records fingerprints and identifiers only, never key material.
    """
    if old_key_id == new_key_id:
        raise HelixProError("rotation requires a new key_id")
    old_fp = create_key_fingerprint(old_key, object_id=object_id, key_id=old_key_id)
    new_fp = create_key_fingerprint(new_key, object_id=object_id, key_id=new_key_id)
    event = {
        "schema": 1,
        "event": "airp_key_rotation",
        "object_id": object_id,
        "old_key_id": old_key_id,
        "new_key_id": new_key_id,
        "old_fingerprint": old_fp.value,
        "new_fingerprint": new_fp.value,
    }
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = signer.sign(canonical)
    return json.dumps(
        {**event, "signature": signature.hex()},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def verify_rotation_link(link: bytes, trusted_public_key: Ed25519PublicKey) -> dict:
    try:
        event = json.loads(link.decode("utf-8"))
        required = {
            "schema", "event", "object_id", "old_key_id", "new_key_id",
            "old_fingerprint", "new_fingerprint", "signature",
        }
        if not isinstance(event, dict) or set(event) != required:
            raise ValueError("invalid rotation event fields")
        if event["schema"] != 1 or event["event"] != "airp_key_rotation":
            raise ValueError("unsupported rotation event")
        if event["old_key_id"] == event["new_key_id"]:
            raise ValueError("rotation key identifiers must differ")
        unsigned = {k: v for k, v in event.items() if k != "signature"}
        canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
        trusted_public_key.verify(bytes.fromhex(event["signature"]), canonical)
        _context(event["object_id"], event["old_key_id"])
        _context(event["object_id"], event["new_key_id"])
        for field in ("old_fingerprint", "new_fingerprint"):
            if not isinstance(event[field], str) or len(event[field]) != 64:
                raise ValueError("invalid fingerprint")
            bytes.fromhex(event[field])
        return event
    except Exception as exc:
        raise HelixProError(f"invalid AIRP key rotation link: {exc}") from exc
