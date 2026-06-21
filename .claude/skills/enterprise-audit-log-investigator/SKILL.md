---
name: enterprise-audit-log-investigator
description: Run common saved searches against the GitHub enterprise audit log — Copilot policy changes, secret-scanning push-protection bypasses, SSO events, allowed-Actions list edits, content-exclusion changes. Each canonical search has a structured query (the `gh api`-equivalent of the audit log search syntax), the matching `action` types, expected normal volume, alert threshold, and what to do if results spike. Use during incident response (something changed and we need to know who/when), during quarterly audit prep, or proactively as part of a security-monitoring rhythm.
---

# enterprise-audit-log-investigator

The audit-log surface is rich but slow to search ad-hoc. This skill encodes the recurring searches as named queries so the user doesn't reinvent the syntax each time. Composes with the org's SIEM ingestion (via the S3 + KMS export path from [[audit-log-export-format]]) but works standalone via `gh api` for one-off investigations.

## When to use

- Incident: "someone changed the Copilot policy at 02:00 — who?"
- Quarterly audit prep: "show me all SSO events for the regulated-data orgs."
- Proactive: weekly sweep for secret-scanning push-protection bypasses (the legitimate-but-overused exception path).
- Triggered by a `weekly-intelligence-digest` finding about a config change at the platform level — confirm whether it's been applied.

## When NOT to use

- Org-level settings comparison → `github-org-audit-runner`.
- Specific user provisioning audit → use SCIM logs directly.
- Continuous monitoring → that's SIEM territory.

## Canonical saved searches

Each named search has: query syntax, action types, expected volume, alert threshold.

### `copilot-policy-changes`

```
gh api enterprises/{enterprise}/audit-log -X GET -f phrase='action:copilot.*'
```

**Matches**: `copilot.policy_updated`, `copilot.seat_assigned`, `copilot.seat_unassigned`, `copilot.policy_assignment_changed`, `copilot.content_exclusion_updated`.
**Expected volume**: low (single-digit per day for a stable org).
**Alert threshold**: more than 20 events in a 24h window, OR any `copilot.policy_updated` outside business hours.

### `secret-scanning-bypasses`

```
gh api enterprises/{enterprise}/audit-log -X GET -f phrase='action:secret_scanning.push_protection_bypass'
```

**Matches**: any `secret_scanning.push_protection_bypass` action.
**Expected volume**: very low (push protection rejects, bypasses are exception path).
**Alert threshold**: more than 5/week. Each event reviewed; the comment justification is the audit evidence.

### `sso-and-saml-events`

```
gh api enterprises/{enterprise}/audit-log -X GET -f phrase='action:org.saml_provider_settings_updated OR action:business.set_actions_fork_pr_workflows_policy'
```

**Matches**: SAML provider config changes, IdP rotation, SSO enforcement changes.
**Expected volume**: rare (changes during planned IdP migrations only).
**Alert threshold**: ANY unplanned event. Always investigate.

### `allowed-actions-changes`

```
gh api enterprises/{enterprise}/audit-log -X GET -f phrase='action:org.update_actions_settings'
```

**Matches**: allow-list edits, GITHUB_TOKEN default permission changes, fork-PR workflow policy changes.
**Expected volume**: low.
**Alert threshold**: any change outside scheduled maintenance window.

### `content-exclusion-changes`

```
gh api enterprises/{enterprise}/audit-log -X GET -f phrase='action:copilot.content_exclusion_updated'
```

**Matches**: org or repo-level content exclusion edits.
**Expected volume**: low after initial config.
**Alert threshold**: more than 3 events in a 24h window, OR any deletion of an existing exclusion pattern (deletions are higher risk than additions).

## Output

Per-search result: a table with timestamp, actor, action, target, and a per-event "anomalous?" flag based on the threshold. Plus a summary at top — total events, anomalies, recommended next action.

Output lands at `vault/research/github/YYYY-MM-DD-audit-log-{search-slug}.md`.

## Composes with

- `gh` CLI (org auth required).
- `github-org-audit-runner` — sister skill for the static settings view.
- `vault-writer.write_event` — anomalous events get auto-staged to `_inbox/` for memory-curator review.
- SIEM ingestion (via [[audit-log-export-format]]) — for continuous monitoring; this skill is the ad-hoc tool.

## Acceptance test (for step 20 done-criteria)

Document at least 5 canonical saved searches with full query / action-list / volume / threshold structure. Each ready to run via `gh api` against a real enterprise.
