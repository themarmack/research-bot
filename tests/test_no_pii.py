"""Repo-wide guard against committing personal data.

This repo is public. A real address or a developer's home path in a tracked
file is a disclosure that a force-push cannot fully undo (GitHub retains
pull-request diffs), so the cheap fix is to never let one land.

The rule is an explicit allowlist, not a heuristic: every email literal in the
tree must be a reserved-for-documentation domain (RFC 2606/6761) or appear in
`ALLOWED_LITERALS` below. Adding a real address fails the build. Extending the
allowlist is a deliberate, reviewable act — that is the point.
"""
import re
import subprocess

import pytest

from _util import REPO_ROOT

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# RFC 2606 / RFC 6761 domains reserved for documentation and testing.
RESERVED_DOMAINS = {"example.com", "example.org", "example.net", "example.edu"}
RESERVED_TLDS = {".test", ".invalid", ".example", ".localhost"}

# Synthetic values that are obviously not real people. Keep this list short and
# justify each addition — every entry is a hole in the guard.
ALLOWED_LITERALS = {
    "you@gmail.com",        # README/skill placeholder for the sender address
    "me@gmail.com",         # ditto
    "example@nowhere.com",  # placeholder in a skill's example frontmatter
    "a@b.co",               # email-validator fixtures: shortest valid forms
    "a@x.com",
    "b@y.com",
}

# Absolute home directories leak the author's username (and often their
# employer, via the path). Skills must use Path.home() / $HOME instead.
HOME_PATH_RE = re.compile(r"/(?:Users|home)/(?!<)[A-Za-z0-9._-]+/")

# Claude Code mangles a project path into a slug (`-Users-alice-Documents-foo`)
# for `~/.claude/projects/`. Same leak, different shape — the slash-form regex
# above does not see it.
PROJECT_SLUG_RE = re.compile(r"-(?:Users|home)-(?!<)[A-Za-z0-9]")

# Paths that legitimately contain otherwise-forbidden shapes.
EXEMPT_PATHS = {"tests/test_no_pii.py"}


def _tracked_text_files():
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=True,
    ).stdout
    for rel in filter(None, out.split("\0")):
        if rel in EXEMPT_PATHS:
            continue
        path = REPO_ROOT / rel
        # Skip symlinks (the root `skills` -> `.claude/skills` bridge) and
        # anything that isn't decodable as text.
        if path.is_symlink() or not path.is_file():
            continue
        try:
            yield rel, path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


ALL_FILES = list(_tracked_text_files())


def _is_allowed(addr):
    if addr in ALLOWED_LITERALS:
        return True
    domain = addr.rsplit("@", 1)[1].lower()
    return domain in RESERVED_DOMAINS or any(
        domain.endswith(tld) for tld in RESERVED_TLDS
    )


def test_tracked_files_were_found():
    """Guard the guard — a broken git call must not silently pass everything."""
    assert len(ALL_FILES) > 50, "git ls-files returned suspiciously few files"


def test_no_real_email_addresses():
    offenders = [
        f"{rel}: {addr}"
        for rel, text in ALL_FILES
        for addr in EMAIL_RE.findall(text)
        if not _is_allowed(addr)
    ]
    assert not offenders, (
        "Non-placeholder email address(es) in tracked files. Use an "
        "example.com address, or add a justified entry to ALLOWED_LITERALS:\n  "
        + "\n  ".join(sorted(set(offenders)))
    )


@pytest.mark.parametrize("pattern", [HOME_PATH_RE, PROJECT_SLUG_RE], ids=["path", "slug"])
def test_no_absolute_home_paths(pattern):
    offenders = [
        f"{rel}: {match}"
        for rel, text in ALL_FILES
        for match in pattern.findall(text)
    ]
    assert not offenders, (
        "Absolute home path(s) in tracked files — these leak a username and "
        "break on every other machine. Use `Path.home()`, `$HOME`, or a "
        "`<placeholder>`:\n  " + "\n  ".join(sorted(set(offenders)))
    )
