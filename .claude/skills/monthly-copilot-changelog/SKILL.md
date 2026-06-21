---
name: monthly-copilot-changelog
description: Monthly scheduled agent. Aggregates the past 30 days of Copilot and GHAS changelog entries into a single digest with the **policy implications** lens — for each change, what (if anything) does the org's policy / canonical FAQ / TPRM file need to update? Run on the 1st of each month; outputs to vault/digests/monthly/YYYY-MM-DD-monthly-copilot-changelog.md. Different from weekly-intelligence-digest: that's a "what changed in the world" brief across many sources; this is a focused, policy-actionable monthly review of Copilot/GHAS specifically.
---

# monthly-copilot-changelog

A monthly cadence Category 2 agent. The weekly-intelligence-digest skims many sources; this one goes deep on the Copilot + GHAS changelog with a "what does our policy / canonical FAQ / TPRM file need to change?" lens.

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: monthly-copilot-changelog
cadence: monthly
schedule_hint: "1st of month, 07:00 local"
source_filter:
  topic_tags: [github, copilot, ghas]
  min_tier: 1
  source_ids: [github-changelog]  # tier-1 vendor primary
  max_items_per_source: 50         # full monthly batch, not weekly's top-5
verify_loadbearing: false           # vendor primary is the authority
curate_findings: true               # stage facts for memory-curator
digest_template_overrides:
  template: monthly-copilot-policy-implications
  why_you_care_extra: |
    For each change, answer THREE questions:
    1. Does this require an update to `copilot-faq-answerer/canonical-answers.md`?
    2. Does this require a change to the TPRM file for Copilot?
    3. Does this require communication to stakeholders (legal / security / audit / MRM)?
    Items requiring none of these get a one-line entry; items requiring any get a full section.
```

## Output document structure

A specialized template — not the standard 5-section digest. Sections:

```markdown
# Monthly Copilot/GHAS Changelog — {month}

## At a glance
{count of items, of which N need policy/FAQ/TPRM action, M need stakeholder comms}

## Items requiring action

### {item title} → {policy | TPRM | stakeholder comms | combination}

**What changed**: {1-2 sentences}

**Action required**:
- {specific action} → {owner}

**Why**: {compliance lens}

**Sources**: {source URLs with credibility tier}

## Items for awareness (no action)

- {one-line per item}

## Cross-references to vault
- Updated canonical answers proposed: {list with [[wikilinks]]}
- Updated facts staged for memory-curator: {list}
- Stakeholder update items queued for `stakeholder-update-writer`: {list}
```

## Composes with

Standard Phase-1 foundation plus:
- [[copilot-faq-answerer]] — canonical-answer override is one of the action types.
- [[stakeholder-update-writer]] — comms-action items feed its next exec/lead/IC update.
- [[memory-curator]] — promotable claims get staged.

## Acceptance test (for step 21 done-criteria)

One monthly digest exercised against a 30-day window of GitHub changelog content. Confirm: policy-implications lens applied per item; cross-references to vault notes that would be updated; at-a-glance count at top.
