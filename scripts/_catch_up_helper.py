#!/usr/bin/env python3
"""
_catch_up_helper.py — invoked by catch-up-missed-runs.sh.

DEPLOYED to ~/Library/Application Support/research-bot/scripts/ — source of truth
is the version in the repo. Re-run schedule-sync.py to deploy edits.

Takes <base-dir> as arg. Reads {base-dir}/scheduled-jobs.yml and state files at
{base-dir}/state/. Invokes the deployed wrapper at {base-dir}/scripts/run-scheduled-job.sh.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

DOW_MAP = {
    "sunday": 6, "monday": 0, "tuesday": 1, "wednesday": 2,
    "thursday": 3, "friday": 4, "saturday": 5,
}


def most_recent_fire(cadence: dict, now: datetime):
    hour = cadence.get("hour", 0)
    minute = cadence.get("minute", 0)

    months = cadence.get("months")
    if months:
        day = cadence.get("day", 1)
        for delta in range(0, 366):
            cand = (now - timedelta(days=delta))
            if cand.month not in months or cand.day != day:
                continue
            cand = cand.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if cand <= now:
                return cand
        return None

    if "day" in cadence:
        day = cadence["day"]
        for delta in range(0, 62):
            cand = (now - timedelta(days=delta))
            if cand.day != day:
                continue
            cand = cand.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if cand <= now:
                return cand
        return None

    dow_name = cadence.get("day_of_week")
    if dow_name:
        target = DOW_MAP[dow_name.lower()]
        for delta in range(0, 14):
            cand = (now - timedelta(days=delta))
            if cand.weekday() != target:
                continue
            cand = cand.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if cand > now:
                continue
            return cand
        return None

    weekdays_only = cadence.get("weekdays_only", False)
    for delta in range(0, 14):
        cand = (now - timedelta(days=delta))
        cand = cand.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if cand > now:
            continue
        if weekdays_only and cand.weekday() >= 5:
            continue
        return cand
    return None


def read_last_run(state_dir: Path, job_id: str):
    p = state_dir / f"{job_id}.last-run"
    if not p.exists():
        return None
    try:
        return datetime.fromisoformat(p.read_text().strip().replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def main():
    if len(sys.argv) < 2:
        print("usage: _catch_up_helper.py <base-dir>", file=sys.stderr)
        sys.exit(64)

    base_dir = Path(sys.argv[1]).resolve()
    cfg_path = base_dir / "scheduled-jobs.yml"
    scripts_dir = base_dir / "scripts"
    state_dir = base_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    default_mode = cfg.get("default_mode", "queue")
    wrapper = scripts_dir / "run-scheduled-job.sh"

    now = datetime.utcnow()
    caught_up = skipped = no_state = 0

    for job in cfg["jobs"]:
        job_id = job["id"]
        skill = job["skill"]
        mode = job.get("mode", default_mode)
        timeout = job.get("timeout_seconds", 600)
        every_n = job["cadence"].get("every_n_weeks", 1)

        expected = most_recent_fire(job["cadence"], now)
        if expected is None:
            print(f"  {job_id}: no past scheduled fire — skip")
            skipped += 1
            continue

        last_run = read_last_run(state_dir, job_id)
        if last_run is None:
            print(f"  {job_id}: no state — first time; firing catch-up for {expected.isoformat()}")
            no_state += 1
        elif last_run >= expected:
            print(f"  {job_id}: up to date (last={last_run.isoformat()}, expected={expected.isoformat()})")
            skipped += 1
            continue
        else:
            print(f"  {job_id}: MISSED (last={last_run.isoformat()}, expected={expected.isoformat()}) — firing catch-up")

        result = subprocess.run(
            ["bash", str(wrapper), job_id, mode, skill, str(timeout), str(every_n)],
            capture_output=True, text=True,
        )
        print(f"    wrapper exit={result.returncode}")
        if result.stderr:
            print(f"    stderr: {result.stderr.strip()}")
        caught_up += 1

    print(f"=== catch-up summary: {caught_up} fired, {skipped} skipped, {no_state} first-time ===")


if __name__ == "__main__":
    main()
