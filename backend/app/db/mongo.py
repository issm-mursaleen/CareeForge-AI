"""Mongo connection + Beanie ODM initialization."""
from __future__ import annotations

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..core.config import get_settings
from ..core.logging import get_logger
from ..models import ALL_DOCUMENTS

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def init_db() -> None:
    global _client, _db
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db]
    await init_beanie(database=_db, document_models=list(ALL_DOCUMENTS))
    logger.info("mongo_connected", db=settings.mongodb_db)


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        logger.info("mongo_closed")


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized — call init_db() first")
    return _db
