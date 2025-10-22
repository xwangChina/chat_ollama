import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import api_router
from .utils.logging import configure_logging

app = FastAPI(title="Chat Ollama Backend", version="0.1.0")

# Configure logging early
configure_logging(extra_loggers=[__name__, "app", "app.api", "app.services"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return a simple health status for readiness probes."""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event() -> None:
    """Log a brief configuration summary on startup."""
    logger = logging.getLogger("app.startup")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    key_set = bool(os.getenv("OPENAI_API_KEY"))
    logger.info(
        "Startup config: OPENAI_BASE_URL=%s, OPENAI_MODEL=%s, OPENAI_API_KEY set=%s",
        base_url,
        model,
        key_set,
    )
