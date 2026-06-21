---
name: copilot-deep-dive
description: On-demand Category 1 researcher focused on GitHub Copilot — enterprise features, models, admin controls, data handling, content exclusions, IP indemnity, agentic features, AGENTS.md governance, Copilot CLI/Chat/Workspace, and Copilot in regulated-environment contexts. Enforces the Obsidian-first contract: vault-querier first against vault/facts/copilot/ and vault/research/copilot/, then web research only for confirmed gaps. Findings land at vault/research/copilot/YYYY-MM-DD-{slug}.md; verified load-bearing claims get staged to _inbox/ for memory-curator to promote to vault/facts/copilot/.
---

# copilot-deep-dive

On-demand deep research on GitHub Copilot, framed for a regulated organization. The canonical Use Case 2 example: when the user (or a stakeholder via the user) asks a Copilot question, this skill answers it Obsidian-first, with verified citations, and contributes back to the vault.

## When to use

- A Copilot question that goes beyond [`copilot-faq-answerer`](../copilot-faq-answerer/SKILL.md)'s 7 canonical answers.
- A net-new question that should become a canonical answer once researched.
- A stakeholder request requires a documented research note (with citations) — e.g., legal asking about IP indemnity edge cases, audit asking about logging granularity, security asking about new agentic feature exposure.

## When NOT to use

- Questions covered by canonical FAQ — answer from there.
- GitHub platform questions not specifically about Copilot — use [`github-platform-watch`](../github-platform-watch/SKILL.md).
- GHAS-specific questions (CodeQL, Dependabot, secret scanning) — use a GHAS skill if one exists; otherwise this skill is OK as a fallback.
- Internal Copilot rollout strategy / metrics — those are `copilot-rollout-playbook` / `copilot-metrics-analyzer` (planned skills).

## Obsidian-first workflow (mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the question's key terms across `vault/facts/copilot/**`, `vault/research/copilot/**`, `vault/insights/**`, `vault/digests/**` (last 90 days).
   - Backlink check on `[[copilot]]` and the question's entities.
2. **Triage findings**:
   - If the vault answers the question fully → return the existing answer with source citations (vault path + original source URLs from the fact's frontmatter). No new write.
   - If partial → identify the **gap**. Web research targets only the gap.
   - If empty → full web research.
3. **Web research** (only on confirmed gaps):
   - Use `source-fetcher` (with `prompt-injection-guard`) on tier-1 sources: GitHub docs, the GitHub blog changelog, official Anthropic / Microsoft / OpenAI announcements relevant to model selection.
   - Extract claims via `claim-extractor`.
4. **Verify load-bearing claims** via `verify-claim` (3-vote refute):
   - Any claim destined for `vault/facts/copilot/` must pass verification.
   - Claims from tier-1 vendor primary sources are exempt (the vendor IS the authority).
   - Claims from secondary sources (analyst blogs, peer-bank posts) get the full 3-vote treatment.
5. **Write the research note** via `vault-writer.write_research`:
   - Path: `vault/research/copilot/YYYY-MM-DD-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: copilot`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: TL;DR + Findings (with quoted anchors) + Sources (with credibility-tier badges).
6. **Stage promotable claims** to `_inbox/copilot-deep-dive/`:
   - Any verified fact-typed claim → `_inbox/copilot-deep-dive/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/copilot/{predicate}.md`.
   - `memory-curator` decides on its next sweep.

## Compliance-relevant framing

Every research note's TL;DR and Findings include a "Why this matters for a regulated org" line tying the finding to:
- SR 11-7 model risk / model governance
- FFIEC IT Handbook
- OCC supervisory letters
- SOX ITGC
- NYDFS 500
- GDPR / data residency

If a finding has no plausible compliance lens, surface it anyway but tag it `#general` rather than `#sdlc`/`#regulator`.

## Output

Research note at `vault/research/copilot/YYYY-MM-DD-{slug}.md`. If the question reveals a canonical-FAQ gap, the body should include a "Proposed canonical answer" section formatted as a `canonical-answers.md` entry, so the user can paste-add it.

## Composes with

- `vault-querier` (Obsidian-first)
- `source-fetcher` + `prompt-injection-guard` (web)
- `claim-extractor` + `verify-claim` (load-bearing verification)
- `vault-writer.write_research` (output)
- `_inbox/copilot-deep-dive/` + `memory-curator` (fact promotion)
- `copilot-faq-answerer` (consumer of promoted facts via `override_facts_predicate`)
- [`email-sender`](../email-sender/SKILL.md) — after `vault-writer.write_research()` succeeds, invoke `prompt_then_send(path)` to ask the user whether to distribute the note via Gmail.

## Acceptance test (for step 11 done-criteria)

One live end-to-end research run produces:
- A research note at `vault/research/copilot/YYYY-MM-DD-{slug}.md` with 5-section structure (TL;DR / Question / Findings / Sources / Proposed-canonical-if-applicable).
- At least one load-bearing claim passed through `verify-claim` (3-Agent refute).
- At least one promotable claim staged to `_inbox/copilot-deep-dive/`.
- All web sources cited with tier badge + accessed date.
- Vault-querier was called first; result documented (gap analysis).
