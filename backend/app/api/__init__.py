from fastapi import APIRouter

from .auth import router as auth_router
from .resume import router as resume_router
from .ranking import router as ranking_router
from .chat import router as chat_router
from .roadmap import router as roadmap_router
from .interview import router as interview_router
from .analytics import router as analytics_router
from .admin import router as admin_router


def build_api_router() -> APIRouter:
    router = APIRouter()
    router.include_router(auth_router, prefix="/auth", tags=["auth"])
    router.include_router(resume_router, prefix="/resumes", tags=["resumes"])
    router.include_router(ranking_router, prefix="/ranking", tags=["ranking"])
    router.include_router(chat_router, prefix="/chat", tags=["chat"])
    router.include_router(roadmap_router, prefix="/roadmap", tags=["roadmap"])
    router.include_router(interview_router, prefix="/interview", tags=["interview"])
    router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
    router.include_router(admin_router, prefix="/admin", tags=["admin"])
    return router
