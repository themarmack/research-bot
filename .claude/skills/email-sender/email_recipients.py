#!/usr/bin/env python3
"""email_recipients.py — parse the email-sender distribution list.

Extracts recipient addresses from `email-distribution.md` per the spec in
SKILL.md "## Parsing". Pure string->list logic so it is unit-testable and lives
in exactly one place; the send flow calls this instead of re-deriving the
parser ad hoc on every invocation.

CLI: `python email_recipients.py <path-to-email-distribution.md>` prints
`{"recipients": [...], "ignored": [...]}` as JSON. `recipients` are the
extracted, case-insensitively de-duplicated addresses under the `## Recipients`
heading; `ignored` are email-shaped strings found OUTSIDE that section
(diagnostic only — never sent to). Apply `validate()` per recipient before
sending; a malformed entry is skipped, not fatal.
"""
import json
import re
import sys

# Email-shaped substring (extraction). Matches the SKILL.md "## Parsing" regex.
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
# Per-recipient validation applied before sending (stricter single-@ shape).
VALID_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_frontmatter(text):
    """Remove a leading YAML frontmatter block (---\\n...\\n---\\n)."""
    if text.startswith("---"):
        m = FRONTMATTER_RE.match(text)
        if m:
            return text[m.end():]
    return text


def validate(addr):
    """True if addr passes the send-time recipient validation."""
    return bool(VALID_RE.match(addr))


def _dedup_ci(items, already=None):
    """Case-insensitive de-dup, order-preserving. `already` seeds seen keys."""
    seen = set(already or ())
    out = []
    for e in items:
        k = e.lower()
        if k not in seen:
            seen.add(k)
            out.append(e)
    return out, seen


def parse_recipients(text):
    """Parse a distribution-list Markdown doc.

    Returns {"recipients": [...], "ignored": [...]}:
      - recipients: addresses under the `## Recipients` H2 (bullets, or a line
        that is itself an email), extracted and case-insensitively de-duped.
      - ignored: email-shaped strings found outside `## Recipients` (diagnostic).
    """
    text = strip_frontmatter(text)
    text = COMMENT_RE.sub("", text)

    in_recipients = False
    in_fence = False
    recips = []
    ignored = []

    for raw in text.splitlines():
        s = raw.strip()
        if s.startswith("```"):          # fenced code block boundary
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if s.startswith("## "):          # H2 opens/closes the Recipients scope
            in_recipients = s[3:].strip().lower() == "recipients"
            continue
        # `###` subsections stay in scope; other lines fall through to matching.
        emails = EMAIL_RE.findall(s)
        if not emails:
            continue
        if in_recipients:
            is_bullet = s.startswith("-") or s.startswith("*")
            whole_is_email = EMAIL_RE.fullmatch(s) is not None
            if is_bullet or whole_is_email:
                recips.extend(emails)
        else:
            ignored.extend(emails)

    recipients, seen = _dedup_ci(recips)
    ignored_dedup, _ = _dedup_ci(ignored, already=seen)
    return {"recipients": recipients, "ignored": ignored_dedup}


def main(argv):
    if len(argv) != 2:
        print(json.dumps({"error": "usage: email_recipients.py <dist-file>"}))
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(json.dumps({"error": f"cannot read {argv[1]}: {e}"}))
        return 1
    print(json.dumps(parse_recipients(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
