---
name: actions-workflow-hardener
description: Review a GitHub Actions workflow YAML file for security hardening issues — unpinned action SHAs, overpermissive GITHUB_TOKEN, missing OIDC for cloud auth, pull_request_target misuse, secret-handling problems, self-hosted-runner risks. Produces a structured finding list with severity, line reference, remediation, and a citation to the underlying GitHub recommendation. Baseline derived from `vault/research/github/2026-06-20-actions-hardening-post-shai-hulud.md` (7 hardening practices from GitHub Docs). Use whenever the user is reviewing a workflow file before merge or auditing inherited workflows.
---

# actions-workflow-hardener

A Category 3 ops tool. The user runs this against a workflow YAML file — either pasted into the conversation or pointed at by path — and gets a prioritized finding list with concrete remediation.

The skill's checks come directly from the 7 hardening practices documented in [[2026-06-20-actions-hardening-post-shai-hulud]]. As that research note is updated (new attack techniques, new GitHub guidance), the checks here update with it.

## When to use

- Reviewing a new workflow before merge.
- Auditing an inherited workflow during repo onboarding.
- Periodic sweep across org-wide workflows when planning a hardening campaign.
- Validating that an existing workflow's `permissions:` block is sane after a refactor.

## When NOT to use

- Pure correctness review (does the workflow work) — that's not this skill's scope.
- Performance optimization — separate concern.
- Repo-level governance (CODEOWNERS, branch protection) — that's `repo-golden-path-scorer` (planned).
- Org-wide GHAS settings — that's `ghas-config-reviewer`.

## Checks

Each check produces a finding object: `{check_id, severity, line, snippet, message, remediation, reference}`.

### `ATH-001` — Missing top-level `permissions:` block (HIGH)

If the workflow file has no top-level `permissions:` declaration AND no per-job declarations, GITHUB_TOKEN defaults to the org-wide default (often `write-all`). Recommend adding a top-level `permissions: contents: read` and escalating per-job only as needed.

**Reference**: GitHub Docs — "Restrict GITHUB_TOKEN permissions" (recommendation 1 in [[2026-06-20-actions-hardening-post-shai-hulud]]).

### `ATH-002` — `permissions: write-all` or per-permission `write` at the top level (CRITICAL)

Top-level write permissions affect every job. If any job genuinely needs write, put the escalation at that job's level, not at the file level.

### `ATH-003` — Third-party action referenced by version tag, not SHA (HIGH)

`uses: someone/some-action@v3` is mutable; `uses: someone/some-action@abc123def456...` is immutable. SHA-pin all third-party actions. Note: official `actions/*` actions (e.g., `actions/checkout@v4`) are usually considered acceptable to version-pin by convention, but org policy may demand SHA pinning everywhere — surface as MEDIUM if `actions/*`, HIGH if any other namespace.

**Detection pattern**: `uses: <owner>/<repo>@<tag>` where `<tag>` doesn't match a 40-char hex SHA.

### `ATH-004` — `pull_request_target` with PR-branch checkout (CRITICAL)

`pull_request_target` runs with target-repo privileges (and access to secrets). A workflow that explicitly checks out the PR head (`actions/checkout@... with: ref: ${{ github.event.pull_request.head.sha }}`) under this trigger is a critical security hole — attacker-controlled code runs with full secret access.

**Detection pattern**: any job triggered by `pull_request_target` that has a checkout step referencing `github.event.pull_request.head.*`.

### `ATH-005` — Long-lived cloud credential in `secrets` (HIGH)

References to `${{ secrets.AWS_ACCESS_KEY_ID }}`, `${{ secrets.AZURE_CLIENT_SECRET }}`, or similar long-lived credential names suggest cloud auth via static secret rather than OIDC.

**Detection pattern**: secret-name regex against a list of known long-lived cloud credential conventions.

**Remediation**: replace with OIDC trust between Actions and the cloud IdP. Specific instructions vary by cloud (`aws-actions/configure-aws-credentials@... with: role-to-assume:`, etc.).

### `ATH-006` — `runs-on: self-hosted` in a workflow that triggers on `pull_request` from external contributors (CRITICAL)

Self-hosted runners + public-repo PR triggers = attacker-controlled code running on the org's infrastructure. Almost never acceptable.

**Detection pattern**: `runs-on: self-hosted` AND `on: pull_request` AND the repo is (or could be) public. (Repo visibility might require the caller to pass the repo's privacy state.)

### `ATH-007` — Secret printed to log without masking (MEDIUM)

`run: echo "key=$MY_SECRET"` will leak the secret to the workflow log if `MY_SECRET` isn't a registered secret. Use `::add-mask::` to protect dynamic secrets.

**Detection pattern**: heuristic — `echo`/`printf` of variables whose names contain `SECRET`, `TOKEN`, `KEY`, `PASSWORD`.

### `ATH-008` — Inline shell substitution from PR title/body/branch (HIGH)

`run: echo "${{ github.event.pull_request.title }}"` is a shell-injection vector. PR titles can contain `$( … )` or backticks.

**Detection pattern**: `${{ github.event.pull_request.* }}` directly inside a `run:` block.

**Remediation**: pass via env, quote properly.

## Output shape

```json
{
  "file": "<path>",
  "findings": [
    {
      "check_id": "ATH-003",
      "severity": "high",
      "line": 17,
      "snippet": "uses: tj-actions/changed-files@v45",
      "message": "Third-party action referenced by version tag; this is mutable.",
      "remediation": "Pin to a full 40-char commit SHA. Dependabot can manage SHA bumps if configured to track this action.",
      "reference": "vault/research/github/2026-06-20-actions-hardening-post-shai-hulud.md#2-pin-actions-to-full-commit-sha-not-version-tags"
    }
  ],
  "summary": {"critical": 1, "high": 2, "medium": 1, "low": 0, "total": 4}
}
```

If zero findings, return the empty list and a `clean: true` flag — don't pad with low-confidence noise.

## Composes with

- [[2026-06-20-actions-hardening-post-shai-hulud]] — the source of truth for the check rationales.
- `vault-querier` — caller may want to surface related findings from prior workflow audits.

## Acceptance test (for step 13 done-criteria)

Run against `tests/bad-workflow.yml` (in this skill folder). Expected:
- ATH-001 (no top-level permissions) — flagged
- ATH-003 (version-tag pin) — flagged (multiple instances)
- ATH-004 (pull_request_target + PR checkout) — flagged
- ATH-005 (long-lived AWS secret) — flagged
- ATH-006 (self-hosted + public PR trigger) — flagged
- Total: 5+ findings, severity correctly assigned
