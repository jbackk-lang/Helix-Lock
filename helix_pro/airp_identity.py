"""High-level AIRP identity lifecycle: fingerprint -> signed ledger -> quorum checkpoint.

The manager accepts a caller-managed Ed25519 signing key and TrustAnchor.
It never persists encryption keys, passwords, or recovery material. A local
ledger event is retained if publishing fails; the result explicitly reports
that the event is pending external anchoring and must not be presented as
quorum-confirmed.
"""
from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .airp_key_fingerprint import (
    KeyFingerprint,
    create_key_fingerprint,
    create_rotation_link,
    verify_key_fingerprint,
    verify_rotation_link,
)
from .airp_ledger import AIRPIntegrityLedger, LedgerVerification
from .cipher import HelixProError


@dataclass(frozen=True)
class IdentityOperationResult:
    event_sequence: int
    event_hash: str
    anchored: bool
    anchor_status: str
    fingerprint: str
    message: str


class AIRPIdentityManager:
    """Coordinates key identity events and externally anchored checkpoints."""

    def __init__(self, ledger: AIRPIntegrityLedger):
        if not isinstance(ledger, AIRPIntegrityLedger):
            raise HelixProError("ledger must be an AIRPIntegrityLedger")
        self.ledger = ledger

    @staticmethod
    def _require_signer_match(ledger: AIRPIntegrityLedger, signer: Ed25519PrivateKey) -> None:
        raw = signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        if raw != ledger.public_key_bytes:
            raise HelixProError("rotation signer must match the AIRP ledger signing key")

    def _publish_result(self, event: dict, fingerprint: str) -> IdentityOperationResult:
        try:
            checkpoint = self.ledger.publish_checkpoint()
            parsed = self.ledger.verify_checkpoint(checkpoint, self.ledger.public_key_bytes)
            if parsed["sequence"] != event["sequence"] or parsed["head_hash"] != event["event_hash"]:
                raise HelixProError("published checkpoint does not cover the new identity event")
            verification = self.ledger.verify()
            if not verification.valid or verification.status != "fully_anchored":
                return IdentityOperationResult(
                    event["sequence"], event["event_hash"], False, verification.status,
                    fingerprint, "Zdarzenie zapisane lokalnie; quorum nie potwierdziło pełnego zakotwiczenia.",
                )
            return IdentityOperationResult(
                event["sequence"], event["event_hash"], True, verification.status,
                fingerprint, "Odcisk zapisany, podpisany i potwierdzony przez skonfigurowane quorum.",
            )
        except Exception as exc:
            return IdentityOperationResult(
                event["sequence"], event["event_hash"], False,
                f"pending_anchor:{type(exc).__name__}", fingerprint,
                "Zdarzenie zapisane lokalnie, ale publikacja lub odczyt checkpointu nie uzyskały potwierdzenia quorum. "
                "Ponów zakotwiczenie po przywróceniu dostępności świadków.",
            )

    def register_key(self, key: bytes, *, object_id: str, key_id: str) -> IdentityOperationResult:
        if not self.ledger.verify_chain():
            raise HelixProError("AIRP local hash chain is invalid; identity event refused")
        fp = create_key_fingerprint(key, object_id=object_id, key_id=key_id)
        event = self.ledger.append("key_fingerprint_registered", object_id, {
            "key_id": key_id,
            "fingerprint_algorithm": fp.algorithm,
            "key_fingerprint": fp.value,
        })
        return self._publish_result(event, fp.value)

    def rotate_key(
        self,
        old_key: bytes,
        new_key: bytes,
        *,
        object_id: str,
        old_key_id: str,
        new_key_id: str,
        signer: Ed25519PrivateKey,
    ) -> IdentityOperationResult:
        if not self.ledger.verify_chain():
            raise HelixProError("AIRP local hash chain is invalid; key rotation refused")
        self._require_signer_match(self.ledger, signer)
        link = create_rotation_link(
            old_key, new_key, object_id=object_id,
            old_key_id=old_key_id, new_key_id=new_key_id, signer=signer,
        )
        parsed = verify_rotation_link(link, signer.public_key())
        event = self.ledger.append("key_fingerprint_rotated", object_id, {
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "old_fingerprint": parsed["old_fingerprint"],
            "new_fingerprint": parsed["new_fingerprint"],
            "rotation_link": link.decode("utf-8"),
        })
        return self._publish_result(event, parsed["new_fingerprint"])

    def verify_key(self, key: bytes, fingerprint: KeyFingerprint | dict, *, object_id: str, key_id: str) -> bool:
        return verify_key_fingerprint(key, fingerprint, object_id=object_id, key_id=key_id)

    def retry_anchor(self) -> LedgerVerification:
        """Publish the current verified ledger head after a previous anchor outage."""
        if not self.ledger.verify_chain():
            raise HelixProError("AIRP local hash chain is invalid; checkpoint not published")
        self.ledger.publish_checkpoint()
        return self.ledger.verify()

    def status(self) -> LedgerVerification:
        return self.ledger.verify()
