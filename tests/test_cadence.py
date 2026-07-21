"""Deterministic tests for the three cadence engines.

`scheduled-jobs.yml` declares each job's cadence. THREE separate functions
interpret that schema and must agree:
  - cadence_to_calendar_intervals (schedule-sync.py) -> launchd StartCalendarInterval
  - most_recent_fire            (_catch_up_helper.py) -> last fire <= now
  - next_fire                   (schedule-status.py)  -> next fire > now
A drift between them silently breaks catch-up / status. These tests pin the
launchd output exactly and assert cross-engine agreement on real cadences.
"""
from datetime import datetime

import pytest

from _util import SCRIPTS, load_module

sync = load_module(SCRIPTS / "schedule-sync.py", "schedule_sync")
catch = load_module(SCRIPTS / "_catch_up_helper.py", "catch_up_helper")
status = load_module(SCRIPTS / "schedule-status.py", "schedule_status")

# Python weekday(): Monday=0 .. Sunday=6 — for asserting the *named* day,
# independent of each engine's internal (differing) day-of-week maps.
PYWD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6}

# A Tuesday, midday — so "most recent" and "next" are clearly on either side.
NOW = datetime(2026, 7, 21, 12, 0, 0)

# The real cadence shapes used in scheduled-jobs.yml.
CADENCES = {
    "daily": {"hour": 7, "minute": 30},
    "weekdays_only": {"hour": 7, "minute": 0, "weekdays_only": True},
    "weekly_mon": {"day_of_week": "monday", "hour": 7, "minute": 0},
    "weekly_sun": {"day_of_week": "sunday", "hour": 18, "minute": 0},
    "biweekly_tue": {"day_of_week": "tuesday", "hour": 8, "minute": 0, "every_n_weeks": 2},
    "monthly": {"day": 1, "hour": 6, "minute": 0},
    "quarterly": {"months": [1, 4, 7, 10], "day": 15, "hour": 9, "minute": 0},
}


# ---- cadence_to_calendar_intervals: exact launchd output --------------------

def test_daily_interval():
    assert sync.cadence_to_calendar_intervals(CADENCES["daily"]) == [
        {"Hour": 7, "Minute": 30}]


def test_weekdays_only_expands_to_mon_fri():
    got = sync.cadence_to_calendar_intervals(CADENCES["weekdays_only"])
    # launchd weekdays 1..5 == Mon..Fri
    assert got == [{"Weekday": wd, "Hour": 7, "Minute": 0} for wd in (1, 2, 3, 4, 5)]


def test_weekly_launchd_weekday_numbers():
    # launchd: sunday=0, monday=1, ... saturday=6
    assert sync.cadence_to_calendar_intervals(CADENCES["weekly_mon"]) == [
        {"Weekday": 1, "Hour": 7, "Minute": 0}]
    assert sync.cadence_to_calendar_intervals(CADENCES["weekly_sun"]) == [
        {"Weekday": 0, "Hour": 18, "Minute": 0}]


def test_biweekly_ignores_every_n_weeks_in_calendar():
    # every_n_weeks is enforced by the wrapper, not the calendar interval.
    assert sync.cadence_to_calendar_intervals(CADENCES["biweekly_tue"]) == [
        {"Weekday": 2, "Hour": 8, "Minute": 0}]


def test_monthly_day_of_month():
    assert sync.cadence_to_calendar_intervals(CADENCES["monthly"]) == [
        {"Day": 1, "Hour": 6, "Minute": 0}]


def test_quarterly_months_expand():
    got = sync.cadence_to_calendar_intervals(CADENCES["quarterly"])
    assert got == [{"Month": m, "Day": 15, "Hour": 9, "Minute": 0}
                   for m in (1, 4, 7, 10)]


# ---- cross-engine agreement -------------------------------------------------

@pytest.mark.parametrize("name", list(CADENCES))
def test_most_recent_before_now_next_after(name):
    cad = CADENCES[name]
    prev = catch.most_recent_fire(cad, NOW)
    nxt = status.next_fire(cad, NOW)
    assert prev is not None and nxt is not None
    assert prev <= NOW < nxt


@pytest.mark.parametrize("name", list(CADENCES))
def test_engines_agree_on_hour_minute(name):
    cad = CADENCES[name]
    for fire in (catch.most_recent_fire(cad, NOW), status.next_fire(cad, NOW)):
        assert fire.hour == cad.get("hour", 0)
        assert fire.minute == cad.get("minute", 0)


@pytest.mark.parametrize("name", ["weekly_mon", "weekly_sun", "biweekly_tue"])
def test_day_of_week_lands_on_named_day(name):
    cad = CADENCES[name]
    want = PYWD[cad["day_of_week"]]
    assert catch.most_recent_fire(cad, NOW).weekday() == want
    assert status.next_fire(cad, NOW).weekday() == want


def test_weekdays_only_lands_on_a_weekday():
    cad = CADENCES["weekdays_only"]
    assert catch.most_recent_fire(cad, NOW).weekday() < 5
    assert status.next_fire(cad, NOW).weekday() < 5


def test_monthly_lands_on_day_of_month():
    cad = CADENCES["monthly"]
    assert catch.most_recent_fire(cad, NOW).day == 1
    assert status.next_fire(cad, NOW).day == 1


def test_quarterly_lands_in_configured_months():
    cad = CADENCES["quarterly"]
    assert catch.most_recent_fire(cad, NOW).month in cad["months"]
    assert status.next_fire(cad, NOW).month in cad["months"]
    assert catch.most_recent_fire(cad, NOW).day == 15
