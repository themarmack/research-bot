"""Deterministic tests for scheduled-job marker auto-expiry.

Policy (EXPIRY_DAYS in _catch_up_helper.py): a queue marker expires when its
filename date is strictly older than its job's cadence window —
daily/weekdays 3, weekly 14, biweekly 21, monthly 45, quarterly 120 days.
Markers for unknown job ids (or unparseable filenames) are never auto-deleted.
The catch-up pass must not backfill a missed run past that same window
(past_expiry), or it would recreate exactly what expiry just deleted.
"""
from datetime import date, datetime, timedelta

import pytest

from _util import SCRIPTS, load_module

catch = load_module(SCRIPTS / "_catch_up_helper.py")

TODAY = date(2026, 8, 28)

JOBS_CFG = {
    "jobs": [
        {"id": "daily-job", "cadence": {"hour": 7, "minute": 30}},
        {"id": "weekday-job", "cadence": {"hour": 7, "minute": 0, "weekdays_only": True}},
        {"id": "weekly-job", "cadence": {"day_of_week": "monday", "hour": 7, "minute": 0}},
        {"id": "biweekly-job", "cadence": {"day_of_week": "tuesday", "hour": 8,
                                           "minute": 0, "every_n_weeks": 2}},
        {"id": "monthly-job", "cadence": {"day": 1, "hour": 7, "minute": 0}},
        {"id": "quarterly-job", "cadence": {"months": [1, 4, 7, 10], "day": 1,
                                            "hour": 9, "minute": 0}},
    ]
}

WINDOWS = {
    "daily-job": 3,
    "weekday-job": 3,   # weekdays_only expires on the daily window
    "weekly-job": 14,
    "biweekly-job": 21,
    "monthly-job": 45,
    "quarterly-job": 120,
}


def marker(job_id, days_old):
    return f"{(TODAY - timedelta(days=days_old)).isoformat()}-{job_id}.md"


# ---- cadence classification -------------------------------------------------

@pytest.mark.parametrize("job", JOBS_CFG["jobs"], ids=lambda j: j["id"])
def test_expiry_days_per_cadence(job):
    assert catch.expiry_days(job["cadence"]) == WINDOWS[job["id"]]


# ---- boundary: exactly at the window is kept, one day past is expired -------

@pytest.mark.parametrize("job_id,window", WINDOWS.items())
def test_marker_at_window_boundary_is_kept(job_id, window):
    expired, unknown = catch.expired_markers([marker(job_id, window)], JOBS_CFG, TODAY)
    assert expired == [] and unknown == []


@pytest.mark.parametrize("job_id,window", WINDOWS.items())
def test_marker_one_day_past_window_is_expired(job_id, window):
    name = marker(job_id, window + 1)
    expired, unknown = catch.expired_markers([name], JOBS_CFG, TODAY)
    assert expired == [name] and unknown == []


def test_todays_marker_is_kept():
    expired, _ = catch.expired_markers([marker("daily-job", 0)], JOBS_CFG, TODAY)
    assert expired == []


# ---- unknown / unparseable markers are never auto-deleted -------------------

def test_unknown_job_id_preserved_even_when_ancient():
    name = marker("retired-job", 400)
    expired, unknown = catch.expired_markers([name], JOBS_CFG, TODAY)
    assert expired == []
    assert unknown == [name]


@pytest.mark.parametrize("name", [
    "notes.md",                       # no date prefix
    "2026-13-99-daily-job.md",        # invalid date
    "2026-08-01-daily-job.txt",       # not a .md marker
    "2026-08-01.md",                  # date but no job id
])
def test_unparseable_filenames_preserved(name):
    expired, unknown = catch.expired_markers([name], JOBS_CFG, TODAY)
    assert expired == []
    assert unknown == [name]


def test_mixed_batch_partitions_correctly():
    names = [
        marker("daily-job", 10),       # expired
        marker("weekly-job", 5),       # kept
        marker("quarterly-job", 121),  # expired
        marker("mystery-job", 60),     # unknown -> preserved
    ]
    expired, unknown = catch.expired_markers(names, JOBS_CFG, TODAY)
    assert sorted(expired) == sorted([names[0], names[2]])
    assert unknown == [names[3]]


# ---- no-backfill-past-expiry guard ------------------------------------------

NOW = datetime(2026, 8, 28, 12, 0, 0)


@pytest.mark.parametrize("job", JOBS_CFG["jobs"], ids=lambda j: j["id"])
def test_past_expiry_agrees_with_marker_expiry(job):
    """A missed fire old enough that its marker would expire must not be
    backfilled; one inside the window may be."""
    window = WINDOWS[job["id"]]
    inside = NOW - timedelta(days=window)
    outside = NOW - timedelta(days=window + 1)
    assert catch.past_expiry(job["cadence"], inside, NOW) is False
    assert catch.past_expiry(job["cadence"], outside, NOW) is True


def test_past_expiry_uses_calendar_days_not_hours():
    # 3 calendar days ago but a later time-of-day: still exactly at the window.
    cad = {"hour": 7, "minute": 30}
    expected = datetime(2026, 8, 25, 23, 59, 0)
    assert catch.past_expiry(cad, expected, NOW) is False
