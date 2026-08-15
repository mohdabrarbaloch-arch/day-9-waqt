"""Unit tests for the astronomy engine (math verified against published values)."""

import math
from datetime import date

import pytest

from app.services import astronomy
from app.services.astronomy import (
    calculate_prayer_times,
    equation_of_time,
    qibla_direction,
    solar_declination,
    sun_times,
)


def test_solar_declination_karachi_summer():
    """Karachi (24.86N) in June — sun is north of the equator (~23.4 deg max)."""
    jd = astronomy._to_jd(date(2026, 6, 21))
    decl = solar_declination(jd)
    assert 23.0 <= decl <= 23.6


def test_solar_declination_winter_south():
    """December solstice — declination is strongly negative."""
    jd = astronomy._to_jd(date(2026, 12, 21))
    decl = solar_declination(jd)
    assert -23.6 <= decl <= -23.0


def test_equation_of_time_range():
    """EoT stays within the physical ±17 minute band."""
    for month in range(1, 13):
        eot = equation_of_time(astronomy._to_jd(date(2026, month, 15)))
        assert -17.5 <= eot <= 17.5


def test_sun_times_sane_karachi():
    """Sunrise ~01:00 UTC (=06:00 PKT), solar noon ~07:27 UTC (=12:27 PKT),
    sunset ~14:06 UTC (=19:06 PKT) for Karachi in August."""
    rise, noon, set_ = sun_times(24.8607, 67.0011, date(2026, 8, 16))
    assert 0 < rise < noon < set_ < 1440
    assert 30 < rise < 120       # 00:30–02:00 UTC → 05:30–07:00 PKT
    assert 420 < noon < 480      # 07:00–08:00 UTC → 12:00–13:00 PKT
    assert 780 < set_ < 900      # 13:00–15:00 UTC → 18:00–20:00 PKT


def test_prayer_times_ordering_karachi():
    """Fajr lands on the previous evening in UTC clock terms for Karachi in
    August (the fajr angle wraps past midnight) — verify the local PKT
    ordering instead, which is what users actually see."""
    from app.services.astronomy import day_times_local

    result = day_times_local(24.8607, 67.0011, date(2026, 8, 16), "Asia/Karachi", method_id=1)
    times = result["times"]
    order = ["fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
    minutes = [
        int(t.split(":")[0]) * 60 + int(t.split(":")[1])
        for t in (times[k] for k in order)
    ]
    assert minutes == sorted(minutes)
    assert result["method_name"] == "University of Karachi"
    assert result["date"] == "2026-08-16"


def test_prayer_times_methods_differ():
    """Different methods (Karachi 18/18 vs ISNA 15/15) give different Fajr."""
    a = calculate_prayer_times(24.8607, 67.0011, date(2026, 8, 16), method_id=1)
    b = calculate_prayer_times(24.8607, 67.0011, date(2026, 8, 16), method_id=2)
    assert a["times"]["fajr"] != b["times"]["fajr"]


def test_hanafi_asr_later_than_shafi():
    """Hanafi Asr (2 shadows) is always later in the day than Shafi (1 shadow)."""
    karachi = (24.8607, 67.0011)
    day = date(2026, 8, 16)
    shafi = calculate_prayer_times(*karachi, day, method_id=1, asr_juristic=1)
    hanafi = calculate_prayer_times(*karachi, day, method_id=1, asr_juristic=2)
    assert _to_min(hanafi["times"]["asr"]) > _to_min(shafi["times"]["asr"])


def test_isha_interval_method_ummalqura():
    """Umm Al-Qura uses a fixed 90-min interval after Maghrib."""
    result = calculate_prayer_times(24.8607, 67.0011, date(2026, 8, 16), method_id=4)
    maghrib = _to_min(result["times"]["maghrib"])
    isha = _to_min(result["times"]["isha"])
    assert isha - maghrib == 90


def test_qibla_karachi():
    """Karachi → Makkah bearing should be ~265-267 deg (slightly west of W)."""
    bearing = qibla_direction(24.8607, 67.0011)
    assert 260.0 <= bearing <= 270.0


def test_qibla_makkah_self():
    """From the Kaaba itself, bearing is undefined-ish; from a point due west
    it must be 90.0 (east)."""
    bearing = qibla_direction(21.4225, 39.8262 - 1.0)
    assert 88.0 <= bearing <= 92.0


def test_high_latitude_middle_of_night():
    """Oslo (59.9N) in June — middle-of-night rule keeps times on the clock."""
    result = calculate_prayer_times(
        59.9139, 10.7522, date(2026, 6, 21), method_id=1, high_lat_rule=1
    )
    times = result["times"]
    for key in ("fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"):
        hh, mm = (int(x) for x in times[key].split(":"))
        assert 0 <= hh <= 23 and 0 <= mm <= 59


def test_monthly_calendar_length():
    days = astronomy.monthly_calendar_local(
        24.8607, 67.0011, 2026, 2, "Asia/Karachi", method_id=1
    )
    assert len(days) == 28


def test_next_prayer_rolls_to_tomorrow():
    from datetime import datetime, timezone

    times = {"fajr": "05:00", "dhuhr": "12:30", "maghrib": "19:00"}
    now = datetime(2026, 8, 16, 20, 0, tzinfo=timezone.utc)
    name, when = astronomy.next_prayer(times, now)
    assert name == "fajr"
    assert when.day == 17
