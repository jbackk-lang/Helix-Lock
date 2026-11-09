"""Primary desktop entry-point wiring regressions; safe to import headlessly."""


def test_primary_app_exposes_protected_key_writer():
    import helix_lock_app

    assert callable(helix_lock_app.write_new_key_file)


def test_primary_app_uses_shared_atomic_output_writer():
    import helix_lock_app

    assert callable(helix_lock_app.atomic_write_bytes)



def test_output_path_guard_rejects_same_path_and_symlink(tmp_path):
    import os
    import pytest
    from helix_lock_app import paths_refer_to_same_file

    source = tmp_path / "encrypted.helixpro"
    source.write_bytes(b"ciphertext")
    assert paths_refer_to_same_file(str(source), str(source))

    alias = tmp_path / "alias.helixpro"
    try:
        alias.symlink_to(source)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable in this environment")
    assert paths_refer_to_same_file(str(source), str(alias))


def test_output_path_guard_rejects_hardlink_alias(tmp_path):
    import os
    import pytest
    from helix_lock_app import paths_refer_to_same_file

    source = tmp_path / "encrypted.helixpro"
    source.write_bytes(b"ciphertext")
    alias = tmp_path / "hardlink.helixpro"
    try:
        os.link(source, alias)
    except OSError:
        pytest.skip("hard links unavailable in this environment")
    assert paths_refer_to_same_file(str(source), str(alias))
