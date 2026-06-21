# scripts/

Standalone scripts used by the toolkit. Unlike skills (which are prompt-based instructions), these are real code invoked from `launchd` (cron's modern replacement) or by you.

## Scheduling system

The toolkit's 9 Category-2 scheduled skills run via macOS `launchd`. Declarative config, idempotent install/uninstall, login-time catch-up for missed runs.

### Architecture (two locations on purpose)

```
<repo>/scripts/                              ← source of truth (you edit here)
   scheduled-jobs.yml
   run-scheduled-job.sh
   catch-up-missed-runs.sh
   _catch_up_helper.py
   schedule-sync.py                          ← deploys + reconciles
   schedule-status.py                        ← read-only status

           ▼  schedule-sync.py copies operational files

~/Library/Application Support/research-bot/  ← deploy location (TCC-unprotected)
   scheduled-jobs.yml
   scripts/
      run-scheduled-job.sh
      catch-up-missed-runs.sh
      _catch_up_helper.py
   state/
      {job-id}.last-run
      {job-id}.last-exit-code

~/Library/LaunchAgents/research-bot.*.plist  ← launchd configs (reference deployed scripts)
~/Library/Logs/research-bot/{job-id}.log     ← per-job logs
~/Obsidian/Research-Brain/_inbox/scheduled-jobs/  ← queue markers
```

**Why two locations?** macOS TCC protects `~/Documents/` from background processes. The repo lives there (convenient editing + iCloud/Time Machine backup). The deployed copies live in `~/Library/Application Support/` where launchd-spawned bash can read them without any permission grant. `schedule-sync.py` keeps them in sync.

### Default mode: queue (zero scheduled-time API cost)

When a job fires, `run-scheduled-job.sh` writes a marker at `~/Obsidian/Research-Brain/_inbox/scheduled-jobs/{date}-{job-id}.md`. You open Claude Code, invoke the skill (`Run the weekly-intelligence-digest skill`), the skill does the real research, and you delete the marker. Markers accumulate if you're away; nothing is lost.

To opt one job into `claude-headless` (auto LLM at scheduled time, uses tokens): add `mode: claude-headless` to that job in `scheduled-jobs.yml`. Requires `ANTHROPIC_API_KEY` in `~/.config/research-bot/env`.

### State for "what's installed" — implicit

The set of `~/Library/LaunchAgents/research-bot.*.plist` files IS the install state. Sync reads `scheduled-jobs.yml`, generates desired plists, diffs vs reality, reconciles. Remove a job from yml → next sync removes its plist. Add → next sync creates.

### Setup (one-time)

```bash
cd <repo-root>
python3 -m pip install -r scripts/requirements.txt
python3 scripts/schedule-sync.py
```

Verify:

```bash
launchctl list | grep research-bot          # should show 10 entries
python3 scripts/schedule-status.py          # detailed per-job status
```

### Editing jobs or runtime scripts

Both edit-then-resync flows are identical:

1. Edit the file in `scripts/` (the yml or any of the operational shell/python scripts).
2. Run `python3 scripts/schedule-sync.py`.

Sync is idempotent — running when nothing changed is a no-op. Always safe.

### Common operations

```bash
# Per-job status
python3 scripts/schedule-status.py

# Dry-run preview
python3 scripts/schedule-sync.py --dry-run

# Uninstall everything
python3 scripts/schedule-sync.py --remove-all

# Manually fire a single job (uses deployed wrapper)
bash "$HOME/Library/Application Support/research-bot/scripts/run-scheduled-job.sh" \
    voices-watcher queue voices-watcher 1800

# Force-fire via launchd (real end-to-end test)
launchctl kickstart -k "gui/$UID/research-bot.voices-watcher"
tail -20 ~/Library/Logs/research-bot/voices-watcher.log
```

### Logs

- Per-job: `~/Library/Logs/research-bot/{job-id}.log`
- Catch-up sweep: `~/Library/Logs/research-bot/catch-up.log`

### Why launchd (not cron)

Apple is deprecating cron. launchd has better semantics for `RunAtLoad` (catch-up runs at login) and `StartInterval` (catch-up re-checks hourly).

### Why no Terraform

Local-laptop launchd state with one user is the wrong shape for Terraform. Community providers exist but aren't maintained. A small Python script is clearer and easier to debug.

### Why deploy outside the repo (rather than granting bash Full Disk Access)

Granting `/bin/bash` Full Disk Access would let launchd-spawned bash read inside `~/Documents/` — but it would also expand the access of every other bash invocation system-wide (any shell script that runs, intentional or otherwise). Deploying the operational files to `~/Library/Application Support/research-bot/` sidesteps the whole TCC question: launchd reads from a TCC-unprotected location, no permission grant required, no expanded attack surface.
