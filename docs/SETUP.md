# Setup Guide

Waqt runs anywhere Python 3.11 runs. Two options: local (SQLite) or Docker (PostgreSQL).

## Option A — Local (fastest)

```bash
# 1. Clone
git clone https://github.com/mohdabrarbaloch-arch/day-9-waqt.git
cd day-9-waqt

# 2. Virtualenv + deps
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 3. Env
cp .env.example .env
# edit SECRET_KEY (min 32 chars)

# 4. Run
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000 — the SPA loads at `/`. API docs at `/docs`.

## Option B — Docker (PostgreSQL)

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:8000
- Postgres 16 runs in the `db` container; `DATABASE_URL` points at it.

## Tests & Lint

```bash
ruff check . && ruff format --check .
pytest -q          # 30+ tests: astronomy math, methods, full API flow
```

## Vercel deployment

The repo is Vercel-ready (`vercel.json` + `api/index.py`). Import it at
vercel.com/new, set `SECRET_KEY`, `CORS_ORIGINS` and (optionally)
`DATABASE_URL`, then Deploy. On Vercel, SQLite automatically falls back to
`/tmp/waqt.db` — fine for demos, but use a hosted Postgres (Neon/Supabase)
for real persistence.
