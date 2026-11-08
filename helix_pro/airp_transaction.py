"""Crash-recoverable file replacement coordinated with the AIRP SQLite registry.

The file and SQLite database cannot participate in one OS transaction. This
module uses a durable sidecar journal and a staged file so recovery can finish
a registry-committed replacement after a process/host interruption.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

from .airp_store import AIRPStore
from .cipher import HelixProError


class AIRPRecoveryError(HelixProError):
    """Recovery journal or on-disk state is ambiguous; manual intervention required."""


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fsync_directory(directory: Path) -> None:
    # Directory fsync is available on POSIX; Windows does not expose it this way.
    if os.name == "nt":
        return
    fd = os.open(str(directory), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_durable(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def _journal_path(target: Path) -> Path:
    return target.with_name(target.name + ".airp-transaction.json")


class AIRPFileTransaction:
    """Commit a new file representation and AIRP metadata with crash recovery.

    The caller must create and cryptographically verify new_blob before calling
    commit(). This class stores no keys or plaintext. Keep the journal and stage
    in the same directory as the target; do not place them in a synced/public
    folder. One transaction per target path is supported.
    """

    def __init__(self, store: AIRPStore):
        self.store = store

    def commit(
        self,
        target_path: str | Path,
        new_blob: bytes,
        *,
        object_id: str,
        expected_version: int,
        expected_blob_sha256: str,
        new_key_id: str,
    ):
        target = Path(target_path).expanduser().resolve()
        if not target.is_file():
            raise HelixProError("AIRP transaction target file does not exist")
        if not new_blob:
            raise HelixProError("new representation must not be empty")
        journal = _journal_path(target)
        if journal.exists():
            raise AIRPRecoveryError("pending AIRP journal exists; recover it before starting another transaction")
        current_hash = _sha256_file(target)
        if current_hash != expected_blob_sha256:
            raise HelixProError("target file does not match the expected AIRP representation")
        state = self.store.get(object_id)
        if state is None or state.version != expected_version or state.blob_sha256 != expected_blob_sha256:
            raise HelixProError("AIRP registry does not match the expected old representation")

        token = uuid4().hex
        staged = target.with_name(f".{target.name}.airp-{token}.stage")
        new_hash = AIRPStore.fingerprint(new_blob)
        record = {
            "schema": 1,
            "object_id": object_id,
            "target": str(target),
            "staged": str(staged),
            "old_version": expected_version,
            "old_hash": expected_blob_sha256,
            "new_version": expected_version + 1,
            "new_hash": new_hash,
            "new_key_id": new_key_id,
        }

        # Stage and journal are durable before changing the trusted registry.
        _write_durable(staged, new_blob)
        if _sha256_file(staged) != new_hash:
            staged.unlink(missing_ok=True)
            raise HelixProError("staged representation failed its SHA-256 check")
        _write_durable(journal, json.dumps(record, sort_keys=True).encode("utf-8"))

        try:
            committed = self.store.commit_rotation(
                object_id,
                new_blob,
                expected_version=expected_version,
                expected_blob_sha256=expected_blob_sha256,
                new_key_id=new_key_id,
            )
        except Exception:
            staged.unlink(missing_ok=True)
            journal.unlink(missing_ok=True)
            _fsync_directory(target.parent)
            raise

        # If this replace is interrupted, recover() completes it from the journal.
        os.replace(staged, target)
        _fsync_directory(target.parent)
        journal.unlink()
        _fsync_directory(target.parent)
        return committed

    def recover(self, target_path: str | Path) -> str:
        """Recover one pending transaction: finish committed update or discard uncommitted stage."""
        target = Path(target_path).expanduser().resolve()
        journal = _journal_path(target)
        if not journal.exists():
            return "clean"
        try:
            record = json.loads(journal.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise AIRPRecoveryError(f"cannot read AIRP journal: {exc}") from exc

        required = {
            "schema", "object_id", "target", "staged", "old_version", "old_hash",
            "new_version", "new_hash", "new_key_id",
        }
        if set(record) != required or record["schema"] != 1:
            raise AIRPRecoveryError("unsupported or malformed AIRP journal")
        if Path(record["target"]).resolve() != target:
            raise AIRPRecoveryError("AIRP journal target path does not match requested file")
        staged = Path(record["staged"]).resolve()
        if staged.parent != target.parent or not staged.name.startswith(f".{target.name}.airp-") or not staged.name.endswith(".stage"):
            raise AIRPRecoveryError("AIRP staged path is outside the target directory or has an invalid name")

        state = self.store.get(record["object_id"])
        target_hash = _sha256_file(target)
        staged_hash = _sha256_file(staged)

        if state is not None and state.version == record["old_version"] and state.blob_sha256 == record["old_hash"]:
            if target_hash != record["old_hash"]:
                raise AIRPRecoveryError("old AIRP state is active but target file no longer matches it")
            if staged.exists():
                staged.unlink()
            journal.unlink()
            _fsync_directory(target.parent)
            return "discarded_uncommitted"

        if (
            state is not None
            and state.version == record["new_version"]
            and state.key_id == record["new_key_id"]
            and state.blob_sha256 == record["new_hash"]
        ):
            if target_hash == record["new_hash"]:
                if staged.exists():
                    staged.unlink()
                journal.unlink()
                _fsync_directory(target.parent)
                return "already_completed"
            if staged_hash != record["new_hash"]:
                raise AIRPRecoveryError("registry committed new version but valid staged file is missing")
            os.replace(staged, target)
            _fsync_directory(target.parent)
            journal.unlink()
            _fsync_directory(target.parent)
            return "completed_committed"

        raise AIRPRecoveryError("AIRP registry state is neither the journaled old nor new version; manual review required")
