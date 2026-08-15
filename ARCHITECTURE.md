# Waqt (وقت) — Architecture

Waqt is a Prayer Times & Qibla Direction application for Muslims in Pakistan and
South Asia. It computes the five daily prayer times (Fajr, Dhuhr, Asr, Maghrib,
Isha) and the Qibla direction **from first principles** — no third-party
astronomy or prayer-time libraries. All math is implemented in
`app/services/astronomy.py` using the standard solar-position and prayer-time
algorithms (equations of time, solar declination, hour angle, twilight-angle
methods).

## System Diagram

```
┌──────────────────────────┐        ┌────────────────────────────────────┐
│   Browser SPA (static)   │        │           FastAPI backend           │
│  ─────────────────────   │  HTTP  │  ────────────────────────────────   │
│ · Today's 5 times +      │ ──────▶ │ /api/auth/*      JWT + bcrypt      │
│   countdown to next      │ ◀────── │ /api/times/*     prayer times      │
│ · Weekly & monthly       │  JSON   │ /api/qibla       qibla bearing     │
│   timetable              │         │ /api/cities/*    search PK cities  │
│ · Qibla compass (canvas) │         │ /api/locations/* saved places      │
│ · Location search + save │         │ /health          liveness probe    │
│ · Dark, mobile-first UI  │         │                                    │
└──────────────────────────┘         │ SQLite (dev) / PostgreSQL (prod)   │
                                     │ · users  · locations  · refreshes  │
                                     └────────────────────────────────────┘
```

## Tech Stack

| Layer      | Choice                                                    |
|------------|-----------------------------------------------------------|
| Backend    | Python 3.11 · FastAPI 0.115 · Pydantic v2                 |
| Database   | SQLAlchemy 2.0 · SQLite (WAL) dev · PostgreSQL 16 (prod)  |
| Auth       | JWT (HS256, 24h) · bcrypt (12 rounds) · rate-limited login|
| Frontend   | Vanilla JS SPA (zero build step) · CSS variables · Canvas |
| Astronomy  | Hand-rolled solar position + prayer-time engine           |
| Ops        | Docker + docker-compose · Vercel (vercel.json + api/)     |
| CI         | GitHub Actions (lint + test) · pytest · ruff              |

## Data Flow

1. Client requests `/api/times?date=2026-08-16&lat=24.86&lng=67.01&tz=Asia/Karachi&method=2`.
2. Backend validates inputs (lat ∈ [-90,90], lng ∈ [-180,180], date, method id,
   tz via `zoneinfo`).
3. `astronomy.py` computes the **Julian date → solar declination & equation of
   time (via the standard NOAA solar position series) → transit/hour-angle
   offsets** for Fajr/Sunrise/Dhuhr/Asr/Maghrib/Isha using the configured
   twilight angles (method presets, e.g. Karachi: Fajr 18°·Isha 18°).
4. For high latitudes (> 48°) the **middle-of-the-night** rule kicks in to avoid
   degenerate results.
5. `asr` uses the **Hanafi** or **Shafi** juristic factor (1 or 2 shadow lengths).
6. Times are rounded to the minute, converted to the requested timezone, and
   returned with an `is_special_day` flag (Fri = Jumu'ah notice).
7. `/api/qibla` returns the great-circle initial bearing from the user's
   location to the Kaaba (21.4225°N, 39.8262°E).

## Scaling Notes

- **Stateless API**: all computations are pure functions of (lat, lng, date, tz,
  method) → trivially horizontally scalable, cacheable at the CDN edge.
- **DB usage is tiny**: users + saved locations only. The heaviest endpoint
  (`/api/times`) does zero DB reads → serverless-friendly.
- **Rate limiting**: in-memory sliding window (10 req/min per IP on auth;
  generous 60/min on read endpoints) — swap for Redis when multi-instance.
- **Caching**: `Cache-Control: public, max-age=3600` on city data and monthly
  timetables; the monthly calendar for a fixed location is immutable → static
  cache forever per date-range.
- **Postgres path**: `DATABASE_URL=postgresql+psycopg://...` with the same
  SQLAlchemy models — no code changes required.
- **Timezone safety**: every calculation takes an explicit IANA tz; we never
  guess the client's zone server-side.

## Security

- Passwords hashed with bcrypt (12 rounds); no plaintext anywhere.
- JWT signed with HS256 using `SECRET_KEY` from env (min 32 chars enforced).
- `slowapi` rate limits on auth + read endpoints; CORS restricted to allow-list.
- Input validation with Pydantic (strict ranges); SQLAlchemy ORM (no raw SQL).
- All secrets via `.env`; `.env.example` documents every variable.
