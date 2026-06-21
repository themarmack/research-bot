---
name: vault-querier
description: Read-side query interface for the Obsidian vault at ~/Obsidian/Research-Brain/. Supports lookups by tag, by frontmatter field, by [[wikilink]] (forward + backlinks), and full-text. Returns `{path, frontmatter, excerpt, links}` per match. Uses filesystem Glob + Grep + Read — no MCP, no daemon. Call this **first** for every on-demand research task (Obsidian-first contract) and any time a vault-writing skill needs to find related notes to link to.
---

# vault-querier

The read side of the vault. Filesystem-based; uses `Glob`, `Grep`, and `Read` — no MCP, no external service. Fast enough for vaults up to a few thousand notes. Switch to mcpvault MCP later if grep starts taking >1s.

## When to use

- **Obsidian-first contract**: every Category 1 (on-demand) research skill calls this **first** before any web research, to find prior facts, research, or decisions on the topic.
- Any vault-writing skill that needs to find existing notes to `[[link]]` to.
- `memory-curator` checking whether a candidate is novel vs already covered.
- Manual lookup ("what do we know about Copilot data handling?").

## When NOT to use

- Reading a single known-path note — use `Read` directly.
- Searching the toolkit repo (`<repo-root>/`) — that's `Grep` on the repo, not this skill.
- Looking up identity/preferences/feedback — that's Tier-1 harness memory, not the vault.

## Prerequisites

- `vault-conventions` should have been called this session so the querier knows folder layout. If not yet called, call it first.

## Query types

### 1. By tag

Find notes tagged with one of the controlled vocabulary entries.

```
query.type = "tag"
query.tag  = "#copilot"
```

Implementation: `Grep` for `tags: \[.*#copilot.*\]` and `tags:.*\n.*#copilot` (handles flow and block YAML) across `~/Obsidian/Research-Brain/**/*.md`. Skip `.templates/`, `_inbox/.dropped/`, and any `_views/` matches (derived).

### 2. By frontmatter field

Find notes where `frontmatter.<key>` equals a value (or contains a substring).

```
query.type   = "frontmatter"
query.key    = "status"
query.value  = "open" | "accepted" | etc.
```

Implementation: `Grep` for `^<key>:\s*<value>` in YAML frontmatter region of `**/*.md`. For decisions, common keys: `status`, `decided_on`, `deciders`. For research: `topic`, `question`. For facts: `entity`, `predicate`.

### 3. By wikilink (forward and backlinks)

Find notes that link to a given target note (backlinks) or that a given note links to (forward links).

```
# Backlinks: who links TO target?
query.type   = "backlinks"
query.target = "sdlc-modernization"   # bare note name, no brackets

# Forward links: who does source link to?
query.type   = "forward_links"
query.source = "Home"
```

Implementation:
- **Backlinks**: union of two sources:
  1. `Grep` for `\[\[<target>\]\]` (with optional alias `\[\[<target>\|.*\]\]`) across all `*.md` in the vault — body wikilinks.
  2. `Grep` for `^links: \[.*\b<target>\b.*\]` in YAML frontmatter — the frontmatter cache.
  Deduplicate by path before returning. Tag each match with `source: "body" | "frontmatter" | "both"` in the result so the caller can see how the backlink was resolved.
- **Forward links**: union of body and frontmatter:
  1. `Read` the source note's body, regex-extract `\[\[([^\]|]+)(\|[^\]]*)?\]\]`, capture target names.
  2. Parse the source note's frontmatter, extract the `links:` array (after the YAML cleanup heuristics below).
  Deduplicate.

**Body-text wikilinks are authoritative** for what a note *says*. The frontmatter `links:` field is a structured cache, useful for fast lookups when a downstream skill has already populated it. Both are valid backlink sources.

### 4. Full-text

Match arbitrary substring or regex across note bodies.

```
query.type = "full_text"
query.pattern = "FFIEC IT Handbook"
```

Implementation: `Grep` with the pattern across `**/*.md` in the vault, excluding `_inbox/.dropped/` and `.templates/`.

## Output shape

For every query type, return a list of matches:

```json
[
  {
    "path": "~/Obsidian/Research-Brain/decisions/2026-06-20-adopt-obsidian-and-ob1-patterns.md",
    "title": "Adopt Obsidian Vault + OB1-Inspired Patterns for Tier-2 Memory",
    "folder": "decisions",
    "frontmatter": {
      "created": "2026-06-20",
      "updated": "2026-06-20",
      "tags": ["decision", "sdlc"],
      "status": "accepted",
      "decided_on": "2026-06-20",
      "links": ["sdlc-modernization", "conventions"]
    },
    "excerpt": "<first 200 chars of body OR the matched line ±2 lines for grep queries>",
    "forward_links": ["sdlc-modernization", "conventions"],
    "backlinks": ["Home"]
  }
]
```

Cap default results at **20**. Pass `limit` in the query to override. Always sort results: matches in `facts/` and `decisions/` first (most authoritative), then `insights/` and `research/`, then `digests/` and `events/`, then `people/` and `projects/`, then everything else.

## Frontmatter parsing

The vault uses YAML frontmatter at the top of every note, bracketed by `---` lines. To parse:

1. Read the file.
2. Extract lines between the first two `---`.
3. Parse as YAML.
4. Most fields are strings, dates (YYYY-MM-DD), or flat lists of strings. `links:` is a list of bare note-name strings (no `[[...]]` wrappers). `tags:` is a list of strings, with or without leading `#`.

If frontmatter is malformed (legacy `[[[notename]]]` triple-bracket nesting, etc.), flatten nested lists and strip `[[` `]]` wrappers heuristically before returning.

## Performance hints

- For backlinks across the whole vault, `Grep` with `\[\[<target>\]\]` is the primary call.
- For tag queries, exclude obvious large directories first (`Glob` filtered) to keep grep scope small.
- Cache the conventions summary from `vault-conventions` across queries within a session.

## Composes with

- Called by every Category 1 research skill (Obsidian-first contract).
- Called by `vault-writer` to find related notes for `[[link]]` generation.
- Called by `memory-curator` to check novelty against existing notes.

## Acceptance test (for step 2 done-criteria)

Run these four queries against the existing vault and verify:

1. **Backlinks to `conventions`** → at least 3 matches: `Home`, `2026-06-20-adopt-obsidian-and-ob1-patterns`, plus several folder README files in the vault.
2. **Backlinks to `sdlc-modernization`** → at least 2 matches: `Home`, `2026-06-20-adopt-obsidian-and-ob1-patterns`.
3. **Forward links from `2026-06-20-adopt-obsidian-and-ob1-patterns`** → returns `[sdlc-modernization, conventions]`.
4. **Full-text query for "OB1"** → returns the decision note and `Home`.

If any query returns zero matches when at least one is expected, surface the failure (per the "stop and report" guardrail) rather than returning an empty list silently.
