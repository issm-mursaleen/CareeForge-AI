from .user import User, UserRole
from .resume import Resume
from .job_match import JobMatch
from .interview import Interview
from .analytics import Analytics
from .ai_log import AILog
from .roadmap import RoadmapDoc
from .chat import ChatSession
from .ml_metrics import MLMetricsDoc
from .good_fit_metrics import GoodFitMetricsDoc

ALL_DOCUMENTS = (
    User,
    Resume,
    JobMatch,
    Interview,
    Analytics,
    AILog,
    RoadmapDoc,
    ChatSession,
    MLMetricsDoc,
    GoodFitMetricsDoc,
)

__all__ = [
    "User", "UserRole", "Resume", "JobMatch", "Interview", "Analytics",
    "AILog", "RoadmapDoc", "ChatSession", "MLMetricsDoc",
    "GoodFitMetricsDoc", "ALL_DOCUMENTS",
]
