---
name: feed-watcher
description: Poll RSS / Atom / JSON-Feed / GitHub-releases sources from the source-registry and return items new since last poll. Persists per-source dedup state under `<repo>/.state/feed-watcher/`. Used by every Category 2 scheduled agent to know what changed since the last run. Composes on source-registry (which sources to poll) and source-fetcher (one-off URL fetch for HTML sources without native feeds). Will migrate to seen-tracker for state once step 6 ships.
---

# feed-watcher

Polls a configurable set of sources from `source-registry` and returns the items that are new since this skill's last run. Every Category 2 scheduled agent (weekly-intelligence-digest, voices-watcher, monthly-copilot-changelog, etc.) calls this at the top of its run to know what changed.

## When to use

- A scheduled agent's first action of the run — fetch new items across its source list.
- A user wants a one-shot "what's new in the last N days from sources tagged X" lookup.

## When NOT to use

- For arbitrary URLs not in `source-registry` — use `source-fetcher` directly.
- For sources without published feeds AND without a stable HTML page — feed-watcher will fail; consider a custom skill.

## How it works

1. **Get the source list** — call `source-registry` with the caller's filter (topic_tags, credibility tier, or an explicit source-id list). Default if nothing specified: every source where `verified: true`.
2. **Per source, poll**:
   - `type: rss | atom | json-feed`: fetch the feed URL via `source-fetcher` (which runs the result through `prompt-injection-guard`). Parse items.
   - `type: github-releases`: fetch `https://api.github.com/repos/{owner}/{repo}/releases` via `source-fetcher`. Parse JSON.
   - `type: html`: fetch the index page via `source-fetcher`. Heuristically extract item titles + links from the page (look for `<article>`, `<li class*="post">`, dated headings, etc.). Mark items with a warning that they came from HTML scrape, not a feed.
   - `type: api`: skill-specific; not implemented in v1 — return a warning.
3. **Compute new items** — for each source, load the prior-run state file at `<repo>/.state/feed-watcher/{source-id}.jsonl`. State format: one JSON object per line, `{item_url, item_id, seen_at}`. Items whose `item_url` (or `item_id` if `item_url` is unstable) is NOT in state are "new."
4. **Update state** — append each new item to the state file with a `seen_at` timestamp.
5. **Return** the new items, grouped by source.

## Output shape

```json
{
  "run_at": "2026-06-20T15:00:00Z",
  "sources_polled": 6,
  "sources_failed": 1,
  "new_items": [
    {
      "source_id": "github-changelog",
      "source_name": "GitHub Changelog",
      "source_tier": 1,
      "items": [
        {
          "title": "Copilot can now ...",
          "url": "https://github.blog/changelog/2026-06-19-...",
          "published_at": "2026-06-19T14:00:00Z",
          "summary": "<first 300 chars of item body, post injection-guard>",
          "warnings": []
        }
      ]
    }
  ],
  "failures": [
    {
      "source_id": "anthropic-news",
      "reason": "html scrape returned 0 items — selector heuristics did not match",
      "url": "https://www.anthropic.com/news"
    }
  ]
}
```

## State management

- State files live at `<repo>/.state/feed-watcher/{source-id}.jsonl`.
- Cap state file size at the **last 500 items per source** — older entries are pruned (FIFO) to bound the file.
- **Append-only writes** — never rewrite the file from scratch except for pruning.
- Concurrency: the toolkit is single-user single-machine; no locking needed for v1.

### Migration to `seen-tracker` (step 6)

Once `seen-tracker` ships, refactor feed-watcher to delegate dedup to it:
- Replace direct file I/O with `seen-tracker.is_new(item)` / `seen-tracker.mark_surfaced(item)` calls.
- Keep the same `.state/feed-watcher/` files until migration is verified; then move them under `seen-tracker`'s state root.

## Failure handling (stop and report)

Per the "stop and report" guardrail in `_meta/conventions.md`: every failed source goes into the `failures` array in the output. **Never silently skip** a feed that didn't poll. Downstream scheduled agents must surface failures in their digest's Sources section (e.g., `could not poll: anthropic-news — html scrape failed`).

Common failures:
- `404` or `5xx` from `source-fetcher` — log and continue with next source.
- Empty HTML scrape (0 items extracted) — likely selector heuristics need tuning; flag.
- Malformed RSS/Atom — try lenient parse; if still fails, log and continue.
- `prompt-injection-guard` returns `suspicious` on a feed body — drop those items from the new-items list, log to failures.

## Composes with

- [`source-registry`](../source-registry/SKILL.md) — which sources to poll.
- [`source-fetcher`](../source-fetcher/SKILL.md) — the actual web fetch.
- [`prompt-injection-guard`](../prompt-injection-guard/SKILL.md) — applied via source-fetcher; suspicious items dropped.
- Future: `seen-tracker` (step 6) — replaces the local state file.

## Acceptance test (for step 3 done-criteria)

Poll the three minimum sources from `source-registry`:
1. `github-changelog` — RSS feed, should return parseable items.
2. `anthropic-news` — HTML scrape; if 0 items, the failure must appear in the `failures` array (not silently dropped).
3. `occ-news-releases` (or another regulator) — similar HTML handling.

On the first run, all items are "new." On a second back-to-back run, all items should be filtered out (state populated). Confirm:
- Output has `sources_polled` ≥ 3.
- State files exist at `<repo>/.state/feed-watcher/github-changelog.jsonl` etc.
- A second run returns zero new items for github-changelog (the only verified-true source).
- Failures from `anthropic-news` and `occ-news-releases` (currently `verified: false`) appear in `failures`, not silently dropped.
