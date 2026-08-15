"""City search endpoint."""

from fastapi import APIRouter, Query

from app.schemas.waqt import CityResponse
from app.services.cities import search_cities

router = APIRouter(prefix="/api/cities", tags=["cities"])


@router.get("", response_model=list[CityResponse])
def list_cities(
    query: str = Query(default="", max_length=60),
    limit: int = Query(default=8, ge=1, le=20),
):
    """Search cities by name or country (empty query returns popular ones)."""
    cities = search_cities(query, limit)
    return [
        CityResponse(
            id=c.id,
            name=c.name,
            country=c.country,
            lat=c.lat,
            lng=c.lng,
            timezone=c.timezone,
        )
        for c in cities
    ]
