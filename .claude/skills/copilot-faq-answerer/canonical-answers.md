# Canonical Copilot answers

Curated answers to the recurring Copilot questions a GitHub admin at a regulated organization fields. Each entry is the canonical baseline; `vault/facts/copilot/{override_facts_predicate}.md` overrides it if more recent.

**Last bulk-verified**: 2026-06-20. Entries with `last_verified` older than 90 days should be re-checked against GitHub Docs.

---

## data-handling

```yaml
id: data-handling
question_patterns:
  - "where does my code go"
  - "is my code used for training"
  - "data handling"
  - "does Copilot send my code to OpenAI"
  - "data residency"
category: data-handling
canonical_answer: |
  GitHub Copilot Business and Enterprise do **not** use customer prompts or code
  suggestions to train the underlying models. Prompts (your code + cursor context) are
  sent to GitHub's inference infrastructure for the duration of generating a suggestion
  and are not retained. Logs that GitHub retains for security and abuse prevention exclude
  prompt content for Business / Enterprise.
compliance_lens: |
  This matters for SR 11-7 model-risk reviews: customer code is not part of the training
  corpus, so the model's behavior is deterministic with respect to your data and risk
  reviews can treat the model as a fixed, vendor-supplied artifact. Confirm contractual
  language matches the docs at audit time.
source_url: https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/setting-policies-for-copilot-in-your-organization/managing-policies-for-copilot-in-your-organization
last_verified: 2026-06-20
override_facts_predicate: data-handling
```

---

## ip-indemnity

```yaml
id: ip-indemnity
question_patterns:
  - "IP indemnity"
  - "what does GitHub indemnify"
  - "copyright protection"
  - "what if Copilot produces copyrighted code"
category: ip-indemnity
canonical_answer: |
  GitHub provides an IP indemnity for paying Copilot Business and Enterprise customers
  covering claims that a Copilot suggestion infringes a third-party's intellectual
  property — provided the customer has the **duplicate detection / public code filter
  enabled** at the org level. Indemnity does not cover suggestions accepted with the
  filter off, nor does it cover code the customer modifies after acceptance.
compliance_lens: |
  This is the single contractual lever that legal and procurement care about most. The
  filter-must-be-on condition means the org's Copilot policy must enforce the filter at
  the org level (not leave it to individual repos). Confirm the indemnity wording with
  legal before publishing internal guidance.
source_url: https://docs.github.com/en/copilot/responsible-use-of-github-copilot-features/responsible-use-of-github-copilot-business
last_verified: 2026-06-20
override_facts_predicate: ip-indemnity
```

---

## content-exclusion

```yaml
id: content-exclusion
question_patterns:
  - "content exclusion"
  - "exclude repo from Copilot"
  - "keep Copilot from seeing my code"
  - "exclude paths from Copilot"
category: content-exclusion
canonical_answer: |
  Content exclusion lets admins specify paths Copilot should not see (used as context) or
  suggest changes to. Configure org-level patterns in the Copilot admin settings; repo-
  level patterns live in `.github/copilot/excludes.yml` (or org-level overrides). As of
  Q2 2026, content exclusion supports glob patterns at the **repo** level, not only the
  org level — previously this was org-only.
compliance_lens: |
  Use content exclusion for any path containing customer data, regulated content, or
  third-party-licensed code with non-compatible terms. Org-level patterns should cover
  catch-all categories (`**/secrets/**`, `**/customer-data/**`); repo-level patterns
  handle service-specific cases. Audit that exclusions are actually enforced by sampling
  Copilot completions in excluded repos at the next GHAS review.
source_url: https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/setting-policies-for-copilot-in-your-organization/excluding-content-from-github-copilot
last_verified: 2026-06-20
override_facts_predicate: content-exclusion
```

---

## audit-logs

```yaml
id: audit-logs
question_patterns:
  - "audit log"
  - "what does Copilot log"
  - "how do we audit Copilot usage"
  - "Copilot audit log retention"
  - "SIEM integration"
category: audit
canonical_answer: |
  Copilot Enterprise logs admin policy changes (assigning seats, content exclusion edits,
  enabling/disabling the public code filter) to the standard GitHub audit log. As of
  Q2 2026, the audit log exports to S3 with KMS encryption in addition to the legacy CSV
  download path — useful for direct SIEM ingestion. User-level prompt content is **not**
  in the audit log; usage metrics (active users, acceptance rates, AI credits per user)
  are in the separate Copilot Usage Metrics API.
compliance_lens: |
  For SOX ITGC and FFIEC purposes, the audit log covers admin/policy actions (the control
  changes auditors care about) but not the prompts themselves (which would be excessive
  for routine compliance and a privacy concern). The S3 export removes the manual-CSV
  evidence-gathering burden — fold it into the same SIEM pipeline as the rest of the
  GitHub audit stream.
source_url: https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/setting-policies-for-copilot-in-your-organization
last_verified: 2026-06-20
override_facts_predicate: audit-log-export-format
```

---

## public-code-filter

```yaml
id: public-code-filter
question_patterns:
  - "public code filter"
  - "duplicate detection"
  - "block suggestions matching public code"
  - "GPL contamination"
category: public-code-filter
canonical_answer: |
  The public code filter (also called "duplicate detection") suppresses Copilot
  suggestions that closely match publicly-available code, reducing the chance of
  inadvertent copyleft contamination or recognizable copying. Required for the IP
  indemnity to apply (see ip-indemnity above). Configure at the org level; cannot be
  turned off per-user.
compliance_lens: |
  The filter is non-optional for any regulated org accepting Copilot's IP indemnity. Org
  policy should enable it by default and disallow per-team exception requests. Confirm at
  audit time by sampling org settings via the GitHub API; the setting must be on.
source_url: https://docs.github.com/en/copilot/managing-copilot/managing-github-copilot-in-your-organization/setting-policies-for-copilot-in-your-organization/managing-policies-for-copilot-in-your-organization
last_verified: 2026-06-20
override_facts_predicate: public-code-filter
```

---

## model-selection

```yaml
id: model-selection
question_patterns:
  - "which model does Copilot use"
  - "can I pick the model"
  - "model selection"
  - "Opus vs MAI-Code"
  - "Copilot model deprecation"
category: model-selection
canonical_answer: |
  Copilot supports multiple models routed per-feature; the default differs per surface
  (Chat, code completion, code review, agents). As of mid-2026, supported model families
  include Anthropic Opus (4.7, 4.8), Microsoft MAI-Code (1, 1-Flash), and OpenAI GPT-5
  variants. Models can be deprecated with ~60-day notice (e.g., Opus 4.6 fast deprecation
  2026-06-29). Admins do **not** currently pin a specific model org-wide as a hard
  policy — users select per session, with the org policy controlling which models are
  available.
compliance_lens: |
  The lack of a hard org-wide pin matters for model-risk: SR 11-7 reviews effectively
  cover the **set of available models**, not a specific one. Maintain an internal record
  of which models are approved and watch the GitHub changelog for deprecations and new
  additions. The deprecation cadence is fast enough that model risk reviews should
  refresh at least quarterly.
source_url: https://github.blog/changelog/label/copilot/
last_verified: 2026-06-20
override_facts_predicate: model-selection
```

---

## agents-md

```yaml
id: agents-md
question_patterns:
  - "AGENTS.md"
  - "how do I govern Copilot per repo"
  - "Copilot policy per repository"
  - "Copilot code review behavior"
category: agents-md
canonical_answer: |
  As of June 2026, Copilot code review reads a repository's `AGENTS.md` file for context
  on review focus, hand-off conventions, and policy. `AGENTS.md` becomes a repo-level
  declarative policy surface for Copilot's review behavior, parallel to CODEOWNERS for
  review routing. Place secure-coding-standard pointers, must-flag patterns, and
  org-specific review priorities in this file.
compliance_lens: |
  Recommend the org's golden-path / template repo gains a stub `AGENTS.md` with policy
  snippets (review for hard-coded secrets, license header compliance, deprecated API
  calls, regulated-data handling patterns). Coordinate with the team that owns the org
  repo template before broad rollout.
source_url: https://github.blog/changelog/2026-06-18-copilot-code-review-agents-md-support-and-ui-improvements
last_verified: 2026-06-20
override_facts_predicate: code-review-reads-agents-md
```

---

## Adding a new entry

When a new question shows up:

1. Invoke `copilot-deep-dive` (step 11) to research it.
2. Distill the research into the YAML shape above.
3. Add to this file with `last_verified: <today>`.
4. If the predicate also makes sense as a typed fact, also stage it for `vault/facts/copilot/{predicate}.md` via `memory-curator`.
