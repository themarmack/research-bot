---
name: runner-security-reviewer
description: Assess a self-hosted runner pool (or a single runner image) against the org's runner-security baseline — ephemeral lifecycle, restricted network egress, runner-group scoping, OS image hardening, secret handling, log retention. Produces a posture report with current state vs expected per item. Use during runner-pool design review, after a runner-related incident, when planning a new restricted runner group for a regulated workload, or as part of quarterly GHAS posture audit.
---

# runner-security-reviewer

A Category 3 ops tool. Self-hosted GitHub Actions runners are simultaneously a high-leverage capability (private-network access for CI) and a high-risk surface (persistent compromise vector per the Shai-Hulud-class attacks). This skill makes the posture review reproducible.

## When to use

- Designing a new runner group for a regulated workload (e.g., the `hardened-codeql` group from step 19).
- Quarterly GHAS posture audit.
- Post-incident review.
- Vendor / contractor review when a third party will host runners on the org's behalf.

## When NOT to use

- Workflow-level review → `actions-workflow-hardener`.
- Individual job-level security → that's per-workflow, not per-runner.
- Org-wide Actions settings → `github-org-audit-runner`.

## Baseline

| Category | Item | Expected | Severity if missing |
|----------|------|----------|---------------------|
| Lifecycle | Runner is ephemeral | one job per runner instance, destroyed after | CRITICAL |
| Lifecycle | Image rebuilt from base on schedule | weekly | HIGH |
| Lifecycle | Runner registration uses just-in-time tokens | yes (not long-lived PATs) | CRITICAL |
| Network | Egress restricted via allow-list | yes (only known endpoints) | HIGH |
| Network | No public IP exposure | runner pulls jobs, doesn't accept inbound | HIGH |
| Network | Outbound to internal services | only the ones declared in the workflow | MEDIUM |
| Image | OS image is corp-hardened base | yes | HIGH |
| Image | No persistent secrets baked into image | no | CRITICAL |
| Image | Container / VM image scanned for CVEs before deploy | yes | HIGH |
| Image | Default user is non-root | yes | HIGH |
| Secrets | Secrets pulled at job start via OIDC | yes | HIGH |
| Secrets | No GITHUB_TOKEN reuse across jobs on the same runner | guaranteed by ephemeral lifecycle | CRITICAL |
| Secrets | Encryption-at-rest for ephemeral disk | yes | MEDIUM |
| Logs | Workflow logs streamed to SIEM | yes | HIGH |
| Logs | Runner system logs retained 90 days | yes | MEDIUM |
| Scoping | Runner group scoped to specific orgs/repos | yes (not enterprise-wide) | HIGH |
| Scoping | Group naming convention identifies purpose | e.g., `hardened-codeql`, not `runner-pool-1` | INFO |
| Public-repo policy | Self-hosted runners disallowed for public-repo PRs | enforced | CRITICAL |

## Workflow

1. **Identify the runner pool/group** to review.
2. **Inspect via `gh api` and/or runner-host inventory**:
   - `gh api orgs/{org}/actions/runner-groups` — group metadata + scope.
   - `gh api orgs/{org}/actions/runner-groups/{id}/runners` — registered runners.
   - Runner host config (cloud or on-prem inventory).
3. **Compare** each item against the baseline.
4. **Produce findings**.

## Output

```json
{
  "runner_group": "hardened-codeql",
  "audit_at": "2026-06-20T16:00:00Z",
  "findings": [...],
  "summary": {"critical":0,"high":2,"medium":1,"info":0,"total":3}
}
```

Lands at `vault/research/github/YYYY-MM-DD-runner-security-{group-slug}.md`.

## Composes with

- `gh api` for the GitHub-side metadata.
- `github-org-audit-runner` — sister skill for the org-level Actions settings.
- `actions-workflow-hardener` — when a finding traces to a workflow misconfiguration rather than a runner-pool one.
- [[2026-06-20-actions-hardening-post-shai-hulud]] — the rationale source.

## Acceptance test (for step 20 done-criteria)

Document the 18-row baseline with severity per item; one sample posture report (live or hypothetical) walking through each baseline category.
