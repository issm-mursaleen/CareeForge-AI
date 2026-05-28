from __future__ import annotations

from fastapi import APIRouter, Depends

from ..models.user import User
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat_service import ChatService
from .dependencies import get_current_user

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    user: User = Depends(get_current_user),
) -> ChatResponse:
    service = ChatService()
    session_id, reply = await service.send(user, req.session_id, req.message, req.resume_id)
    return ChatResponse(session_id=session_id, reply=reply)
