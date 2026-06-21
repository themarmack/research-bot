#!/bin/bash
# catch-up-missed-runs.sh — runs at login + hourly via launchd.
#
# DEPLOYED to ~/Library/Application Support/research-bot/scripts/ — source of truth
# is the version in the repo's scripts/. Re-run schedule-sync.py to deploy edits.

set -euo pipefail

BASE_DIR="$HOME/Library/Application Support/research-bot"
SCRIPTS_DIR="$BASE_DIR/scripts"
STATE_DIR="$BASE_DIR/state"
LOG_DIR="$HOME/Library/Logs/research-bot"
LOG_FILE="$LOG_DIR/catch-up.log"

mkdir -p "$STATE_DIR" "$LOG_DIR"

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" >> "$LOG_FILE"
}

log "===== catch-up sweep starting ====="

python3 "$SCRIPTS_DIR/_catch_up_helper.py" "$BASE_DIR" 2>&1 | tee -a "$LOG_FILE"

log "===== catch-up sweep finished ====="
