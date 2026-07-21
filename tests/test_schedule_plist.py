"""Light tests for the launchd plist builders (pure dict construction)."""
from pathlib import Path

from _util import SCRIPTS, load_module

sync = load_module(SCRIPTS / "schedule-sync.py", "schedule_sync_plist")
LOGS = Path("/tmp/logs")


def test_build_job_plist_shape():
    job = {"id": "daily-cve-digest", "skill": "daily-cve-digest",
           "cadence": {"hour": 7, "minute": 0, "weekdays_only": True},
           "timeout_seconds": 600}
    d = sync.build_job_plist(job, "queue", LOGS)
    assert d["Label"].endswith("daily-cve-digest")
    assert d["RunAtLoad"] is False
    assert d["ProgramArguments"][0] == "/bin/bash"
    assert d["ProgramArguments"][1].endswith("run-scheduled-job.sh")
    assert d["ProgramArguments"][2] == "daily-cve-digest"  # job id
    assert d["ProgramArguments"][4] == "daily-cve-digest"  # skill
    # weekdays_only -> a list of five calendar intervals
    assert isinstance(d["StartCalendarInterval"], list)
    assert len(d["StartCalendarInterval"]) == 5


def test_single_interval_is_dict_not_list():
    job = {"id": "voices-watcher", "skill": "voices-watcher",
           "cadence": {"hour": 7, "minute": 30}}
    d = sync.build_job_plist(job, "queue", LOGS)
    assert d["StartCalendarInterval"] == {"Hour": 7, "Minute": 30}


def test_mode_defaults_and_override():
    base = {"id": "x", "skill": "x", "cadence": {"hour": 1, "minute": 0}}
    assert sync.build_job_plist(base, "queue", LOGS)["ProgramArguments"][3] == "queue"
    override = dict(base, mode="claude-headless")
    assert sync.build_job_plist(override, "queue", LOGS)["ProgramArguments"][3] == "claude-headless"


def test_plist_bytes_deterministic():
    job = {"id": "x", "skill": "x", "cadence": {"hour": 1, "minute": 2}}
    d = sync.build_job_plist(job, "queue", LOGS)
    assert sync.plist_bytes(d) == sync.plist_bytes(d)


def test_catch_up_plist():
    d = sync.build_catch_up_plist(LOGS)
    assert d["RunAtLoad"] is True
    assert d["StartInterval"] == 3600
    assert d["ProgramArguments"][1].endswith("catch-up-missed-runs.sh")
