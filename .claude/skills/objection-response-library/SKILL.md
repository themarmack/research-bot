---
name: objection-response-library
description: Pre-built responses to the recurring objections to Copilot / AI dev tooling from legal, security, audit, model risk, and skeptical developers. Reads canonical entries from `./canonical-objections.md` in this skill folder. Each entry: the objection (paraphrased), audience (legal / security / audit / MRM / skeptical-dev), the steel-manned concern, the response (with citations and what the org actually does), and what NOT to say (anti-patterns). Use whenever the user gets an objection in writing or a meeting and wants a fast, calibrated response that doesn't sound dismissive or evasive.
---

# objection-response-library

The companion to `copilot-faq-answerer` for **objection-shaped** questions. FAQ entries answer "how does X work?" — these entries answer "we're concerned about X." The difference matters: objections need acknowledgment of the underlying concern before answering, and they often have multiple layers (what the objector said, what they actually mean, what would satisfy them).

## When to use

- The user receives an objection in writing (email, PR comment, exception ticket).
- The user is preparing for a meeting where a known objection is expected.
- Drafting an objection-response section for the `stakeholder-update-writer`'s IC tier.

## When NOT to use

- Pure factual questions → `copilot-faq-answerer`.
- A net-new objection nobody has raised before — research it via `copilot-deep-dive` first, then add to the library.

## Response anatomy

Every objection response has 5 parts:

1. **Acknowledge the concern** — restate what the objector is actually worried about (steel-manned, not strawmanned). "You're concerned that X could happen because Y."
2. **What the org actually does** — the concrete control or process that addresses the concern.
3. **Source citation** — link to the canonical FAQ entry, GitHub Docs, regulator guidance, or internal policy.
4. **What this does NOT cover** — explicit limits. Objectors often have a follow-up objection ready; pre-empt it with honest scope.
5. **Next step if not satisfied** — what's the proper escalation / exception path.

**Anti-patterns to avoid** (and the skill warns against these):
- Dismissive: "GitHub indemnifies us, so this isn't a concern." (Doesn't acknowledge concern, doesn't address actual risk.)
- Evasive: "We're working on that." (Treat the objector as a peer who deserves a real answer.)
- Over-promising: "This is fully mitigated." (Real risk controls have limits; pretending otherwise costs credibility.)
- Vendor-speak: parroting GitHub's marketing language. The objector knows it's marketing.

## Resolution order

For each incoming objection:

1. **Match to a canonical objection** in `canonical-objections.md` by `objection_patterns`.
2. **Check the vault** via `vault-querier` for any newer fact or decision overriding the canonical response.
3. **Apply the org's posture** (regulated-org lens, your specific controls).
4. **Cite** the source.
5. **Surface limits** — what the canonical response does NOT cover.

If no canonical match: stop and report. Suggest invoking `copilot-deep-dive` to research, draft a proposed canonical entry, and once user-approved add to the library.

## Composes with

- `vault-querier` — newer facts may override canonical responses.
- `copilot-faq-answerer` — overlapping content; objection library wraps FAQ entries with the steel-man + limits structure.
- `stakeholder-update-writer` — IC-tier FAQ section often pulls from here.

## Acceptance test (for step 15 done-criteria)

The skill ships with ≥5 canonical objection entries in `canonical-objections.md` covering at minimum:
1. Legal — IP indemnity edge case ("what if our developer modifies a suggestion?")
2. Security — prompt injection from third-party content
3. Audit — lack of per-suggestion traceability for SOX evidence
4. Model risk (SR 11-7 successor) — Copilot doesn't fit MRM scope
5. Skeptical dev — quality / over-reliance / junior-dev impact

Each entry has all 5 anatomy parts populated and at least one source URL.
