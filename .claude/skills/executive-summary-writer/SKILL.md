---
name: executive-summary-writer
description: Turn an existing research note into a 1-page executive summary personalized to a named audience (e.g. `ciso`, `vp-eng`, `ceo`, or `default`). **Invoke ONLY when the user explicitly asks for an exec summary** — never as a post-write step in a Category 1 researcher flow. Loads audience preferences — length, voice, format, emphasize/avoid lists, special interests, section toggles — from `~/Obsidian/Research-Brain/_config/exec-preferences.md`. Writes the summary to `vault/insights/YYYY-MM-DD-exec-summary-{audience}-{slug}.md` via `vault-writer.write_insight`, then composes with `email-sender.prompt_then_send` to optionally deliver via Gmail. The 8-section structure (BLUF, Why This Matters Now, Key Findings, Implications, Recommended Action, Risks, Next Decision Point, Sources) is the spine — three sections are mandatory; the other five are toggleable per audience. Stop-and-reports on missing source note, missing prefs file, missing `## Default` section, or unknown audience.
---

# executive-summary-writer

The skill that produces 1-page executive summaries from research notes. Tunes length, voice, format, and section emphasis per named audience by reading a Markdown preferences doc the user maintains in Obsidian. First skill in the toolkit to do per-audience personalization — every exec read of a research finding can be calibrated to that exec's actual taste.

## When to use

**Only on explicit user request.** Triggers include:

- `"Summarize that research for the CISO."`
- `"Give me an exec summary of the latest Copilot research."`
- `"Produce a 1-page version of <note> for VP Eng."`
- `"I need CISO + VP Eng + Default versions of this for sharing."`

Research notes do NOT auto-convert into exec summaries when they're written. The Category 1 researchers (`copilot-deep-dive`, `sdlc-best-practice`, etc.) finish at the research-note write — they do NOT chain into this skill. The user decides which research findings warrant an exec pass.

## When NOT to use

- **Auto-triggered after a `vault-writer.write_research` succeeds.** Even if the research seems exec-worthy, do not auto-invoke. Wait for the user's explicit ask.
- Source content is a digest (`vault/digests/{cadence}/...`), not research — digests are already summarized; this skill doesn't second-summarize. If you really want an exec take on a digest, copy the digest body to a `research/` note first.
- Decision memos, ADRs, RFCs — those have their own writer skills (`decision-memo-writer`, `adr-writer`, `rfc-writer`) with different structural conventions. The exec summary spine doesn't fit a formal decision request.
- Non-research input (raw meeting notes, fragments) — produce a `research/` note first; this skill assumes the source has TL;DR + Findings already shaped by the Category 1 researcher.
- Stakeholder-update-style multi-tier batched updates (CIO/CISO + VP Eng + IC in one document) — that's `stakeholder-update-writer`'s job. This skill is single-audience, single-source, on-demand.

## Prerequisites

- `vault-conventions` cached this session (for the `insight.yml` schema).
- `~/Obsidian/Research-Brain/_config/exec-preferences.md` exists with at least a `## Default` section. Missing → stop-and-report. Copy [`exec-preferences.example.md`](./exec-preferences.example.md) to that path on first use.

## The 8-section structure

The spine of every summary. Three mandatory, five toggleable per audience. Total target: ~200 words (override via prefs).

| # | Section | Mandatory? | Purpose |
|---|---------|------------|---------|
| 1 | **Bottom Line Up Front (BLUF)** | ✅ | 1-2 sentences. The actual answer. If they only read this, they know what changed and why it matters. |
| 2 | **Why This Matters Now** | optional | What triggered surfacing this? (regulator move, peer move, deadline, incident.) Skip for evergreen research. |
| 3 | **Key Findings** | ✅ | 3-5 bullets. Each with a source-tier marker `[T1]`/`[T2]`/`[T3]` and a confidence indicator if non-obvious. |
| 4 | **Implications for Us** | optional | "So what" — concrete impact on the org's posture, programs, or pending decisions. |
| 5 | **Recommended Action** | ✅ | 1-3 concrete next steps. Each with owner + rough timeline if applicable. "I recommend we..." framing. |
| 6 | **Risks & What We're Watching** | optional | Uncertainty, dissent in sources, what to monitor before next checkpoint. |
| 7 | **Next Decision Point** | optional | When does this come back to them? What would they need to decide? "By DATE we should..." |
| 8 | **Sources** (footer) | ✅ | Tier-1 citations with URLs + vault path to the deeper research note for follow-up. Minimal. |

The 3 mandatory sections never disappear — that's the discipline that keeps the document a 1-pager. Prefs can toggle the other 5 on/off, override length, tune voice, etc.

## Helpers

### `summarize_for(source_note_path, audience="default", subject_override=None)`

The primary action. Steps:

1. Resolve `source_note_path` to an absolute path; read the file (Markdown + YAML frontmatter). Missing → stop-and-report #1.
2. Load `~/Obsidian/Research-Brain/_config/exec-preferences.md`; parse audiences (see [Parsing](#parsing)). Missing file → stop-and-report #2. Missing `## Default` → #3.
3. Look up `audiences[audience]`. Unknown handle → stop-and-report #4 listing available handles. For missing fields on a named audience, fall back to the corresponding `## Default` field (field-by-field merge).
4. Build the writing prompt:
   - Include the source note's TL;DR + Findings + Sources as "research input."
   - Apply the audience's `length`, `format`, `voice`, `emphasize`, `avoid`, `special_interests`.
   - Toggle optional sections per `sections` field (e.g. `+next-decision-point, -risks`).
   - If `special_interests` overlaps with the research topic, surface those points explicitly in BLUF or Key Findings.
   - Apply `regulated-finance-framer` as a prompt fragment for the "Implications for Us" section so framing stays consistent with other Category 1 outputs.
   - Pass the audience's free-form prose (everything under the bold-key fields that isn't a field itself) verbatim as "additional context about this reader."
5. Generate the 8-section summary respecting mandatory/optional toggles.
6. Compose the slug from the source note's title (lowercase-kebab, truncate at 50 chars).
7. Call `vault-writer.write_insight(...)` with:
   - Path: `vault/insights/YYYY-MM-DD-exec-summary-{audience}-{slug}.md`
   - Frontmatter per `insight.yml` plus `audience: {handle}` and `source_research: {vault-relative-path-to-source}`.
   - Body: the 8-section structure.
8. Compose with `email-sender.prompt_then_send(written_path)` — asks `[y/n]` to deliver via the existing distribution list.

Return:

```python
{
    "path": "vault/insights/2026-06-23-exec-summary-ciso-agentic-features.md",
    "audience": "ciso",
    "source_research": "research/copilot/2026-06-22-agentic-features.md",
    "word_count": 148,
    "sections_included": ["bluf", "key-findings", "recommended-action", "next-decision-point", "sources"],
    "sections_omitted": ["why-this-matters-now", "implications", "risks"],
    "email_action": "sent" | "skipped" | "prompted"
}
```

### `list_audiences()`

User-facing diagnostic. Loads and parses `exec-preferences.md`; prints each audience with its length, voice, emphasize, and which optional sections are toggled on. No mail traffic, no file writes. Useful before invoking `summarize_for` with a new audience name to confirm the prefs file parses cleanly.

## Parsing — exec-preferences.md

Markdown with YAML frontmatter (frontmatter ignored by the parser; consumed by Obsidian for display).

1. Strip the YAML frontmatter (`---\n...\n---\n` block at top, if present).
2. Strip HTML comments (`<!-- ... -->`) — anything inside is ignored, so commenting out a field or whole audience pauses it.
3. Scan for H2 (`##`) headings. Each H2 is one audience. The H2 title becomes the audience `handle` (lowercased, spaces → hyphens) unless an explicit `**handle**:` field under that audience overrides it.
4. The first H2 whose title (case-insensitive) is `Default` is required — it's the fallback for unspecified audiences.
5. Under each H2, recognize these **bold-key fields** (Markdown `- **key**: value` lines):
   - `handle` — kebab-case identifier (optional override)
   - `role` — descriptive (informational; copied into the summary's frontmatter as audience context)
   - `length` — integer (target word count; trailing "words"/"w" stripped)
   - `format` — `bullets` | `prose` | `mixed`
   - `voice` — free-text descriptor
   - `emphasize` — comma-separated list
   - `avoid` — comma-separated list
   - `special_interests` — comma-separated list
   - `sections` — comma-separated `+name`/`-name` toggles (e.g. `+next-decision-point, -risks`); recognized section names: `bluf`, `why-this-matters-now`, `key-findings`, `implications`, `recommended-action`, `risks`, `next-decision-point`, `sources`. Mandatory sections cannot be turned off; the parser silently drops `-bluf` etc. with a note in the return.
6. Everything else under each H2 (paragraphs, sub-bullets, prose) is collected as `additional_context` for that audience — passed verbatim to the writing prompt.
7. Sections OTHER than the audience H2 list (e.g. `## How it's parsed` documentation in the file) are scanned for diagnostic only; their content does not become an audience.

Defaults applied when a named audience omits a field:
- Pull the corresponding value from `## Default` field-by-field.
- If `## Default` also omits the field, apply built-in defaults: `length=200`, `format=bullets`, `voice=declarative, dense, forward-looking`, `emphasize=[]`, `avoid=[]`, `special_interests=[]`, `sections=all`.

## Stop and report — enumerated cases

Each surfaces a structured error to the caller:

1. **Source research note missing** → `"Source note not found at <path>. Pass an absolute path or a vault-relative path starting at 'research/'."`
2. **exec-preferences.md missing** → `"~/Obsidian/Research-Brain/_config/exec-preferences.md not found. Copy .claude/skills/executive-summary-writer/exec-preferences.example.md to that path and edit."`
3. **`## Default` section missing** → `"exec-preferences.md is missing the required '## Default' section. Add it as the fallback for unspecified audiences."`
4. **Named audience not found** → `"Audience '<name>' not in exec-preferences.md. Available: [default, ciso, vp-eng]."` (Available list parsed at run time so it reflects whatever the user actually has.)
5. **Source note empty / no body** → `"Source note at <path> has no body content to summarize. Confirm the research write completed before invoking exec-summary."`
6. **Insight write collision** (same date + audience + slug) → per `vault-writer.write_insight`'s idempotency rule, the slug gets a `-2`, `-3` suffix; no error to the caller.

Email-side failures (missing `GMAIL_APP_PASSWORD`, missing distribution list, SMTP error) flow through `email-sender`'s own stop-and-report cases — the summary remains written; only delivery fails.

## Output shape

Frontmatter follows `_meta/schema/insight.yml` plus two skill-specific extras:

```yaml
---
title: "Exec summary — agentic Copilot features ({audience} take)"
created: 2026-06-23
updated: 2026-06-23
tags: [insight, executive-summary, copilot]
source_skill: executive-summary-writer
confidence: 2
audience: ciso                                                # the handle that drove the prefs lookup
source_research: research/copilot/2026-06-22-agentic-features.md   # vault-relative
links: []
---
```

Body: the 8-section structure with section omission/length/voice tuned per audience prefs. Headings are H2 (`##`); BLUF is H2 even though it's brief, so the document scans top-to-bottom in Obsidian.

## Composition

- [`vault-conventions`](../vault-conventions/SKILL.md) — schemas + tag vocabulary (cached).
- [`vault-querier`](../vault-querier/SKILL.md) — fetch source research note + any backlink context (related facts, prior digests on the same topic). The backlink context isn't pasted into the summary; it's input to the writing prompt so the summary can say things like "this is consistent with our 2026-Q1 research."
- [`vault-writer.write_insight`](../vault-writer/SKILL.md) — write the summary to `vault/insights/`.
- [`email-sender.prompt_then_send`](../email-sender/SKILL.md) — post-write, ask `[y/n]` to deliver via the existing distribution list. Matches the pattern Category 1 researchers already use.
- [`regulated-finance-framer`](../regulated-finance-framer/SKILL.md) — applied as a prompt fragment for the "Implications for Us" section.

## Acceptance test (live round-trip)

1. **Default audience, full sections**: Pick a recent research note at `vault/research/copilot/...`. Run `summarize_for(<path>)` (audience defaults to `default`). Confirm: output at `vault/insights/YYYY-MM-DD-exec-summary-default-{slug}.md`, all 8 sections present, ~200 words, prompts to email after write.
2. **Named audience override**: Run `summarize_for(<same path>, audience="ciso")`. Confirm: output is shorter (~150 words), risk-forward voice, "Next Decision Point" present (per CISO `sections` toggle), file path includes `-exec-summary-ciso-`.
3. **`list_audiences()`**: Returns the 3 audiences from the template (default + ciso + vp-eng) with their length + voice + emphasize fields. No mail traffic, no file writes.
4. **Unknown audience**: Run with `audience="cfo"` when no CFO section exists. Confirm: stop-and-report #4 listing available audiences.
5. **Missing prefs**: Temporarily rename `_config/exec-preferences.md`. Confirm: stop-and-report #2 with the exact remediation path.
6. **Missing Default**: Edit a copy of the template to remove the `## Default` H2. Confirm: stop-and-report #3.
7. **Paused audience**: Wrap an audience's H2 + body in `<!-- ... -->`. Confirm `list_audiences()` no longer lists it; `summarize_for(..., audience=that-handle)` stop-and-reports #4.
