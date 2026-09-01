---
name: vault-conventions
description: Load the Obsidian vault's conventions, folder schemas, and controlled tag vocabulary into a compact structured summary so that any skill which reads or writes the vault follows the rules. Returns folders, frontmatter schemas (all 9), tag vocabulary, research-topic vocabulary, and inbox-promotion rules in one bundle. Call this first before any vault read or write. Caches within a session — re-call only if vault `_meta/` has changed. Use before the first vault read or write in any session — every vault-touching skill (vault-querier, vault-writer, memory-curator, digest-writer, every Category 1 researcher and Category 2 scheduled agent) calls this first.
---

# vault-conventions

**Path convention**: `vault/` is shorthand for `~/Obsidian/Research-Brain/`; all skills use the `vault/` form.

The bootstrap skill for vault-aware work. Loads `vault/_meta/` and returns a structured summary so that downstream skills (`vault-querier`, `vault-writer`, `memory-curator`, every Category 1 researcher) all follow the same conventions consistently.

## When to use

- **Before** the first vault read or write in a session.
- After the user reports that vault conventions have changed (re-load).
- Inside any skill that asks "which folder should this note go in?" — call once at the top.

## When NOT to use

- Mid-session repeat calls if `_meta/` is unchanged — cache the summary and reuse.
- Before reading a single known-path note (e.g., reading `Home.md` directly).

## What to read

Read all of:

- `vault/_meta/conventions.md` — canonical layout, default frontmatter, writing rules.
- `vault/_meta/tags.md` — controlled tag vocabulary.
- `vault/_meta/inbox-rules.md` — promote / patch / drop heuristics.
- `vault/_meta/schema/*.yml` — all 9 folder schemas (`default`, `fact`, `event`, `decision`, `insight`, `person`, `project`, `research`, `digest`).

## Output shape

```json
{
  "vault_path": "~/Obsidian/Research-Brain",
  "folders": {
    "people": {"path": "people/{handle}.md", "authority": "mixed", "schema": "person"},
    "projects": {"path": "projects/{slug}.md", "authority": "curated", "schema": "project"},
    "decisions": {"path": "decisions/YYYY-MM-DD-{slug}.md", "authority": "curated", "schema": "decision"},
    "insights": {"path": "insights/{slug}.md", "authority": "curated", "schema": "insight"},
    "facts": {"path": "facts/{entity}/{predicate}.md", "authority": "curated", "schema": "fact"},
    "events": {"path": "events/YYYY-MM-DD/{slug}.md", "authority": "append-only", "schema": "event"},
    "research": {"path": "research/{topic}/YYYY-MM-DD-{slug}.md", "authority": "curated", "schema": "research"},
    "digests": {"path": "digests/{cadence}/YYYY-MM-DD-{skill}.md", "authority": "curated", "schema": "digest"},
    "_inbox": {"path": "_inbox/{agent-id}/", "authority": "transient"},
    "_views": {"path": "_views/", "authority": "derived"}
  },
  "schemas": {
    "default": { /* required fields + per-field types */ },
    "fact": { /* extends default + entity, predicate, value, source_url */ },
    "event": { ... },
    "decision": { ... },
    "insight": { ... },
    "person": { ... },
    "project": { ... },
    "research": { ... },
    "digest": { ... }
  },
  "research_topics": ["ai-coding-tools", "ai-governance", "appsec", "codeql", "compliance", "container-security", "copilot", "dependabot", "frontier-model", "ghas", "github", "incident", "peer-bank", "regulator", "sdlc-best-practice", "sources", "supply-chain", "vendor"],
  "tags": {
    "domain": ["#sdlc", "#copilot", "#github", "#codeql", "#dependabot", "#ghas", "#ai-coding-tools", "#frontier-model", "#supply-chain", "#peer-bank", "#vendor"],
    "regulatory": ["#regulator", "#compliance-framework", "#ai-governance"],
    "kind": ["#decision", "#fact", "#event", "#insight", "#research", "#digest", "#person", "#project"],
    "workflow_status": ["#open", "#blocked", "#stale", "#superseded"],
    "confidence": ["#unverified", "#disputed"],
    "sensitivity": ["#external-only", "#do-not-share"]
  },
  "inbox_rules": {
    "promote_when": "novel + specific + future-useful + sourced + (surprise OR load-bearing)",
    "patch_when": "an existing durable note for the same entity/predicate or slug exists and new info adds to it",
    "drop_when": "already known unchanged | marketing claim | identity/preferences/feedback content | #do-not-share without approval | confidence 1 AND no source_url",
    "guardrail": "never silently drop content with substance — if uncertain, tag #needs-review and leave in _inbox/"
  },
  "writing_standard": {
    "self_contained": "Another AI reading this with zero prior context should understand what it means.",
    "stop_and_report": "Surface errors rather than silently skip content."
  },
  "links_format": "frontmatter `links:` is a YAML list of plain note-name strings (no `[[...]]` wrappers, no nested brackets). Example: `links: [conventions, sdlc-modernization]`. The wikilink syntax `[[Note Title]]` is for body text only."
}
```

## Controlled topic vocabulary — `vault/research/{topic}/`

The `{topic}` segment of `vault/research/{topic}/YYYY-MM-DD-{slug}.md` comes from a controlled vocabulary, authorized in [[2026-08-28-topic-vocabulary-and-vault-path-convention]]:

`ai-coding-tools`, `ai-governance`, `appsec`, `codeql`, `compliance`, `container-security`, `copilot`, `dependabot`, `frontier-model`, `ghas`, `github`, `incident`, `peer-bank`, `regulator`, `sdlc-best-practice`, `sources`, `supply-chain`, `vendor`

Rules:

- Every research write MUST use an existing topic from this list — no ad-hoc topic folders.
- Adding a new topic is allowed, but requires a `vault/decisions/` note first (per the curated-artifacts rule); update this list in the same change.

## Caching rule

Within a session, after the first call, store the summary in working context. Only re-read `_meta/` if:
- The user reports they edited a schema, tag, or rule.
- A `decisions/` note was just written that proposes a `_meta` change.
- More than 24 hours have passed since the first load (defensive).

## Composes with

- Called by [`vault-querier`](../vault-querier/SKILL.md) on first invocation.
- Called by [`vault-writer`](../vault-writer/SKILL.md) before any write to apply the right schema.
- Called by [`memory-curator`](../memory-curator/SKILL.md) before applying promote/patch/drop logic.

## Acceptance test (for step 2 done-criteria)

Read all four `_meta/*.md` files and all nine schemas in `_meta/schema/`. Return a summary that:
- Lists all 10 vault folders with their path templates.
- Includes all 9 schemas by name.
- Includes the controlled tag vocabulary grouped by category.
- Includes the writing standard (both rules) and the inbox guardrail verbatim.
