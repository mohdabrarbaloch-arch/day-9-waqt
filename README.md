# 🕌 Waqt (وقت) — Prayer Times & Qibla Direction

> Prayer times, computed **from first-principles astronomy** — no external
> prayer-time or astronomy libraries. A from-scratch solar engine, a clean
> API, and a premium mobile-first app.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/tests-32%20passing-2fbf71)
![Lint](https://img.shields.io/badge/ruff-passing-2fbf71)
![License](https://img.shields.io/badge/license-MIT-d4af37)

**Day 9 of the 30-Day AI Software Engineer Challenge.**

---

## ✨ Why this exists

Millions of Muslims check prayer times on their phones every single day — but
almost nobody knows *how* those times are computed. Waqt is a complete,
from-scratch implementation of the astronomical algorithms behind prayer
times and Qibla: solar declination, equation of time, hour angles, twilight
angles, 16 calculation methods (University of Karachi, ISNA, MWL, Umm Al-Qura,
Diyanet…), Hanafi/Shafi Asr, and the middle-of-the-night rule for high
latitudes.

It's a real tool **and** a reference implementation — clean, tested,
production-ready.

## 🚀 Features

- ⏱ **Five daily prayer times** with a live countdown to the next prayer
- 🧭 **Qibla compass** — canvas-drawn bearing to the Kaaba (great-circle math)
- 🗓 **Full monthly timetable** — any month, any year, any location
- 🏙 **120+ city database** (Pakistan + South Asia + key world cities) with search
- 🕌 **16 calculation methods** + Hanafi/Shafi Asr toggle
- 🔐 **JWT + bcrypt auth**, saved locations, rate-limited login
- 📱 **Mobile-first SPA** — dark, gold, zero build step, zero tracking
- 🧮 **All math from scratch** — Meeus solar-position series, documented
- 🐳 **Docker + PostgreSQL 16** compose setup · Vercel-ready · CI-ready

## 🖼 Screenshots

Screenshots are generated in the repository under `screenshots/` (added in the
v1.0.0 release). They show the hero countdown, the five timings, the monthly
timetable, and the Qibla compass on a phone-sized viewport.

## 🌐 Live demo

**Deployment status: built and verified locally — Vercel deploy pending**
(a Vercel account/token is required to go live; the repo is fully
Vercel-ready — `vercel.json` + `api/index.py` are in place).

- Repo: https://github.com/mohdabrarbaloch-arch/day-9-waqt
- Release: https://github.com/mohdabrarbaloch-arch/day-9-waqt/releases/tag/v1.0.0

## 🛠 Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 · FastAPI · Pydantic v2 |
| DB | SQLAlchemy 2.0 · SQLite (dev) · PostgreSQL 16 (Docker) |
| Auth | JWT (HS256) · bcrypt (12 rounds) |
| Frontend | Vanilla JS SPA · CSS variables · Canvas Qibla compass |
| Ops | Docker · docker-compose · Vercel (serverless) |

## 📦 Install & run

```bash
git clone https://github.com/mohdabrarbaloch-arch/day-9-waqt.git
cd day-9-waqt
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env          # set SECRET_KEY (min 32 chars)
uvicorn app.main:app --reload
```

→ App at http://localhost:8000 · API docs at http://localhost:8000/docs

Docker:

```bash
docker compose up --build
```

Full instructions: [docs/SETUP.md](docs/SETUP.md) · [docs/USAGE.md](docs/USAGE.md) · [docs/API.md](docs/API.md)

## 🧪 Tests

```bash
pytest -q        # astronomy math, methods, Qibla, auth, times, locations, rate limits
ruff check .     # lint
```

## 🔭 How the math works

1. **Julian Day** for the given date
2. **Solar declination** & **equation of time** (Meeus low-precision series)
3. **Solar noon** (transit) = 12:00 − 4·longitude − EoT
4. **Hour angle** at each twilight angle → Fajr / Isha offsets
5. **Asr** via shadow factor (1 or 2) hour angle
6. **Maghrib** = sunset (90.833°); **Isha** = angle or fixed interval (Umm Al-Qura: +90 min)
7. **High latitudes**: middle-of-the-night rule when |lat| > 48°
8. **Qibla**: initial great-circle bearing to the Kaaba (21.4225°N, 39.8262°E)

See [ARCHITECTURE.md](ARCHITECTURE.md) and `app/services/astronomy.py`.

## 📄 License

MIT — see [LICENSE](LICENSE). Built by ABraz Baloch · Day 9/30.
