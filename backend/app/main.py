"""FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import build_api_router
from .core.config import get_settings
from .core.logging import configure_logging, get_logger
from .core.ml_model import load_model
from .db import close_db, init_db
from .middleware import RequestLoggingMiddleware, register_exception_handlers

configure_logging()
logger = get_logger("app")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("startup", env=settings.env)
    await init_db()

    # Load the local TF-IDF job-role classifier into process memory so
    # request handlers can predict synchronously without disk I/O.
    load_model()

    # Warm caches that cost real time on the first request
    try:
        from ai_engine.preprocessing import ensure_nltk
        ensure_nltk()
        # Loading the SBERT model eagerly is commented out so local dev boots instantly
        # get_sbert_model()
    except Exception as e:  # noqa: BLE001
        logger.warning("warmup_failed", error=str(e))

    yield
    await close_db()
    logger.info("shutdown")


app = FastAPI(
    title="CareerForge AI",
    version="0.1.0",
    description="AI-native career platform — resumes, ranking, interviews, roadmaps.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
register_exception_handlers(app)

app.include_router(build_api_router(), prefix=settings.api_v1_prefix)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": app.version, "env": settings.env}
