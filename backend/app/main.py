"""FastAPI entrypoint for the read-only MoneyGraph investigation API."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import router
from backend.app.api.models import HealthResponse
from backend.app.api.repository import get_repository


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Load and validate the immutable analysis snapshot once at startup."""
    get_repository()
    yield


app = FastAPI(
    title="HackAlem MoneyGraph API",
    description="Read-only access to deterministic investigation hypotheses.",
    version="0.3.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
