"""Deterministic tests for the email distribution-list parser.

The parser decides WHO receives email, so its behavior is load-bearing.
"""
from _util import SKILLS, load_module

er = load_module(SKILLS / "email-sender" / "email_recipients.py", "email_recipients")


def parse(text):
    return er.parse_recipients(text)


def test_basic_bullets_under_recipients():
    doc = """## Recipients
- alice@example.com
- bob@example.com
"""
    assert parse(doc)["recipients"] == ["alice@example.com", "bob@example.com"]


def test_frontmatter_is_stripped():
    doc = """---
title: Email Distribution
tags: [config]
---
## Recipients
- alice@example.com
"""
    assert parse(doc)["recipients"] == ["alice@example.com"]


def test_only_recipients_section_is_live():
    doc = """## How to edit
- example@nowhere.com
## Recipients
- real@example.com
## Notes
- footer@example.com
"""
    out = parse(doc)
    assert out["recipients"] == ["real@example.com"]
    # emails outside the section are reported as ignored, never sent
    assert "example@nowhere.com" in out["ignored"]
    assert "footer@example.com" in out["ignored"]


def test_html_comment_pauses_a_recipient():
    doc = """## Recipients
- active@example.com
<!-- - paused@example.com — out on PTO -->
"""
    out = parse(doc)
    assert out["recipients"] == ["active@example.com"]
    assert "paused@example.com" not in out["recipients"]
    assert "paused@example.com" not in out["ignored"]


def test_multiple_emails_on_one_bullet():
    doc = """## Recipients
- alice@example.com, bob@example.com
"""
    assert parse(doc)["recipients"] == ["alice@example.com", "bob@example.com"]


def test_case_insensitive_dedup_preserves_first():
    doc = """## Recipients
- Alice@Example.com
- alice@example.com
"""
    assert parse(doc)["recipients"] == ["Alice@Example.com"]


def test_fenced_code_block_is_ignored():
    doc = """## Recipients
- real@example.com
```
- codeblock@example.com
```
"""
    out = parse(doc)
    assert out["recipients"] == ["real@example.com"]
    assert "codeblock@example.com" not in out["recipients"]


def test_bare_email_line_without_bullet_counts():
    doc = """## Recipients
plain@example.com
"""
    assert parse(doc)["recipients"] == ["plain@example.com"]


def test_recipients_heading_is_case_insensitive():
    doc = """## RECIPIENTS
- a@example.com
"""
    assert parse(doc)["recipients"] == ["a@example.com"]


def test_subsection_stays_in_scope():
    doc = """## Recipients
### Leadership
- ciso@example.com
### Engineering
- vp@example.com
"""
    assert parse(doc)["recipients"] == ["ciso@example.com", "vp@example.com"]


def test_no_recipients_section_yields_empty():
    doc = """## Notes
- someone@example.com
"""
    assert parse(doc)["recipients"] == []


def test_validate_accepts_normal_and_rejects_malformed():
    assert er.validate("a@b.co")
    assert not er.validate("bad@@invalid")
    assert not er.validate("no-at-sign.com")
    assert not er.validate("has space@example.com")


def test_matches_real_distribution_list(tmp_path):
    """Sanity: the committed live list parses to two real recipients."""
    from pathlib import Path
    live = Path.home() / "Obsidian/Research-Brain/_config/email-distribution.md"
    if not live.exists():
        import pytest
        pytest.skip("live distribution list not present")
    out = parse(live.read_text(encoding="utf-8"))
    assert "michael.marmack@gmail.com" in out["recipients"]
    assert "michael.marmack2@spglobal.com" in out["recipients"]
    assert all(er.validate(a) for a in out["recipients"])
