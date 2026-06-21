---
name: weekly-self-review
description: End-of-week personal-reflection skill, distinct from weekly-review (which surveys the vault's writes). This is about the **user's** week — what they worked on, what energized vs drained, what they want to focus on next week, what's nagging at them. Outputs a private reflection note that doesn't aim for objectivity. Use on Friday afternoon or Sunday evening for personal end-of-week reflection.
---

# weekly-self-review

The personal-reflection sibling of `weekly-review`. Where `weekly-review` surveys what the *vault* accumulated, this skill surveys what the *user* experienced. Different audience (just the user), different voice (subjective, frank), different goal (personal calibration, not program intelligence).

## When to use

- Friday afternoon or Sunday evening end-of-week reflection.
- Periodic recalibration after a stretch of intense work.
- Pre-vacation handoff prep — what's nagging that should be written down.

## When NOT to use

- Vault-content weekly synthesis → `weekly-review`.
- Stakeholder communication → `stakeholder-update-writer`.
- Decision capture → `decision-memo-writer` or `quick-capture` (decision format).

## Reflection prompts

The skill walks the user through 5 standard prompts:

1. **What worked this week?** — moments worth replicating.
2. **What drained?** — patterns worth tweaking.
3. **What did I learn?** — knowledge worth keeping.
4. **What's nagging?** — open loops worth surfacing.
5. **Where do I want to focus next week?** — intentional, not aspirational.

## Output structure

```markdown
# Weekly Self Review — {week ending date}

[5 prompts and responses]

## Action items from this review
- {if any concrete actions emerge}

## Calibration
- Energy/satisfaction: {1-10}
- Trend vs prior weeks: {↑ / ↓ / →}
```

Lands at `vault/insights/YYYY-MM-DD-self-review.md` (the slug `self-review` keeps these distinct from `weekly-review`).

## Acceptance test

SKILL.md describes the 5-prompt structure. Live exercise deferred — the next Friday is the natural fixture.
