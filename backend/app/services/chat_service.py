"""AI career-advisor chat — backed by Mistral AI."""
from __future__ import annotations

import uuid

from beanie import PydanticObjectId

from ..core.config import get_settings
from ..core.exceptions import ExternalServiceError
from ..models.chat import ChatMessage, ChatSession
from ..models.resume import Resume
from ..models.user import User
from ai_engine.llm.mistral_client import MistralClient

_SYSTEM_BASE = (
    "You are CareerForge AI — a concise, practical career advisor. "
    "Give advice on resumes, interviews, career growth, skill development, "
    "and job search. Be specific, actionable, and brief. Never invent jobs "
    "or companies. If asked about anything off-topic, redirect to careers."
)


class ChatService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.mistral_api_key:
            raise ExternalServiceError("MISTRAL_API_KEY not configured")
        self._client = MistralClient(api_key=settings.mistral_api_key)

    async def send(
        self,
        user: User,
        session_id: str | None,
        message: str,
        resume_id: str | None = None,
    ) -> tuple[str, str]:
        session = await self._load_or_create(user, session_id)
        session.messages.append(ChatMessage(role="user", content=message))

        system = _SYSTEM_BASE
        if resume_id:
            resume = await Resume.find_one(
                Resume.user_id == user.id,
                Resume.id == PydanticObjectId(resume_id),
            )
            if resume and resume.raw_text:
                snippet = resume.raw_text[:3000]
                system += (
                    f"\n\nThe candidate's resume is provided below. Use it to give "
                    f"personalised advice.\n\nResume:\n{snippet}"
                )

        history = "\n".join(f"{m.role}: {m.content}" for m in session.messages[-10:])
        prompt = f"{system}\n\nConversation so far:\n{history}\n\nassistant:"
        try:
            reply = await self._client.generate_content_async(prompt)
        except Exception as e:
            raise ExternalServiceError(f"Mistral call failed: {e}") from e

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
