---
name: scheduled-agent-runner
description: Orchestration wrapper for every Category 2 scheduled skill. Standardizes the lifecycle: load last-run state via seen-tracker → fetch via feed-watcher → extract claims via claim-extractor → verify load-bearing ones via verify-claim → format via digest-writer → write via vault-writer → curate findings via memory-curator → emit a one-line summary for the runner log. Lets every scheduled agent (weekly-intelligence-digest, voices-watcher, weekly-review, monthly-copilot-changelog, etc.) be ~30 lines of "what to fetch, how to frame the why-you-care" instead of 200 lines of plumbing.
---

# scheduled-agent-runner

The orchestration convention every Category 2 (scheduled) skill follows. Without this wrapper, each scheduled agent would re-implement state loading, dedup, fetch, claim mining, verification, write, curation, and logging. With it, a scheduled agent is mostly a config blob and a custom "why you care" prompt.

## When to use

- **Every Category 2 scheduled skill** uses this as its top-level run loop.
- Manual one-shot runs of a scheduled agent (e.g., user says "run weekly-intelligence-digest now") use the same wrapper.

## When NOT to use

- Category 1 on-demand research skills — those have a different lifecycle (Obsidian-first contract, single-question scope, no recurrence).
- Direct `vault-writer` calls (decisions, individual facts) — no run-state, no digest, no orchestration needed.

## Standard lifecycle

Every scheduled-agent run follows this exact sequence:

```
1.  load_conventions()        ← vault-conventions cached output
2.  load_last_run_state()     ← seen-tracker bulk lookup for this skill
3.  fetch_candidates()        ← feed-watcher with the agent's filter
4.  filter_new()              ← seen-tracker.bulk_filter → keep new + updated
5.  extract_claims()          ← claim-extractor per source body (Category 2 digests
                                that don't need claim-level granularity skip this)
6.  verify_loadbearing()      ← verify-claim only on claims tagged as load-bearing
                                (top-of-digest items, anything destined for facts/)
7.  build_digest_input()      ← assemble TL;DR, items, failures, frontmatter context
8.  write_digest()            ← digest-writer → vault-writer.write_digest
9.  curate_findings()         ← stage promotable claims to _inbox/ → memory-curator
10. mark_surfaced()           ← seen-tracker.mark_surfaced for every item written
11. maybe_email()             ← email-sender.auto_send(path, "digest") — sends
                                the digest to every recipient parsed from the
                                vault distribution list
12. emit_summary()            ← one-line runner-log entry (includes email status)
```

Steps 5–6 are optional per agent. A pure "what shipped this week" digest (changelog aggregator) may not need claim-level verification — the source IS the authority. A regulator-watch digest with novel interpretations does need it.

Step 11 (`maybe_email`) is always invoked for any digest surface. It loads the recipient list from `~/Obsidian/Research-Brain/_config/email-distribution.md` and sends the digest to every parsed recipient. If the distribution file is missing or empty, `maybe_email` stop-and-reports and step 12's summary line shows `email_failed=<reason>`. Email failure does NOT roll back the vault write — the note is durable; email is a delivery channel only.

## Per-agent config

Every scheduled agent declares its config as a header in its own SKILL.md. The runner reads:

```yaml
agent_name: weekly-intelligence-digest
cadence: weekly                   # daily | weekly | biweekly | monthly | quarterly
schedule_hint: "Monday 07:00"      # informational; actual scheduling is the user's cron
source_filter:                     # passed to feed-watcher
  topic_tags: [github, copilot, frontier-model, regulator, supply-chain]
  min_tier: 1
  max_items_per_source: 5
verify_loadbearing: true           # whether to invoke verify-claim
curate_findings: true              # whether to stage to _inbox/ + run memory-curator
digest_template_overrides:         # optional, mostly the regulated-org lens
  why_you_care_extra: "Emphasize SR 11-7 and FFIEC implications when applicable."
```

The runner injects these into the lifecycle steps. The agent's own SKILL.md instructions are short: framing, voice, what to emphasize. The plumbing belongs here.

## State

- `last_run_at` — timestamp recorded after a successful run, used by `digest-writer` for the "since last digest" framing.
- `last_digest_path` — vault path of the most recent digest written; previous_digest link.
- `seen.jsonl` — managed by `seen-tracker` under `.state/<agent_name>/`.
- All state lives at `<repo>/.state/<agent_name>/`.

## Output (per run)

A single summary line emitted to stdout (or captured by the caller):

```
[2026-06-20T07:01:23Z] weekly-intelligence-digest: polled=8 sources, new_items=14, verified=5, written=vault/digests/weekly/2026-06-20-weekly-intelligence-digest.md, emailed=3/3, failures=2 (anthropic-news html-scrape, openai-news html-scrape)
```

The `emailed=` segment reports per-recipient delivery (`sent/total`). Possible values:
- `emailed=3/3` — full delivery to every parsed recipient.
- `emailed=2/3` — partial delivery; skipped recipients appear in the failures section.
- `email_failed=<reason>` — config or SMTP error from `email-sender` (missing distribution list, empty list, missing app password, SMTP auth failure, etc.). The vault write still succeeded; only the send failed.

Plus the digest file in the vault and any `_inbox/<agent_name>/` stages for `memory-curator` to process on its next sweep.

## Failure handling

Per the stop-and-report guardrail, ANY of these surface to the summary line and to the digest's Sources section:

- A source that failed to poll
- A claim that came back inconclusive from `verify-claim`
- A `vault-writer` schema-validation rejection
- A `memory-curator` drop with substantive content
- An `email-sender` failure (misconfig, SMTP, partial recipient delivery) — surfaces as `emailed=<list>(sent/total)` or `email_failed=<reason>`; the digest itself remains written.

A failed run **still emits a partial summary** — the digest file is written even if 2 of 8 sources failed, or even if email delivery failed entirely. Sources section makes the gaps visible.

## Composes with

Every Phase-1 skill plus the curator:
- `vault-conventions`, `vault-querier`, `vault-writer` (vault I/O)
- `source-registry`, `feed-watcher`, `source-fetcher`, `prompt-injection-guard` (data plane)
- `claim-extractor`, `verify-claim` (verification spine)
- `seen-tracker` (dedup)
- `digest-writer` (formatter)
- `memory-curator` (post-digest cleanup)
- [`email-sender`](../email-sender/SKILL.md) (step 11 — auto-send to the vault distribution list)

This is also the single seam where the OB1-borrowed `weekly-review` skill plugs in — it follows the same lifecycle but with a different `source_filter` (the vault itself) and a different digest template (Week at a Glance / Themes / Open Loops / Connections / Gaps / Focus).

## Acceptance test (for step 6 done-criteria)

Hand the runner a minimal no-op agent config:

```yaml
agent_name: noop-test-agent
cadence: daily
source_filter: { topic_tags: [github] }
verify_loadbearing: false
curate_findings: false
```

Run end-to-end. Confirm:
- Sequence steps 1, 2, 3, 4, 7, 8, 10, 11, 12 execute (skips 5, 6, 9 per config; step 11 `maybe_email` stop-and-reports with `email_failed=distribution list missing` when no `_config/email-distribution.md` exists — that's expected in the acceptance test fixture).
- A digest file lands at `vault/digests/daily/YYYY-MM-DD-noop-test-agent.md`, even if empty body (just TL;DR-style empty + Sources section).
- `.state/noop-test-agent/seen.jsonl` is created and populated.
- Summary line is emitted.

Live exercise happens when step 7 (`weekly-intelligence-digest`) wraps real consumer logic around this runner.
