---
name: copilot-rollout-playbook
description: Generate a tailored Copilot expansion plan for a target team or BU. Takes a team description (size, language stack, current Copilot adoption state, business priorities, regulatory exposure) and produces a 5-phase rollout — prerequisites, training, pilot, expansion, steady-state. Pulls org-specific constants (data residency, content exclusion, public code filter, IP indemnity terms) from `vault/facts/copilot/` so the plan reflects the current configuration, not generic GitHub guidance. Use when a team lead asks "how do we roll Copilot out to my team?" or when planning an org-wide expansion wave.
---

# copilot-rollout-playbook

A Category 3 ops tool. The user runs this against a target team and gets a tailored, sourced rollout plan ready to share with the team lead. Composes with `copilot-faq-answerer` for the policy answers stakeholders will ask during rollout, and with `objection-response-library` for the resistance points.

## When to use

- A team lead requests Copilot rollout for their team.
- Planning an org-wide expansion wave; need a template plan customized per BU.
- Refreshing a stalled rollout — figure out which of the 5 phases the team is actually in.

## When NOT to use

- General "should we adopt Copilot" question — that's a decision, not a rollout.
- Specific config debugging (workflow won't trigger, content exclusion not enforcing) — those are `actions-workflow-hardener` / `ghas-config-reviewer`.
- Cost modeling for the rollout — that's `copilot-metrics-analyzer`.

## Required inputs

- **Team size** (devs).
- **Language stack** — affects what models route per-feature and what training emphasizes.
- **Current Copilot adoption state** — none / partial / org-wide.
- **Business priorities** — feature velocity / quality / cost reduction / regulatory readiness.
- **Regulatory exposure** — which regulated-data flows touch this team's repos (e.g., payments → PCI-DSS, customer data → privacy laws).

## Bank-specific constants (loaded from vault)

The skill loads these from `vault/facts/copilot/` so plans reflect the org's current posture, not GitHub generic:

- **[[data-residency-regions]]** — org uses US data residency
- **[[data-residency-surcharge]]** — 10% AI-credits surcharge baked into cost expectations
- **[[fedramp-moderate-authorization]]** — supports the SOC 2 / ISO conversation
- **[[audit-log-export-format]]** — S3 + KMS path replaces CSV downloads
- **[[code-review-reads-agents-md]]** — `AGENTS.md` is the repo-level policy surface
- **[[usage-metrics-ai-credits-per-user]]** — `ai_credits_used` API field for chargeback

## 5-phase plan structure

### Phase 1 — Prerequisites (1-2 weeks)
- TPRM file for Copilot updated and current.
- Team's repos are GHAS-onboarded baseline (per `ghas-config-reviewer` baseline).
- Content exclusion patterns reviewed and adjusted for this team's data-sensitivity profile.
- Public code filter confirmed on at org level (required for IP indemnity).
- Allocated seats budget includes the 10% data-residency surcharge buffer.

### Phase 2 — Training (concurrent with Phase 1)
- Mandatory training module for the team (1 hour): data handling, IP indemnity, content exclusion, what NOT to paste into Chat, exception process.
- Per-language additions (Java / TypeScript / Python specifics) where the model defaults differ.
- "What Copilot is NOT" expectations: not a fact source, hallucinated API call-outs, the developer remains the author for SOX evidence purposes.

### Phase 3 — Pilot (4-6 weeks)
- 20-30% of the team enrolled.
- Success criteria (defined per-team but typically): >70% weekly active users, acceptance rate within ±10 of org baseline, zero secret-scanning push-protection bypasses by Copilot-generated content.
- Weekly check-in on pilot metrics via the planned `copilot-metrics-analyzer` skill output.
- Exception process tested: at least one exception request submitted via [[exception-request-drafter]] (planned skill) and resolved through the proper governance path.

### Phase 4 — Expansion (4-8 weeks)
- Remaining team enrolled in cohorts (no big-bang).
- `AGENTS.md` added to the team's primary repos with team-specific review priorities.
- Team-specific guidance updates in CONTRIBUTING.md.
- Manager check-in: any team member raising quality or skill-atrophy concerns (see [[objection-response-library]] skeptical-dev entries) gets a 1:1 conversation.

### Phase 5 — Steady state (ongoing)
- Monthly metrics review via `copilot-metrics-analyzer` for cost-attribution + outlier detection.
- Quarterly check-in on `AGENTS.md` effectiveness — is Copilot review behavior matching what we asked for?
- Annual rollout refresh — re-do Phase 2 training as canonical answers in `copilot-faq-answerer` evolve.
- Exception sunset: any rollout exceptions from Phase 3 reviewed annually for whether they're still needed.

## Output

A single markdown file the user shares with the team lead. Sections:

1. **Context** — team description, current state.
2. **Bank-specific constants applied** — list of facts loaded from vault.
3. **5-phase plan** — concrete actions per phase with target dates.
4. **Success metrics** — per-phase.
5. **Open questions** — anything that needs the team lead's input.
6. **Sources** — facts + decisions referenced.

Land at `vault/research/copilot/YYYY-MM-DD-rollout-{team-slug}.md` (research-style; user can also copy into a team doc).

## Composes with

- `vault-querier` — load facts.
- `copilot-faq-answerer` — embeds policy answers inline.
- `objection-response-library` — pre-empts known resistance.
- `copilot-metrics-analyzer` — Phase 3 and 5 cycles call this.

## Acceptance test (for step 16 done-criteria)

Generate one rollout plan for a hypothetical team (5-50 devs, mixed language stack, current adoption ≤30%, regulatory exposure stated). Confirm the output has all 6 sections, all 5 phases with concrete actions, and references at least 4 facts from `vault/facts/copilot/`.
