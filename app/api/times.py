"""Prayer times + Qibla endpoints."""

from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.schemas.waqt import QiblaResponse, TimesRequest
from app.services import astronomy
from app.services.methods import METHODS

router = APIRouter(prefix="/api", tags=["times"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/times")
@limiter.limit("60/minute")
def get_times(
    request: Request,  # noqa: ARG001
    params: TimesRequest = Query(),  # noqa: B008
) -> dict:
    """Prayer times for a location on a given date (default: today, Asia/Karachi)."""
    day = params.date or date.today()
    try:
        result = astronomy.day_times_local(
            latitude=params.latitude,
            longitude=params.longitude,
            day=day,
            tz_name=params.timezone,
            method_id=params.method,
            asr_juristic=params.asr_juristic,
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=422, detail=f"Calculation failed: {exc}"
        ) from exc
    return result


@router.get("/times/month")
@limiter.limit("20/minute")
def get_month(
    request: Request,  # noqa: ARG001
    year: int = Query(ge=2000, le=2100),
    month: int = Query(ge=1, le=12),
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    timezone: str = "Asia/Karachi",
    method: int = Query(default=1, ge=1, le=16),
    asr_juristic: int = Query(default=0, ge=0, le=2),
) -> dict:
    """Full prayer timetable for a whole month."""
    try:
        days = astronomy.monthly_calendar_local(
            latitude, longitude, year, month, timezone, method, asr_juristic
        )
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=422, detail=f"Calculation failed: {exc}"
        ) from exc
    return {
        "year": year,
        "month": month,
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "method": method,
        "days": days,
    }


@router.get("/qibla", response_model=QiblaResponse)
@limiter.limit("60/minute")
def get_qibla(
    request: Request,  # noqa: ARG001
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
) -> QiblaResponse:
    """Qibla direction (bearing from true North) for a location."""
    bearing = astronomy.qibla_direction(latitude, longitude)
    return QiblaResponse(
        latitude=latitude,
        longitude=longitude,
        bearing_degrees=round(bearing, 2),
        bearing_cardinal=cardinal(bearing),
    )


@router.get("/methods")
def get_methods() -> list[dict]:
    """All supported calculation methods."""
    return [
        {
            "id": m.id,
            "name": m.name,
            "region": m.region,
            "fajr_angle": m.fajr_angle,
            "isha_angle": m.isha_angle,
            "isha_interval": m.isha_interval,
            "asr_factor": m.asr_factor,
        }
        for m in METHODS.values()
    ]


@router.get("/now")
@limiter.limit("60/minute")
def get_now(
    request: Request,  # noqa: ARG001
    latitude: float = Query(ge=-90.0, le=90.0),
    longitude: float = Query(ge=-180.0, le=180.0),
    timezone: str = "Asia/Karachi",
    method: int = Query(default=1, ge=1, le=16),
    asr_juristic: int = Query(default=0, ge=0, le=2),
) -> dict:
    """Today's times + which prayer is next and when."""
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    today = now.date()
    result = astronomy.day_times_local(
        latitude, longitude, today, timezone, method, asr_juristic
    )
    name, when = astronomy.next_prayer(result["times"], now)
    return {
        **result,
        "now": now.isoformat(),
        "next_prayer": name,
        "next_prayer_at": when.isoformat(),
    }


def cardinal(bearing: float) -> str:
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((bearing + 22.5) // 45) % 8
    return directions[idx]
