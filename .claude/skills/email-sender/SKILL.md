---
name: email-sender
description: Send a freshly-written vault note (digest or research) via Gmail SMTP to the single distribution list defined in `~/Obsidian/Research-Brain/_config/email-distribution.md`. Scheduled digests auto-send to everyone on the list; research notes prompt the user `[y/n]` before sending. Loads recipients from a plain-Markdown bullet list — Obsidian-native, no YAML, no per-digest routing. Stop-and-reports on missing config, empty list, missing `GMAIL_APP_PASSWORD`, or SMTP failure. Reads Gmail credentials from `~/.config/research-bot/env` (`GMAIL_SEND_ADDRESS` + `GMAIL_APP_PASSWORD`). Use immediately after `vault-writer.write_digest` or `vault-writer.write_research` succeeds.
---

# email-sender

The post-write distribution hook. Every vault write worth surfacing beyond the local Obsidian copy goes through here. Scheduled digests fire-and-forget to the distribution list; ad-hoc research notes prompt the user `[y/n]` before sending. The vault note remains the canonical record; email is a delivery channel, not a replacement.

## When to use

- Immediately after `vault-writer.write_digest()` succeeds — invoked from `scheduled-agent-runner` step 11.
- Immediately after `vault-writer.write_research()` succeeds in any Category 1 researcher — researcher invokes `prompt_then_send`.
- User explicitly asks: "email this", "send the latest weekly digest to my distribution list", "show me my distribution list".

## When NOT to use

- Writes to `facts/`, `events/`, `decisions/`, `insights/`, `people/`, `projects/`, `_inbox/` — durable knowledge, not distribution targets. (`auto_send` no-ops on these surfaces.)
- Non-interactive context AND surface is `research` — `prompt_then_send` requires a user; degrade gracefully by skipping.
- Mid-stream (vault write hasn't completed yet — wait for the write).

## Prerequisites

Two pieces of config:

1. **Gmail credentials** at `~/.config/research-bot/env`:
   ```
   GMAIL_SEND_ADDRESS=you@gmail.com
   GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx
   ```
   Requires 2-Step Verification enabled on the account. Generate at https://myaccount.google.com/apppasswords ("Mail" → "Other / research-bot"). Use the helper script: `scripts/set-gmail-credentials.sh "you@gmail.com" "xxxx xxxx xxxx xxxx"` (note the leading space to keep the command out of shell history).

2. **Distribution list** at `~/Obsidian/Research-Brain/_config/email-distribution.md`. Copy [`email-distribution.example.md`](./email-distribution.example.md) to that path on first use and edit.

If either is missing, the skill stops and reports — never silently drops.

## Helpers

### `send_note(note_path, subject_override=None)`

The primary action. Steps:

1. Resolve `note_path` to an absolute path; read the file (Markdown with optional YAML frontmatter).
2. Load and parse `~/Obsidian/Research-Brain/_config/email-distribution.md` (see [Parsing](#parsing)).
3. Read `GMAIL_SEND_ADDRESS` and `GMAIL_APP_PASSWORD` from the environment. Missing → stop-and-report referencing the setup helper.
4. Build the message:
   - **Subject**: `subject_override` if given, else derive from the note (see [Subject derivation](#subject-derivation)).
   - **Body**: full Markdown of the note (frontmatter stripped), plus a footer linking back to the vault path.
   - **From**: `GMAIL_SEND_ADDRESS`. **To**: `GMAIL_SEND_ADDRESS` (self). **Bcc**: every parsed recipient — addresses are NOT disclosed to other recipients.
5. Open `smtplib.SMTP_SSL("smtp.gmail.com", 465)`, `login(GMAIL_SEND_ADDRESS, GMAIL_APP_PASSWORD)`, `send_message(...)`, close.
6. Per-recipient validation: skip addresses that don't match `^[^\s@]+@[^\s@]+\.[^\s@]+$`. A single bad entry doesn't lose the rest.

Return:

```python
{
    "sent_to":  ["addr1@example.com", "addr2@example.com"],
    "skipped":  [{"email": "bad@@invalid", "reason": "invalid format"}],
    "subject":  "[Weekly Intelligence Digest] 2026-06-22 — ...",
    "from":     "you@gmail.com"
}
```

### `prompt_then_send(note_path)`

For research notes. Asks the user, then calls `send_note` or skips.

1. Load + parse the distribution list (so the prompt can show the recipient count).
2. Ask the user: `"Send this research note to your distribution list (N recipients)? [y/n]"` — also show the first 3 recipients to confirm the right list.
3. Parse the answer. `y` / `yes` / `send` → call `send_note(note_path)`. Anything else → skip.
4. Return `{action: "sent" | "skipped", ...}`.

### `auto_send(note_path, surface)`

Non-interactive path for `scheduled-agent-runner` step 11.

1. If `surface != "digest"` → no-op, return `{action: "noop", reason: "non-digest surface"}`.
2. Load + parse the distribution list. Missing/empty → stop-and-report (surfaces in runner summary as `email_failed=...`).
3. Call `send_note(note_path)`. Return its result with `action: "sent"`.

This helper **never prompts** — non-interactive scheduled context. Misconfig still stop-and-reports per the rules below; the digest itself remains written.

### `show_list()`

User-facing diagnostic. Loads, parses, and prints the distribution-list contents — what would happen on the next send. No mail traffic. Useful before relying on auto-send.

## Parsing

The distribution-list file is Markdown. The parser:

1. Strips YAML frontmatter (the `---\n...\n---\n` block at the top, if present).
2. Strips HTML comments (`<!-- ... -->`) — anything inside is ignored, so commenting out a bullet pauses the recipient.
3. Scans line by line. A line contributes a recipient if:
   - It starts with `-` (a Markdown bullet) AND contains an email-shaped substring, OR
   - The entire line, after stripping whitespace, IS an email-shaped substring (no leading bullet required).
4. Email regex: `\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b`.
5. Multiple emails on one bullet line are all extracted (so `- alice@example.com, bob@example.com` works).
6. Case-insensitive deduplication on the parsed list.

Prose mentions of an email (text not on a bullet and not standing alone on a line) are ignored — only structurally list-shaped lines count. This means you can write whatever you want above the recipient list without leaking addresses into the send.

Validation: if 0 recipients are parsed, **stop and report** — the file exists but is empty of structurally-list-shaped emails. The user is told to add at least one bullet.

## Stop and report — enumerated cases

Each surfaces a structured error to the caller (and to the runner summary line for scheduled jobs):

1. **Distribution list missing** → `"email-distribution.md not found at ~/Obsidian/Research-Brain/_config/email-distribution.md. Copy .claude/skills/email-sender/email-distribution.example.md to that path and edit."`
2. **List parses to zero recipients** → `"email-distribution.md contains no email addresses on bullet lines. Add at least one '- you@example.com' line."`
3. **`GMAIL_APP_PASSWORD` missing** → `"GMAIL_APP_PASSWORD not set in ~/.config/research-bot/env. Run 'scripts/set-gmail-credentials.sh \"you@gmail.com\" \"xxxx xxxx xxxx xxxx\"' to set."`
4. **`GMAIL_SEND_ADDRESS` missing** → similar.
5. **SMTP auth failure** → `"Gmail SMTP auth failed for <send-address>. App password may be expired or revoked — regenerate at https://myaccount.google.com/apppasswords."`
6. **SMTP send failure (network, server-level bounce)** → `"Send failed: <smtplib error>. Per-recipient results: [sent=N, skipped=M]."`
7. **Invalid email format on a recipient** → skip that recipient, continue with the rest, surface in the return `skipped` list (NOT a stop-and-report — degraded delivery proceeds).

The vault note remains written even if email fails. Email is a delivery channel, not a write-blocker.

## Message body shape (v1 — plain text Markdown)

```
{full markdown of the note, frontmatter stripped}

---
Landed in your vault at: digests/weekly/2026-06-22-weekly-intelligence-digest.md
Sent via research-bot email-sender. Distribution list lives in your vault at _config/email-distribution.md.
```

Gmail's web UI renders Markdown ASCII passably. The vault path in the footer points the reader back to the canonical copy. HTML rendering, attachments, and inline images are explicitly out of scope for v1.

## Subject derivation

| Source | Subject template | Example |
|--------|------------------|---------|
| Digest (`vault/digests/{cadence}/...`) | `[{Cadence Title-Case} {Skill Title-Case}] {YYYY-MM-DD} — {first H1 of body, truncated to 60 chars}` | `[Weekly Intelligence Digest] 2026-06-22 — Copilot Q3 roadmap & 3 new CVEs` |
| Research (`vault/research/{topic}/...`) | `[{Topic Title-Case} Research] {YYYY-MM-DD} — {frontmatter.title, truncated to 60 chars}` | `[Copilot Research] 2026-06-22 — Agentic features & SR 11-7 implications` |
| Override | Use `subject_override` verbatim. | n/a |

Truncation at 60 chars + `…` keeps the subject readable. Note frontmatter `title` is the source of truth when present; H1 of body is the fallback.

## Composes with

- [`vault-writer`](../vault-writer/SKILL.md) — successful return triggers email-sender invocation. vault-writer does NOT call email-sender; the calling skill makes the explicit call.
- [`scheduled-agent-runner`](../scheduled-agent-runner/SKILL.md) — step 11 calls `auto_send`.
- Category 1 researchers (`copilot-deep-dive`, `sdlc-best-practice`, `financial-regulator-watch`, `ai-governance-research`, `peer-bank-tech-intel`, `incident-postmortem-research`, `copilot-faq-answerer`, …) — call `prompt_then_send` after `vault-writer.write_research` succeeds.

## Acceptance test (single SMTP round-trip)

1. Create a minimal `email-distribution.md` in the vault with one bullet pointing to the user's own email.
2. Pick any existing digest in `~/Obsidian/Research-Brain/digests/`.
3. Invoke: `email-sender.send_note("<that path>")`.
4. Confirm: email lands in inbox within ~10 seconds; subject follows the template; body contains the digest Markdown; footer references the vault path.
5. Misconfig drill: remove `GMAIL_APP_PASSWORD` from env; re-invoke; confirm stop-and-report #3 surfaces exactly as documented.
6. Bad-recipient drill: add `bad@@invalid` to the list; send; confirm the valid recipient gets mail and `skipped` lists the bad entry.
7. Pause drill: wrap a bullet with `<!-- ... -->`; re-parse; confirm that address is excluded.
