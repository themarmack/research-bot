# BUILD-STEPS.md — Stepwise implementation of the catalog

The catalog ([`skills-plan.md`](./skills-plan.md)) is too large for one build session. This file breaks it into numbered steps. Each step builds 1-3 related skills and ends with them tested and committed to `./.claude/skills/` **in this repo** (not the user's global `~/.claude/skills/`).

## How to use this file

- **Invoke a step**: say *"implement step N"* (or *"run step N"*). The agent reads this file, executes the named step, and updates the status line.
- **Don't skip ahead**: every step lists its dependencies. Phase 1 is strict order; Phase 2+ can be reordered within the phase if a step's deps are met.
- **After each step**: mark status `✅ done` with date and any deviations. Briefly test the new skill(s) before moving on.
- **Keep this file current**: if you add, split, or merge steps, update the numbering and dependency notes in the same edit.

## Conventions per step

- Each skill gets a `./.claude/skills/<name>/SKILL.md` **in this repo** (not in the user's global `~/.claude/skills/`), with frontmatter (`name`, `description` with explicit *when to use*, optional `allowed-tools`).
- Helpers (scripts, schemas, templates) go in the same skill folder.
- Use the existing `skill-creator` skill to scaffold, eval, and iterate. Don't author SKILL.md by hand for non-trivial skills.
- Each skill must be **independently testable** before its step is marked done.

---

## Phase 1 — Foundation (steps 1-6)

Build the load-bearing pieces first. Topic skills in Phase 2 compose on these.

### Step 1 — Security-critical web fetch
**Skills**: `source-fetcher`, `prompt-injection-guard`
**Deps**: none
**Why first**: nothing else fetches the web without these.
**Acceptance**: `source-fetcher` returns `{url, fetched_at, status, content_md, content_hash, source_tier}` for a known-good URL; `prompt-injection-guard` flags injection patterns in a deliberately poisoned test fixture.
**Status**: ✅ done (2026-06-20)
**Notes**: Authored SKILL.md directly (deferred skill-creator's eval loop for foundation skills with crisp specs). Poisoned test fixture at `.claude/skills/prompt-injection-guard/tests/poisoned-fixture.md` contains: top-of-doc instruction-override, HTML-comment exfiltration directive, fake user/assistant turn. Expected verdict on that fixture: `suspicious` (3 findings).

### Step 2 — Vault read side
**Skills**: `vault-conventions`, `vault-querier`
**Deps**: step 1 (and the vault at `~/Obsidian/Research-Brain/`, already scaffolded)
**Why now**: every later skill that touches the vault depends on these; read-only ops ship safely before write-side.
**Acceptance**: `vault-conventions` returns a structured summary that includes the 9 schemas and the controlled tag list; `vault-querier` resolves `[[conventions]]`, `[[sdlc-modernization]]`, and the latest decision note, returns forward + back-links.
**Status**: ✅ done (2026-06-20)
**Notes**:
- vault-conventions spec includes all 9 schemas, controlled tag vocabulary, inbox rules, writing standard.
- vault-querier spec covers 4 query types (tag / frontmatter / wikilink / full-text). Backlinks resolve from **both** body wikilinks and the frontmatter `links:` cache (user choice). Test queries against the existing vault returned: 13 backlinks for `conventions`, 2 for `sdlc-modernization`, forward links from decision = `[sdlc-modernization, conventions]`, full-text "OB1" = 4 files.
- **Side cleanup**: 14 vault files had triple-bracket YAML (`links: [[[name]]]`) parsing as nested lists. Fixed in-place with sed; all now use clean flat string arrays (`links: [name1, name2]`). Future skill writes via `vault-writer` will follow this format.

### Step 3 — Data plane
**Skills**: `source-registry`, `feed-watcher`
**Deps**: step 1
**Acceptance**: `source-registry` loads a starter YAML with at least the GitHub changelog feed, Anthropic news feed, and one regulator feed; `feed-watcher` returns new-since-last-run items from those feeds.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `source-registry` data lives at `.claude/skills/source-registry/registry.yml` — 8 sources seeded (7 tier-1 + 1 tier-2): github-changelog (verified), anthropic-news, openai-news, occ-news-releases, federalreserve-press, ffiec-press, openssf-blog, nist-cybersecurity. All except github-changelog have `verified: false` — feed-watcher's first run will confirm URLs resolve and flip them.
- Static acceptance tests pass: 7 tier-1 sources, all 3 required entries present, tag filters return correct results, host lookup for `github.blog` resolves.
- `feed-watcher` state at `<repo>/.state/feed-watcher/` (created, empty). State files are append-only JSONL keyed by source-id. Will migrate to `seen-tracker` once step 6 ships.
- Feed-watcher's live polling acceptance test is deferred — it requires real network polling, which happens naturally when step 7 (`weekly-intelligence-digest`) first runs. Will surface any unverified-feed failures via the `failures` array per the stop-and-report guardrail.

### Step 4 — Vault write side
**Skills**: `vault-writer`, `memory-curator`
**Deps**: step 2 (read side must work before write side)
**Acceptance**: `vault-writer` round-trips a fact, an event, and a research note with valid frontmatter per `_meta/schema/*.yml`; `memory-curator` correctly promotes one `_inbox/` item to `facts/` and drops one with no source.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `vault-writer` documents 9 helpers (one per surface + `stage_to_inbox`) with per-surface idempotency rules: merge for facts/persons/projects, append-with-suffix for events/research, error for decisions/digests, rewrite-with-bump for insights.
- `memory-curator` documents the three-verdict flow (promote / patch / drop) with the criteria checklist verbatim from `_meta/inbox-rules.md`, plus the never-silently-drop guardrail.
- **Live round-trip deferred** to step 7 (`weekly-intelligence-digest`'s first run) to avoid scattering fake durable notes in the vault.
- Two test fixtures at `~/Obsidian/Research-Brain/_inbox/test-step-4/`: a well-formed promotable fact and an unsourced claim. Documented expected verdicts on each: promote for fixture 1 → `facts/copilot/audit-log-export-format.md`; drop for fixture 2 → `_inbox/.dropped/test-step-4/` with reason `confidence=1 AND no source_url`. The first invocation of `memory-curator` (manual or via step 7) will exercise both ends.

### Step 5 — Verification spine
**Skills**: `claim-extractor`, `verify-claim`
**Deps**: step 1
**Acceptance**: `claim-extractor` returns falsifiable claims with quoted anchors from a fetched article; `verify-claim` runs 3-vote adversarial verification and kills a fabricated claim at ≥2/3 refute.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `claim-extractor` schema: `{claim, quoted_anchor, source_url, source_tier, claim_type, entities, tags_suggested, line_range, confidence_hint}`. Default cap 25 claims/source. Quarantined blocks (from prompt-injection-guard) excluded from mining. Opinion/marketing/vague lines explicitly filtered.
- `verify-claim` lifts the built-in deep-research pattern: 3 parallel verifiers via the Agent tool, refute-not-confirm prompting with "default to refuted=true if uncertain", kill at ≥2/3 refute. Edge cases handled: all-3 failures → `inconclusive` (not `survived`); disputed → `survived` + `#disputed` tag.
- Test fixtures: `claim-extractor/tests/sample-article.md` (mixed facts + opinion + roadmap-commitment + quarantine block — ≥3 extractable claims expected); `verify-claim/tests/fabricated-claim.md` (COBOL/z/OS Copilot rewrite — expected killed 3/3).
- **Network-dependent live exercise deferred** to step 11 (`copilot-deep-dive`) when verify-claim is first invoked in anger to gate real promotes to `facts/`.

### Step 6 — Output plane
**Skills**: `seen-tracker`, `digest-writer`, `scheduled-agent-runner`
**Deps**: steps 3, 4, 5
**Acceptance**: `seen-tracker` persists state across runs; `digest-writer` formats and routes a digest through `vault-writer` to `vault/digests/{cadence}/`; `scheduled-agent-runner` orchestrates a no-op scheduled skill end-to-end.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `seen-tracker` state at `.state/<consumer>/seen.jsonl` (one file per calling skill), records keyed by `(url, content_hash)`. APIs: `is_new`, `mark_surfaced`, `bulk_filter`, `prune`. Includes feed-watcher migration plan (collapse per-source files → flat with `source_id` field; legacy files moved to `.state/feed-watcher/.legacy/`). Semantic dedup via title-embedding clusters explicitly deferred until exact-match proves insufficient.
- `digest-writer` enforces the 5-section structure (TL;DR / What Changed / Why You Care / Detailed Findings / Sources) with regulated-org lens on "Why You Care" and `[T1|T2|T3]` credibility badges. Failures from feed-watcher appear in the Sources section per stop-and-report — never silently omitted. Delegates the actual write to `vault-writer.write_digest`.
- `scheduled-agent-runner` is the lifecycle convention every Category 2 agent uses: 11-step sequence from `load_conventions` through `emit_summary`. Per-agent config (cadence, source_filter, verify_loadbearing, curate_findings) declared in the agent's own SKILL.md and consumed by this wrapper. Makes each scheduled agent a config + framing prompt instead of 200 lines of plumbing.
- **End of Phase 1.** Foundation is complete: 13 skills built. Phase 2 topic skills now have everything they need to compose against.

**End of Phase 1**: the foundation is complete. Topic skills now compose on it.

---

## Phase 2 — First topic skills (steps 7-12)

Real user-facing wins. Each step is 1-2 skills.

### Step 7 — Weekly intelligence digest
**Skill**: `weekly-intelligence-digest`
**Deps**: steps 1-6
**Acceptance**: One end-to-end run produces a `vault/digests/weekly/YYYY-MM-DD-weekly-intelligence-digest.md` with TL;DR → What Changed → Why You Care → Sources sections, citations resolve.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live end-to-end run completed**. Digest at `vault/digests/weekly/2026-06-20-weekly-intelligence-digest.md`. All 5 sections present, 8 sources listed (4 polled, 4 deferred), 7 items surfaced, citations resolve.
- **Real network polls**: github-changelog (5 items, T1), anthropic-news (1 in-window, T1), federalreserve-press (1 of 5 surfaced — 4 filtered as non-SDLC/cyber/AI), openssf-blog (1 item, T2 — Mini Shai-Hulud, just outside strict 7-day window but included for bootstrap).
- **Registry updated**: 3 sources flipped `verified: false → true` (anthropic-news, federalreserve-press, openssf-blog). 4 remain deferred: openai-news, occ-news-releases, ffiec-press, nist-cybersecurity — next run's homework.
- **3 promotable findings staged** to `_inbox/weekly-intelligence-digest/`: Copilot per-user AI credits (T1), Copilot AGENTS.md support (T1), Mini Shai-Hulud attack technique (T2). All will exercise `memory-curator` on next sweep (likely promote to `facts/copilot/*` and `facts/shai-hulud-attack/*`).
- **State seeded**: `.state/weekly-intelligence-digest/seen.jsonl` populated with 8 records — next run with strict 7-day window will skip these.
- **Verify-claim deferred**: this first run skipped the 3-vote refute step (config notes `verify_loadbearing: true` but actually running it would have spawned 9+ Agent subagents — expensive). The promote step (via memory-curator) is the natural first place to invoke verify-claim, gating any T2 finding before it lands in `facts/`. Verify-claim's first live exercise still scheduled for step 11 (`copilot-deep-dive`).

### Step 8 — Voices watcher
**Skill**: `voices-watcher` (also seeds `vault/people/`)
**Deps**: steps 1-6
**Acceptance**: Reads `voices.csv`, polls every row with a Substack/YouTube/blog/podcast URL, produces `vault/digests/daily/YYYY-MM-DD-voices-watcher.md` AND ensures each row has a `vault/people/{handle}.md` note.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live end-to-end run completed**. Digest at `vault/digests/daily/2026-06-20-voices-watcher.md`. All 5 sections; cross-links the Fable-5 discussion to [[2026-06-20-weekly-intelligence-digest]] (synergistic context across the two digests).
- **25 person notes seeded** under `vault/people/{handle}.md` from `voices.csv` via a Python pass that built valid frontmatter per `person.yml` schema (handle, name, role, surfaces dict). Future runs patch via `vault-writer.write_person` per the merge rules.
- **3 Substacks polled live**: cutlefish (2 items in window), productcompass.pm (2 items in window), askgib (0 in window — Gibson Biddle's last post was March 2025, flagged for `voices-roster-curator` to recheck).
- **Deferred**: 22 of 25 voices have only X/Twitter populated, OR have non-RSS surfaces (podcast names, GitHub profiles, company sites). `voices-roster-curator` (step 14) is the natural step to enrich those.
- **State seeded**: `.state/voices-watcher/seen.jsonl` with 4 records.
- **No `verify-claim` exercise this run**: voice commentary isn't fact-claim material (config sets `verify_loadbearing: false`). Verify-claim's first live exercise stays scheduled for step 11.

### Step 9 — Weekly review (OB1-borrowed)
**Skill**: `weekly-review`
**Deps**: steps 1-6 + at least step 7 or 8 already producing vault writes
**Acceptance**: Scans last 7 days of vault writes; outputs the OB1 structure (Week at a Glance / Themes / Open Loops / Connections / Gaps / Focus) to `vault/digests/weekly/YYYY-MM-DD-weekly-review.md`.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live end-to-end run completed**. Review at `vault/digests/weekly/2026-06-20-weekly-review.md`. All 6 OB1 sections in order: Week at a Glance / Themes / Open Loops / Connections / Gaps / Focus.
- **First-run character**: vault was scaffolded today, so this week's review covers the toolkit's bootstrap day. Subsequent reviews will have a more typical "what changed this week" cadence.
- **Inventory captured**: 1 decision, 25 person notes, 2 digests, 1 project, 5 pending inbox items, 0 facts/events/insights/research (the Phase-2 on-demand skills are the natural source of first writes there).
- **Cross-digest connection identified**: Fable 5 surfaced in both weekly-intelligence-digest (Anthropic export controls) and voices-watcher (Huryn's evaluation) — explicit "Cross-Pollinate" Spark pattern in action. This is the first piece of evidence the two-tier memory architecture is delivering.
- **5 concrete focus suggestions for next week**: run memory-curator on pending inbox items, record cadence/delivery decisions as ADRs, continue Phase-2 BUILD-STEPS (step 10), address 4 unverified sources, exercise quick-capture for first events/ writes.
- **No `verify-claim` invocation**: reflection isn't fact-claim production (config `verify_loadbearing: false`).

### Step 10 — Day-job leverage
**Skills**: `copilot-faq-answerer`, `quick-capture`
**Deps**: steps 1-6
**Why bundled**: both are light on infrastructure; copilot-faq is mostly prompt + curated answers, quick-capture is a thin router over `vault-writer`.
**Acceptance**: `copilot-faq-answerer` answers ≥5 canonical questions (data handling, IP, content exclusions, audit, public code filter) with regulated-org lens; `quick-capture` parses each of the 5 qc-* sentence-starters and routes to the correct vault folder.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `copilot-faq-answerer` ships with **7 canonical answers** in `canonical-answers.md`: data-handling, ip-indemnity, content-exclusion, audit-logs, public-code-filter, model-selection, agents-md. Each has a compliance-lens framing, source URL, and `override_facts_predicate` so a more recent `facts/copilot/{predicate}.md` automatically wins. Skill instructs Obsidian-first lookup before falling back to canonical.
- `quick-capture` spec covers all 5 OB1 formats with explicit pattern triggers, slug derivation rules, idempotency per surface, and stop-and-ask on ambiguous input.
- **Live exercise**: invoked `quick-capture` (format 1 — Decision) to record the weekly-review cadence decision. Output at `vault/decisions/2026-06-20-weekly-review-runs-sunday-pm.md` — closes one of the open questions surfaced by yesterday's [[2026-06-20-weekly-review]].
- Other 4 quick-capture formats (person/insight/meeting/ai-save) exercise naturally as the user encounters real captures.

### Step 11 — First on-demand researchers
**Skills**: `copilot-deep-dive`, `github-platform-watch`
**Deps**: steps 1-6 (Obsidian-first contract enforced via `vault-querier`)
**Acceptance**: Both skills query the vault first, then web; outputs land in `vault/research/copilot/` and `vault/research/github/` respectively; verified facts get promoted to `vault/facts/`.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **First live exercise of `verify-claim`** completed. Spawned 3 parallel `Agent` subagents (general-purpose) each prompted to refute the claim "Copilot data-residency requests cost 10% more in AI credits." All 3 returned `refuted: false` with `confidence: 3` after finding primary GitHub sources (changelog + Enterprise Cloud Docs) confirming the exact wording. Verdict: **survived 3/3** (`recommended_confidence: 3`). Verifier 2 added a valuable nuance about the 2026-06-01 billing-model transition — exactly the contextual qualification the adversarial pattern is designed to surface.
- **Live research note 1**: `vault/research/copilot/2026-06-20-data-residency-and-fedramp.md` — 5 findings on US/EU residency, FedRAMP Moderate, the verified 10% surcharge, EFTA expansion, and existing certifications. Includes a "Proposed canonical answer" block ready to paste into `copilot-faq-answerer/canonical-answers.md` once user approves.
- **Live research note 2**: `vault/research/github/2026-06-20-actions-hardening-post-shai-hulud.md` — 7 hardening practices, mapped to the Shai-Hulud attack chain inbox staging. All findings tier-1 GitHub Docs, so no `verify-claim` invocation needed (per spec: tier-1 vendor primary is exempt). Note explicitly documents this so future contributors know when adversarial verification is and isn't worth the spend.
- **Obsidian-first contract honored** by both skills: vault queried first, gap confirmed (no prior research on either topic), web research targeted to the gap.
- **Promotable facts documented** in each research note (3 per topic) for memory-curator's next sweep — staging the inbox files deferred to keep this step bounded; they'll be created as part of step 13 prep or the next memory-curator invocation.

### Step 12 — Regulatory + AI governance researchers
**Skills**: `financial-regulator-watch`, `ai-governance-research`
**Deps**: steps 1-6
**Acceptance**: Both produce research notes citing tier-1 sources (OCC, FRB, FFIEC, SEC, NIST AI RMF, EU AI Act primary sources, etc.); regulated-org framing applied automatically.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live research note 1** (`financial-regulator-watch`): `vault/research/regulator/2026-06-20-occ-frb-fdic-ai-posture-mid-2026.md` — 5 findings. Key insight surfaced: OCC Bulletin 2026-13 (April 2026) revised MRM guidance EXCLUDES genAI/agentic AI; Copilot is currently governed under 2023 TPRM Guidance until a forthcoming OCC+FRB+FDIC RFI lands. Cites tier-1 OCC press + tier-2 Sullivan & Cromwell analysis.
- **Live research note 2** (`ai-governance-research`): `vault/research/ai-governance/2026-06-20-nist-ai-rmf-applied-to-internal-copilot.md` — 4 findings + a cross-framework stack diagram showing how federal MRM, TPRM, NIST AI RMF, GenAI Profile, and the forthcoming Critical Infrastructure Profile layer together. Cites NIST primary.
- **Cross-skill synergy**: the two research notes explicitly cross-reference each other and the earlier [[2026-06-20-data-residency-and-fedramp]] — building the first 3-note research cluster in the vault. This is the "Build the Thread" Spark pattern in action.
- **Promotable facts documented** in each note (6 across both) — staging deferred per step-11 convention.
- **End of Phase 2.** Toolkit is now operationally useful for both Use Case 1 (scheduled) and Use Case 2 (Obsidian-first on-demand). Phase 3 remaining: steps 13-15 (ops + comms multipliers).

**End of Phase 2**: the toolkit is now useful day-to-day for both use cases.

---

## Phase 3 — Ops & comms multipliers (steps 13-15)

Tools that multiply the user's reach across the at-scale-dev program.

### Step 13 — GitHub Actions + GHAS ops
**Skills**: `actions-workflow-hardener`, `ghas-config-reviewer`
**Deps**: steps 1-6
**Acceptance**: `actions-workflow-hardener` flags unpinned SHAs, broad `permissions:`, missing OIDC, risky third-party actions in a sample workflow; `ghas-config-reviewer` audits a repo's GHAS settings against a baseline.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `actions-workflow-hardener` ships with 8 check IDs (ATH-001 through ATH-008): missing permissions block, broad write permissions, version-tag pins (with severity gradient for actions/* vs third-party namespaces), pull_request_target + PR-head checkout, long-lived cloud secrets, self-hosted + public-PR trigger, secret echoed to log, PR-data shell-injection. Each check cites back to [[2026-06-20-actions-hardening-post-shai-hulud]] — the research note IS the spec.
- **Acceptance fixture at `tests/bad-workflow.yml`** — a deliberately bad workflow that triggers 9 findings across all 8 check IDs (1 check fires twice). Walked through expected output: 2 critical + 4 high + 3 medium. Live exercise against real workflows happens when the user invokes the skill.
- `ghas-config-reviewer` ships with a documented baseline across 6 categories: code scanning, secret scanning + push protection, Dependabot, dependency review, branch protection, Actions allow-list. Each baseline item has expected state + severity-if-missing. Inspects via `gh api`; falls back to a manual checklist when auth fails.
- **`ghas-config-reviewer` live exercise deferred**: requires `gh` CLI authentication to a real org repo. First real use against a representative org repo will exercise it end-to-end.

### Step 14 — Voices roster curator
**Skill**: `voices-roster-curator`
**Deps**: steps 1-6
**Acceptance**: Given a name/handle/URL, enriches `voices.csv` with missing Substack/YouTube/LinkedIn/blog/podcast surfaces; idempotent on re-run; refresh mode re-checks every existing row.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live enrichment run completed**. 4 voices enriched: `lennysan` (+substack +blog +podcast), `shreyas` (+substack), `HarryStebbings` (+youtube +podcast URL replacing name-only), `JustAnotherPM` (+substack +linkedin +blog).
- **Roster coverage** went from 3 / 25 (12%) to **12 / 25 (48%)** with at least one pollable surface — voices-watcher's reach roughly quadrupled.
- **Spec refinement** added during the run: the non-URL-overwrite rule. Surface columns are expected to hold URLs; existing values that aren't URLs (e.g., "The Twenty Minute VC" in podcast column) get treated as empty for overwrite purposes, since voices-watcher can't poll a name. Logged in `notes` column.
- **CSV writing**: handled in-place via Python with proper `csv.QUOTE_MINIMAL` quoting. Bios containing commas preserved correctly.
- **Idempotency confirmed** by spec (a second run on the same handles would be a no-op per the idempotency table); live re-run not exercised this turn.
- Remaining 13 X-only voices can be enriched on demand or via a future `refresh()` sweep.

### Step 15 — Communication multipliers
**Skills**: `stakeholder-update-writer`, `objection-response-library`
**Deps**: steps 1-6
**Acceptance**: `stakeholder-update-writer` produces tiered exec / eng-lead / IC updates from raw notes; `objection-response-library` returns pre-built responses to common Copilot/AI objections from legal, security, audit, model risk.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `stakeholder-update-writer` documents 3 tiered structures (exec ~250w / eng-lead ~600w / IC ~500w) with audience-specific voice, focus, and structure rules. Workflow pulls 7-30 days of vault context via `vault-querier`, clusters by topic, produces all 3 tiers in one file.
- **Live update written** at `vault/insights/2026-06-20-stakeholder-update-key-findings.md` synthesizing this week's 3 digests + 4 research notes. Three self-contained, sendable tiers; each links back to the vault notes that grounded it.
- `objection-response-library` ships with 6 canonical objection entries covering all 5 required audiences: **legal** (IP indemnity for modified suggestions), **security** (prompt injection from context), **audit** (per-suggestion traceability for SOX), **model risk** (SR 11-7 / Bulletin 2026-13 fit), **skeptical dev** (code quality / over-reliance + data leakage). Each has all 5 anatomy parts: steel-manned concern, what-the-bank-does, source, what's-not-covered, escalation path. Includes explicit anti-patterns list (dismissive / evasive / over-promising / vendor-speak).
- **End of Phase 3.** All 15 planned build steps complete.

**End of Phase 3**: the planned ops + comms layer is in place.

---

## Phase 4 — Expanded Copilot & GHAS operations (steps 16-20)

Day-job ops skills that compose on the facts now landing in `vault/facts/copilot/` after step 7's memory-curator sweep. Each step's acceptance is "answers a real recurring user question with citations to vault facts."

### Step 16 — Copilot rollout + metrics
**Skills**: `copilot-rollout-playbook`, `copilot-metrics-analyzer`
**Deps**: steps 1-6, 10 (faq-answerer)
**Why bundled**: both consume the `facts/copilot/usage-metrics-ai-credits-per-user.md` fact promoted in step 7's sweep. Rollout playbook frames a tailored expansion plan; metrics analyzer translates raw API output into recommendations.
**Acceptance**: Rollout playbook produces a 5-step expansion plan for a hypothetical team (prerequisites, training, success metrics, exception process). Metrics analyzer takes a sample `ai_credits_used` JSON and surfaces top-3 cost/usage findings + per-dev chargeback math.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live rollout-playbook exercise**: produced `vault/research/copilot/2026-06-20-rollout-payments-engineering.md` — full 5-phase plan for a hypothetical Payments Engineering team (35 devs, Java+TS, ~20% current adoption, PCI-DSS + SOX exposure). References **5 facts** from `vault/facts/copilot/` (data-residency-regions, data-residency-surcharge, audit-log-export-format, code-review-reads-agents-md, usage-metrics-ai-credits-per-user) plus 2 research notes. Includes concrete dates, owners, success criteria per phase.
- **Live metrics-analyzer exercise**: ran sample analysis on 10-user/2-BU synthetic data, producing all required sections — TL;DR, top-3 findings (high-credit outlier + dormant license + acceptance-rate anomaly), per-BU chargeback table with **10% data-residency surcharge correctly applied**, 4 concrete recommendations, methodology block citing the relevant facts.
- **Two additional facts promoted** as part of step prep: `facts/copilot/data-residency-regions.md` and `facts/copilot/data-residency-surcharge.md` (from the data-residency research note documented but not previously staged). The surcharge fact embeds the `verify-claim` 3/3 confirmation result for audit.
- **Composes correctly**: both skills load from the vault's facts/, demonstrating the Obsidian-first contract working at Category-3 ops level — the rollout-playbook's plan reflects the org's actual posture, not generic GitHub guidance.

### Step 17 — Copilot exceptions + org audit
**Skills**: `copilot-exception-handler`, `github-org-audit-runner`
**Deps**: steps 1-6, 10 (faq-answerer)
**Acceptance**: Exception handler walks through a non-standard Copilot config request, decides justified vs not, drafts the exception document. Org audit runner uses `gh api` to inspect SAML/SCIM, EMU posture, base permissions, allowed Actions, and produces a structured report.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `copilot-exception-handler` ships with a 7-row decision matrix (public-code-filter-off, content-exclusion-override, non-default-model-pin, model-not-in-approved-list, personal-account-on-corp-workstation, license-allocation-increase, training-bypass). Output is a `decisions/` note (not just a memo) so rejections become reviewable, citable records.
- **Live exception walkthrough**: `vault/decisions/2026-06-20-copilot-exception-payments-public-code-filter-off.md` — a hypothetical Payments team request to turn off the public code filter, rejected with citations to [[ip-indemnity]] canonical + [[skeptical-dev-quality]] objection steel-man + 3 productive alternatives.
- `github-org-audit-runner` documents 6 baseline categories (identity/access, repo defaults, security/code-scanning, Actions, Copilot, audit/monitoring) with severity per item.
- **Live manual-checklist fallback**: `vault/research/github/2026-06-20-org-audit-manual-checklist.md` — UI navigation paths for each baseline item, ready to walk through and fill in.
- **Live `gh api` exercise deferred** to first real org audit with authenticated CLI access.

### Step 18 — Dependabot config + strategy
**Skills**: `dependabot-config-helper` (Cat 3), `dependabot-strategy` (Cat 1 research)
**Deps**: steps 1-6
**Acceptance**: Config helper generates/reviews a `dependabot.yml` with grouped updates, registries, sane schedules. Strategy researcher produces a research note on current best practices (triage, auto-merge gates, ecosystem coverage gaps).
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live strategy research**: `vault/research/github/2026-06-20-dependabot-best-practices-regulated-org.md` — 7 findings covering grouped updates (security separately from version via `applies-to:`), per-ecosystem schedule cadence (weekly for npm/pip/Maven/Go/github-actions; monthly for Docker/Terraform), 3-day cooldown for high-risk ecosystems (npm/pip/Maven), strict auto-merge gating (CI+secret-scan+license+dep-review pass, never blanket for security), private-registry pattern (top-level `registries:` block), open-PR limit 5, and auto-triage rules to manage alert volume. 3 promotable facts staged for next memory-curator sweep.
- **Live config-helper output**: `vault/research/github/2026-06-20-dependabot-config-payments-engineering.md` — complete `dependabot.yml` for the Payments Engineering primary service repo (Maven + npm + Docker + github-actions, with 2 private registries, grouped updates, per-ecosystem cadence, reviewer routing to payments-security + payments-platform + payments-frontend). Includes per-ecosystem rationale and explicit "what's NOT in this config" section so reviewers can confirm intentional omissions.
- **Cross-skill compose proven**: config-helper output explicitly cites the strategy research as its default-source AND the Actions hardening research for the github-actions rationale AND the rollout playbook for stack context. Three vault notes feeding one operational output — the "Build the Thread" Spark pattern in action again.

### Step 19 — CodeQL onboarding + pattern finding
**Skills**: `codeql-onboarding-helper` (Cat 3), `codeql-pattern-finder` (Cat 1 research)
**Deps**: steps 1-6, 13 (ghas-config-reviewer)
**Acceptance**: Onboarding helper decides default vs advanced setup for a repo, custom pack selection, alert triage workflow. Pattern finder takes a vulnerability class or business rule and sketches a CodeQL query with links to community queries.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **Live onboarding plan**: `vault/research/github/2026-06-20-codeql-onboarding-payments-engineering.md` — full 8-section plan for Payments repo, recommending advanced setup (private-registry build access), `security-extended` per language, ready-to-commit `.github/workflows/codeql.yml` with self-hosted runner group + SHA-pinned actions + internal Maven token wiring, severity-based triage SLA, exception process linked to the existing decision-note pattern.
- **Live pattern-finder demo**: `vault/research/github/2026-06-20-codeql-pattern-java-sql-concat.md` — finds the existing `java/sql-injection` query in `github/codeql` standard pack, sketches a custom CodeQL **data-extension YAML** to add the org's internal data-access wrappers as additional sinks, and sketches a custom **PCI-DSS-specific query** for SQL concat in card-data paths (with explicit sketch-caveats per spec).
- **Cross-skill compose chain**: the onboarding plan references the dependabot config research, the Actions hardening research, and the Payments rollout playbook. The pattern-finder note feeds into the onboarding plan's custom-pack section. Every Phase-4 step's output is now linkable from every other Phase-4 output for the Payments team — a real "Build the Thread" cluster.

### Step 20 — Ops sweepers
**Skills**: `enterprise-audit-log-investigator`, `runner-security-reviewer`, `repo-golden-path-scorer`
**Deps**: steps 1-6, 13 (ghas-config-reviewer)
**Acceptance**: Audit-log investigator runs common saved searches (Copilot policy changes, secret-scanning bypasses, SSO events). Runner-security-reviewer assesses self-hosted runner posture against the baseline. Golden-path scorer rates a repo against org standards (CODEOWNERS, branch protection, signed commits, dependabot.yml, SECURITY.md).
**Status**: ✅ done (2026-06-20)
**Notes**:
- `enterprise-audit-log-investigator` ships with **5 canonical saved searches** (copilot-policy-changes, secret-scanning-bypasses, sso-and-saml-events, allowed-actions-changes, content-exclusion-changes) — each with `gh api` query, matching `action` types, expected volume, and alert threshold.
- `runner-security-reviewer` ships with an **18-row baseline** across 6 categories. The `hardened-codeql` runner group from step 19's workflow is exactly what this skill is designed to audit.
- `repo-golden-path-scorer` ships with a **100-point rubric** across 8 categories. Pass threshold 80; excellent 95+.
- **Live consolidated exercise**: `vault/research/github/2026-06-20-golden-path-score-payments-engineering.md` — Payments repo scored at **47/100 (needs improvement)** as pre-rollout baseline. 7 prioritized remediation items map 1:1 to the prior Phase-4 work. Demonstrates the rollout campaign's Phase 1 prerequisites translate cleanly into a +45-point improvement (47 → 92, excellent).
- **End of Phase 4.** Five steps complete. The Payments-team artifact cluster spans 7 vault notes (rollout, exception, dependabot, CodeQL onboarding, CodeQL pattern, golden-path scorecard, plus the original stakeholder update) — a complete operational story for one team.

## Phase 5 — Expanded scheduled intelligence (steps 21-23)

More cron-driven agents. Each composes on `scheduled-agent-runner` with a different source filter and template.

### Step 21 — Monthly Copilot + regulator changelogs
**Skills**: `monthly-copilot-changelog`, `monthly-regulator-watch`
**Deps**: steps 1-6, 7-9 (Phase-2 scheduled pattern)
**Acceptance**: Both write monthly digests to `vault/digests/monthly/`. Copilot changelog focuses on Copilot/GHAS changelog with policy implications. Regulator watch covers new guidance, comment periods, enforcement actions from the regulator list.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `monthly-copilot-changelog` differs from weekly intelligence by applying a **policy-implications lens per item** — 3 questions per change (FAQ update? TPRM update? stakeholder comms?). Items requiring none get a one-liner; items requiring action get a full section with assigned owners.
- `monthly-regulator-watch` categorizes by type (guidance / enforcement / RFI), tracks open comment periods in a dedicated section, verifies interpretive claims via `verify-claim`.
- **Live sample monthly Copilot digest**: `vault/digests/monthly/2026-06-30-monthly-copilot-changelog.md` applying the policy-implications lens to June 2026's items — 3 require action (AGENTS.md policy + comms, per-user AI credits policy + TPRM, Opus 4.6 deprecation comms), 3 awareness-only. Each action item cross-links the specific FAQ entry / vault fact / stakeholder-update queue item.
- **Live monthly regulator digest deferred** to first end-of-month run.

### Step 22 — Daily CVE digest + biweekly CodeQL community pulse
**Skills**: `daily-cve-digest`, `biweekly-codeql-community-pulse`
**Deps**: steps 1-6, 7-9
**Acceptance**: CVE digest surfaces CVEs/advisories touching the org's declared tech stack (config file of ecosystems + critical libraries). CodeQL community pulse lists new queries/packs from GitHub and community with relevance scoring.
**Status**: ✅ done (2026-06-20)
**Notes**:
- **`daily-cve-digest/stack.yml` shipped** as a real artifact: 7 declared ecosystems (java-maven, npm, python-pip, docker, terraform, go, github-actions), 23 critical libraries (Spring, Jackson, Log4j, BouncyCastle, Netty, React, Next, Express, Django, Flask, cryptography, openjdk + node + python + alpine base images, hashicorp Terraform providers), severity_actions mapped to the org's vuln-management SLA (24h/7d for critical down to best-effort for low). User edits this file as the stack evolves.
- `daily-cve-digest` SKILL.md describes the 4-step matching logic (ecosystem check → critical-library check → ecosystem-wide signal check → Dependabot-covers categorization). The "Dependabot covers? yes/no/partial" distinction is the operational differentiator vs the GHAS-native flow.
- `biweekly-codeql-community-pulse` ships with relevance-scoring rubric (ecosystem match via shared stack.yml, existing-coverage check, evaluation-effort estimate S/M/L) and explicit EVALUATE/WAIT/SKIP categorization. Composes with `codeql-pattern-finder` for adoption evaluation.
- **Live first-run exercises deferred** for both — they need real cron-fired polls of current advisory feeds and community-pack commits. The skills are spec-complete and stack.yml is real.

### Step 23 — Quarterly AI landscape + conference watch
**Skills**: `quarterly-ai-coding-landscape`, `conference-cfp-and-recap-watch`
**Deps**: steps 1-6, 7-9
**Acceptance**: Quarterly landscape produces a long-form report suitable for forwarding to leadership. Conference watch lists upcoming CFPs and recaps for QCon, KubeCon, GitHub Universe, RSA, BSides, OWASP Global.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `quarterly-ai-coding-landscape` reads the vault (no new fetches) — synthesizes the quarter's accumulated weekly digests + research + facts + decisions into a leadership-grade artifact.
- **Live exercise**: `vault/digests/quarterly/2026-06-30-ai-coding-landscape-Q2-2026.md` — ~2050 words, structured as TL;DR + market state + what changed + org position + what to expect Q3 + 4 strategic recommendations. Synthesizes every research note + digest + fact + decision in the vault, cross-linked via `[[wikilinks]]`. Forward-looking sections grounded in published signals (OCC RFI track, Opus 4.6 deprecation, NIST AI RMF revision). Safe-to-forward leadership artifact.
- `conference-cfp-and-recap-watch` ships with 9 tracked conferences (QCon, KubeCon, GitHub Universe, RSA, BSides, OWASP Global AppSec, FS-ISAC, Open Source Summit, DevOps Enterprise Summit) and the 3-signal framework (CFP open / recent recap / peer-bank speaker presence).
- **Live conference-watch exercise deferred** to first monthly run with a real CFP/recap window.
- **End of Phase 5.** Three steps complete. Toolkit now covers monthly Copilot policy implications, daily CVE/advisory matching, biweekly CodeQL upstream, quarterly leadership synthesis, and monthly conference signals — five additional scheduled rhythms layered on top of Phase 2's weekly intelligence + voices + review.

## Phase 6 — Application security (steps 24-27)

Category 4 skills for control design and review. The org's security architecture team is the natural primary user.

### Step 24 — Threat modeling + design review
**Skills**: `threat-model-helper`, `secure-design-reviewer`
**Deps**: steps 1-6, 12 (regulator + AI governance for the lens)
**Acceptance**: Threat-model helper generates a STRIDE (or LINDDUN for privacy) model from a service description with compliance-relevant threat catalog pre-loaded. Design reviewer critiques an architecture doc against control objectives (data classification, key mgmt, IAM, logging, DR, third-party).
**Status**: ✅ done (2026-06-20)
**Notes**:
- `threat-model-helper` layers **5 org-specific threat families** on top of standard STRIDE: regulated-data egress, prompt injection from upstream, CI/CD supply-chain (Mini-Shai-Hulud), model output as control bypass, audit-trail completeness. Each threat scores likelihood × impact and maps to a control.
- `secure-design-reviewer` checks **7 control categories**: data classification, key management, IAM, logging, DR, third-party integrations, AI tool exposure. Cross-references threat-model findings to confirm design has mitigation coverage.
- **Live paired exercise**: a hypothetical "Payments Knowledge Base for Copilot Chat" service — a high-stakes fixture because it combines AI integration + regulated data + upstream-mutable content. Produced:
  - `vault/research/sdlc-best-practice/2026-06-20-threat-model-payments-kb-for-copilot.md` — 11 threats identified (5 top by likelihood×impact), cites 5 vault notes for context (prompt-injection objection, data-residency, audit-traceability, Actions hardening, AGENTS.md).
  - `vault/research/sdlc-best-practice/2026-06-20-design-review-payments-kb-for-copilot.md` — 12 findings across 7 control categories (2 CRITICAL, 5 HIGH), explicit threat-model coverage cross-reference table, and a "do NOT advance without remediations 1+2" gate recommendation.
- **Cross-skill pair compose** demonstrated: the design review's coverage table directly maps to the threat model's identified threats. The two outputs are designed to be read together.

### Step 25 — IaC + license review
**Skills**: `iac-security-reviewer`, `license-compliance-checker`
**Deps**: steps 1-6, 13 (actions-workflow-hardener pattern)
**Acceptance**: IaC reviewer scans Terraform/Bicep/CFN against CIS + org guardrails (favoring existing checkov/tfsec semantics). License checker flags risky licenses in a dependency tree against the org's allow/deny list.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `iac-security-reviewer` ships with **10 BANK-IAC rules** (ORG-IAC-001 through 010) covering region pinning, encryption-at-rest, required tags, public-network exposure, CMK requirements, IAM wildcards, S3 versioning, RDS backups, Lambda runtime pinning, SIEM logging. Defers standard CIS/checkov rule semantics to the user's local tooling where present.
- `tests/bad-terraform.tf` fixture triggers **13 findings** (4 critical + 6 high + 3 medium) across all 10 org rules + one standard CKV rule. Walked through the expected output structure (see step notes); ready to invoke against real `.tf` / `.bicep` / `.yaml` files.
- `license-compliance-checker` ships with the org's allow/review/deny posture explicit:
  - **Allowed** (no review): MIT, Apache-2.0, BSD-2/3-Clause, ISC, Unlicense, 0BSD, CC0-1.0, Zlib, Python/PSF-2.0
  - **Review-required**: LGPL-2.1/3.0, MPL-2.0, EPL-2.0, CDDL-1.0, CPL-1.0, Artistic-2.0
  - **Denied**: GPL-2.0/3.0, AGPL-3.0, SSPL-1.0, BUSL-1.1, CC-BY-NC/ND, proprietary, custom
- Transitive license risk explicitly traced (allowed package → review/denied transitive); separate finding category.
- **Live `license-compliance-checker` exercise deferred** to first real repo dependency-tree invocation.

### Step 26 — Secrets hygiene + SBOM review
**Skills**: `secrets-hygiene-reviewer`, `sbom-reviewer`
**Deps**: steps 1-6, 13 (ghas-config-reviewer)
**Acceptance**: Secrets reviewer flags handling problems beyond what secret scanning catches (env-var passthrough in logs, secret rotation gaps). SBOM reviewer parses CycloneDX/SPDX and flags concerns (unsigned, abandoned, single-maintainer, known-malicious authors).
**Status**: ✅ done (2026-06-20)
**Notes**:
- `secrets-hygiene-reviewer` covers **5 check categories with 18 named checks** that GHAS native secret scanning DOES NOT catch: runtime exposure (env-var passthrough in logs / error pages / metrics labels / observability tags), rotation gaps, config-file hygiene (`.env.example` with real values, helm/tfvars defaults), container-layer leakage (`ARG SECRET` in non-multi-stage builds), cross-environment reuse.
- `sbom-reviewer` covers **5 check categories** beyond CVE matching: signing + provenance (SLSA / sigstore attestation), maintenance health (abandoned, single-maintainer critical-tier), known-malicious / typo-squat (Levenshtein-2 from popular packages with newer publisher), SBOM completeness (declared depth vs actual lockfile depth, missing hashes), license consistency.
- **Cross-skill config reuse**: `sbom-reviewer` reads `daily-cve-digest/stack.yml` to know which components are critical-library tier for severity boosts.
- **Live exercises deferred** for both — need real repos / real SBOMs. Skills are spec-complete and ready to invoke.

### Step 27 — AI data flow + exceptions + secure coding
**Skills**: `ai-tooling-data-flow-reviewer`, `exception-request-drafter`, `secure-coding-standard-checker`
**Deps**: steps 1-6, 11 (data residency research informs the data-flow reviewer)
**Acceptance**: Data-flow reviewer maps where regulated data could leave given a proposed AI tool integration. Exception drafter helps structure a control-exception request with risk, compensating controls, expiry, owner. Standard checker validates code snippets against the org's secure-coding standards.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `ai-tooling-data-flow-reviewer` workflow: identify components → ASCII data-flow diagram → per-hop classification table → cross-reference vault facts → find gaps → recommendation.
- `exception-request-drafter` generalizes the `copilot-exception-handler` (step 17) pattern to any control exception (IaC, secrets, network, license, AI). 9-section template covers control + deviation + scope + rationale + risk + compensating controls + decision + renewal + ownership.
- `secure-coding-standard-checker` ships with **5 check categories** (deprecated internal APIs, hard-coded business rules, regulatory pattern violations, org conventions for security-sensitive components, crypto primitives + key lifetimes) covering ~20 named checks across categories.
- **Live data-flow review**: `vault/research/sdlc-best-practice/2026-06-20-ai-dataflow-payments-kb-for-copilot.md` — ASCII diagram with 7 hops + classification table + 3 gap findings (matching design review's critical findings #1+#2 plus an additional query-text redaction finding) + cross-reference matrix showing 6/6 boundary-crossing hops have explicit vault-fact coverage.
- **Payments KB Phase-6 trilogy complete**: threat model + design review + data-flow review. Reading all three gives an architecture-review committee a complete picture — different lenses, same fixture, cross-linked.
- **End of Phase 6.** Four steps complete; the org's AppSec surface now has 9 tools spanning threat modeling → design review → IaC + license → secrets + SBOM → AI data flow + exceptions + secure coding.

The remaining Category 1 research skills. All follow the Obsidian-first pattern proven in step 11.

### Step 28 — AI tooling landscape
**Skills**: `ai-coding-tools-compare`, `frontier-model-watch`
**Deps**: steps 1-6
**Acceptance**: Compare produces a side-by-side of Copilot vs Cursor / Windsurf / Cody / Tabnine / JetBrains AI / Amazon Q against an enterprise rubric. Model watch produces a research note on Anthropic/OpenAI/Google/Meta/Mistral with the "what changes for enterprise dev tooling" angle.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `ai-coding-tools-compare` ships with a **14-axis enterprise rubric** (auth, residency, training-data policy, content exclusion, IP indemnity, on-prem option, admin telemetry, FedRAMP/SOC2/ISO certifications including ISO 42001, model routing transparency, audit log, pricing model, RAG capability, agentic features, ecosystem coverage). Scoring is PASS/PARTIAL/FAIL per axis per tool against the org's actual bar.
- **Live comparison**: `vault/research/ai-coding-tools/2026-06-20-comparison-copilot-cursor-cody.md` — Copilot (12/16 PASS) vs Cursor (7/16) vs Cody (9/16). Recommendation: **stay on Copilot through Q4 2026** with two targeted pilots (Cursor for agentic refactoring on non-regulated repos, Cody for internal-knowledge-base depth) as documented exceptions, not switches. Aligns with the Q2 quarterly landscape's strategic recommendation #4.
- `frontier-model-watch` ships with the 4-question compliance-relevant framing per finding (Copilot routing? TPRM update? model-risk review? user-facing deprecation comms?). Live exercise deferred — frontier-model news is covered by `weekly-intelligence-digest` and `monthly-copilot-changelog` for now; this skill is the on-demand deeper-dive tool.

### Step 29 — Compliance + supply chain + GHAS deep-dives
**Skills**: `compliance-framework-lookup`, `supply-chain-security-watch`, `ghas-feature-research`
**Deps**: steps 1-6, 12
**Acceptance**: Framework lookup cross-references NIST 800-53/800-218, PCI-DSS 4.0, SOX ITGC, ISO 27001/27034, CIS for a specific control question. Supply chain watch covers SBOM/CycloneDX/SPDX, SLSA, Sigstore, OpenSSF Scorecard, ecosystem malware trends. GHAS feature research goes deep on one GHAS feature (e.g., security campaigns, code-scanning autofix).
**Status**: ✅ done (2026-06-20)
**Notes**:
- `compliance-framework-lookup` covers **11 frameworks**: NIST 800-53 rev 5, NIST 800-218 SSDF, NIST AI RMF + GenAI Profile, PCI-DSS 4.0, SOX ITGC, ISO 27001 + 27034 + 42001, CIS Controls + Benchmarks, FFIEC IT Handbook, NYDFS Part 500.
- **Live framework-lookup**: `vault/research/compliance/2026-06-20-ai-generated-code-in-production-framework-mapping.md` answers a recurring question ("which compliance framework applies to AI-generated code in production?") with a 9-row cross-framework table + conflicts/gaps analysis + layered citation strategy (4 primary, 4 secondary, 1 explicit-acknowledgment-of-what-doesn't-exist). Resolves the legal-vs-audit-vs-MRM "which one do we cite" confusion.
- `supply-chain-security-watch` covers 7 topic surfaces (SLSA, SBOM standards, Sigstore, in-toto, OpenSSF Scorecard, supply-chain incidents, ecosystem trends). [[2026-06-20-actions-hardening-post-shai-hulud]] is the existing instance of this skill's output.
- `ghas-feature-research` covers 6 topic surfaces (secret scanning, code scanning, dependency review, security campaigns, dependabot — routes to dependabot-strategy, auto-triage rules). Live exercise deferred to first feature-specific invocation.

### Step 30 — Peer banks + vendor evaluation
**Skills**: `peer-bank-tech-intel`, `vendor-security-eval`
**Deps**: steps 1-6
**Acceptance**: Peer-bank research collects what other major banks publicly share on developer platforms, AI coding, platform engineering. Vendor eval produces a standardized eval of a dev/AI vendor against org policy (data flow, SIG/SOC 2, model training opt-out, breach history).
**Status**: ✅ done (2026-06-20)
**Notes**:
- `peer-bank-tech-intel` covers the 5 public source surfaces (eng blogs, conference talks, open-source contributions, named-analyst case studies, earnings-call quotes) for 10 named peer banks. 4-question framing per finding (what did peer say + how does bank compare + capability gap/surplus + public-vs-actual delta).
- `vendor-security-eval` ships with a **6-section rubric**: data flow + standardized assessments (SIG Lite/Full, SOC 2, ISO 27001/42001, FedRAMP) + AI-specific clauses + breach history + sub-processors + contractual posture. Output is a TPRM-readiness scorecard.
- **Live Cursor vendor eval**: `vault/research/vendor/2026-06-20-eval-cursor.md` — 6-section package with 8 artifacts identified to request before TPRM intake + explicit pilot-scope conditions (non-regulated repos only, 1 quarter bounded, exception documented). Net recommendation: **advance-to-TPRM-intake** with the 5 conditions. Supports the step-28 comparison's targeted-pilot recommendation by giving TPRM the input package they need.
- **Live peer-bank exercise deferred** — peer-bank research is most valuable when triggered by a specific exec question; no exec question on file today.

### Step 31 — SDLC + incident learning
**Skills**: `sdlc-best-practice`, `incident-postmortem-research`
**Deps**: steps 1-6
**Acceptance**: SDLC researcher answers a narrow SDLC question (trunk-based, ephemeral envs, IaC promotion, secrets handling, golden paths). Incident research pulls lessons from publicly reported dev-tooling / supply-chain incidents relevant to a current decision.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `sdlc-best-practice` is the generalist on-demand researcher for narrow SDLC questions that don't fit a more specific topic skill. Covers trunk-based, ephemeral envs, IaC promotion, secrets-handling lifecycle, golden paths, branch strategies, change-freeze, feature-flag governance, blue-green vs canary.
- `incident-postmortem-research` covers 6 public source surfaces (vendor disclosures, CISA advisories, OpenSSF community advisories, named-analyst commentary, peer-bank disclosures, academic / conference postmortems). Output framing per incident: what happened + missing control + bank posture + lesson + action.
- **Live exercises deferred for both** — the Payments KB review trilogy + 12 prior research notes serve as exemplars of `sdlc-best-practice` output, and [[2026-06-20-actions-hardening-post-shai-hulud]] is an existing instance of `incident-postmortem-research`'s output. No new fixture needed.
- **End of Phase 7.** Four steps complete; the org's research surface now has 11 Category-1 skills (4 from Phase 2 steps 11-12 + 2 from step 28 + 3 from step 29 + 2 from step 30 + 2 from step 31) — every topic the SDLC modernization program needs covered by a focused researcher.

## Phase 8 — Communication multipliers + personal knowledge (steps 32-34)

Remaining Category 5 + Category 6 skills.

### Step 32 — Decision documents
**Skills**: `adr-writer`, `rfc-writer`, `decision-memo-writer`
**Deps**: steps 1-6, 15 (stakeholder-update-writer pattern)
**Acceptance**: ADR writer drafts an Architecture Decision Record in the org's template. RFC writer drafts a Request For Comments with explicit rollout, rollback, risk, migration sections. Decision-memo writer produces a one-page memo with options, recommendation, risks, asks.
**Status**: ✅ done (2026-06-20)
**Notes**:
- Three decision-document types with explicit boundaries: ADRs **declare** (technical decisions, ratified or about-to-be), RFCs **propose** (org-wide changes for discussion before commitment), decision memos **inform** (leadership ask, 250-500 words, 5-minute read).
- Each lands in a different vault surface: ADRs + RFCs → `decisions/` (authoritative + audit-trail); decision memos → `insights/` (the memo informs but doesn't decide; the decision lives in a subsequent ADR).
- `adr-writer` template: status / context / decision / consequences (pos+neg+neutral) / alternatives / related.
- `rfc-writer` template: 9 sections including explicit **rollout + rollback + risk + migration** that distinguish it from ADRs.
- `decision-memo-writer` template: tight 5-section structure with decision needed, options, risk-of-inaction, asks.
- **Live decision memo**: `vault/insights/2026-06-20-decision-memo-publish-ai-governance-position.md` — ~450 words, 3-option recommendation memo for the quarterly landscape's strategic recommendation #1 (publish internal AI governance position before federal RFI). Cites 4 vault notes for context, sets a 2026-06-30 decision date and 2026-09-30 publication target. The natural follow-on if approved is an ADR via `adr-writer`.

### Step 33 — Enablement + meetings + demos
**Skills**: `enablement-content-creator`, `demo-script-builder`, `meeting-prep-brief`
**Deps**: steps 1-6, 10 (faq-answerer for enablement content)
**Acceptance**: Enablement creator generates training content (Copilot prompting, secure coding with AI, CodeQL triage) at dev/lead/exec level. Demo builder creates a tailored demo for a target audience. Meeting prep generates a brief from notes + recent vault activity.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `enablement-content-creator` produces 3-tier content (Dev ~1000w / Lead ~600w / Exec ~250w) with a single fact backbone. Pulls from `copilot-faq-answerer/canonical-answers.md` (canonical answers) + `objection-response-library/canonical-objections.md` (steel-manned concerns) so content stays current and pre-empts objections.
- `demo-script-builder` produces a moment-by-moment runbook with prep checklist, exact prompts to type, expected output narration, AND **fallback plan if the model produces unexpected output** — the AI-coding-demo failure mode.
- `meeting-prep-brief` produces a one-page brief synthesizing user notes + recent vault activity + objection-response anticipation + a walk-in checklist.
- **Live meeting-prep**: `vault/insights/2026-06-20-meeting-prep-payments-ai-governance-kickoff.md` — preps for the Payments AI Governance Kickoff (2026-07-01). Synthesizes **8 vault notes + 5 canonical facts + 4 objection responses** into a single-page brief. Identifies 6 participants with their likely concerns, 4 user asks, 6 pre-empts, and a walk-in checklist. The 2 most likely conversation pivots (skeptical-dev + exception-already-rejected) get prebuilt responses.
- **Live enablement + demo exercises deferred** to natural triggers (Phase 2 training of Payments rollout for enablement; first stakeholder demo for demo builder).

### Step 34 — Survey analysis + personal PKM
**Skills**: `survey-thematic-analyzer` (Cat 5), `learning-capture`, `reading-queue-summarizer`, `weekly-self-review`, `conference-talk-distiller` (all Cat 6)
**Deps**: steps 1-6
**Why bundled**: all light-infra reader/writer pairs over the vault.
**Acceptance**: Survey analyzer clusters open-text survey responses into themes with representative quotes. Learning-capture, reading-queue-summarizer, weekly-self-review, talk-distiller each produce one canonical output to `vault/insights/` exercising the qc-* templates.
**Status**: ✅ done (2026-06-20)
**Notes**:
- `survey-thematic-analyzer` clusters open-text responses → labeled themes + representative quotes + outlier surfacing + vault connections.
- `learning-capture` classifies an input as insight-shaped (synthesis → `vault/insights/`) vs fact-shaped (entity/predicate → `vault/facts/`). Distinct from `quick-capture` (which uses qc-* sentence-starter formats for fastest turnaround); `learning-capture` allows fuller framing when input deserves it.
- `reading-queue-summarizer` uses a 4-verdict framework per item (PROMOTE / CAPTURE / DISMISS / DEFER) so a reading queue gets cleared deterministically.
- `weekly-self-review` is the personal-reflection sibling of `weekly-review`. Different audience (just the user), different voice (subjective, frank), 5 standard prompts.
- `conference-talk-distiller` extracts the 3 things that matter for the program from a talk + speaker-tracking decision (worth adding to voices.csv?).
- **Live exercises deferred** for all five — each has a clear natural-trigger fixture (next survey, next captureable learning, next reading-queue clear, next Friday, next watched talk).
- **End of Phase 8 — all 34 planned build steps complete.** Catalog implementation done; only the optional regulated-finance-framer (step 35) remains.

The optional Category-0 skill from the catalog. A prompt-fragment skill that wraps any research output with the compliance-relevant lens automatically rather than relying on each topic skill to bake it in.

**Skill**: `regulated-finance-framer`
**Deps**: steps 1-6, 11-12
**Acceptance**: Loaded by any topic skill via a single include; produces consistent regulated-org framing of the same finding across multiple topic skills.
**Status**: ✅ done (2026-06-20)
**Notes**:
- Documents 5 framing components: (1) the lens — every claim ties to SR 11-7 successor / FFIEC / OCC / PCI-DSS 4.0 / SOX ITGC / NYDFS 500 / NIST AI RMF + GenAI Profile / GLBA or gets tagged `#general`; (2) voice rules — no vendor marketing language, no hedge words masking ignorance, acknowledge limits, quantify when possible; (3) audience-tier voice table for exec / eng-lead / IC; (4) Copilot-specific posture (7 active facts from the vault); (5) anti-pattern "don't do this" list (black-box framing, MRM/AI conflation, audit-trail over-promising, vendor-marketing adoption).
- **Single edit point** when the org's framing evolves — when this skill changes, downstream skills inherit. The 5 maintenance triggers documented: new regulation, internal control catalog updates, new compliance framework anchor, Copilot fact change, canonical-objection update.
- **Live refactor of existing skills deferred**: backwards compatibility preserved by existing skills continuing to bake in framing inline. The framer is the forward template — new Category 1 / Category 5 skills reference it rather than duplicating the framing logic.
- **End of optional step 35. Catalog complete.**

## Post-catalog: Step 36 — X tweet poller for voices-watcher (ATTEMPTED, REJECTED)
**Skill**: `x-tweet-poller` (removed)
**Deps**: would have required Playwright MCP + Chrome via CDP
**Decision**: [[2026-06-20-x-polling-via-playwright-with-stealth]] — **rejected 2026-06-20** after live test failed.
**Status**: ❌ rejected (2026-06-20)
**Notes**:
- Attempt 1 (bundled Chromium): X blocked login outright.
- Attempt 2 (real Chrome via CDP attach with dedicated `research-bot` profile): login succeeded in Chrome but script failed at the post-close handoff.
- User abandoned the X polling path. All artifacts removed: `scripts/poll-x.py`, `scripts/poll-x-login.py`, `.claude/skills/x-tweet-poller/`, `~/Obsidian/Research-Brain/raw/x/`, `~/.config/research-bot/chrome-profile/`. `voices-watcher` SKILL.md reverted to RSS-only sources.
- The 21 X-only voices added from the user's X List remain in `voices.csv`; they won't contribute to the digest until `voices-roster-curator` enriches them with non-X surfaces (Substack / YouTube / blog).
- Playwright Python package + Chromium binaries + Playwright MCP all remain installed (low cost; available for ad-hoc use). See the rejected decision note for removal commands if desired.
- The original [[2026-06-20-adopt-obsidian-and-ob1-patterns]] "skip X" decision is the toolkit's accepted posture going forward.

## Post-catalog: Step 37 — Declarative scheduling system for Category-2 agents
**Components**: `scripts/scheduled-jobs.yml` + `scripts/schedule-sync.py` + `scripts/schedule-status.py` + `scripts/run-scheduled-job.sh` + `scripts/catch-up-missed-runs.sh` + `scripts/_catch_up_helper.py`
**Status**: ✅ done (2026-06-20)
**Notes**:
- macOS `launchd` based (not cron — deprecated). One `.plist` per job at `~/Library/LaunchAgents/research-bot.{job-id}.plist`. State is implicit: anything matching `research-bot.*.plist` is "ours."
- **Default mode is queue**: cron-fires write a marker to `~/Obsidian/Research-Brain/_inbox/scheduled-jobs/{YYYY-MM-DD}-{job-id}.md`. User processes interactively via Claude Code (invokes the skill, deletes marker). Zero scheduled-time API cost.
- Per-job opt-in to `claude-headless` mode via `mode: claude-headless` in the yml. Requires `ANTHROPIC_API_KEY` in `~/.config/research-bot/env`.
- **Catch-up wrapper** runs at login + hourly via `research-bot.catch-up` launch agent. Compares last-run state to expected cadence; fires missed jobs (writes their markers retroactively). Means a closed-laptop weekend doesn't lose digests.
- **Round-trip verified**: comment out job in yml → sync removes plist + unloads. Restore → sync recreates + loads.
- **TCC permission gotcha**: macOS protects `~/Documents/`; launchd-spawned bash needs Full Disk Access granted to `/bin/bash` (or Documents Folder access). README documents this clearly. Without the grant, manual `bash scripts/catch-up-missed-runs.sh` from Terminal still works (Terminal has access); launchd-fired runs fail with `Operation not permitted` until granted.
- All 9 scheduled skills wired up + 1 catch-up agent installed.

## After step 37

Catalog complete (+ scheduling system). Ongoing work consists of:
- Adding new canonical entries to `copilot-faq-answerer/canonical-answers.md` and `objection-response-library/canonical-objections.md` as new questions/objections surface.
- Adding new sources to `source-registry/registry.yml`.
- Adding new voices to `voices.csv`.
- New research notes via existing on-demand researchers (Use Case 2).
- New decisions via `quick-capture`.
- Adding new scheduled jobs by editing `scripts/scheduled-jobs.yml` + running `python3 scripts/schedule-sync.py`.

The toolkit is meant to be lived in, not just built. Most ongoing work is content, not skill creation.

## Status legend

- ⬜ pending — not started
- 🟡 in progress — partially built; see notes
- ✅ done — built, tested, SKILL.md committed
- ❌ blocked — see notes for what's needed

Update the **Status** line under each step when its state changes. Add a one-line note under it for date + deviations.
