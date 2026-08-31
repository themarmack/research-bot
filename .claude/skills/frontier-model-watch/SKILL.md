---
name: frontier-model-watch
description: On-demand Category 1 researcher for frontier-model news (Anthropic, OpenAI, Google, Meta, Mistral, emerging) with the "what changes for enterprise dev tooling" angle. Specifically — which models route through Copilot per-feature? What deprecations are imminent? What new capabilities affect AI-tool TPRM posture or model-risk reviews? Output at vault/research/frontier-model/YYYY-MM-DD-{slug}.md. Composes with ai-coding-tools-compare (model side of the tool comparison) and the weekly-intelligence-digest (the recurring intelligence pipe). Use when the user asks to research a specific frontier-model release, deprecation, availability shift, or benchmark on demand — producing a fresh, cited research note — not the scheduled quarterly landscape survey (quarterly-ai-coding-landscape), a tool-level comparison (ai-coding-tools-compare), or a recurring news sweep (weekly-intelligence-digest).
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

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the model / vendor key terms across `vault/research/frontier-model/**`, `vault/facts/{model-or-vendor}/**` (e.g. `anthropic`, `openai`, `google`), `vault/facts/copilot/**` (model-routing facts live there), and recent `vault/digests/**` (last 90 days — `weekly-intelligence-digest` and `quarterly-ai-coding-landscape` carry model news).
   - Backlink check on the model / vendor entities (e.g. `[[anthropic]]`, `[[gpt-5]]`).
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: each lab's own announcement / docs pages (tier-1 for THEIR model, tier-3 for cross-lab claims), the GitHub Copilot changelog for routing changes, official deprecation notices.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - A vendor's claims about its own model are tier-1 (no verification); benchmark interpretations, cross-lab comparisons, and availability/export-control analysis get the full 3-vote treatment.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/frontier-model/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: frontier-model`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/frontier-model-watch/`:
   - Any verified fact-typed claim (e.g. a deprecation date, a routing change) → `_inbox/frontier-model-watch/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{model-or-vendor}/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

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
