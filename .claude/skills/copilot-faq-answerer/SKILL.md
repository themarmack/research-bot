---
name: copilot-faq-answerer
description: Answer the recurring GitHub Copilot questions a regulated-environment GitHub admin fields daily (data handling, IP indemnity, content exclusions, audit logs, model selection, public code filter, knowledge bases, AGENTS.md governance). Reads canonical answers from `./canonical-answers.md` in this skill folder, applies them with the compliance-relevant lens, and cites GitHub's authoritative source. Also checks the Obsidian vault (`facts/copilot/*`) for any more recent fact that should override the canonical answer. Use whenever the user (or a stakeholder via the user) asks a Copilot policy / controls question.
---

# copilot-faq-answerer

The day-job lever. The user fields the same handful of Copilot questions across stakeholders, legal, security, audit, and engineering. This skill makes the response consistent, sourced, and compliance-framed — and updates itself as `vault/facts/copilot/` accumulates new fact notes.

## When to use

- Someone asks the user a Copilot question fitting one of the canonical categories below.
- A stakeholder update needs a one-paragraph answer to a recurring Copilot concern.
- The user is drafting a policy document and wants a single source of truth for the org's posture.

## When NOT to use

- Truly novel Copilot questions with no canonical answer — those go through `copilot-deep-dive` (step 11), which does fresh research and lands in `vault/research/copilot/`.
- Questions about a specific repo's config — that's `ghas-config-reviewer` territory.
- Questions about Copilot rollout strategy / metrics — that's `copilot-rollout-playbook` / `copilot-metrics-analyzer`.

## Answer-resolution order

For each question:

1. **Obsidian-first check**: query `vault/facts/copilot/` (via `vault-querier`) for any fact with a matching `predicate` more recent than the canonical answer's `last_verified` date. If found, **prefer the vault fact** and note that the canonical answer is being overridden.
2. **Canonical answer**: look up `canonical-answers.md` in this skill folder.
3. **Apply the regulated-org lens**: every answer ends with a 1-2 sentence "What this means for a regulated org" line that ties the technical answer to control objectives (SR 11-7 model risk, FFIEC, OCC, NYDFS 500, SOX ITGC).
4. **Cite the source**: every answer includes a link to GitHub's authoritative doc and the date the canonical answer was last verified.

If no canonical answer covers the question, **stop and report**: surface the gap to the user, suggest invoking `copilot-deep-dive` to research it, and offer to add the new question + answer to `canonical-answers.md` once researched.

## Output shape

Plain-language answer suitable for forwarding to a stakeholder:

```
**Question**: <restated>

**Answer**: <canonical answer, 2-4 sentences, vendor language minimized>

**What this means for a regulated organization**: <1-2 sentence framing>

**Source**: [GitHub Docs link]({url}) (canonical answer last verified {date}; checked against vault facts on {today})
```

For internal use (not stakeholder-facing), optionally add a "Caveats" section noting nuance (e.g., "this applies to Copilot Business; Enterprise has additional controls").

## Maintaining `canonical-answers.md`

The file in this skill folder is a structured list of Q&A entries, each with:

```yaml
- id: short-kebab-case
  question_patterns:
    - "data handling"
    - "where does my code go"
    - "is my code used for training"
  category: data-handling | ip-indemnity | content-exclusion | audit | model-selection | public-code-filter | custom-instructions | knowledge-bases | agents-md
  canonical_answer: |
    <plain-language answer>
  compliance_lens: |
    <1-2 sentence regulated-org framing>
  source_url: https://docs.github.com/...
  last_verified: 2026-06-20
  override_facts_predicate: data-handling   # vault-querier looks for facts/copilot/{this}.md
```

Add new entries as new questions appear. The skill should propose an addition (drafted in this format) when it has to defer to `copilot-deep-dive` for an unanswered question — the user accepts or refines.

## Composes with

- `vault-querier` — Obsidian-first check for newer facts.
- `vault-writer.write_fact` — when a deep-dive research result should become a canonical fact.
- `copilot-deep-dive` (step 11) — fallback for novel questions.

## Acceptance test (for step 10 done-criteria)

Five canonical answers shipped in `canonical-answers.md` covering at minimum:
1. Data handling — where does code go, is it used for training?
2. IP indemnity — what does GitHub indemnify against?
3. Content exclusions — repo-level and org-level patterns.
4. Audit logs — what activity is logged, where does it land?
5. Public code filter — when is it on, what does it do?

Each entry has a non-empty `canonical_answer`, `compliance_lens`, `source_url`, `last_verified`, and `override_facts_predicate`.
