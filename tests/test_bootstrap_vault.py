"""Deterministic tests for the vault bootstrap script.

The script is the only path a new user has to a working vault, and it writes
into a directory that may already hold hand-edited notes — so the properties
that matter are "creates the documented tree" and "never clobbers by default".
"""
import pytest

from _util import REPO_ROOT, SCRIPTS, load_module

bv = load_module(SCRIPTS / "bootstrap-vault.py", "bootstrap_vault")


def test_creates_every_documented_folder(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)
    for rel in bv.VAULT_DIRS:
        assert (vault / rel).is_dir(), f"missing folder: {rel}"


def test_copies_the_meta_scaffold(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)
    assert (vault / "_meta/conventions.md").is_file()
    assert (vault / "_meta/tags.md").is_file()
    assert (vault / "_meta/inbox-rules.md").is_file()
    # All nine folder schemas the vault-conventions skill expects.
    schemas = sorted(p.name for p in (vault / "_meta/schema").glob("*.yml"))
    assert len(schemas) == 9, schemas


def test_copies_obsidian_note_templates(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)
    templates = list((vault / ".templates").glob("*.md"))
    assert templates, "no note templates copied"


def test_seeds_config_from_skill_examples(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)
    assert (vault / "_config/email-distribution.md").is_file()
    assert (vault / "_config/exec-preferences.md").is_file()


def test_is_idempotent(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)
    second = bv.bootstrap(vault)
    assert second.copied == [], "second run rewrote files"
    assert second.created == [], "second run recreated folders"


def test_does_not_clobber_user_edits(tmp_path):
    """The whole point: a populated vault must survive a re-run."""
    vault = tmp_path / "vault"
    bv.bootstrap(vault)

    edited = vault / "_config/email-distribution.md"
    edited.write_text("## Recipients\n- someone@example.com\n", encoding="utf-8")
    note = vault / "facts/copilot/ip-indemnity.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text("durable fact", encoding="utf-8")

    bv.bootstrap(vault)

    assert "someone@example.com" in edited.read_text(encoding="utf-8")
    assert note.read_text(encoding="utf-8") == "durable fact"


def test_force_refreshes_scaffold_but_spares_config(tmp_path):
    vault = tmp_path / "vault"
    bv.bootstrap(vault)

    conventions = vault / "_meta/conventions.md"
    conventions.write_text("stale", encoding="utf-8")
    config = vault / "_config/email-distribution.md"
    config.write_text("## Recipients\n- keep@example.com\n", encoding="utf-8")

    bv.bootstrap(vault, force=True)

    assert conventions.read_text(encoding="utf-8") != "stale", "scaffold not refreshed"
    assert "keep@example.com" in config.read_text(encoding="utf-8"), "config clobbered"


def test_dry_run_writes_nothing(tmp_path):
    vault = tmp_path / "vault"
    r = bv.bootstrap(vault, dry_run=True)
    assert not vault.exists()
    assert r.created, "dry run should still report planned work"


def test_missing_template_dir_stops_and_reports(tmp_path):
    with pytest.raises(FileNotFoundError):
        bv.bootstrap(tmp_path / "vault", template_dir=tmp_path / "nope")


def test_vault_dirs_match_conventions_layout():
    """The conventions file is the spec; VAULT_DIRS is the implementation.

    Every folder named in the Layout table must actually get created, or a
    skill will write into a directory that does not exist.
    """
    conventions = (REPO_ROOT / "vault-template/_meta/conventions.md").read_text(
        encoding="utf-8"
    )
    created = set(bv.VAULT_DIRS)
    for folder in [
        "_meta", "_config", "_inbox", "_views",
        "people", "projects", "decisions", "insights",
        "facts", "events", "research", "digests",
    ]:
        assert f"`{folder}/" in conventions, f"{folder} not documented in conventions"
        assert folder in created, f"{folder} documented but never created"
