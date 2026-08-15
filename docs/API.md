# API Reference

Base URL: `http://localhost:8000` (prod: your Vercel URL)
Interactive docs: `/docs` (Swagger UI)

All JSON. Errors: `{"detail": "..."}` with proper HTTP status codes.

---

## Auth

### `POST /api/auth/register`
Create an account (rate-limited: 5/min/IP).

```json
{ "name": "Ali", "email": "ali@example.com", "password": "secret123" }
```
→ `201` `{ "access_token": "...", "token_type": "bearer", "expires_in_minutes": 1440 }`

### `POST /api/auth/login`
(rate-limited: 10/min/IP). Same body → `200` with token.

### `GET /api/auth/me`
`Authorization: Bearer <token>` → `200` `{ id, email, name, created_at }`

---

## Prayer Times

### `GET /api/times`
Query params:
| param | type | default | notes |
|---|---|---|---|
| latitude | float | — | -90..90 (required) |
| longitude | float | — | -180..180 (required) |
| date | YYYY-MM-DD | today | |
| timezone | str | Asia/Karachi | IANA zone |
| method | int | 1 | 1..16 |
| asr_juristic | int | 0 | 0=auto, 1=Shafi, 2=Hanafi |

→ `200` `{ date, times: {fajr, sunrise, dhuhr, asr, maghrib, isha}, method, method_name, asr_juristic, is_special_day, timezone, latitude, longitude }`

### `GET /api/times/month`
`year` (2000-2100), `month` (1-12) + same location params → `200` with `days[]` (each like the single-day response).

### `GET /api/now`
Same params → today's times + `now`, `next_prayer`, `next_prayer_at` (ISO).

### `GET /api/methods`
→ `200` list of all 16 calculation methods `{ id, name, region, fajr_angle, isha_angle, isha_interval, asr_factor }`.

---

## Qibla

### `GET /api/qibla?latitude=..&longitude=..`
→ `200` `{ latitude, longitude, bearing_degrees, bearing_cardinal }`

---

## Cities

### `GET /api/cities?query=karachi&limit=8`
→ `200` `[{ id, name, country, lat, lng, timezone }]` — empty query returns popular cities.

---

## Locations (auth required)

### `GET /api/locations`
Bearer token → `200` list of saved locations.

### `POST /api/locations`
```json
{ "name": "Home", "latitude": 24.86, "longitude": 67.0, "timezone": "Asia/Karachi" }
```
→ `201` saved row. `409` on duplicate name.

### `DELETE /api/locations/{id}`
→ `204`. `404` if missing/not yours.

---

## Health

### `GET /health`
→ `200` `{ "status": "ok", "service": "waqt", "version": "1.0.0" }`
