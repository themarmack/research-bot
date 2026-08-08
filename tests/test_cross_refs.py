"""Deterministic cross-reference lint — no dangling references.

Conservative on purpose: only checks references with a single unambiguous
resolution (scheduled-jobs skill ids, a few known file refs), to avoid the
false positives a broad backtick scan would produce.
"""
import yaml

from _util import REPO_ROOT, SKILLS, SCRIPTS


def _skill_dirs():
    return {p.name for p in SKILLS.iterdir() if p.is_dir()}


def test_scheduled_jobs_skills_resolve():
    with open(SCRIPTS / "scheduled-jobs.yml") as f:
        data = yaml.safe_load(f)
    skills = _skill_dirs()
    for job in data["jobs"]:
        assert job["skill"] in skills, f"job '{job['id']}' references missing skill '{job['skill']}'"


def test_email_sender_referenced_files_exist():
    base = SKILLS / "email-sender"
    for fname in ("render_and_send.py", "email_recipients.py", "SKILL.md"):
        assert (base / fname).exists(), f"email-sender missing {fname}"


def test_daily_cve_digest_stack_file_exists():
    assert (SKILLS / "daily-cve-digest" / "stack.yml").exists()


def test_skills_symlink_resolves_to_dot_claude():
    # The evolve bridge: root `skills/` must resolve to `.claude/skills/`.
    link = REPO_ROOT / "skills"
    assert link.is_symlink()
    assert link.resolve() == (REPO_ROOT / ".claude" / "skills").resolve()
