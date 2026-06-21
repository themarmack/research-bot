---
name: ai-tooling-data-flow-reviewer
description: Given a proposed AI tool integration (Copilot Chat knowledge base, Cursor on a regulated repo, an internal LLM gateway routing to an external provider, a Copilot agentic action that touches a system of record), map the complete data flow and flag every place regulated data could leave the org's boundary. Cross-references vault facts (data residency, content exclusion, audit log paths) to validate the org's posture matches the integration's actual flows. Produces a data-flow diagram (ASCII), a per-hop classification table, and a findings list. Use before greenlighting any new AI tool integration touching production systems or regulated data.
---

# ai-tooling-data-flow-reviewer

The skill that answers "if we wire AI tool X into system Y, where does our regulated data end up?" Specialized for AI integrations because the data flow is non-obvious (inference happens off-org-network) and the controls are different (content exclusion + residency vs traditional network egress).

## When to use

- New AI tool integration proposed (Copilot knowledge base, internal LLM gateway, Cursor on regulated repo, MCP server enabling agentic actions).
- Existing AI integration adds a new data source.
- AI tool vendor announces a new data-handling feature (e.g., residency change, new context-loading path).
- Pre-CAB review for any AI-related change.

## When NOT to use

- Generic data-flow review without AI angle → `secure-design-reviewer`.
- AI tool selection / vendor evaluation → `vendor-security-eval` (planned step 30).
- Specific Copilot policy question → `copilot-faq-answerer`.

## Workflow

1. **Identify the integration scope**: components, source data, destination.
2. **Build the data-flow diagram** (ASCII): every hop from data source through AI tool to consumer.
3. **Per-hop classification**: at each hop, what data classification crosses? Does it cross a trust boundary? What's the control at that hop?
4. **Cross-reference vault facts**: check Copilot data-residency posture, content exclusion config, audit log path, IP indemnity scope — does the org's existing posture cover this flow's claims?
5. **Find the gaps**: hops where the org's posture doesn't cover the flow.
6. **Produce a structured output**.

## Output structure

```markdown
# AI Tool Data Flow Review — {integration name}

## Integration summary
{1-paragraph}

## Data-flow diagram
[ASCII showing components + arrows + trust boundaries]

## Per-hop classification table
| Hop | From | To | Data class | Trust boundary crossed? | Control at hop | Gap? |

## Findings
- [per gap: severity, evidence, remediation]

## Cross-reference: vault facts
[which existing facts cover which hops]

## Recommendation
{advance / advance-with-remediation / reject}
```

Lands at `vault/research/sdlc-best-practice/YYYY-MM-DD-ai-dataflow-{integration-slug}.md`.

## Composes with

- [`threat-model-helper`](../threat-model-helper/SKILL.md) — natural pair (threat model = what can go wrong; this skill = where the data goes).
- [`secure-design-reviewer`](../secure-design-reviewer/SKILL.md) — AI tool exposure category.
- `vault-querier` — load Copilot facts ([[data-residency-regions]], [[data-residency-surcharge]], etc.).

## Acceptance test (for step 27 done-criteria)

One data-flow review exercise. The Payments KB threat-modeled in step 24 is the natural fixture — produce its data-flow review.
