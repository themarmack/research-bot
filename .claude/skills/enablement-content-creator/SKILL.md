---
name: enablement-content-creator
description: Generate training / enablement content for the SDLC modernization program — Copilot prompting, secure coding with AI, CodeQL triage, GHAS workflows, AGENTS.md authoring. Produces tiered content (dev / lead / exec) with the same factual backbone but different framing, depth, and call-to-action per audience. Pulls from copilot-faq-answerer canonical answers (recently extended via memory-curator's promoted facts) and objection-response-library steel-manned concerns. Output lands at vault/insights/YYYY-MM-DD-enablement-{topic-slug}.md.
---

# enablement-content-creator

The training-content factory. Most enablement materials get written once and rot; this skill makes "regenerate based on current facts" cheap so content stays accurate.

## When to use

- New module needed for the rollout playbook's Phase-2 training step.
- An existing module is stale (facts in vault have been updated past its `last_verified`).
- A specific question is being asked enough to merit standalone training content.
- Onboarding cohort needs the consolidated module set.

## When NOT to use

- One-time stakeholder update → `stakeholder-update-writer`.
- Single objection response → `objection-response-library`.
- Quick FAQ answer → `copilot-faq-answerer`.

## Tier structure

| Tier | Length | Voice | Focus |
|------|--------|-------|-------|
| Dev | ~600-1200 words + examples | practical, friendly, low jargon | "what to do in your IDE today" |
| Lead | ~400-800 words | explanatory, balances depth with brevity | "what your team needs to know + watch for" |
| Exec | ~150-300 words | declarative, dense | "what changes + what you should know to approve" |

## Workflow

1. **Identify the topic** (Copilot prompting, secure coding with AI, CodeQL triage, AGENTS.md authoring, etc.).
2. **Load supporting facts** from `vault/facts/` + `copilot-faq-answerer/canonical-answers.md`.
3. **Load steel-manned concerns** from `objection-response-library/canonical-objections.md` so the tier content pre-empts objections.
4. **Draft per tier** using the structure above.
5. **Cross-reference**: every claim cites a vault fact or research note.

## Output structure

```markdown
# Enablement — {topic}

## Tier 1 — Dev
[content]

## Tier 2 — Lead
[content]

## Tier 3 — Exec
[content]

## Versioning
- Based on facts as of: {date}
- Vault facts cited: [[wikilink list]]
- Refresh trigger: when any cited fact's `last_verified` changes
```

Lands at `vault/insights/YYYY-MM-DD-enablement-{topic-slug}.md`.

## Composes with

- `copilot-faq-answerer` — canonical-answer source.
- `objection-response-library` — steel-manned concerns to pre-empt.
- `vault-querier` — load facts + recent research for currency.
- `stakeholder-update-writer` — exec-tier enablement often pairs with stakeholder communication.

## Acceptance test (for step 33 done-criteria)

SKILL.md covers the 3-tier structure + workflow. Live exercise deferred — Phase 2 of the Payments rollout has a training-module step that's the natural fixture, scheduled for 2026-06-28.
