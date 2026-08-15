"""Waqt — Prayer Times & Qibla Direction API + SPA.

Run locally:
    uvicorn app.main:app --reload

Docs: http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import auth, cities, locations, times
from app.core.config import get_settings
from app.core.database import init_db

STATIC_DIR = Path(__file__).resolve().parent / "static"

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Waqt API",
    description="Prayer times & Qibla direction — astronomical engine from first principles.",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(times.router)
app.include_router(locations.router)
app.include_router(cities.router)

# Static SPA
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "waqt", "version": "1.0.0"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    f = STATIC_DIR / "favicon.svg"
    return FileResponse(f) if f.exists() else FileResponse(STATIC_DIR / "index.html")
