"""AI career-advisor chat — backed by Groq."""
from __future__ import annotations

import uuid

from ..core.config import get_settings
from ..core.exceptions import ExternalServiceError
from ..models.chat import ChatMessage, ChatSession
from ..models.user import User
from ai_engine.llm.groq_client import GroqClient

_SYSTEM = (
    "You are CareerForge AI — a concise, practical career advisor. "
    "Give advice on resumes, interviews, career growth, skill development, "
    "and job search. Be specific, actionable, and brief. Never invent jobs "
    "or companies. If asked about anything off-topic, redirect to careers."
)


class ChatService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.groq_api_key:
            raise ExternalServiceError("GROQ_API_KEY not configured")
        self._client = GroqClient(api_key=settings.groq_api_key)

    async def send(self, user: User, session_id: str | None, message: str) -> tuple[str, str]:
        session = await self._load_or_create(user, session_id)
        session.messages.append(ChatMessage(role="user", content=message))

        history = "\n".join(f"{m.role}: {m.content}" for m in session.messages[-10:])
        prompt = f"Conversation so far:\n{history}\n\nassistant:"
        try:
            reply = await self._client.generate_content_async(prompt, system_prompt=_SYSTEM)
        except Exception as e:
            raise ExternalServiceError(f"Groq call failed: {e}") from e

        session.messages.append(ChatMessage(role="assistant", content=reply))
        await session.save()
        return session.session_id, reply

    @staticmethod
    async def _load_or_create(user: User, session_id: str | None) -> ChatSession:
        if session_id:
            existing = await ChatSession.find_one(
                ChatSession.user_id == user.id, ChatSession.session_id == session_id
            )
            if existing:
                return existing
        new = ChatSession(user_id=user.id, session_id=session_id or uuid.uuid4().hex)
        await new.insert()
        return new
