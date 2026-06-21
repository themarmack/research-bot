---
name: secrets-hygiene-reviewer
description: Review a repo / service for secret-handling problems BEYOND what GHAS secret scanning catches at commit time. Focus areas — runtime exposure (env-var passthrough into logs / error pages / metrics labels / observability tags), rotation gaps (secrets used past their declared lifetime), config-file secrets in inheritable paths (`.env.example` with real values, dotfiles in dev containers), shell-history leakage in entry points, secrets in container layers (visible via `docker history`), and secret reuse across environments (prod credentials used in non-prod). Produces a structured finding list with severity, evidence, remediation. Use during service onboarding to GHAS, after a secret-leakage near-miss, or as a portfolio audit step.
---

# secrets-hygiene-reviewer

The secrets surface that **isn't** at-commit-time. GHAS secret scanning catches the "secret pasted into a file and committed" case beautifully; this skill catches everything else.

## When to use

- New service onboarding to GHAS — confirms hygiene beyond commit-scan coverage.
- After a near-miss (a secret got logged, almost got pushed, almost got into an error page).
- Container-build hardening review.
- Portfolio audit of high-blast-radius repos.

## When NOT to use

- At-commit secret scanning → GHAS native (already covered by push protection per [[ghas-config-reviewer]] baseline).
- Secret rotation operations → not in scope; this skill flags rotation gaps, doesn't perform rotation.
- Cryptographic key review → that's design review (`secure-design-reviewer` key-management category).

## Check categories

### 1. Runtime exposure

| Check | Severity |
|-------|----------|
| Env var named `*_SECRET`, `*_TOKEN`, `*_KEY`, `*_PASSWORD` referenced in `log.info/debug` or printf-style output | HIGH |
| Error pages / 500-handlers that include env vars in the response body | CRITICAL |
| Metrics labels include secret-named env vars (Prometheus / OpenTelemetry) | HIGH |
| Observability tags / span attributes include secrets | HIGH |
| Shell-history leakage at entry points (`echo $TOKEN`, `set -x` enabled without scrub) | MEDIUM |

### 2. Rotation gaps

| Check | Severity |
|-------|----------|
| Secret used past its declared `expires_at` (per the secrets registry, if available) | HIGH |
| No documented rotation schedule for a secret | MEDIUM |
| Rotation depends on a manual step with no calendar reminder | LOW |
| Service has hardcoded retry-on-secret-failure that masks rotation events | MEDIUM |

### 3. Config-file hygiene

| Check | Severity |
|-------|----------|
| `.env.example` contains a real value (not a placeholder) | CRITICAL |
| Dotfile in a dev-container template includes a real secret | CRITICAL |
| Helm `values.yaml` or chart default includes a real secret | HIGH |
| Terraform `.tfvars` includes a real secret (vs sourced from KMS / SSM) | CRITICAL |

### 4. Container-layer leakage

| Check | Severity |
|-------|----------|
| `Dockerfile` `ARG SECRET=...` or `ENV SECRET=...` in a non-multi-stage build (secret persists in final image layer) | CRITICAL |
| Secret baked into image at build-time visible via `docker history` | CRITICAL |
| Secret in `.dockerignore`-bypassed path (e.g., `.git` history when source is COPYed) | HIGH |

### 5. Cross-environment reuse

| Check | Severity |
|-------|----------|
| Same secret value used in `prod` and `non-prod` (per the secrets registry) | CRITICAL |
| Service config references the same secret name across environments without per-env override | HIGH |
| Test fixtures use real secret values (rather than synthetic) | HIGH |

## Workflow

1. **Identify scope**: repo / service / image.
2. **Walk each check category** against the scope.
3. **Per finding**: cite specific evidence (line / file / image layer).
4. **Produce findings list**: structured per usual ops-skill shape.
5. **Summary**: counts per severity + by category.

## Output structure

```markdown
# Secrets Hygiene Review — {scope}

## Summary
- Findings: {N} ({critical/high/medium/low counts})
- By category: runtime exposure / rotation / config-file / container-layer / cross-env

## Findings
[per finding: id, category, severity, evidence, remediation]

## Cross-references
- Existing GHAS secret scanning posture: {covered / gap}
- vault notes referenced: {list}
```

Lands at `vault/research/sdlc-best-practice/YYYY-MM-DD-secrets-hygiene-{scope-slug}.md`.

## Composes with

- [`ghas-config-reviewer`](../ghas-config-reviewer/SKILL.md) — at-commit scan coverage; this skill picks up where that one ends.
- [`secure-design-reviewer`](../secure-design-reviewer/SKILL.md) — key management category overlaps.
- [`actions-workflow-hardener`](../actions-workflow-hardener/SKILL.md) — ATH-005 (long-lived cloud creds) overlaps.

## Acceptance test (for step 26 done-criteria)

5 check categories documented with at least 18 named checks; severity levels assigned per the org's blast-radius model. Live exercise against real repo deferred to first invocation.
