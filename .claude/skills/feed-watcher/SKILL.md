---
name: feed-watcher
description: Poll RSS / Atom / JSON-Feed / GitHub-releases sources from the source-registry and return items new since last poll. Dedup state is persisted via seen-tracker under `<repo>/.state/<agent_name>/seen.jsonl`, keyed by the calling agent — feed-watcher holds no state of its own. Composes on source-registry (which sources to poll) and source-fetcher (one-off URL fetch for HTML sources without native feeds). Use when a Category 2 scheduled agent starts its run (its first action, to learn what changed since the last run) and when the user wants a one-shot "what's new in the last N days from sources tagged X" lookup.
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
3. **Compute new items** — delegate to `seen-tracker`: call `seen-tracker.bulk_filter(<agent_name>, items)`, where `<agent_name>` is the calling scheduled agent (e.g. `weekly-intelligence-digest`). State lives at `<repo>/.state/<agent_name>/seen.jsonl`; feed-watcher performs no state file I/O of its own. Items in the `new` and `updated` buckets are "new."
4. **Marking surfaced is the caller's job** — the scheduled agent calls `seen-tracker.mark_surfaced` for every item it actually publishes (runner lifecycle step 10), so an item that fetched but never made a digest is retried next run.
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

All dedup state is owned by [`seen-tracker`](../seen-tracker/SKILL.md) at `<repo>/.state/<agent_name>/seen.jsonl` — one file per calling agent, so each scheduled agent's "what have I already surfaced?" is isolated from every other agent's. Record schema, pruning caps, append-only semantics, and concurrency posture are defined in seen-tracker's SKILL.md; feed-watcher never touches state files directly.

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
- [`seen-tracker`](../seen-tracker/SKILL.md) — cross-run dedup state, keyed by the calling agent.

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
