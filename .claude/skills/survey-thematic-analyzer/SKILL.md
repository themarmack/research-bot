---
name: survey-thematic-analyzer
description: Cluster open-text survey responses into themes with representative quotes. Takes raw responses (developer experience surveys, Copilot rollout retros, post-incident surveys) and produces a structured analysis with theme labels, response counts per theme, 2-3 representative quotes per theme, and outlier responses worth surfacing individually. Use when analyzing developer surveys or Copilot rollout feedback.
---

# survey-thematic-analyzer

The qualitative-analysis skill. Closed-form survey data is easy to analyze; open-text responses are where the real signal lives but the analysis cost has historically been prohibitive.

## When to use

- Developer experience survey (annual / pulse).
- Copilot rollout retro responses.
- Post-incident "what would have helped" survey.
- Conference attendee feedback.

## When NOT to use

- Closed-form (yes/no, Likert) responses → standard quantitative tools.
- Interviews → different methodology; use a transcript-specific tool.

## Workflow

1. **Read responses**: structured list of `{respondent_id, role, response_text}`.
2. **Cluster by theme** using NLP grouping or LLM-driven cluster identification.
3. **For each theme**: label, count, 2-3 verbatim representative quotes (with respondent context).
4. **Surface outliers**: responses that don't cluster — sometimes the most informative.
5. **Cross-reference vault**: do any themes connect to known objections, decisions, or open questions?

## Output structure

```markdown
# Survey Analysis — {survey name}

## Sample
- N responses
- Roles distribution: ...

## Themes
### Theme 1: {label} (N responses, X%)
- Representative quotes:
  - "{quote}" — {role}
- Vault connection: [[wikilink if applicable]]

### Outliers worth surfacing
- {quote} — {why it's worth noting}
```

Lands at `vault/insights/YYYY-MM-DD-survey-analysis-{slug}.md`.

## Acceptance test

SKILL.md describes the workflow. Live exercise deferred to first actual survey input.
