---
name: conference-cfp-and-recap-watch
description: Monthly scheduled agent that tracks upcoming CFPs and post-event recaps for the conferences that matter to a regulated-org SDLC lead — QCon, KubeCon, GitHub Universe, RSA, BSides, OWASP Global AppSec, FS-ISAC, Open Source Summit, DevOps Enterprise Summit. Surfaces (a) CFPs opening in the next 90 days with compliance-relevant tracks, (b) talks from recent events worth viewing. Output at vault/digests/monthly/YYYY-MM-DD-conference-watch.md. Useful for: deciding which conferences to send people to, finding talks to share in stakeholder updates, planning the org's own speaker pipeline.
---

# conference-cfp-and-recap-watch

A monthly Category 2 agent that wraps a niche but high-value source surface. Conferences are where peer banks publicly share what they're actually doing — and where the bank can plant a stake by speaking at one.

## Agent config (consumed by `scheduled-agent-runner`)

```yaml
agent_name: conference-cfp-and-recap-watch
cadence: monthly
schedule_hint: "15th of month, 09:00 local"
source_filter:
  custom: conference-list
  conferences:
    - { name: "QCon", track_filter: "Architecture, AI, DevOps" }
    - { name: "KubeCon + CloudNativeCon" }
    - { name: "GitHub Universe" }
    - { name: "RSA Conference" }
    - { name: "BSides", note: "track local chapters" }
    - { name: "OWASP Global AppSec" }
    - { name: "FS-ISAC Summit", note: "regulated-environment focus" }
    - { name: "Open Source Summit" }
    - { name: "DevOps Enterprise Summit" }
verify_loadbearing: false
curate_findings: false
digest_template_overrides:
  template: conference-watch
  why_you_care_extra: |
    Three signals per conference:
    1. CFP opening in next 90 days with compliance-relevant track? — opportunity to submit.
    2. Recent event (past 60 days)? — talks worth viewing/sharing.
    3. Peer-bank speaker presence? — what other regulated orgs are talking about publicly.
```

## Output structure

```markdown
# Conference Watch — {month}

## At a glance
- {N CFPs open with compliance-relevant tracks}
- {M conferences recently held; K talks recommended}
- {J peer-bank speaker slots tracked}

## CFPs open

### {Conference} — CFP closes {date}
- **Compliance-relevant tracks**: {list}
- **Submission recommendation**: {worth submitting? proposed topic}
- **Owner if pursued**: {who would draft the proposal}

## Recent event recaps

### {Conference} ({event dates})
- **Talks worth viewing**:
  - "{title}" by {speaker} — {1-sentence why}
- **Peer-bank speakers**: {list}
- **Themes that recurred**: {1-2 lines}

## Items for awareness
- one-liners

## Cross-references to vault
- Talks for `learning-capture` later: {list}
- Speaker submissions queued: {list}
- Peer-bank intel feeding `peer-bank-tech-intel` research: {list}
```

Lands at `vault/digests/monthly/YYYY-MM-DD-conference-watch.md`.

## Composes with

Standard Phase-1 foundation. Feeds:
- `peer-bank-tech-intel` (planned Cat 1 research) — speaker presence is intel.
- `learning-capture` (planned Cat 6 PKM) — captured talks become insights.
- `enablement-content-creator` (planned Cat 5) — talk content seeds internal training material.

## Acceptance test (for step 23 done-criteria)

SKILL.md covers the 3-signal framework per conference (CFP open / recent recap / peer-bank presence) and the conference list. Live first-run exercise deferred to first monthly cron firing.
