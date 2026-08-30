from fastapi import APIRouter
from .auth import router as auth_router
from .cases import router as cases_router
from .evidence import router as evidence_router
from .timeline import router as timeline_router
from .gaps import router as gaps_router
from .contradictions import router as contradictions_router
from .recommendations import router as recommendations_router
from .investigation import router as investigation_router
from .reports import router as reports_router
from .dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(cases_router)
api_router.include_router(evidence_router)
api_router.include_router(timeline_router)
api_router.include_router(gaps_router)
api_router.include_router(contradictions_router)
api_router.include_router(recommendations_router)
api_router.include_router(investigation_router)
api_router.include_router(reports_router)
api_router.include_router(dashboard_router)

__all__ = ["api_router"]
