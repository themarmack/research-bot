---
name: seen-tracker
description: Persistent per-skill dedup primitive. Stores `{key, content_hash, seen_at, source_id, metadata}` JSONL state at `<repo>/.state/<consumer-skill>/seen.jsonl` so scheduled agents and curators know what they've already surfaced across runs. Without this, weekly digests repeat last week's news. Exposes `is_new(item)` and `mark_surfaced(item)` semantics. Default-keyed on `url + content_hash`; supports optional title-embedding cluster keys for semantic dedup later. Replaces feed-watcher's v1 per-source state file.
---

# seen-tracker

Persistent deduplication state. Every scheduled agent and every curator that needs to know "have I already surfaced this?" across separate runs uses this skill rather than rolling its own state. Without it, the `weekly-intelligence-digest` would re-report last week's GitHub changelog every Monday.

## When to use

- A scheduled agent has fetched candidate items (from `feed-watcher` or a manual fetch) and needs to filter to "new since last run."
- `memory-curator` is checking whether an `_inbox/` item is novel before promoting.
- Any skill that wants to avoid re-processing a URL it's already handled.

## When NOT to use

- Single-session dedup (just use an in-memory `Set` and discard).
- Vault-content novelty checks — that's `vault-querier`, not this. seen-tracker is for **external sources** (URLs, feed items, fetched docs); `vault-querier` is for what's already in the vault.

## Storage layout

```
<repo>/.state/<consumer-skill>/seen.jsonl
```

One JSONL file per consumer skill. Examples:
- `.state/feed-watcher/seen.jsonl`
- `.state/voices-watcher/seen.jsonl`
- `.state/weekly-intelligence-digest/seen.jsonl`
- `.state/memory-curator/seen.jsonl`

`<consumer-skill>` is the name of the calling skill (NOT seen-tracker itself).

## Record schema (one JSON object per line)

```json
{"key":"https://github.blog/changelog/2026-06-19-foo","content_hash":"a1b2…","seen_at":"2026-06-20T15:00:00Z","source_id":"github-changelog","title":"Copilot can now…","metadata":{}}
```

- **`key`** — the primary dedup key. Default = URL. Required.
- **`content_hash`** — sha256 of normalized content body (after `prompt-injection-guard`). Used to detect "same URL, different content" cases — when both differ, treat as new.
- **`seen_at`** — ISO-8601 when this skill first surfaced the item.
- **`source_id`** — registry source id if applicable (`github-changelog`, `anthropic-news`, …).
- **`title`** — short human label so the file is reviewable.
- **`metadata`** — freeform key/value (e.g., `{cadence:"daily", surfaced_in_digest:"2026-06-20-weekly-intelligence-digest"}`).

## API

### `is_new(consumer, item) → bool`

1. Load `.state/<consumer>/seen.jsonl` (cache per-session after first load).
2. Build a set of `(key, content_hash)` pairs.
3. If the item's `(key, content_hash)` is NOT in the set → return `true`.
4. If only the `key` matches but the `content_hash` differs → return `true` (content changed). Caller should treat this as an update.
5. Else → return `false`.

### `mark_surfaced(consumer, item)`

Append a record to `.state/<consumer>/seen.jsonl`. Append-only — never rewrite from scratch except for pruning.

### `bulk_filter(consumer, items[]) → {new: [], already_seen: [], updated: []}`

Common helper for scheduled agents — pass the candidate list, get back the three buckets in one call. Most efficient when checking many items.

### `prune(consumer, keep_last_n=1000)`

Cap the state file at the most recent N records (FIFO). Each consumer's reasonable cap depends on volume:
- `feed-watcher`: 2000 (high-volume across all sources)
- `voices-watcher`: 1000
- `weekly-intelligence-digest`: 500
- Default: 1000

Run prune at the **end** of each agent run (low priority — only if file size > cap × 1.5).

## Optional: semantic dedup

For digests that aggregate multiple sources covering the same story (e.g., the Anthropic launch announcement appears in both Anthropic-news AND OpenAI-news AND GitHub-changelog), exact URL/hash dedup isn't enough. Future enhancement: maintain a title-embedding cluster index in `.state/<consumer>/clusters.jsonl` so two items with embedding cosine > 0.85 are treated as same-story.

Defer until exact dedup proves insufficient. v1 = exact only.

## Concurrency

Single-user single-machine toolkit. No file locking in v1. If two agents write to the same consumer's state file simultaneously, the last writer wins and we may lose a few records — acceptable. If volume grows, add `flock` later.

## Failure modes — stop and report

- State file missing → treat as fresh start (return all items as new). Log a `state_initialized` warning on first run.
- State file malformed JSONL → skip malformed lines, log to caller, continue. Don't crash.
- Disk write fails → surface to caller; the agent's run should be reported as partial-success.

## Feed-watcher migration

`feed-watcher` currently writes per-source state at `.state/feed-watcher/{source-id}.jsonl`. Migration on first invocation of seen-tracker:
1. If `.state/feed-watcher/seen.jsonl` does not exist AND any `{source-id}.jsonl` files exist, merge them into the new flat file with each record gaining a `source_id` field.
2. Rename old per-source files to `.state/feed-watcher/.legacy/{source-id}.jsonl` (audit trail).
3. Subsequent runs use the flat file.

## Composes with

- [`feed-watcher`](../feed-watcher/SKILL.md) — calls `bulk_filter` on every poll to drop already-seen items.
- [`memory-curator`](../memory-curator/SKILL.md) — calls `is_new` on inbox candidates before promote.
- Every Category 2 scheduled agent — calls `bulk_filter` after fetching candidates.

## Acceptance test (for step 6 done-criteria)

1. Call `mark_surfaced("feed-watcher", item)` with a sample item.
2. Call `is_new("feed-watcher", item)` with the same item → returns `false`.
3. Call `is_new("feed-watcher", different_item)` → returns `true`.
4. Confirm `.state/feed-watcher/seen.jsonl` exists and contains the record.
5. Restart the session and re-run step 2 → still returns `false` (state persisted).

Live exercise happens when step 7 (`weekly-intelligence-digest`) first runs.
