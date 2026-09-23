"""FastAPI entrypoint for MoneyGraph."""

from fastapi import FastAPI

app = FastAPI(title="HackAlem MoneyGraph API")


@app.get("/health")
def health() -> dict[str, str]:
    """Return a minimal health check for local development."""
    return {"status": "ok"}
