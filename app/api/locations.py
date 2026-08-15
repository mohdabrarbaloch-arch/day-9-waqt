"""Saved-locations endpoints (authenticated)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models import SavedLocation, User
from app.schemas.waqt import LocationCreate, LocationResponse

router = APIRouter(prefix="/api/locations", tags=["locations"])
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=list[LocationResponse])
def list_locations(
    current: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    rows = db.scalars(
        select(SavedLocation)
        .where(SavedLocation.user_id == current.id)
        .order_by(SavedLocation.created_at.desc())
    ).all()
    return rows


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
def create_location(
    request: Request,  # noqa: ARG001
    payload: LocationCreate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(SavedLocation).where(
            SavedLocation.user_id == current.id,
            SavedLocation.name == payload.name.strip(),
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="A location with this name already exists"
        )
    row = SavedLocation(
        user_id=current.id,
        name=payload.name.strip(),
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone=payload.timezone,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(SavedLocation, location_id)
    if row is None or row.user_id != current.id:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(row)
    db.commit()
    return None
