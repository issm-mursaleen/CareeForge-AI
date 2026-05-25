from __future__ import annotations

from datetime import datetime
from typing import Literal

from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    ts: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(Document):
    user_id: PydanticObjectId
    session_id: str
    title: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_history"
        indexes = [IndexModel([("user_id", 1), ("session_id", 1)])]
