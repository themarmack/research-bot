---
name: biweekly-codeql-community-pulse
description: Biweekly scheduled agent. Surveys the github/codeql repo + community packs for new queries, modified queries, and new packs published in the past 14 days. Relevance-scores each against the org's stack (using daily-cve-digest's stack.yml as the source of in-scope ecosystems) — surface only ecosystem-matching results. Output at vault/digests/biweekly/YYYY-MM-DD-codeql-community-pulse.md. Feeds the codeql-pattern-finder skill — every relevant new community query is a candidate for the org's adoption queue.
---

# biweekly-codeql-community-pulse

The CodeQL upstream watch. Every two weeks, surfaces new community work that's worth evaluating for the org's CodeQL pack rollout. Composes with `codeql-pattern-finder` (which evaluates specific queries for adoption) and `codeql-onboarding-helper` (which deploys adopted queries).

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: biweekly-codeql-community-pulse
cadence: biweekly
schedule_hint: "every other Tuesday 08:00 local"
source_filter:
  custom: codeql-community
  sources:
    - https://github.com/github/codeql/commits/main.atom
    - https://github.com/codeql-packs  # community packs org
  stack_match_config: ../daily-cve-digest/stack.yml  # filter to in-scope ecosystems only
  max_items: 30
verify_loadbearing: false  # community queries are evaluated, not "verified" as facts
curate_findings: false      # adoption decisions go through codeql-pattern-finder, not memory-curator
digest_template_overrides:
  template: codeql-community-pulse
  why_you_care_extra: |
    Per item:
    1. Which in-scope ecosystem does this target?
    2. Is the query syntactic (cheap, easy to deploy) or taint-tracking (expensive, needs tuning)?
    3. What's the closest existing match in the org's current suite, and is this duplicative?
    4. Estimated effort to evaluate-for-adoption (S / M / L).
```

## Sections per item

For each surfaced query:

1. **Title** + repo path + author.
2. **Targets**: language + ecosystem from `stack.yml`.
3. **Type**: syntactic / taint-tracking / metadata-extension.
4. **Existing-coverage check**: closest match in the org's current `security-extended` suite.
5. **Estimated evaluation effort**: S (≤1 day) / M (1-3 days) / L (1+ weeks).
6. **Adoption recommendation**:
   - **EVALUATE**: looks promising, queue for `codeql-pattern-finder` evaluation
   - **WAIT**: experimental / marked as preview / low community usage
   - **SKIP**: duplicative or out-of-scope

## Output structure

```markdown
# CodeQL Community Pulse — {period}

## At a glance
- {N new queries / packs / modifications in scope}
- {X recommended EVALUATE; Y WAIT; Z SKIP}

## Recommended EVALUATE

### {query title}
[per-item fields above]

## Recommended WAIT
- one-liners

## Recommended SKIP
- one-liners

## Cross-references to vault
- New queries queued for [[codeql-pattern-finder]] evaluation: {list}
- Codeql-onboarding plans potentially affected (pattern adoption): {list}
```

Lands at `vault/digests/biweekly/YYYY-MM-DD-codeql-community-pulse.md`.

## Composes with

Standard Phase-1 foundation. Also:
- [`codeql-pattern-finder`](../codeql-pattern-finder/SKILL.md) — every EVALUATE item is a candidate.
- [`codeql-onboarding-helper`](../codeql-onboarding-helper/SKILL.md) — adopted queries flow to the deployment plans.
- `daily-cve-digest/stack.yml` — the ecosystem-filter source.

## Acceptance test (for step 22 done-criteria)

SKILL.md covers the relevance-scoring rubric (in-scope ecosystem + existing-coverage check + evaluation-effort estimate) and explicit EVALUATE/WAIT/SKIP categorization. Live first-run exercise deferred to first biweekly cron firing.
