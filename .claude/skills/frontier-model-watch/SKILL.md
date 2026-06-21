---
name: frontier-model-watch
description: On-demand Category 1 researcher for frontier-model news (Anthropic, OpenAI, Google, Meta, Mistral, emerging) with the "what changes for enterprise dev tooling" angle. Specifically — which models route through Copilot per-feature? What deprecations are imminent? What new capabilities affect AI-tool TPRM posture or model-risk reviews? Output at vault/research/frontier-model/YYYY-MM-DD-{slug}.md. Composes with ai-coding-tools-compare (model side of the tool comparison) and the weekly-intelligence-digest (the recurring intelligence pipe).
---

# frontier-model-watch

The model-side companion to `ai-coding-tools-compare`. Tools matter; models matter; the intersection is where the org's stack actually lives. This skill keeps the frontier-model dimension grounded specifically in "what changes for the org's Copilot deployment / AI tool posture."

## When to use

- Major model release (Anthropic Opus 4.x → 4.y, OpenAI GPT-5.x → 6.x, etc.).
- Model deprecation announcement (e.g., Opus 4.6 fast 2026-06-29).
- Model availability shift (e.g., Fable 5 / Mythos 5 US export-control situation 2026-06-12).
- Benchmark publication that reframes per-model strengths.
- Annual frontier-model landscape summary.

## When NOT to use

- Specific Copilot question → `copilot-faq-answerer`.
- AI tool comparison → `ai-coding-tools-compare`.
- AI governance framework → `ai-governance-research`.

## Obsidian-first workflow

Same as other Category 1 researchers — query vault first, web second.

## Topic taxonomy

For the research note's `topic` field, use `frontier-model`. Vault facts under `vault/facts/{model-or-vendor}/`.

## Compliance-relevant framing per finding

For each model finding, answer:
1. Does this affect what Copilot will route to for this org? When?
2. Does this change the AI-tool TPRM file?
3. Does this require a model-risk review (if the org's posture includes one for AI tools)?
4. Is there a deprecation date that triggers user-facing communication?

## Composes with

Standard Phase-1 foundation. Cross-feeds:
- `weekly-intelligence-digest` — recurring frontier model news.
- `ai-coding-tools-compare` — model side of the tool comparison.
- `copilot-faq-answerer` — model-selection canonical answer needs updates when models shift.

## Acceptance test (for step 28 done-criteria)

One research note exercising a specific frontier-model topic with the compliance-relevant framing applied per finding.
