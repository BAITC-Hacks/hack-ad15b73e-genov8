"""FastAPI entrypoint for the read-only MoneyGraph investigation API."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.api.models import HealthResponse
from backend.app.api.repository import get_repository


ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Load configuration and validate the analysis snapshot once at startup."""
    load_dotenv(ROOT_ENV_FILE, override=False)
    get_repository()
    yield


app = FastAPI(
    title="HackAlem MoneyGraph API",
    description="Read-only access to deterministic investigation hypotheses.",
    version="0.4.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
