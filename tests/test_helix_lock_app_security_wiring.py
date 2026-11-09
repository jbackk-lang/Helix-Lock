"""Primary desktop entry-point wiring regressions; safe to import headlessly."""


def test_primary_app_exposes_protected_key_writer():
    import helix_lock_app

    assert callable(helix_lock_app.write_new_key_file)


def test_primary_app_uses_shared_atomic_output_writer():
    import helix_lock_app

    assert callable(helix_lock_app.atomic_write_bytes)
