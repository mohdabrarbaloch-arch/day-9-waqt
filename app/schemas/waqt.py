"""Pydantic v2 schemas for auth, locations, cities and prayer times."""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Locations ----------
class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    timezone: str = Field(min_length=1, max_length=64)


class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- Prayer times ----------
class TimesRequest(BaseModel):
    date: date_type | None = None
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    timezone: str = "Asia/Karachi"
    method: int = Field(default=1, ge=1, le=16)
    asr_juristic: int = Field(default=0, ge=0, le=2)

    @field_validator("timezone")
    @classmethod
    def _valid_tz(cls, v: str) -> str:
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        try:
            ZoneInfo(v)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {v}") from exc
        return v


class QiblaResponse(BaseModel):
    latitude: float
    longitude: float
    bearing_degrees: float
    bearing_cardinal: str


class CityResponse(BaseModel):
    id: int
    name: str
    country: str
    lat: float
    lng: float
    timezone: str

    model_config = {"from_attributes": True}
