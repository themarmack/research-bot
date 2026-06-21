---
name: source-registry
description: Curated YAML registry of high-signal sources (vendor changelogs, regulator feeds, security advisories, peer-bank blogs) that any research or scheduled-agent skill should load WHERE to look from. Loads `./registry.yml` from this skill's folder and supports filters by topic tag, credibility tier, source type, or host lookup. Used by feed-watcher (which sources to poll), source-fetcher (host → credibility-tier lookup), and every Category 1 + Category 2 skill (curated source list per topic).
---

# source-registry

The single source of truth for which web sources the toolkit trusts and watches. Lives as a YAML file (`registry.yml`) alongside this SKILL.md. No skill should hard-code a feed URL — they all go through this registry. Adding or pruning a source is one YAML edit; no code changes.

## When to use

- A scheduled agent needs the list of sources for a given topic (`feed-watcher` calls this).
- `source-fetcher` needs `source_tier` for a host it just fetched.
- A Category 1 research skill needs the canonical seed source list for its topic.
- The user wants to add or remove a source (edit `registry.yml` directly).

## When NOT to use

- For ad-hoc URLs the user supplied in a prompt — those are one-off, don't add to the registry.
- For internal company URLs — never put internal hosts here; they don't belong in a portable registry.

## Schema (per source entry)

```yaml
- id: short-kebab-case-unique          # required, primary key
  name: Human-readable name            # required
  url: https://example.com/feed.xml    # required
  type: rss | atom | json-feed | html | api | github-releases   # required
  host: example.com                    # required, used for host→tier lookup
  topic_tags:                          # required, must come from _meta/tags.md
    - copilot
    - github
  credibility_tier: 1 | 2 | 3          # required; 1 = vendor primary, 2 = quality industry, 3 = unverified
  cadence_hint: daily | weekly | biweekly | monthly | quarterly  # optional poll-frequency suggestion
  paywalled: true | false              # required
  verified: true | false               # whether feed URL has been confirmed to resolve and parse
  notes: |                             # optional; freeform context
    Why this source is on the list, what it covers, gotchas.
```

## Query API

The skill supports four kinds of read:

### 1. Load all

Return every source entry as a list. Used at toolkit-init or for debugging.

### 2. Filter by topic tag(s)

```
query.tags = [copilot]                # OR-match: any source with #copilot
query.tags = [copilot, github]        # OR-match by default
query.require_all_tags = true         # AND-match if explicit
```

### 3. Filter by credibility tier

```
query.min_tier = 1                    # only tier-1 sources
query.max_tier = 2                    # tiers 1 and 2 (skip unverified)
```

### 4. Lookup by host

Used by `source-fetcher` to tag a freshly-fetched URL with its `source_tier`.

```
query.host = "github.blog"            # returns the source entry, or null
```

If host is not in the registry, return `null` and let the caller default to `credibility_tier: 3` (per `default_credibility_tier` at the top of `registry.yml`).

## Output shape

For filter queries, return a list of source entries (full YAML shape above). For host lookups, return a single entry or `null`.

## How to load

1. `Read` `./registry.yml` in this skill folder.
2. Parse as YAML.
3. Validate: every entry has the required fields; `id` is unique; `topic_tags` come from the controlled vocabulary in `~/Obsidian/Research-Brain/_meta/tags.md` (call `vault-conventions` if not cached).
4. Apply the requested filter.
5. Return.

If validation fails (duplicate id, unknown tag, missing required field), **stop and report** per the writing standard — do not silently skip a malformed entry.

## Versioning

`registry.yml` has a top-level `version:` field. Bump it when the schema changes (e.g., add a new required field). Skills should warn if `version` is newer than they understand.

## Adding a source

1. Edit `registry.yml`, append a new entry with `verified: false`.
2. Use `feed-watcher` to attempt a single fetch — it will fail loudly if the URL doesn't resolve or parse.
3. Once feeds-watcher succeeds, flip `verified: true` in the YAML.

## Composes with

- [`feed-watcher`](../feed-watcher/SKILL.md) — calls this with topic-tag or credibility filter to get the polling list.
- [`source-fetcher`](../source-fetcher/SKILL.md) — calls this with host lookup to set `source_tier` on fetched content.

## Acceptance test (for step 3 done-criteria)

Load `registry.yml`. Confirm:
- Has at least 3 sources tagged at credibility-tier 1.
- Includes `github-changelog` (the GitHub blog changelog feed).
- Includes one Anthropic source (`anthropic-news`).
- Includes at least one regulator source (`occ-news-releases`, `federalreserve-press`, or `ffiec-press`).
- Filter by `topic_tags: [github]` returns at least 1 source.
- Filter by `topic_tags: [regulator]` returns at least 1 source.
- Host lookup for `github.blog` returns the github-changelog entry; host lookup for `unknown.example.com` returns `null`.
