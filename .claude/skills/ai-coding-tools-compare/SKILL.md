---
name: ai-coding-tools-compare
description: Produce a side-by-side comparison of AI coding tools — GitHub Copilot vs Cursor vs Windsurf vs Cody vs Tabnine vs JetBrains AI vs Amazon Q Developer vs emerging entrants — against the org's enterprise rubric. Rubric axes — auth (SSO/SAML/SCIM), data flow (residency, content exclusion, training-data policy), IP indemnity, on-prem / single-tenant options, admin telemetry, FedRAMP/SOC2/ISO certifications, model routing transparency, audit log access. Use during periodic re-evaluation (currently scheduled annual, more often if regulator activity surfaces), vendor selection for a specific use case, or before responding to "should we switch to X?" questions from leadership.
---

# ai-coding-tools-compare

The "should we be using X instead of Copilot?" answer with structure. Most comparisons in the wild are vendor-marketing pageant scoring; this one applies the org's actual procurement / TPRM / compliance rubric.

## When to use

- Periodic re-evaluation cadence (currently annual; revisit if regulator activity, vendor change, or material capability gap forces it).
- Vendor selection for a specific use case (e.g., agentic refactoring of legacy COBOL — does Cursor's UX matter more than Copilot's posture there?).
- Leadership question: "I saw a demo of Cursor — should we switch?"
- Annual Copilot TPRM-file review needs a comparative posture summary.

## When NOT to use

- Specific Copilot questions → `copilot-faq-answerer`.
- Frontier-model comparison (which model is best) → `frontier-model-watch`.
- Tool selection for non-coding AI (chatbot platforms, knowledge management) → out of scope.

## Enterprise rubric (the comparison axes)

| Axis | What we check |
|------|---------------|
| **Auth** | SSO via SAML, SCIM provisioning, EMU support, IP allow-list |
| **Data residency** | US / EU regions available + enforced at tenant level |
| **Training-data policy** | Do customer prompts train models? Default + contractual options |
| **Content exclusion** | Org-level + repo-level + path-level patterns |
| **IP indemnity** | Scope of indemnity + conditions (e.g., filter requirement) |
| **On-prem / single-tenant** | Available for regulated buyers? At what tier? |
| **Admin telemetry** | Active users, acceptance rate, cost attribution per user/team |
| **Certifications** | FedRAMP Moderate, SOC 2 Type 2, ISO 27001, ISO 42001 |
| **Model routing transparency** | Which model is invoked for which surface? Documented? |
| **Audit log access** | Admin actions logged? Streamed to SIEM? Retention? |
| **Pricing model** | Per-seat / consumption / surcharge for residency? |
| **Knowledge-base / RAG capability** | Native? Via integration? Auditable? |
| **Agentic features** | Multi-step actions? With what guardrails? |
| **Ecosystem coverage** | IDEs supported (VS Code, JetBrains, Vim/Neovim, CLI) |

## Workflow

1. **Identify tools to compare** (default: Copilot + top alternatives; subset for use-case-specific comparison).
2. **For each tool, fill the rubric**: cite primary sources (vendor docs, official changelog) for each axis.
3. **For each axis, score**: PASS / PARTIAL / FAIL against the org's bar.
4. **Cross-reference vault facts** for Copilot baseline (the org's known position).
5. **Identify gaps**: where would switching help vs hurt for specific use cases.
6. **Recommendation** with explicit time-bound — "this comparison valid through {date}; re-evaluate at {trigger}."

## Output structure

```markdown
# AI Coding Tools Comparison — {date}

## Tools in scope
[list]

## Rubric scoring (PASS / PARTIAL / FAIL per axis per tool)
[matrix]

## Per-tool summary
### {tool name}
- Strengths vs Copilot
- Gaps vs org rubric
- Where it might fit (specific use case)

## Recommendation
- Headline: stay / switch / use alongside
- Valid through: {date / trigger}

## Sources
{vendor docs + vault facts}
```

Lands at `vault/research/ai-coding-tools/YYYY-MM-DD-comparison-{slug}.md`.

## Composes with

- `vault-querier` — load Copilot baseline facts.
- `vendor-security-eval` (planned step 30) — deeper single-vendor evaluation.
- `frontier-model-watch` — model-side, not tool-side, dimension.
- `stakeholder-update-writer` — exec-tier output naturally pulls from this.

## Acceptance test (for step 28 done-criteria)

One live comparison exercise covering Copilot + at least 3 alternatives across all 14 rubric axes. Verdict cited per axis per tool.
