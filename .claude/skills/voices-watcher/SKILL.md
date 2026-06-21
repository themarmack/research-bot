---
name: voices-watcher
description: Daily scheduled agent that polls the AI/product-strategy voices roster (~/voices.csv at repo root, seeded from @natebjones's X Following list), surfaces new Substack / YouTube / blog / podcast items per voice, and produces a daily digest at vault/digests/daily/YYYY-MM-DD-voices-watcher.md. Also keeps vault/people/{handle}.md in sync with the roster — creates missing person notes on first run, patches surface URLs as voices-roster-curator enriches them. Does NOT poll X/Twitter (per the decision in decisions/2026-06-20-adopt-obsidian-and-ob1-patterns).
---

# voices-watcher

The daily intelligence pipe for what the AI / product-strategy commentariat is publishing. Reads the human-curated roster at `voices.csv` (repo root), polls every voice's Substack / YouTube / blog / podcast feeds, and surfaces what's new in a single digest the user reads each morning.

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: voices-watcher
cadence: daily
schedule_hint: "07:30 local"
source_filter:
  custom: voices.csv               # NOT source-registry — uses voices.csv at repo root
  surfaces:                        # which columns to poll
    - substack
    - youtube
    - blog
    - podcast
  max_items_per_voice: 3
verify_loadbearing: false          # commentary is not "fact-claim" material; skip 3-vote refute
curate_findings: false             # findings stay in the digest; user decides what to promote manually
seed_people_notes: true            # ensure vault/people/{handle}.md exists for every roster row
digest_template_overrides:
  why_you_care_extra: |
    Voices are commentators, not vendors. Frame "Why You Care" by tying threads to active
    SDLC modernization questions, Copilot rollout posture, peer-bank concerns, or AI
    governance work. If a post is purely off-topic for the org context, surface the
    title only — don't generate a Why-You-Care line.
```

## How it differs from `weekly-intelligence-digest`

This skill **does not use `source-registry`**. The voices roster is human-curated outside the registry because it's a long, slowly-changing list of people (not vendor/regulator surfaces). Edits to who's watched happen by editing `voices.csv` (or via `voices-roster-curator` once it ships in step 14), not by editing the registry.

`scheduled-agent-runner`'s lifecycle still applies — the runner accepts a `source_filter.custom: voices.csv` and routes to the voices loader instead of the registry loader.

## Per-row polling logic

For each row in `voices.csv`:

1. **Skip** if no row has any of the polling-surface columns populated (`substack`, `youtube`, `blog`, `podcast`).
2. For each populated surface URL:
   - Call `source-fetcher` on the URL (Substack and most blogs have RSS at `<base>/feed`; try that first, fall back to scraping the page).
   - Extract recent items (up to `max_items_per_voice`).
   - `seen-tracker.bulk_filter` against `.state/voices-watcher/seen.jsonl`.
3. Group new items by voice.
4. Skip voices with zero new items in the period (don't pad the digest with "nothing new from X").

## Person-note seeding

For every row in `voices.csv`, ensure a `vault/people/{handle}.md` note exists with frontmatter populated from the CSV columns (handle, name, bio_snippet, role, surfaces dict). On first run this creates ~25 notes; on subsequent runs it patches:
- New surface URLs from the CSV → merged into `surfaces` dict
- New `notes` column entries → appended to the note's body
- Existing human-written body content → **preserved** (per `vault-writer.write_person` idempotency rules)

Use `vault-writer.write_person` for this — never write directly.

## Digest structure

Standard 5-section structure (per `digest-writer`):

- **TL;DR**: top 3 voices by signal — voices whose new item is most relevant to compliance/SDLC/Copilot. Format each as `[[handle]]: <one-line takeaway>`.
- **What Changed**: one bullet per (voice, item) pair: `**[[handle]]** — *<title>* ([source link]) (accessed YYYY-MM-DD)`.
- **Why You Care**: per item where applicable, the compliance-relevant framing line. Skip if the item is purely off-topic.
- **Detailed Findings**: top 3 items in 2-3 sentences each.
- **Sources**: list of voices polled, voices with new items, voices skipped (no pollable surface yet).

## Output

`vault/digests/daily/YYYY-MM-DD-voices-watcher.md` — the digest.
`vault/people/{handle}.md` — created or patched, one per roster row.

## Composes with

- Roster: `voices.csv` (repo root) — human-curated.
- All Phase-1 foundation skills via `scheduled-agent-runner`.
- `vault-writer.write_person` for people-note seeding (uses person.yml schema).

## Acceptance test (for step 8 done-criteria)

One end-to-end run. Confirm:
- Daily digest at `vault/digests/daily/YYYY-MM-DD-voices-watcher.md` exists with 5 sections.
- Every row in `voices.csv` has a corresponding `vault/people/{handle}.md` note (~25 files).
- Each person note has valid frontmatter per `person.yml`.
- The digest surfaces real new items from at least 2 polled Substacks.
- Sources section lists which voices were polled vs skipped.
- `.state/voices-watcher/seen.jsonl` populated.
