---
name: claim-extractor
description: Extract falsifiable claims from a fetched source document, returning a standard `{claim, quoted_anchor, source_url, source_tier, claim_type}` schema per claim. Filters out opinions, marketing fluff, vague generalizations, and unverifiable forward-looking statements. Used by every Category 1 research skill (Obsidian-first contract) before passing claims to verify-claim, and by memory-curator when staging multi-claim documents into _inbox/. Composes on source-fetcher (the input is its content_md) and prompt-injection-guard (already applied upstream).
---

# claim-extractor

Reads a fetched source document and extracts the **falsifiable** claims — statements with truth-value, anchored to a verbatim excerpt in the source. Downstream skills (`verify-claim`, `memory-curator`) consume the standard claim schema; without this layer, research outputs become a soup of "the article says…" assertions with no falsifiability and no anchor.

## When to use

- Inside any Category 1 research skill after fetching a source via `source-fetcher` — extract claims before deciding which to verify and persist.
- Inside `weekly-intelligence-digest` / `voices-watcher` / any Category 2 agent when an item is interesting enough to mine.
- Inside `memory-curator` when staging a multi-claim document into `_inbox/` — each claim becomes its own candidate.

## When NOT to use

- Single-fact inputs (the user typed "GitHub Copilot data handling is X" — already a claim, no extraction needed).
- Code snippets, schemas, structured data — those aren't claims.
- The body of a digest the toolkit just wrote — that's our own output, not external sourced material.

## Input

```json
{
  "content_md": "<markdown body, post prompt-injection-guard>",
  "source_url": "https://example.com/article",
  "source_tier": 1 | 2 | 3,
  "fetched_at": "2026-06-20T15:00:00Z"
}
```

The `content_md` is whatever `source-fetcher` returned. Quarantined blocks (from `prompt-injection-guard`) should be **excluded** from claim mining — they are not trustworthy source material.

## What counts as falsifiable

A claim is falsifiable if a competent reader could in principle confirm or refute it from independent evidence. Concretely:

- ✅ **Falsifiable**: "Copilot Enterprise audit log now exports to S3 with KMS encryption." "FFIEC's 2026 IT Handbook adds Section 7.4 on AI/ML risk." "Anthropic released Claude Opus 4.7 on May 14, 2026."
- ❌ **Not falsifiable** (opinion / marketing / vague): "Copilot is a game-changer." "Most banks struggle with X." "This is the most important AI update of the year."
- ❌ **Forward-looking without commitment** (skip unless tied to a dated commitment): "We plan to support…" "Coming soon…" "Expected in Q4." (Keep if tied to an official roadmap entry; drop if vague intent.)

## What to exclude

- Content inside quarantine blockquotes (per `prompt-injection-guard`).
- Boilerplate (author bio, footer disclaimers, "subscribe" CTAs).
- Headings without a corresponding declarative sentence (they're navigation, not claims).
- Direct quotes attributed to a person (those are claims-about-a-person, not the source's claim; capture as a separate `claim_type: attribution`).

## Output schema

```json
[
  {
    "claim": "Copilot Enterprise audit log now exports to S3 with KMS encryption.",
    "quoted_anchor": "Audit log now exports to S3 with KMS encryption (previously CSV download only).",
    "source_url": "https://example.com/article",
    "source_tier": 1,
    "claim_type": "fact | event | quantitative | attribution | comparative | roadmap-commitment",
    "entities": ["copilot", "github"],
    "tags_suggested": ["copilot", "ghas"],
    "line_range": [12, 12],
    "confidence_hint": 2
  }
]
```

Field guidance:

- **`claim`**: cleanly stated, self-contained — "another AI with zero prior context should understand it" (per the writing standard).
- **`quoted_anchor`**: a verbatim excerpt from `content_md` that supports the claim. Required; if you can't find an anchor, the claim isn't extractable.
- **`source_tier`**: copy from input.
- **`claim_type`**: one of the enum values. Most claims are `fact` (typed claim about an entity) or `event` (something happened on a date). `quantitative` for numeric claims with values. `attribution` for "X said Y." `comparative` for "X is better/larger/cheaper than Y." `roadmap-commitment` for dated forward-looking statements with vendor backing.
- **`entities`**: lowercase-kebab entity names (e.g., `copilot`, `ffiec`, `johncutlefish`). Used downstream to route facts to `facts/{entity}/{predicate}.md`.
- **`tags_suggested`**: from the controlled vocabulary in `~/Obsidian/Research-Brain/_meta/tags.md`. Used downstream to set frontmatter `tags:`.
- **`line_range`**: approximate `[start, end]` line numbers in `content_md` for the quoted anchor — helps a human reviewer locate context.
- **`confidence_hint`**: a starting confidence (1-3) based on `source_tier` + claim specificity. The actual confidence gets set after `verify-claim`.

## Default caps

- Max **25 claims per source** to keep downstream verification tractable (per the built-in `deep-research` pattern). If the source has more, return the top 25 by load-bearing-ness (specific facts > comparatives > attributions > marketing-adjacent).
- If 0 falsifiable claims found, return an empty list **with a `warnings` field** explaining why ("source is opinion piece", "all content was quarantined", "source is a CTA / signup page"). Per the stop-and-report guardrail: caller must know zero was a deliberate result, not silent failure.

## Composes with

- [`source-fetcher`](../source-fetcher/SKILL.md) — input is its `content_md`.
- [`prompt-injection-guard`](../prompt-injection-guard/SKILL.md) — already applied; quarantined blocks excluded from mining.
- [`verify-claim`](../verify-claim/SKILL.md) — downstream; takes the extracted claims and runs adversarial verification.
- `memory-curator` — uses extracted claims to decide promote/patch/drop per claim.

## Acceptance test (for step 5 done-criteria)

Run on `tests/sample-article.md` (in this skill folder). Expected:
- ≥3 falsifiable claims extracted.
- Each claim has a non-empty `quoted_anchor` that exists verbatim in the source.
- Vague / opinion lines are **not** extracted.
- A claim from inside a quarantine block (if the fixture has one) is **not** extracted.
- Output includes `entities` and `tags_suggested` from the controlled vocabulary.
