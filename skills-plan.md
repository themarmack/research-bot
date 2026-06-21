# Skill Catalog — SDLC Modernization, GitHub/Copilot, Regulated Finance

## Context

You lead SDLC modernization for thousands of developers at a heavily regulated environment, balancing innovation against elevated security/compliance demands. You're a GitHub admin who fields frequent Copilot and platform questions and you operate GHAS (CodeQL, Dependabot, secret scanning). You want a personal toolkit of Claude skills — most are on-demand research/ops helpers, plus at least one scheduled agent that aggregates external news weekly. This file is a brainstormed catalog; implementation comes later.

A few cross-cutting design notes that should apply to most skills here:
- **Regulated-finance lens** baked into prompts: compliance-grade controls, data residency, model/data egress, auditability, SR 11-7 model risk, FFIEC, OCC, PCI-DSS, SOX ITGC, GLBA, NYDFS 500.
- **Enterprise GitHub assumption**: GHEC + EMU + SAML/OIDC, GHAS enabled, Copilot Business/Enterprise.
- **Output discipline**: every research/digest skill should emit dated notes with source URLs so output is reviewable months later.
- **No raw code/data leakage**: research skills must not paste internal repo contents into web prompts; ops skills that read repos should call that out.

---

## Use Cases

The toolkit serves two primary use cases. Every skill in the catalog supports one or the other (sometimes both).

### Use case 1 — Scheduled weekly research

A growing list of cron-driven skills that run standard research prompts on a fixed cadence and drop dated digests into the vault. Each scheduled skill answers a recurring question — "what changed in Copilot this week?", "what did the AI commentariat publish?", "what's new from US bank regulators?" — without the user having to ask. The list is meant to **expand over time**: any "what's new in X?" question worth asking weekly is a candidate for a new Category 2 skill.

- **Primary category**: Category 2 — Scheduled / Recurring Agents.
- **Output destination**: `~/Obsidian/Research-Brain/digests/{cadence}/YYYY-MM-DD-{skill}.md`.
- **Foundation depended on**: `scheduled-agent-runner` + `feed-watcher` + `seen-tracker` + `digest-writer` + `vault-writer`.

### Use case 2 — Ad-hoc research (Obsidian-first)

When the user asks a question on demand, the skill **checks the Obsidian vault first** via `vault-querier` for prior research on the topic, then expands to the web only for confirmed gaps. New findings are written back to the vault so the next ad-hoc question on the same topic builds on prior work instead of starting from scratch. Verified facts get promoted into `vault/facts/{entity}/{predicate}.md` so subsequent questions get the answer instantly without re-research.

- **Primary category**: Category 1 — Research (on-demand). The Obsidian-first contract is mandatory for every Category 1 skill.
- **Output destination**: `~/Obsidian/Research-Brain/research/{topic}/YYYY-MM-DD-{slug}.md`; verified facts also promoted to `vault/facts/`.
- **Foundation depended on**: `vault-querier` (read first) + `source-fetcher` + `claim-extractor` + `verify-claim` + `vault-writer` + `memory-curator`.

---

## Memory Architecture

The toolkit uses two complementary memory tiers.

**Tier 1 — Harness auto-memory** at `~/.claude/projects/<this-project>/memory/`. Narrow, auto-loaded into every conversation by the Claude Code harness. Holds identity, preferences, feedback only. Stays under ~10 entries — the index truncates past 200 lines. Auto-maintained.

**Tier 2 — Obsidian vault** at `~/Obsidian/Research-Brain/`. Broad, queried on demand via `vault-querier`. Holds knowledge, research, facts, decisions, events, people, projects, and digests from scheduled agents. Structure follows `jrcruciani/obsidian-memory-for-ai` v3.1 conventions: three surfaces (human narratives, atomic typed facts, episodic events) plus inbox/views ops folders.

`memory-curator` decides which tier gets each candidate. Default for factual / episodic / research content is Tier 2 (the vault). Default for "how should Claude treat the user" is Tier 1. The two never duplicate.

See `~/Obsidian/Research-Brain/_meta/conventions.md` for the vault's full layout, frontmatter schemas, and link conventions. Every skill that reads or writes the vault loads that file first via `vault-conventions`.

---

## Category 0 — Foundational Base Skills

The 15+ topic-specific research skills below should stay thin. To make that possible, build a small layer of shared infrastructure skills first. These are the load-bearing pieces — every other research skill composes with them.

**What the research said** (grounding for this section):

- The built-in `deep-research` skill already encodes a strong 5-stage pattern: **Scope → Search → Fetch → Verify → Synthesize** with bounded fan-out (5 search angles, top ~15 sources) and a 3-vote adversarial verification step (kill a claim at ≥2/3 refutes). Worth extracting the verification pattern as a reusable primitive.
- The 2025-2026 production trend is **multi-model orchestration** with specialized sub-agents (Perplexity Computer routes across 20+ models; Microsoft Researcher uses model-of-best-fit). Implication: a base skill that wraps "delegate this subtask to the right agent" lets topic skills stay short.
- **Prompt injection from fetched web content** is OWASP LLM01:2025 for the third year running, with active CVEs in Copilot (CVSS 9.6) and Cursor (CVSS 9.8). January 2026 research showed 5 crafted docs can manipulate a RAG agent 90% of the time. Implication: a `prompt-injection-guard` is not optional for skills that fetch arbitrary web content, and Meta's **Rule of Two** (pick at most 2 of {process untrusted input, access sensitive systems, change external state}) is a useful constraint to bake in.
- **Adversarial verification** (refute-not-confirm, 3-judge panels, multi-agent debate per LoCal / FACT-AUDIT) is the dominant pattern for reducing hallucinated facts. Reusable as a single primitive.
- For scheduled/recurring agents, **dedup needs both layers**: URL/content-hash for exact repeats, embedding similarity for semantic dupes (same story from two outlets). Title-hash + content-hash is the cheap default; vector dedup only when worth the dependency.

**Proposed base skills:**

- **source-registry** — A curated YAML/JSON of high-signal sources per topic (regulator feeds, vendor changelogs, security advisories, peer-bank blogs). Each entry: `{url, type: rss|atom|html|api|github-releases, topic_tags[], credibility_tier: 1-3, cadence_hint, paywalled, notes}`. Single source of truth so every topic skill loads the right slice instead of redefining sources.
- **source-fetcher** — Wraps WebFetch with timeout/retry, redirect handling, robots.txt respect, content-type detection, and a `{url, fetched_at, status, content_md, content_hash, source_tier}` return shape. Passes content through `prompt-injection-guard` before returning.
- **prompt-injection-guard** — Pre/post filter for fetched content before it reaches downstream LLM calls. Strips obvious injection patterns, flags suspicious blocks for human review, enforces Meta's Rule of Two at the skill level. Non-negotiable for anything that fetches arbitrary URLs.
- **feed-watcher** — Poll RSS / Atom / JSON Feed / GitHub release feeds (and GitHub changelog RSS). Returns items new since last run. Used by every scheduled agent.
- **claim-extractor** — Given a fetched document, extract falsifiable claims as `{claim, quoted_anchor, source_url, source_tier}`. Standard schema reused across all research skills so downstream verification and synthesis can be shared.
- **verify-claim** — Direct extraction of deep-research's adversarial verification: spawn N (default 3) independent verifiers prompted to *refute* the claim, kill at ≥2/3 refutes, return `{verdict, vote_breakdown, evidence}`. Reusable everywhere a load-bearing claim needs scrutiny — not just research.
- **seen-tracker** — Persistent dedup for scheduled agents. Stores per-skill state at `~/.claude/state/<skill>/seen.jsonl` keyed by `url + content_hash` (and optionally a title-embedding bucket for semantic dupes). Exposes `is_new(item)` and `mark_surfaced(item)`. Without this, weekly digests repeat last week's news.
- **digest-writer** — Canonical output format for digests and research reports. Sections: TL;DR (3 bullets) → What Changed (with explicit "since {last_run_date}") → Why You Care (compliance/regulatory lens, plain language) → Detailed Findings → Sources (with credibility tier badges and accessed-date). Formats the digest and delegates the actual write to `vault-writer`, which lands it under `~/Obsidian/Research-Brain/digests/{cadence}/YYYY-MM-DD-<skill>.md`. Enforces consistent citations so output is auditable months later.
- **scheduled-agent-runner** — Convention/wrapper for skills meant to run on cron. Locates last-run state, calls `seen-tracker`, calls `digest-writer` (which writes through `vault-writer`), then runs `memory-curator` on the digest's findings to promote durable items into `vault/facts/`, `vault/events/`, or `vault/people/` as appropriate. Emits a one-line summary for the runner log. Lets the 5+ scheduled agents in Category 2 share orchestration code.
- **regulated-finance-framer** *(optional but high-leverage)* — A prompt-fragment skill that wraps any research output with the compliance-relevant lens (control objectives, regulator angle, model risk hooks). Loaded by topic skills via a single include rather than copy-pasted into 15 SKILL.md files.
- **vault-conventions** — Reads `~/Obsidian/Research-Brain/_meta/conventions.md`, `_meta/schema/*.yml`, and `_meta/tags.md` and returns a compact structured summary. Any skill that reads or writes the vault loads this first so it follows the conventions consistently. Output sized to fit in skill context.
- **vault-querier** — Read side of the vault. Filesystem grep + glob + frontmatter parse, no MCP. Supports queries by tag, by frontmatter field, by `[[wikilink]]` (forward + backlinks), and full-text. Returns `{path, frontmatter, excerpt, links}`. Fast enough for vaults of a few thousand notes; switch to mcpvault MCP if you outgrow it.
- **vault-writer** — Write side of the vault, replacing the legacy `~/research/` output of `digest-writer`. Routes a note to the correct folder, applies the right frontmatter schema, generates `[[wikilinks]]` to related notes via `vault-querier`. Helpers per surface: `write_fact`, `write_event`, `write_research`, `write_digest`, `write_insight`, `write_person`, `write_project`, `stage_to_inbox`. Idempotent on key fields — updates existing notes instead of duplicating. Composes with `prompt-injection-guard` on any fetched content before writing.
- **memory-curator** — Decides what's durable enough to land in the vault. Given a candidate (research finding, decision, fact, event, insight), classifies as **promote** (specific folder + frontmatter), **patch** (which existing `[[note]]` to update), or **drop** (stays ephemeral). Criteria documented in `~/Obsidian/Research-Brain/_meta/inbox-rules.md`: novelty, falsifiability, future utility, surprise factor, link-richness, source quality. Runs on `_inbox/` to promote staged writes; also runs ad-hoc when a skill wants to write a finding directly. Default-drops for unsourced agent claims and `#disputed` items.

**Build order for the foundation:** `source-fetcher` + `prompt-injection-guard` first (security-critical), then `source-registry` + `feed-watcher` (data plane), then `claim-extractor` + `verify-claim` (verification spine), then `seen-tracker` + `digest-writer` + `scheduled-agent-runner` (output plane). Only then start on topic-specific research skills — they'll be 1/3 the size if the foundation is in place.

---

## Category 1 — Research (on-demand)

Single-shot deep-dives invoked when you need a current answer on a specific topic.

**Obsidian-first contract** (mandatory for every skill in this category): the skill MUST query `vault-querier` first to find prior research, facts, and digests on the topic. It then expands to web research only for confirmed gaps — questions the vault cannot already answer. New findings are written back via `vault-writer` to `vault/research/{topic}/YYYY-MM-DD-{slug}.md`, and any falsifiable typed claims are promoted via `memory-curator` to `vault/facts/{entity}/{predicate}.md`. This keeps the vault as the canonical source of truth and prevents repeating the same web research across sessions.

- **copilot-deep-dive** — Latest GitHub Copilot features, models behind Copilot, enterprise admin controls, data handling, content exclusions, Copilot Chat/CLI/Workspace/Agents status; framed for a regulated org.
- **github-platform-watch** — Targeted research on a GitHub product area (Actions, Advanced Security, Audit Log, Billing, Packages, Issues/Projects, Enterprise) with changelog citations.
- **ai-coding-tools-compare** — Side-by-side of Copilot vs Cursor / Windsurf / Cody / Tabnine / JetBrains AI / Amazon Q Developer against an enterprise rubric (auth, data flow, IP indemnity, on-prem options, admin telemetry).
- **frontier-model-watch** — What's new from Anthropic, OpenAI, Google, Meta, Mistral, with an "what changes for enterprise dev tooling" angle.
- **codeql-pattern-finder** — Given a vulnerability class or business rule, find or sketch a CodeQL query; link to relevant CodeQL packs and community queries.
- **dependabot-strategy** — Research current best practices for triage, grouped updates, auto-merge gates, exception workflows, ecosystems coverage gaps.
- **ghas-feature-research** — Deep-dive on a GHAS feature (secret scanning push protection, code scanning autofix, supply-chain, security campaigns) including rollout caveats.
- **financial-regulator-watch** — Targeted scan of OCC, FRB SR letters, FDIC, FFIEC, SEC, FINRA, CFPB, NYDFS, FCA, ECB for guidance touching software risk, AI, third-party risk, cyber.
- **compliance-framework-lookup** — Quick cross-reference across NIST 800-53/800-218 SSDF, PCI-DSS 4.0, SOX ITGC, ISO 27001/27034, CIS benchmarks for a specific control question.
- **ai-governance-research** — NIST AI RMF, EU AI Act, US executive orders, state AI laws, ISO 42001, model cards — what applies to internal AI dev tooling.
- **sdlc-best-practice** — Current best practice for a narrow SDLC concern (trunk-based, ephemeral envs, IaC promotion, secrets, SBOM, signing, golden paths, platform engineering).
- **supply-chain-security-watch** — SBOM/CycloneDX/SPDX, SLSA, Sigstore, in-toto, OpenSSF Scorecard, npm/PyPI/Maven malware trends.
- **peer-bank-tech-intel** — What other major banks publicly share on developer platforms, AI coding, platform engineering (eng blogs, conference talks, public RFCs).
- **vendor-security-eval** — Standardized eval of a dev/AI vendor against your organization policy concerns (data flow diagram, SIG/SOC 2, model training opt-out, breach history).
- **incident-postmortem-research** — Pull lessons from publicly reported dev-tooling / supply-chain incidents relevant to a current decision.

## Category 2 — Scheduled / Recurring Agents

Run on a cron, write a dated digest file (and optionally post somewhere). Default cadence in parens.

- **weekly-intelligence-digest** (Mon AM) — The flagship. Aggregates the last 7 days across: GitHub changelog + roadmap, Copilot release notes, Anthropic/OpenAI/Google model news, major AI coding tool updates, OpenSSF/CISA/NVD advisories touching the org's stack, top regulator releases, top peer-bank eng blog posts. Output: one ranked markdown digest with "what changed", "why you care", source URLs.
- **daily-cve-digest** (weekday AM) — CVEs/advisories that touch the org's declared tech stack (a config file of ecosystems + critical libraries). Surface what Dependabot will/won't pick up.
- **monthly-copilot-changelog** (1st) — Just the Copilot/GHAS changelog with policy implications called out.
- **monthly-regulator-watch** (1st) — New guidance, comment periods, enforcement actions from the regulator list above.
- **quarterly-ai-coding-landscape** (start of quarter) — Long-form landscape report suitable for forwarding to leadership.
- **biweekly-codeql-community-pulse** — New CodeQL queries/packs from GitHub and the community, with relevance scoring.
- **conference-cfp-and-recap-watch** (monthly) — Upcoming CFPs and recaps for QCon, KubeCon, GitHub Universe, RSA, BSides, OWASP Global, etc.
- **voices-watcher** (daily AM) — Polls Substack / YouTube / blog RSS / podcast feeds for every entry in `voices.csv` (the human-editable roster at repo root, seeded from @natebjones's Following list). Surfaces new items since last run. Two outputs: (1) a daily digest at `vault/digests/daily/YYYY-MM-DD-voices-watcher.md` via `digest-writer`; (2) ensures every roster entry has a `vault/people/{handle}.md` note (creates or updates via `vault-writer`) so digest items can `[[link]]` to durable people notes. Composes on `feed-watcher` + `seen-tracker` + `digest-writer` + `prompt-injection-guard`. Skips rows where no RSS surface is recorded yet. Direct X/Twitter polling deliberately excluded — X requires paid API or self-hosted RSSHub; you opted to track these voices via their longer-form surfaces instead.
- **weekly-review** (Sunday PM) — Borrowed from OB1's Weekly Review pattern. Scans the past 7 days of writes across `vault/digests/`, `vault/research/`, `vault/events/`, `vault/decisions/`, and `_inbox/`. Output structure (per OB1): **Week at a Glance** (top-level summary) → **Themes** (clusters across captures) → **Open Loops** (unresolved action items, decisions in `proposed` status) → **Connections** (notes that link to each other or share entities) → **Gaps** (topics with weak coverage) → **Focus suggestions** for the coming week. Lands at `vault/digests/weekly/YYYY-MM-DD-weekly-review.md`.

## Category 3 — GitHub Admin & Copilot Ops

Reusable patterns for the questions and requests you handle as admin.

- **copilot-faq-answerer** — Canonical answers to recurring Copilot questions (data handling, IP indemnity, content exclusions, model selection, audit logs, public code filter, custom instructions, knowledge bases), pre-tuned to the org's posture.
- **copilot-rollout-playbook** — Generate a tailored expansion plan for a team or BU: prerequisites, training, success metrics, exception process.
- **copilot-metrics-analyzer** — Take Copilot usage metrics (active users, acceptance rate, chat usage) and translate into recommendations and talking points.
- **copilot-exception-handler** — Walk through whether a request for non-standard Copilot config is justified and how to document it.
- **github-org-audit-runner** — Step-through audit of org settings, SAML/SCIM, EMU posture, base permissions, secret scanning, push protection, allowed Actions, runner groups.
- **repo-golden-path-scorer** — Score a repo against the org's golden-path standards (CODEOWNERS, branch protection, required checks, signed commits, dependabot.yml, SECURITY.md).
- **dependabot-config-helper** — Generate or review a `dependabot.yml` with grouped updates, registries, schedules sane for the org.
- **codeql-onboarding-helper** — Decide default vs advanced setup for a repo, custom pack selection, alert triage workflow, exception process.
- **ghas-config-reviewer** — Audit a repo/org's GHAS configuration against your baseline.
- **runner-security-reviewer** — Self-hosted runner posture review (ephemeral, network egress, OIDC to cloud, image hardening).
- **actions-workflow-hardener** — Review a workflow for pinned SHAs, `permissions:` minimization, OIDC, secret usage, third-party action risk.
- **enterprise-audit-log-investigator** — Helper for common audit log searches (Copilot policy changes, secret scanning bypasses, SSO events).
- **voices-roster-curator** — Given a name, @handle, or URL, finds the person's publishing surfaces (Substack, YouTube, X/Twitter, LinkedIn, personal blog, podcasts) via web search + fetch, then adds or updates the row in `voices.csv` at repo root. Also has a "refresh" mode that re-checks every existing row for new surfaces. Idempotent: never duplicates rows; merges new surfaces into existing entries. Paired with `voices-watcher`.

## Category 4 — SDLC & Application Security

For when you're reviewing or designing controls rather than researching.

- **threat-model-helper** — Generate a STRIDE (or LINDDUN for privacy) model from a service description; pre-loaded with compliance-relevant threat catalog.
- **secure-design-reviewer** — Critique an architecture doc against control objectives (data classification, key mgmt, IAM, logging, DR, third-party).
- **iac-security-reviewer** — Review Terraform/Bicep/CFN against CIS + org guardrails; favor existing checkov/tfsec semantics.
- **license-compliance-checker** — Flag risky licenses in a dependency tree against the org's allow/deny list.
- **secrets-hygiene-reviewer** — Review a repo or workflow for secret handling problems beyond what secret scanning catches.
- **sbom-reviewer** — Parse a CycloneDX/SPDX SBOM and flag concerns (unsigned, abandoned, single-maintainer, known-malicious authors).
- **ai-tooling-data-flow-reviewer** — Given a proposed AI tool integration, map the data flow and flag where regulated data could leave.
- **exception-request-drafter** — Help draft a control exception with proper structure (risk, compensating controls, expiry, owner) that the GRC team will accept.
- **secure-coding-standard-checker** — Check a code snippet against the org's secure coding standards (with citations into the internal standard).

## Category 5 — Communication & Influence

Multiplies your reach across a at-scale-dev program.

- **stakeholder-update-writer** — Turn raw progress notes into a tiered update (exec, eng lead, IC) for the modernization program.
- **adr-writer** — Draft an Architecture Decision Record in the org's template.
- **rfc-writer** — Draft an RFC for a platform change with explicit rollout, rollback, risk, and migration sections.
- **enablement-content-creator** — Generate training content (Copilot prompting, secure coding with AI, CodeQL triage) at dev / lead / exec level.
- **objection-response-library** — Pre-built responses to common Copilot/AI objections from legal, security, audit, model risk, and skeptical devs.
- **demo-script-builder** — Build a tailored Copilot/SDLC demo for a target audience and use case.
- **survey-thematic-analyzer** — Cluster developer survey free-text into themes with representative quotes.
- **meeting-prep-brief** — Generate a brief from notes + recent activity for a stakeholder meeting.
- **decision-memo-writer** — One-page decision memo with options, recommendation, risks, and asks.

## Category 6 — Personal Knowledge Management

Optional but high-leverage given the volume of inputs you process.

- **learning-capture** — Save a structured note from an article or conversation. Writes via `vault-writer` to `vault/insights/{slug}.md` (or `vault/facts/{entity}/{predicate}.md` if the captured content is atomic and falsifiable). Tags from the controlled vocabulary in `_meta/tags.md`.
- **quick-capture** — Borrowed from OB1's Quick Capture Templates. Parses a one-line input matching one of five sentence-starter formats and routes to the right vault folder via `vault-writer`. Formats: `Decision: …. Context: …. Owner: ….` → `vault/decisions/`; `[Name] — [what you learned].` → `vault/people/`; `Insight: …. Triggered by: ….` → `vault/insights/`; `Meeting with [who] about [topic]. Key points: …. Action items: ….` → `vault/events/{date}/`; `Saving from [tool]: [key takeaway].` → `vault/insights/`. Templates exist at `~/Obsidian/Research-Brain/.templates/qc-*.md`.
- **reading-queue-summarizer** — Triage and summarize a backlog of saved articles/papers. Writes each summary via `vault-writer` to `vault/research/reading-queue/YYYY-MM-DD-{slug}.md` and stages any standout claims to `_inbox/` for `memory-curator` to promote into `facts/`.
- **weekly-self-review** — End-of-week reflection / next-week planning prompt tied to your program goals.
- **conference-talk-distiller** — Turn a talk's slides/transcript into the 3 things that matter for your program.

---

## Suggested Build Order

Foundation first, then a thin starter set of topic skills on top of it.

**Phase 1 — Foundation (Category 0)**
1. `source-fetcher` + `prompt-injection-guard` — security-critical; nothing else fetches the web without these.
2. Vault scaffold at `~/Obsidian/Research-Brain/` already done (folders + `_meta/conventions.md` + schemas + templates). Open it once in Obsidian to confirm it's recognized.
3. `vault-conventions` + `vault-querier` — read side; no destructive ops, safe to ship first. Every later skill depends on these.
4. `source-registry` + `feed-watcher` — data plane.
5. `vault-writer` + `memory-curator` — write side; gated on the read side being solid.
6. `claim-extractor` + `verify-claim` — verification spine, lifted from the built-in `deep-research` pattern.
7. `seen-tracker` + `digest-writer` (now delegating to `vault-writer`) + `scheduled-agent-runner` — output plane for recurring agents.

**Phase 2 — First topic skills (compose on the foundation)**
8. `weekly-intelligence-digest` — the scheduled agent you explicitly asked for; seeds the source list other skills will reuse.
9. `voices-watcher` — the AI/product-voices roster watcher; reads `voices.csv` seeded from @natebjones's Following list; populates `vault/people/`.
10. `copilot-faq-answerer` — immediate daily-job leverage; mostly prompt, light on infra.
11. `copilot-deep-dive` + `github-platform-watch` — first two on-demand researchers.
12. `financial-regulator-watch` + `ai-governance-research` — your differentiator vs generic SDLC content.

**Phase 3 — Ops & comms (pull in as needed)**
13. `actions-workflow-hardener` + `ghas-config-reviewer` — recurring ops asks.
14. `voices-roster-curator` — enrich `voices.csv` rows with missing Substack/YouTube/blog/podcast surfaces, add new voices over time.
15. `stakeholder-update-writer` + `objection-response-library` — communication multipliers.

Everything else can be pulled in as needed.

## Open Questions Before Building

- **Delivery target for the weekly digest**: local markdown file in the vault (default — already covered), but also email or Slack? Vault-only is fine for now.
- **Sources**: do you have a curated source list (RSS feeds, newsletters, peer-bank blogs you trust) that should seed the research skills?
- **Internal systems**: any internal docs/portals (control catalog, standards, GRC tool) we should plan to pull into ops skills? (Don't share contents now — just flag what exists.)
- **Confidentiality**: should research skills be allowed to mention your employer by name in prompts, or stay generic ("a large regulated org")?
- **Voices roster scope**: is `voices.csv` only the watcher's input, or also a public-ish artifact you might share with peers? Affects whether to add columns like `recommended_for` or keep it terse.
- **`weekly-review` cadence**: default is Sunday PM. Confirm if Friday afternoon or Monday AM would suit you better.
- **`quick-capture` invocation**: from the Claude CLI, an Obsidian QuickAdd hook, or both?

## Verification

This is a planning artifact, not code. "Done" looks like: you read this list, mark which skills to build / cut / add, answer the open questions above, then a follow-up run uses `skill-creator` to build the first batch in `./.claude/skills/` **in this repo** (project-scoped, versioned with the catalog — not the global `~/.claude/skills/`). The numbered build sequence lives in `BUILD-STEPS.md`.
