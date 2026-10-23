import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api import download, fixtures, games
from app.database import init_db
from app.scheduler import start_scheduler, stop_scheduler

ROOT_POSTERS = Path(__file__).resolve().parent.parent.parent / "posters"
BACKEND_POSTERS = Path(__file__).resolve().parent.parent / "posters"
POSTERS_DIR = ROOT_POSTERS if ROOT_POSTERS.exists() else BACKEND_POSTERS
POSTERS_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Game Archive API", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")] if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router, prefix="/games", tags=["games"])
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(download.router, prefix="/download", tags=["download"])
app.include_router(download.router, prefix="/api/download", tags=["download"])
app.include_router(fixtures.router)
app.mount("/posters", StaticFiles(directory=str(POSTERS_DIR)), name="posters")


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}


@app.get("/", tags=["meta"])
async def root():
    return {"name": "Game Archive API", "docs": "/docs"}