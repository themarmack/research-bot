---
name: memory-curator
description: Decide whether an inbox item or candidate finding should be promoted to a durable vault folder, patched onto an existing note, or dropped. Applies the rules from ~/Obsidian/Research-Brain/_meta/inbox-rules.md (novelty, falsifiability, future utility, surprise, sourcing). Runs on _inbox/{agent-id}/ items to sweep them or can be called ad-hoc by a skill before a direct vault-writer call. Composes with vault-querier for novelty checks and vault-writer for the actual promote/patch writes. Default-drops unsourced agent claims; never silently drops content with substance — uncertain items get tagged #needs-review.
---

# memory-curator

The gatekeeper for what becomes durable in the vault. Most agent writes go through `_inbox/` first; the curator decides whether they earn promotion to `facts/`, `events/`, `decisions/`, `insights/`, or `research/`; get patched onto an existing note; or get archived to `_inbox/.dropped/` for audit.

## When to use

- **Inbox sweep** (scheduled or manual): process accumulated `_inbox/{agent-id}/` items.
- **Pre-check before a direct vault-writer call** when the source is a web fetch (not user-curated).
- A research skill discovers a finding mid-run and wants to know: "should this be durable?"

## When NOT to use

- For human writes to curated surfaces (`decisions/`, `insights/`) — those are authoritative; the curator only catches agent stages.
- For scheduled-agent digest writes — digests are append-only historical records, written directly via `vault-writer`'s `write_digest`.

## Three verdicts

For every candidate:

1. **promote** — write a new durable note at a specific surface + path.
2. **patch** — update an existing durable note (which one + merge instructions).
3. **drop** — move to `_inbox/.dropped/{agent-id}/{timestamp}-{slug}.md` with a documented reason. **Never silently delete.**

## Decision rules (from `_meta/inbox-rules.md`)

### Promote when ALL hold:
- **novel** — no existing durable note covers the same `entity/predicate` or `topic/question` (check via `vault-querier`)
- **specific** — concrete answer to a concrete question
- **future-useful** — plausibly worth looking up again
- **sourced** — `source_url` present, OR `source_skill: human` AND user authored
- **surprise or load-bearing** — changes the user's mental model OR will be referenced by other notes

### Patch when:
- a durable note exists for the same `entity/predicate` (facts), same slug (insights/persons/projects), or same dated event AND
- the inbox item adds new info (more sources, updated value, additional participants, etc.)

### Drop when ANY hold:
- already known and unchanged
- marketing claim without falsifiable substance
- content about identity / preferences / feedback (belongs in Tier-1, not the vault)
- `#do-not-share` content from internal sources without user approval
- `confidence: 1` AND no `source_url`

### Guardrail (the hard rule from `_meta/inbox-rules.md`)

**Never silently drop content with substance.** If uncertain, do **not** auto-drop — leave the item in `_inbox/` with tag `#needs-review` and a `curator_uncertainty:` line in the body explaining why. Drops are reserved for explicit rule matches; the `.dropped/` folder is the audit trail.

## Workflow

1. **List candidates**: read `_inbox/{agent-id}/*.md` (or accept an explicit payload).
2. **For each candidate**:
   - Parse its frontmatter and body.
   - Identify entity / predicate / slug / topic from frontmatter or body cues.
   - **Novelty check**: `vault-querier` for matching `facts/{entity}/{predicate}.md`, related `insights/{slug}.md`, recent `research/{topic}/`, etc.
   - Apply the criteria checklist above.
   - Emit a verdict with target surface + path (for promote/patch) or reason (for drop).
3. **Execute**:
   - **promote**: call `vault-writer.write_{surface}` with the candidate's payload. On success, delete the inbox file.
   - **patch**: read the target durable note, merge fields per `vault-writer`'s idempotency rules, call `write_{surface}` again. On success, delete the inbox file.
   - **drop**: move the inbox file to `_inbox/.dropped/{agent-id}/{timestamp}-{slug}.md` and append a body line:
     ```
     > 🗑 dropped by memory-curator: <reason> (2026-06-20T15:30:00Z)
     ```
   - **needs_review**: leave in place, append `tags: [#needs-review]` to frontmatter and `> ⚠ curator uncertainty: <why>` to body.
4. **Return** the summary.

## Output shape

```json
{
  "agent_id": "voices-watcher",
  "processed": 12,
  "promoted": 5,
  "patched": 2,
  "dropped": 4,
  "needs_review": 1,
  "actions": [
    {
      "inbox_path": "_inbox/voices-watcher/2026-06-20T15-30-00-johncutlefish-substack-url.md",
      "verdict": "promote",
      "target_surface": "facts",
      "target_path": "facts/johncutlefish/substack-url.md",
      "reason": "novel + sourced + specific + load-bearing"
    },
    {
      "inbox_path": "_inbox/voices-watcher/2026-06-20T15-31-00-unknown-claim.md",
      "verdict": "drop",
      "moved_to": "_inbox/.dropped/voices-watcher/2026-06-20T15-31-00-unknown-claim.md",
      "reason": "confidence=1 AND no source_url"
    }
  ]
}
```

## Recoverability

Drops are **not destructive**. Items in `_inbox/.dropped/` remain on disk indefinitely. The user can move any item back into `_inbox/{agent-id}/` to re-run curation, or directly into a durable folder if they disagree with the verdict.

## Composes with

- [`vault-conventions`](../vault-conventions/SKILL.md) — schemas + `inbox-rules.md`.
- [`vault-querier`](../vault-querier/SKILL.md) — novelty checks.
- [`vault-writer`](../vault-writer/SKILL.md) — the actual promote/patch writes.

## Acceptance test (for step 4 done-criteria)

Two test inbox items exist at `~/Obsidian/Research-Brain/_inbox/test-step-4/`:

1. **`promotable-fact.md`** — well-formed fact candidate with `source_url`, `entity`, `predicate`, `value`, confidence 2. Expected verdict: **promote** → `facts/copilot/data-handling.md` (or similar). Inbox file gets deleted after promote.
2. **`unsourced-claim.md`** — claim without `source_url`, confidence 1. Expected verdict: **drop** → moved to `_inbox/.dropped/test-step-4/`. Body gets the "dropped by memory-curator: confidence=1 AND no source_url" line appended.

When `memory-curator` is first invoked (in step 7+, or manually via "run memory-curator on _inbox/test-step-4/"), the output should show:
- `processed: 2, promoted: 1, dropped: 1`
- Both items routed correctly per the rules.

Until the first invocation, the fixtures are evidence that the spec covers both ends of the promote/drop spectrum.
