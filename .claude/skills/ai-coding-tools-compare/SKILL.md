---
name: ai-coding-tools-compare
description: Produce a side-by-side comparison of AI coding tools — GitHub Copilot vs Cursor vs Windsurf vs Cody vs Tabnine vs JetBrains AI vs Amazon Q Developer vs emerging entrants — against the org's enterprise rubric. Rubric axes — auth (SSO/SAML/SCIM), data flow (residency, content exclusion, training-data policy), IP indemnity, on-prem / single-tenant options, admin telemetry, FedRAMP/SOC2/ISO certifications, model routing transparency, audit log access. Use when the user asks to compare AI coding tools (Copilot vs Cursor vs Windsurf vs Cody vs others) against the org's enterprise rubric, or asks "should we switch to X?" — during periodic re-evaluation, vendor selection for a specific use case, or before responding to leadership. For an in-depth single-tool study (not a comparison) use copilot-deep-dive.
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

## Workflow (Obsidian-first, mandatory)

1. **Query the vault first** via `vault-querier`:
   - Full-text search the tools' names across `vault/research/ai-coding-tools/**` (prior comparisons), `vault/facts/copilot/**` (the org's known Copilot baseline), `vault/research/vendor/**` (per-vendor evaluations), `vault/research/frontier-model/**` (model-routing facts), and recent `vault/digests/**` (last 90 days — `quarterly-ai-coding-landscape` output lands there).
   - Backlink check on each tool's entity (e.g. `[[cursor]]`, `[[copilot]]`).
2. **Triage findings**:
   - If a current comparison already covers the asked tools and axes → return it with source citations (vault path + original source URLs). No new write.
   - If partial → identify the **gap** (which tools / axes are missing or stale). Web research targets only those cells.
   - If empty → full comparison.
   - A **gap** means the vault has no note ≤90 days old answering the question.
3. **Identify tools to compare** (default: Copilot + top alternatives; subset for use-case-specific comparison).
4. **For each tool, fill the rubric** — vault facts first; for confirmed gaps, use `source-fetcher` (with `prompt-injection-guard`) on primary sources (vendor docs, official changelog) per axis, extracting claims via `claim-extractor`.
5. **Verify load-bearing claims** via `verify-claim` (3-vote refute) — a vendor's claims about its own product are tier-1; competitive claims and third-party characterizations get the full 3-vote treatment before affecting a score.
6. **For each axis, score**: PASS / PARTIAL / FAIL against the org's bar.
7. **Identify gaps**: where would switching help vs hurt for specific use cases.
8. **Recommendation** with explicit time-bound — "this comparison valid through {date}; re-evaluate at {trigger}."
9. **Write the comparison note** via `digest-writer` (which delegates the file write to `vault-writer.write_research`):
   - Path: `vault/research/ai-coding-tools/YYYY-MM-DD-comparison-{slug}.md`
   - Frontmatter per `research.yml` schema: `topic: ai-coding-tools`, `question`, `sources`, `findings_count`, `verified_claims`.
   - Body: the output structure below, with credibility-tier badges on every source.
10. **Stage promotable claims** to `_inbox/ai-coding-tools-compare/`:
    - Any verified fact-typed claim (e.g. a vendor's certification or training-data policy) → `_inbox/ai-coding-tools-compare/{timestamp}-{slug}.md` with `suggested_surface: facts` and `suggested_path: facts/{vendor-entity}/{predicate}.md`.
    - `memory-curator` decides on its next sweep.

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
- `vendor-security-eval` — deeper single-vendor evaluation.
- `frontier-model-watch` — model-side, not tool-side, dimension.
- `stakeholder-update-writer` — exec-tier output naturally pulls from this.

## Acceptance test (for step 28 done-criteria)

One live comparison exercise covering Copilot + at least 3 alternatives across all 14 rubric axes. Verdict cited per axis per tool.
