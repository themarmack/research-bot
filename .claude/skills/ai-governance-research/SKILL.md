---
name: ai-governance-research
description: On-demand Category 1 researcher targeting AI governance frameworks and regulations applicable to internal AI dev tooling — NIST AI RMF, EU AI Act, US executive orders, state AI laws (California, Colorado, etc.), ISO 42001, model cards, and the org-specific application of each. Enforces Obsidian-first contract. Outputs at vault/research/ai-governance/YYYY-MM-DD-{slug}.md; verified facts get staged for memory-curator promotion to vault/facts/{framework-entity}/. Use when the user asks to research whether or how an AI governance framework or AI-specific law applies to internal AI dev tooling — producing a fresh, cited research note — as opposed to financial-services regulator guidance (financial-regulator-watch) or a cross-framework control-ID mapping for a single control question (compliance-framework-lookup).
---

# ai-governance-research

Companion to `financial-regulator-watch`. Where the regulator-watch covers the *financial-services regulator* lens, this skill covers the *AI-specific governance* lens — frameworks that apply to AI tooling regardless of industry, but with practical implications for how the org uses AI dev tools (Copilot, internal LLM gateways, agentic SDLC features).

## When to use

- Question about whether a specific AI framework applies to internal dev tooling (the user's domain).
- Mapping a org's existing AI risk posture to NIST AI RMF / ISO 42001 / EU AI Act categories.
- Background research before a policy decision (e.g., "should our AI tool catalog require model cards?").
- Comparing posture across frameworks (NIST AI RMF + EU AI Act + state law).

## When NOT to use

- Financial-services regulator guidance → `financial-regulator-watch`.
- Specific Copilot / GitHub / vendor questions → `copilot-deep-dive` or `github-platform-watch`.
- AI-tool vendor evaluation — that's [`vendor-security-eval`](../vendor-security-eval/SKILL.md).

## Source taxonomy

Tier-1 primary sources:

| Framework | Authoritative source |
|-----------|----------------------|
| NIST AI RMF (1.0 + Generative AI Profile) | nist.gov |
| EU AI Act | EUR-Lex (Regulation 2024/1689 + Annexes) |
| US Executive Orders on AI | whitehouse.gov, federalregister.gov |
| ISO 42001 | iso.org (standard text often gated; use ISO's public summaries + commentary) |
| State AI laws | state legislative trackers (Colorado SB24-205, NYC Local Law 144, California SB-1047, etc.) |
| Model cards | original Mitchell et al. paper + Hugging Face card spec |
| Anthropic / OpenAI / Google AI policy releases | each lab's own policy/safety pages — tier-1 for THEIR model, tier-3 for cross-lab claims |

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/research/ai-governance/**`, `vault/facts/{framework-entity}/**` (e.g. `nist-ai-rmf`, `eu-ai-act`, `iso-42001`), and recent `vault/digests/**` (last 90 days).
   - Backlink check on the framework's entity (e.g. `[[eu-ai-act]]`) and the question's other entities.
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources from the source taxonomy above (nist.gov, EUR-Lex, federalregister.gov, iso.org, state legislative trackers, lab policy pages).
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute). AI governance frameworks are interpretation-heavy — there's lots of analyst commentary on what the EU AI Act "really" means for a specific use case. Framework text itself is tier-1 (no verification); apply `verify-claim` liberally on any interpretive claim before promoting to a fact.
5. **Write the research note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/ai-governance/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic` from the taxonomy below, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/ai-governance-research/`:
   - Any verified fact-typed claim → `_inbox/ai-governance-research/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{framework-entity}/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

## Topic taxonomy

For the research note's `topic` field:
- `nist-ai-rmf` / `eu-ai-act` / `us-executive-orders` / `state-ai-laws` / `iso-42001` / `model-cards`
- `cross-framework-mapping` — when comparing how one use case maps across multiple frameworks

## Compliance-relevant framing

For each AI-governance finding, the framing answers: "Does this apply to the org's internal Copilot deployment? If so, what control or process change is implied?"

The org's AI governance work is also constrained by the financial-services regulator stack (SR 11-7 model risk, FFIEC IT Handbook, NYDFS Part 500's AI amendments) — so most research notes will explicitly cross-reference [`financial-regulator-watch`](../financial-regulator-watch/SKILL.md) output where the two overlap.

## Composes with

The Phase-1 foundation named in the workflow above (`vault-querier`, `source-fetcher` + `prompt-injection-guard`, `claim-extractor` + `verify-claim`, `digest-writer` → `vault-writer`, `_inbox/` + `memory-curator`). Naturally pairs with `financial-regulator-watch` — most decisions need both lenses.

- [`executive-summary-writer`](../executive-summary-writer/SKILL.md) — **only when the user explicitly asks for an exec summary** (never auto-invoked after vault write). Takes the just-written research note's path and produces a 1-page summary tuned to a named audience (CISO, VP Eng, etc.).
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 12 done-criteria)

One live end-to-end research run produces a note at `vault/research/ai-governance/YYYY-MM-DD-{slug}.md` with tier-1 source citations and explicit "applies to internal Copilot deployment? → yes/no/partial + which controls" mapping.
