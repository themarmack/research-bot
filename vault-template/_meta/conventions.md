---
title: Vault Conventions
created: 2026-06-20
updated: 2026-06-20
tags: [meta]
source_skill: human
confidence: 3
links: []
---

# Research-Brain — Vault Conventions

This vault is the toolkit's **Tier-2 long-term memory**. Tier-1 memory lives at `~/.claude/projects/<this-project>/memory/` and holds only identity, preferences, and feedback. **This vault holds knowledge, research, facts, decisions, and events.**

If you are an AI agent, load this file first (via the `vault-conventions` skill) before reading or writing anything else here.

## Layout

| Folder | What goes here | Authority |
|--------|----------------|-----------|
| `_meta/` | Conventions, schemas, controlled vocabularies | curated |
| `_config/` | Delivery configuration (e.g. `email-distribution.md`). Not knowledge — never queried by `vault-querier`. | curated |
| `_inbox/{agent-id}/` | Agent-staged writes awaiting curation | transient |
| `_views/` | Derived / regenerated. Never hand-edit. | derived |
| `people/{handle}.md` | One note per person (voices, peers, regulators-named, leadership) | mixed |
| `projects/{slug}.md` | One note per project, including the SDLC modernization program | curated |
| `decisions/YYYY-MM-DD-{slug}.md` | Architecture decisions, dated, with status | curated |
| `insights/{slug}.md` | Syntheses, essays, learnings | curated |
| `facts/{entity}/{predicate}.md` | One durable typed fact per file | curated |
| `events/YYYY-MM-DD/{slug}.md` | Episodic, append-only | append-only |
| `research/{topic}/YYYY-MM-DD-{slug}.md` | Outputs from on-demand research skills | curated |
| `digests/{cadence}/YYYY-MM-DD-{skill}.md` | Outputs from scheduled-agent skills | curated |

**Note on `_config/`**: holds operational config for skills that distribute vault content outside the vault (e.g. `email-sender` reads `_config/email-distribution.md` — a plain-Markdown bullet list of recipients, Obsidian-native and deliberately not YAML). `vault-querier` skips it, `vault-writer` never writes here, and `memory-curator` ignores it. See `_config/README.md` for the contract.

## Default frontmatter

Every note has at minimum:

```yaml
---
title: string
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [string]            # use only entries from _meta/tags.md
source_skill: string      # which skill wrote it (or "human")
confidence: 1 | 2 | 3     # 1 tentative, 2 likely, 3 verified
links: [string]           # forward [[wikilinks]] referenced from the body
---
```

Folder-specific schemas in `_meta/schema/*.yml` add required fields per surface (e.g. `facts/` requires `entity`, `predicate`, `value`, `source_url`; `decisions/` requires `status`, `decided_on`).

## Linking

- Use `[[Note Title]]` wikilinks in body text. Obsidian resolves them; `vault-querier` reads forward links and backlinks for graph traversal.
- Tag from the controlled vocabulary in `tags.md` only. Adding a new tag is a `_meta` change, not an inline decision.
- Prefer linking to atomic `facts/{entity}/{predicate}` notes over re-stating the fact in body text. This keeps facts canonically updateable.

## Writing rules

- Agents write through `vault-writer`, which applies the right schema and folder. Humans can write directly anywhere.
- Agents must stage uncertain writes to `_inbox/{agent-id}/` first. Only `memory-curator` promotes from `_inbox/` to durable folders.
- Append-only folders (`events/`) never get overwrites; new events get new files.
- Atomic facts are one-fact-per-file under `facts/{entity}/{predicate}.md`. Updating a fact rewrites that one file; never bundle multiple facts in one note.
- The frontmatter `updated` field changes on every save; `created` never changes after first write.

## Writing standard (borrowed from OB1)

Two rules every note must satisfy. Both are borrowed verbatim from Nate Jones's [OB1 — `docs/02-companion-prompts.md`](https://github.com/NateBJones-Projects/OB1/blob/main/docs/02-companion-prompts.md):

- **Self-contained** — *"Another AI reading this with zero prior context should understand what it means."* Practically: always cite source URLs in frontmatter `source_url` (for facts) or in the body (for everything else); link related notes via `[[wikilinks]]`; never assume conversation context. If a note only makes sense if you remember today's chat, it isn't durable yet — stage it to `_inbox/` and let the curator promote it once it stands alone.
- **Stop and report** — *"Stop and report errors rather than silently skip content."* Practically: `vault-writer` surfaces failed writes rather than swallowing them; `memory-curator` flags content it can't classify with `#needs-review` and leaves it in `_inbox/` instead of dropping it; scheduled agents never quietly omit a feed they couldn't fetch — they report the gap in the digest's Sources section.

## Design lenses (borrowed from OB1's Spark patterns)

When proposing a new skill, classify it against these five workflow patterns. Most strong candidates fit at least one:

- **Save This** — preserve AI-generated insights so they don't evaporate at session end.
- **Before I Forget** — capture perishable context (a meeting just ended, a decision just got made).
- **Cross-Pollinate** — search across tools and prior notes before re-doing the work. Our Obsidian-first contract for Category 1 skills is the canonical implementation.
- **Build the Thread** — accumulate insight over time on a topic. The `facts/` and `insights/` folders are designed for this; scheduled digests feed them.
- **People Context** — remember what matters about people. `people/{handle}.md` plus the `voices.csv` roster.

These lenses are not a taxonomy notes belong in — they're a sanity check for "is this skill worth building."

## What does NOT belong here

- Identity, preferences, feedback → Tier-1 harness memory.
- Ephemeral session state → stays in the current conversation.
- Code or skill SKILL.md files → live in the toolkit repo's `.claude/skills/`, project-scoped and versioned with the catalog.
- Credentials, secrets, internal-only company content → never.
- Personal journaling, calendars, todos → use a different vault if you want those mixed in.

## See also

- `tags.md` — controlled tag vocabulary
- `inbox-rules.md` — promotion criteria the `memory-curator` skill applies
- `schema/*.yml` — per-folder frontmatter schemas
- `.templates/*.md` — note templates for Obsidian's "templates" feature
