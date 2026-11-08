import pytest
from cryptography.exceptions import InvalidTag
from experiments.helix_native_secure_envelope import generate_key, protect_bytes, recover_bytes
from experiments.helix_security_performance_gate import evaluate, rejected


def test_authenticated_envelope_rejects_tampering():
    key = generate_key()
    env = protect_bytes(b"security regression", key)
    assert recover_bytes(env, key)[0] == b"security regression"
    for index in (0, 4, 12, len(env) - 1):
        altered = bytearray(env)
        altered[index] ^= 1
        assert rejected(bytes(altered), key)
    assert rejected(env[:-1], key)
    assert rejected(env, generate_key())


def test_report_checks():
    report = evaluate(sizes=(16,), trials=2)
    row = report["results"][0]
    assert all(value == 2 for value in row["checks_passed"].values())
    assert row["envelope_bytes"] >= 16
    assert row["encrypt_mib_per_s"] > 0
