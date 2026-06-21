---
name: email-sender
description: Send a freshly-written vault note (digest or research) via Gmail SMTP to a configured recipient list. Loads lists from `~/Obsidian/Research-Brain/_config/email-lists.yml`; auto-routes scheduled digests per the `digest_routing` map; prompts the user for research notes. Stop-and-reports on missing config, malformed YAML, unknown list, empty list, missing `GMAIL_APP_PASSWORD`, or SMTP failure. Reads Gmail credentials from `~/.config/research-bot/env` (`GMAIL_SEND_ADDRESS` + `GMAIL_APP_PASSWORD`). Use immediately after `vault-writer.write_digest` or `vault-writer.write_research` succeeds.
---

# email-sender

The post-write distribution hook. Every vault write that's worth surfacing beyond the local Obsidian copy goes through here. Scheduled digests get auto-routed via `digest_routing`; ad-hoc research notes prompt the user for a list (or skip). The vault note remains the canonical record; email is a delivery channel, not a replacement.

## When to use

- Immediately after `vault-writer.write_digest()` succeeds — invoked from `scheduled-agent-runner` step 12.
- Immediately after `vault-writer.write_research()` succeeds in any Category 1 researcher — researcher invokes `prompt_then_send`.
- User explicitly asks: "email this to {list}", "send the latest weekly digest to leadership", "what are my email lists?".

## When NOT to use

- Writes to `facts/`, `events/`, `decisions/`, `insights/`, `people/`, `projects/`, `_inbox/` — those are durable knowledge, not distribution targets. (`auto_send_if_routed` no-ops on these surfaces.)
- The user is in a non-interactive context AND the surface is `research` — `prompt_then_send` requires a user; degrade gracefully by skipping.
- Sending to a list when the calling skill is mid-stream (vault write hasn't actually completed yet — wait for the write).

## Prerequisites

Two pieces of config:

1. **Gmail credentials** at `~/.config/research-bot/env`:
   ```
   GMAIL_SEND_ADDRESS=you@gmail.com
   GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```
   Requires 2-Factor Auth enabled on the Google account. Generate the 16-char app password at https://myaccount.google.com/apppasswords (select "Mail" → "Other / research-bot").

2. **Recipient lists** at `~/Obsidian/Research-Brain/_config/email-lists.yml`. Copy [`recipients.example.yml`](./recipients.example.yml) to that path on first use and edit.

If either is missing, the skill stops and reports — never silently drops.

## Helpers

The three behaviors callers invoke. Implementation is Python via `smtplib.SMTP_SSL("smtp.gmail.com", 465)` — no third-party dependencies needed (`pyyaml` is already pulled in by the scheduling system).

### `send_to_list(note_path, list_name, subject_override=None)`

The primary action. Steps:

1. Resolve `note_path` to an absolute path; read the file. The file is a Markdown note with YAML frontmatter.
2. Load and validate `~/Obsidian/Research-Brain/_config/email-lists.yml` (see [Validation](#validation)).
3. Look up `lists[list_name]`. Unknown → stop-and-report with the available list names.
4. Read `GMAIL_SEND_ADDRESS` and `GMAIL_APP_PASSWORD` from the environment. Missing → stop-and-report referencing `~/.config/research-bot/env`.
5. Build the message:
   - **Subject**: `subject_override` if given, else derive from the note: `[{cadence or topic}] {YYYY-MM-DD} — {title}`. `cadence` and `title` come from the note's frontmatter; date comes from the file path. Example: `[Weekly Intelligence Digest] 2026-06-22 — Copilot Q3 roadmap & 3 new CVEs`.
   - **Body**: the full Markdown of the note (frontmatter stripped), plus a footer: `\n\n---\nLanded in your vault at: {vault-relative path}. This message was sent via the research-bot email-sender skill.`
   - **From**: `GMAIL_SEND_ADDRESS`. **To**: each recipient's email. Use `Bcc` for >1 recipient so addresses aren't disclosed across the list.
   - Message format: `email.message.EmailMessage` with plain-text content type. (HTML rendering is explicitly v2.)
6. Open `smtplib.SMTP_SSL("smtp.gmail.com", 465)`, `login(GMAIL_SEND_ADDRESS, GMAIL_APP_PASSWORD)`, `send_message(...)`, close.
7. Per-recipient try/except: a single bad address skips that recipient and continues. The return value lists what worked and what didn't.

Return:

```python
{
    "sent_to": ["addr1@example.com", "addr2@example.com"],
    "skipped": [{"email": "bad@@invalid", "reason": "invalid format"}],
    "errors": [],            # per-recipient SMTP errors (not auth — auth fails whole send)
    "subject": "[Weekly Intelligence Digest] 2026-06-22 — ...",
    "list_name": "leadership"
}
```

### `prompt_then_send(note_path, suggested_list=None)`

For research notes. Asks the user, then calls `send_to_list` or skips.

1. Load and validate the config (same as above).
2. Read `lists.keys()` — the available list names.
3. Ask the user in conversation: `"Email this research note to which list? Available: leadership, team, self — or 'skip'."` If `suggested_list` is provided, mention it as the default ("default: self").
4. Parse the response. Accept exact list name, "skip", "no", or empty (treat as skip).
5. If skip → return `{action: "skipped", reason: "user_choice"}`.
6. If a valid list name → call `send_to_list(note_path, list_name)` and return the result with `action: "sent"`.
7. If invalid → re-ask once, then default to skip.

### `auto_send_if_routed(note_path, surface, agent_name)`

The non-interactive path for `scheduled-agent-runner` step 12.

1. If `surface != "digest"` → no-op, return `{action: "noop", reason: "non-digest surface"}`.
2. Load + validate the config.
3. Look up `digest_routing[agent_name]`. Absent → no-op, return `{action: "noop", reason: "no routing entry"}`. (Not every digest needs auto-send.)
4. Call `send_to_list(note_path, digest_routing[agent_name])` and return its result with `action: "sent"`.

This helper **never prompts** — it's invoked from a non-interactive scheduled run. Misconfig (malformed YAML, missing env var, unknown list) still stop-and-reports per the rules below, surfacing to the runner's summary line.

## Validation

`email-lists.yml` schema:

```yaml
version: int          # required, must equal 1
lists:                # required, map<list-name, list-spec>, non-empty
  <name>:
    description: str  # required
    recipients:       # required, list, non-empty
      - email: str    # required
        name: str     # required
        role: str     # optional
digest_routing:       # optional, map<agent-id, list-name>
  <agent-id>: <list-name>
```

Validation runs on every load (no edit-time hook — follows the `source-registry` pattern). Loader:

1. File exists at `~/Obsidian/Research-Brain/_config/email-lists.yml`. Missing → stop-and-report (#1 below).
2. YAML parses. Parser error → stop-and-report (#2).
3. `version == 1`. Wrong → stop-and-report (#3).
4. `lists` present, non-empty. Each entry has `description` (str) and `recipients` (non-empty list of dicts with `email` + `name`). Schema mismatch → stop-and-report (#3).
5. For every entry in `digest_routing`, the value must be a key of `lists`. Unknown reference → stop-and-report (#4).

Email-format validation (RFC-5322 simplified — `^[^@\s]+@[^@\s]+\.[^@\s]+$`) is applied **per recipient at send time**, not at load time. Bad addresses are skipped, not fatal — degraded delivery beats no delivery.

## Stop and report — enumerated cases

Each surfaces a structured error to the caller (and to the digest's summary line when invoked from `scheduled-agent-runner`):

1. **Vault config missing** → `"email-lists.yml not found at ~/Obsidian/Research-Brain/_config/email-lists.yml. Copy .claude/skills/email-sender/recipients.example.yml to that path and edit."`
2. **YAML malformed** → `"Failed to parse email-lists.yml (line N: <yaml.YAMLError>). Fix and retry."`
3. **Schema invalid** → `"email-lists.yml schema error at <field>: <what's wrong>. See .claude/skills/email-sender/recipients.example.yml for the canonical shape."`
4. **Unknown list name** → `"List '<name>' not found. Available: [<comma-separated list of keys>]."`
5. **Empty list** → `"List '<name>' has no recipients. Add at least one {email, name} entry."`
6. **`GMAIL_APP_PASSWORD` missing** → `"GMAIL_APP_PASSWORD not set in ~/.config/research-bot/env. See README §Email delivery (optional) for setup."`
7. **`GMAIL_SEND_ADDRESS` missing** → `"GMAIL_SEND_ADDRESS not set in ~/.config/research-bot/env. See README §Email delivery (optional) for setup."`
8. **SMTP auth failure** → `"Gmail SMTP auth failed for <send-address>. App password may be expired or revoked — regenerate at https://myaccount.google.com/apppasswords."`
9. **SMTP send failure (network, recipient bounce at server level)** → `"Send failed: <smtplib error>. Per-recipient results: [sent=N, failed=M]."`
10. **Invalid email format on a recipient** → skip that recipient, continue with the rest, surface in the return `skipped` list (NOT a stop-and-report — degraded delivery proceeds).

The vault note remains written even if the send fails. Email is a delivery channel, not a write-blocker.

## Message body shape (v1 — plain text Markdown)

```
{full markdown of the note, frontmatter stripped}

---
Landed in your vault at: digests/weekly/2026-06-22-weekly-intelligence-digest.md
Sent via research-bot email-sender. Configured lists live in your vault at _config/email-lists.yml.
```

Gmail's web UI renders Markdown ASCII passably. The vault path in the footer points the reader back to the canonical copy. HTML rendering, attachments, and inline images are explicitly out of scope for v1.

## Subject derivation

| Source | Subject template | Example |
|--------|------------------|---------|
| Digest (`vault/digests/{cadence}/...`) | `[{Cadence Title-Case} {Skill Title-Case}] {YYYY-MM-DD} — {first H1 of body, truncated to 60 chars}` | `[Weekly Intelligence Digest] 2026-06-22 — Copilot Q3 roadmap & 3 new CVEs` |
| Research (`vault/research/{topic}/...`) | `[{Topic Title-Case} Research] {YYYY-MM-DD} — {frontmatter.title, truncated to 60 chars}` | `[Copilot Research] 2026-06-22 — Agentic features & SR 11-7 implications` |
| Override | Use `subject_override` verbatim. | n/a |

Truncation at 60 chars + `…` keeps the subject readable in mail clients. The note's frontmatter `title` is the source of truth when present; H1 of body is the fallback.

## Composes with

- [`vault-writer`](../vault-writer/SKILL.md) — the writer whose successful return triggers an email-sender invocation. vault-writer itself does NOT call email-sender; the calling skill (scheduled-agent-runner, or a Category 1 researcher) makes the explicit call.
- [`scheduled-agent-runner`](../scheduled-agent-runner/SKILL.md) — step 12 calls `auto_send_if_routed`.
- Category 1 researchers (`copilot-deep-dive`, `sdlc-best-practice`, `financial-regulator-watch`, `ai-governance-research`, `peer-bank-tech-intel`, `incident-postmortem-research`, `copilot-faq-answerer`, …) — call `prompt_then_send` after `vault-writer.write_research` succeeds.

## Acceptance test (single SMTP round-trip)

A live exercise to confirm the SMTP path:

1. Create a minimal `email-lists.yml` in the vault with one list `self` containing the user's own email.
2. Pick any existing digest in `~/Obsidian/Research-Brain/digests/`.
3. Invoke: `email-sender.send_to_list("<that path>", "self")`.
4. Confirm: the email lands in the user's inbox within ~10 seconds, the subject follows the template, the body contains the digest Markdown, the footer references the vault path.
5. Misconfig drill: remove `GMAIL_APP_PASSWORD` from env, re-invoke, confirm stop-and-report message #6 surfaces exactly as documented (no partial send, no silent skip).
6. Bad-recipient drill: add `bad@@invalid` to a second list with one valid + one invalid entry, send, confirm the valid recipient receives mail and `skipped` contains the bad entry.

If any of these fail, fix the skill before relying on auto-send from scheduled jobs.
