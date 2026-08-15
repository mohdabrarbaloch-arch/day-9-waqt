"""Astronomy engine for Waqt.

All math is implemented from first principles — no third-party astronomy
libraries. The solar position follows the standard low-precision series used
by NOAA/Almanac implementations (accuracy well under a minute for prayer-time
purposes):

    Julian Day  ->  mean solar noon (transit)  ->  equation of time
                ->  solar declination          ->  hour angle at twilight
                ->  prayer times

References: Jean Meeus "Astronomical Algorithms"; NOAA solar calculator;
standard definitions used by the University of Karachi method.
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.services.methods import get_method

# Kaaba (Masjid al-Haram, Makkah)
KAABA_LAT = 21.4225
KAABA_LNG = 39.8262

DEG = math.pi / 180.0
RAD = 180.0 / math.pi

# Mean synodic parameters (Meeus, ch. 25)
MEAN_OBLIQUITY_EPOCH = 23.43929111  # epsilon0 for J2000 epoch (23.4392911 deg)
J2000 = 2451545.0  # Julian Day for 2000-01-01 12:00 TT


def _to_jd(d: date) -> float:
    """Convert a Gregorian date to a Julian Day number (UTC noon-based)."""
    y, m = d.year, d.month
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (
        math.floor(365.25 * (y + 4716))
        + math.floor(30.6001 * (m + 1))
        + d.day
        + b
        - 1524.5
    )


def _julian_century(jd: float) -> float:
    """Julian centuries since J2000 epoch."""
    return (jd - J2000) / 36525.0


def solar_declination(jd: float) -> float:
    """Solar declination in degrees for a Julian Day (Meeus low precision)."""
    n = _julian_century(jd)
    # Mean longitude of the Sun
    l0 = (280.46646 + n * (36000.76983 + n * 0.0003032)) % 360.0
    # Mean anomaly of the Sun
    m = 357.52911 + n * (35999.05029 - 0.0001537 * n)
    m_rad = m * DEG
    # Equation of center
    c = (
        math.sin(m_rad) * (1.914602 - n * (0.004817 + 0.000014 * n))
        + math.sin(2 * m_rad) * (0.019993 - 0.000101 * n)
        + math.sin(3 * m_rad) * 0.000289
    )
    # True longitude
    true_lng = l0 + c
    # Apparent longitude (correct for nutation + aberration)
    omega = 125.04 - 1934.136 * n
    apparent_lng = true_lng - 0.00569 - 0.00478 * math.sin(omega * DEG)
    # Obliquity of the ecliptic
    epsilon = MEAN_OBLIQUITY_EPOCH + 0.00000036 * n
    # Declination
    return RAD * math.asin(math.sin(epsilon * DEG) * math.sin(apparent_lng * DEG))


def equation_of_time(jd: float) -> float:
    """Equation of time in minutes (solar - mean)."""
    n = _julian_century(jd)
    epsilon = MEAN_OBLIQUITY_EPOCH + 0.00000036 * n
    l0 = (280.46646 + n * (36000.76983 + n * 0.0003032)) % 360.0
    m = 357.52911 + n * (35999.05029 - 0.0001537 * n)
    e = 0.016708634 - n * (0.000042037 + 0.0000001267 * n)
    m_rad = m * DEG
    y = math.tan(epsilon * DEG / 2.0) ** 2
    eot = (
        y * math.sin(2 * l0 * DEG)
        - 2 * e * math.sin(m_rad)
        + 4 * e * y * math.sin(m_rad) * math.cos(2 * l0 * DEG)
        - 0.5 * y * y * math.sin(4 * l0 * DEG)
        - 1.25 * e * e * math.sin(2 * m_rad)
    )
    return RAD * 4.0 * eot


def _hour_angle(latitude: float, declination: float, depression: float) -> float:
    """Hour angle (degrees) when the sun is `depression` degrees below the
    horizon (positive = below; negative = above, e.g. Asr)."""
    lat_rad = latitude * DEG
    dec_rad = declination * DEG
    a = -math.sin(depression * DEG)
    cos_h = (a - math.sin(lat_rad) * math.sin(dec_rad)) / (
        math.cos(lat_rad) * math.cos(dec_rad)
    )
    cos_h = max(-1.0, min(1.0, cos_h))
    return RAD * math.acos(cos_h)


def mid_day_time(jd: float, longitude: float) -> float:
    """Solar noon (transit) in minutes from local midnight at UTC."""
    return 720.0 - 4.0 * longitude - equation_of_time(jd)


def _minutes_to_datetime(day_start: datetime, minutes: float) -> datetime:
    """Add fractional minutes (UTC-based) to a naive UTC day-start."""
    return day_start + timedelta(minutes=minutes)


def sun_times(
    latitude: float,
    longitude: float,
    day: date,
    zenith: float | None = None,
) -> tuple[float, float, float]:
    """Return (sunrise, solar_noon, sunset) in minutes-from-UTC-midnight.

    zenith: official sunrise/sunset uses 90.833° (refraction + solar radius).
    """
    jd = _to_jd(day)
    decl = solar_declination(jd)
    eot = equation_of_time(jd)
    noon = 720.0 - 4.0 * longitude - eot
    z = zenith if zenith is not None else 90.833
    ha = _hour_angle(latitude, decl, z - 90.0)  # depression below horizon
    sunrise = noon - ha * 4.0
    sunset = noon + ha * 4.0
    return sunrise, noon, sunset


def qibla_direction(latitude: float, longitude: float) -> float:
    """Initial great-circle bearing (degrees clockwise from true North)
    from the given location to the Kaaba."""
    lat1, lng1 = latitude * DEG, longitude * DEG
    lat2, lng2 = KAABA_LAT * DEG, KAABA_LNG * DEG
    d_lng = lng2 - lng1
    y = math.sin(d_lng)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        d_lng
    )
    bearing = RAD * math.atan2(y, x)
    return (bearing + 360.0) % 360.0


def _normalize_to_day(t: float) -> float:
    """Wrap minutes to [0, 1440)."""
    return t % 1440.0


def _high_lat_adjust(
    latitude: float,
    fajr_angle: float,
    isha_angle: float,
    night_minutes: float,
) -> tuple[float, float]:
    """Middle-of-the-night rule for high latitudes (|lat| > 48°).

    Returns adjusted (fajr_offset_after_midnight, isha_offset_after_sunset).
    """
    if abs(latitude) <= 48.0:
        return 0.0, 0.0
    # Night is sunset -> next sunrise; split at midnight.
    # Fajr = midnight + (fajr_angle / total_angle) * half_night
    # Isha = sunset + (isha_angle / total_angle) * half_night
    total_angle = fajr_angle + isha_angle
    if total_angle <= 0:
        return 0.0, 0.0
    half_night = night_minutes / 2.0
    fajr_off = (fajr_angle / total_angle) * half_night
    isha_off = (isha_angle / total_angle) * half_night
    return fajr_off, isha_off


def calculate_prayer_times(
    latitude: float,
    longitude: float,
    day: date,
    method_id: int = 1,
    asr_juristic: int = 0,  # 0 = method default, 1 = Shafi, 2 = Hanafi
    high_lat_rule: int = 0,  # 0 = none, 1 = middle of the night
) -> dict[str, str | float | bool]:
    """Compute the five daily prayer times for a location + date.

    Returns a dict with times as "HH:MM" (24h) plus ISO strings and metadata.
    Times are computed in UTC minutes then shifted to local by the caller —
    this function is timezone-agnostic (returns UTC-based clock times).
    """
    method = get_method(method_id)
    factor = asr_juristic if asr_juristic in (1, 2) else int(method.asr_factor)

    sunrise, noon, sunset = sun_times(latitude, longitude, day)
    decl = solar_declination(_to_jd(day))

    # Dhuhr = solar noon
    dhuhr = noon

    # Asr: shadow factor hour angle (Hanafi = 2 shadows, Shafi = 1).
    # Sun altitude = atan(1 / (factor + tan|lat-dec|)); depression is negative.
    alt = math.degrees(math.atan2(1.0, factor + math.tan(abs(latitude - decl) * DEG)))
    asr_ha = _hour_angle(latitude, decl, -alt)
    asr = dhuhr + asr_ha * 4.0

    # Fajr
    fajr_ha = _hour_angle(latitude, decl, method.fajr_angle)
    fajr = noon - fajr_ha * 4.0

    # Isha (angle or fixed interval after Maghrib)
    if method.isha_interval is not None and method.isha_interval > 0:
        isha = sunset + method.isha_interval
    else:
        isha_ha = _hour_angle(latitude, decl, method.isha_angle)
        isha = dhuhr + isha_ha * 4.0

    # High-latitude adjustment (only when the simple math gives impossible times)
    if high_lat_rule == 1 and abs(latitude) > 48.0:
        night = (sunrise + 1440.0 - sunset) % 1440.0
        fajr_off, isha_off = _high_lat_adjust(
            latitude, method.fajr_angle, method.isha_angle, night
        )
        midnight = (sunset + night / 2.0) % 1440.0
        fajr = (midnight + fajr_off) % 1440.0
        isha = (sunset + isha_off) % 1440.0

    times = {
        "fajr": _fmt(fajr),
        "sunrise": _fmt(sunrise),
        "dhuhr": _fmt(dhuhr),
        "asr": _fmt(asr),
        "maghrib": _fmt(sunset),
        "isha": _fmt(isha),
    }
    return {
        "date": day.isoformat(),
        "times": times,
        "method": method.id,
        "method_name": method.name,
        "asr_juristic": factor,
        "is_special_day": day.weekday() == 4,  # Friday -> Jumu'ah
    }


def _fmt(minutes: float) -> str:
    """Format minutes-from-midnight to "HH:MM" (24h), wrapping to [0,1440)."""
    minutes = _normalize_to_day(minutes)
    total = int(round(minutes)) % 1440
    h, m = divmod(total, 60)
    return f"{h:02d}:{m:02d}"


# ---------------------------------------------------------------------------
# Public API: timezone-aware helpers used by the routers
# ---------------------------------------------------------------------------


def day_times_local(
    latitude: float,
    longitude: float,
    day: date,
    tz_name: str,
    method_id: int = 1,
    asr_juristic: int = 0,
) -> dict[str, str | float | bool]:
    """Prayer times as local clock strings for a given IANA timezone."""
    raw = calculate_prayer_times(latitude, longitude, day, method_id, asr_juristic)
    tz = ZoneInfo(tz_name)
    # Convert each UTC-clock minute value into local clock time by computing
    # the UTC offset at a representative instant (solar noon) — robust to DST.

    # Compute offset via a representative instant (solar noon) to avoid DST edge
    noon_utc = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    noon_minutes = mid_day_time(_to_jd(day), longitude)
    rep = noon_utc + timedelta(minutes=noon_minutes)
    local_rep = rep.astimezone(tz)
    offset_minutes = (local_rep.utcoffset() or timedelta(0)).total_seconds() / 60.0

    times = raw["times"]
    local_times: dict[str, str] = {}
    for key, value in times.items():
        hh, mm = (int(x) for x in str(value).split(":"))
        minutes = hh * 60 + mm
        local_times[key] = _fmt(minutes + offset_minutes)

    out = dict(raw)
    out["times"] = local_times
    out["timezone"] = tz_name
    out["latitude"] = latitude
    out["longitude"] = longitude
    return out


def monthly_calendar_local(
    latitude: float,
    longitude: float,
    year: int,
    month: int,
    tz_name: str,
    method_id: int = 1,
    asr_juristic: int = 0,
) -> list[dict]:
    """Full prayer timetable for a month (list of per-day dicts)."""
    days: list[dict] = []
    first = date(year, month, 1)
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    d = first
    while d <= last:
        days.append(
            day_times_local(latitude, longitude, d, tz_name, method_id, asr_juristic)
        )
        d += timedelta(days=1)
    return days


def next_prayer(times: dict[str, str], now_local: datetime) -> tuple[str, datetime]:
    """Given local "HH:MM" times and the current local datetime, return the
    name and datetime of the next prayer (today or tomorrow)."""
    now_minutes = now_local.hour * 60 + now_local.minute
    best: tuple[str, datetime] | None = None
    for name, value in times.items():
        hh, mm = (int(x) for x in value.split(":"))
        t_minutes = hh * 60 + mm
        candidate = now_local.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if t_minutes <= now_minutes:
            candidate += timedelta(days=1)
        if best is None or candidate < best[1]:
            best = (name, candidate)
    assert best is not None
    return best
