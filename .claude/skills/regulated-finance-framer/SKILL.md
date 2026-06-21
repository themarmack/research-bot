---
name: regulated-finance-framer
description: Reusable prompt-fragment skill consolidating the regulated-org framing rules that every Category 1 research skill and Category 5 comms skill currently bakes into its own SKILL.md. Any topic skill that needs the compliance-relevant lens can include this fragment via a single reference rather than re-implementing the framing. When the org's posture, regulatory environment, or control catalog evolves, edit this skill once and every downstream skill inherits. Use as an `import` from any skill that wants the standard compliance framing applied to its output.
---

# regulated-finance-framer

The shared compliance-lens prompt fragment. Without it, every research / comms skill duplicates the same framing logic; with it, framing evolves in one place.

## When to use (as a downstream skill author)

- Authoring a new Category 1 research skill — include this fragment to get the standard framing.
- Authoring a Category 5 comms skill that needs the compliance-relevant tier framing.
- Updating an existing skill to align with current framing rules.

## When NOT to use

- Skills with surface-specific framing that's intentionally different (e.g., `quick-capture` doesn't need this — it's not framing content, just routing it).
- Pure mechanical skills (vault-writer, seen-tracker, etc.).

## The framing fragment

When a calling skill produces research / synthesis / communication output, the framing fragment applies these rules:

### 1. The lens

Every claim, finding, recommendation, or summary should connect to one of:

- **SR 11-7 successor + the genAI carve-out** (per [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]] — Copilot governed under TPRM not MRM until the RFI lands)
- **FFIEC IT Handbook** — Operations, Development & Acquisition, Wholesale Payment Systems chapters
- **OCC supervisory expectations** — semiannual risk perspective + bulletins
- **PCI-DSS 4.0** — when card-data paths are touched
- **SOX ITGC** — change management evidence at PR level; the keystroke-level limit is acknowledged ([[audit-per-suggestion-traceability]])
- **NYDFS Part 500** — for NY-regulated entities
- **NIST AI RMF + Generative AI Profile (NIST AI 600-1)** — voluntary but operationally the right anchor for AI governance
- **GLBA / privacy law** — when customer data is in play

If a finding doesn't tie to any of these, tag it `#general` and surface the disconnect — sometimes a finding genuinely doesn't fit the lens and that should be visible.

### 2. The voice rules

- **No vendor marketing language.** "Game-changer" / "revolutionary" / "AI-powered" — all banned in output produced by skills using this framer.
- **No hedge words masking ignorance.** Don't write "may potentially affect" when you mean "we don't know yet." If you don't know, say "uncertain — would need {specific research} to determine."
- **Acknowledge limits explicitly.** If the framework citation doesn't actually cover a finding, name the gap.
- **Quantify when possible.** "10% surcharge", "7-day SLA", "47/100 baseline" — specific numbers beat vague qualifiers.

### 3. The audience-tier voice (when producing tiered output)

| Tier | Length | Voice | Cite |
|------|--------|-------|------|
| Exec | ≤250 words | declarative, dense | risk + decision-needed |
| Eng lead | 400-600 words | explanatory, tight | what-team-needs-to-do |
| IC | 300-500 words | friendly, practical | what-to-do + what-not-to-do |

### 4. The Copilot-specific posture (current state)

When the output touches Copilot or AI tools:

- US data residency on (per [[data-residency-regions]])
- Public code filter required at org level (per [[ip-indemnity]])
- 10% AI-credits surcharge baked into cost expectations (per [[data-residency-surcharge]])
- TPRM governance (not MRM) per [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]]
- Audit log via S3 + KMS (per [[audit-log-export-format]])
- Per-suggestion audit trail does NOT exist (per [[audit-per-suggestion-traceability]])
- AGENTS.md is the repo-level governance surface (per [[code-review-reads-agents-md]])

### 5. The "don't do this" anti-pattern list

When framing, avoid:

- **Treating AI tools as black boxes.** Cite specific facts, not generic "AI is risky."
- **Conflating MRM with AI governance.** The OCC carve-out matters — don't roll Copilot up to SR 11-7 just because it's an AI system.
- **Promising audit evidence that doesn't exist.** Per-suggestion tracking does NOT exist; PR-level evidence is the boundary; saying otherwise damages credibility.
- **Adopting vendor framing uncritically.** Vendor marketing language signals lack of independent review.

## How calling skills reference this

Calling skills include in their SKILL.md a line like:

```
This skill applies framing per [`regulated-finance-framer`](../regulated-finance-framer/SKILL.md). When the framer's rules update, this skill's output framing updates accordingly without per-skill changes.
```

Or load it programmatically when the skill is invoked (read the fragment, prepend / inject into prompt context).

## Maintenance

This is the **single edit point** when the org's framing evolves. Triggers for editing:

- New federal banking regulation publishes (especially the forthcoming genAI RFI).
- The org's internal control catalog is updated.
- A new compliance framework (e.g., ISO 42001 certification) becomes the org's anchor.
- A Copilot fact in `vault/facts/copilot/` materially changes (e.g., data residency adds a region).
- A canonical objection in `objection-response-library/canonical-objections.md` is added / superseded.

When this skill is edited, run a sweep of the downstream skills that include it to confirm their output still aligns. Alternatively, the framer can publish a version string (`framer_version: 2026-06-20`) and downstream skills can declare which version they target.

## Acceptance test (for step 35 done-criteria)

The 5 framing components are documented (lens / voice / tier / Copilot posture / anti-patterns). Existing skills (especially the Category 1 researchers from steps 11-12 and 28-31) could now reference this skill rather than duplicate the framing logic. Live refactor of existing skills to use this fragment is deferred — backwards compatibility is preserved by them continuing to bake in the framing inline; this skill is the forward template.
