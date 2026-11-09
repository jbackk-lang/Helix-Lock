"""Canonical, non-secret TIMDR state records for the HTKE research branch.

This module deliberately does not derive keys or encrypt data. It provides a
stable, versioned representation whose digest can later be used as public
HKDF context. TIMDR projections remain separately namespaced (M/S, G, K).
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any

__all__ = ["HelixStateRecord", "canonical_state_bytes", "hkss_digest"]

_SCHEMA = "helix-htke-state"
_SCHEMA_VERSION = 1
_HKSS_DOMAIN = b"HELIX-HTKE-HKSS-v1\x00"
_ALLOWED_PROJECTIONS = frozenset({"M/S", "G", "K"})
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,127}$")


def _identifier(value: str, field: str) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise ValueError(f"{field} must be a non-empty canonical identifier")
    return value


def _validate_public_value(value: Any, path: str = "projection") -> None:
    """Validate JSON-compatible data while forbidding binary floats.

    Numeric TIMDR values must be normalized decimal strings with units
    documented by the caller/schema. This avoids platform-dependent float
    serialization in a value that will be hashed.
    """
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        raise ValueError(f"{path}: floating-point values are not canonical; use decimal strings")
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _validate_public_value(item, f"{path}[{index}]")
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path}: object keys must be strings")
            _validate_public_value(item, f"{path}.{key}")
        return
    raise ValueError(f"{path}: unsupported value type {type(value).__name__}")


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    return value


@dataclass(frozen=True)
class HelixStateRecord:
    """Immutable public context for one object/key-purpose/epoch.

    M/S, G and K projection payloads are intentionally independent.
    Values are descriptive public metadata, never secret key material.
    """

    object_id: str
    key_purpose: str
    epoch: int
    timdr_revision: str
    adapter_version: str
    projections: Mapping[str, Any]
    previous_checkpoint: str | None = None
    schema_version: int = _SCHEMA_VERSION

    def __post_init__(self) -> None:
        _identifier(self.object_id, "object_id")
        _identifier(self.key_purpose, "key_purpose")
        _identifier(self.timdr_revision, "timdr_revision")
        _identifier(self.adapter_version, "adapter_version")
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int) or self.epoch < 0:
            raise ValueError("epoch must be a non-negative integer")
        if self.schema_version != _SCHEMA_VERSION:
            raise ValueError(f"unsupported state schema version: {self.schema_version}")
        if self.previous_checkpoint is not None:
            _identifier(self.previous_checkpoint, "previous_checkpoint")
        if not isinstance(self.projections, Mapping):
            raise ValueError("projections must be a mapping")
        unknown = set(self.projections) - _ALLOWED_PROJECTIONS
        if unknown:
            raise ValueError(f"unknown TIMDR projection(s): {', '.join(sorted(unknown))}")
        for name, payload in self.projections.items():
            if not isinstance(payload, Mapping):
                raise ValueError(f"projection {name!r} must be an object")
            _validate_public_value(payload, f"projections.{name}")
        # Freeze a defensive copy: later caller mutation cannot change HKSS.
        object.__setattr__(self, "projections", _freeze(self.projections))

    def to_dict(self) -> dict[str, Any]:
        """Return a detached logical record suitable for canonical encoding."""
        return {
            "schema": _SCHEMA,
            "schema_version": self.schema_version,
            "object_id": self.object_id,
            "key_purpose": self.key_purpose,
            "epoch": self.epoch,
            "timdr_revision": self.timdr_revision,
            "adapter_version": self.adapter_version,
            "previous_checkpoint": self.previous_checkpoint,
            "projections": {
                name: _thaw(self.projections[name])
                for name in sorted(self.projections)
            },
        }


def canonical_state_bytes(record: HelixStateRecord) -> bytes:
    """Serialize a state record deterministically as UTF-8 canonical JSON."""
    if not isinstance(record, HelixStateRecord):
        raise TypeError("record must be a HelixStateRecord")
    encoded = json.dumps(
        record.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return encoded.encode("utf-8")


def hkss_digest(record: HelixStateRecord) -> str:
    """Return the public SHA-256 digest of the canonical state record.

    HKSS is a digest/commitment, not a digital signature, MAC, secret, or key.
    Authenticity must be provided by the AIRP/checkpoint trust mechanism.
    """
    return hashlib.sha256(_HKSS_DOMAIN + canonical_state_bytes(record)).hexdigest()
