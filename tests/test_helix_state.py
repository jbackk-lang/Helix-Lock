import hashlib

import pytest

from helix_pro.helix_state import (
    HelixStateRecord,
    canonical_state_bytes,
    hkss_digest,
)


def make_record(**overrides):
    values = dict(
        object_id="object-01",
        key_purpose="file-encryption",
        epoch=3,
        timdr_revision="gia-timdr@abc123",
        adapter_version="0.1.0",
        previous_checkpoint="checkpoint-02",
        projections={
            "M/S": {"tempo": "1.2500", "drift": "-0.002", "unit": "s"},
            "G": {"surface_id": "mesh-7", "s_periodic": False},
            "K": {"phase": "1.5707963267948966", "unit": "rad"},
        },
    )
    values.update(overrides)
    return HelixStateRecord(**values)


def test_canonical_serialization_is_repeatable():
    record = make_record()
    assert canonical_state_bytes(record) == canonical_state_bytes(record)


def test_projection_mapping_order_does_not_change_encoding():
    a = make_record(projections={"M/S": {"tempo": "1.25"}, "K": {"phase": "0.5"}})
    b = make_record(projections={"K": {"phase": "0.5"}, "M/S": {"tempo": "1.25"}})
    assert canonical_state_bytes(a) == canonical_state_bytes(b)


def test_projection_namespaces_remain_distinct():
    a = make_record(projections={"M/S": {"value": "1"}, "K": {"value": "2"}})
    b = make_record(projections={"M/S": {"value": "2"}, "K": {"value": "1"}})
    assert hkss_digest(a) != hkss_digest(b)


def test_digest_has_domain_separated_sha256_shape():
    record = make_record()
    digest = hkss_digest(record)
    expected = hashlib.sha256(
        b"HELIX-HTKE-HKSS-v1\x00" + canonical_state_bytes(record)
    ).hexdigest()
    assert digest == expected
    assert len(digest) == 64


@pytest.mark.parametrize("field,value", [
    ("object_id", ""),
    ("key_purpose", "bad value with spaces"),
    ("timdr_revision", ""),
    ("adapter_version", ""),
    ("epoch", -1),
    ("epoch", True),
    ("schema_version", 2),
])
def test_invalid_metadata_is_rejected(field, value):
    with pytest.raises(ValueError):
        make_record(**{field: value})


def test_unknown_projection_is_rejected():
    with pytest.raises(ValueError, match="unknown TIMDR projection"):
        make_record(projections={"X": {"value": "1"}})


def test_projection_payload_must_be_object():
    with pytest.raises(ValueError, match="must be an object"):
        make_record(projections={"K": ["not", "an", "object"]})


def test_floats_are_rejected_for_cross_runtime_canonicalization():
    with pytest.raises(ValueError, match="decimal strings"):
        make_record(projections={"K": {"phase": 1.25}})


def test_nested_non_string_keys_are_rejected():
    with pytest.raises(ValueError, match="keys must be strings"):
        make_record(projections={"G": {"nested": {1: "value"}}})


def test_digest_changes_when_epoch_or_checkpoint_changes():
    base = make_record()
    assert hkss_digest(base) != hkss_digest(make_record(epoch=4))
    assert hkss_digest(base) != hkss_digest(make_record(previous_checkpoint="checkpoint-03"))


def test_record_is_immutable_at_attribute_level():
    record = make_record()
    with pytest.raises((AttributeError, TypeError)):
        record.epoch = 4
