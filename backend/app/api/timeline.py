from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.timeline import TimelineListResponse, TimelineRebuildRequest, TimelineRebuildResponse
from app.services.timeline_service import TimelineService
from app.auth.dependencies import get_current_user, require_investigator
from app.models.user import User

router = APIRouter(prefix="/timeline", tags=["Timeline Reconstruction Engine"])

@router.get("", response_model=TimelineListResponse)
def get_timeline(
    case_id: int = Query(..., description="ID of the case to get timeline for"),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve chronologically ordered and correlated timeline events for a case."""
    return TimelineService.get_timeline(db=db, case_id=case_id, skip=skip, limit=limit)

@router.post("/rebuild", response_model=TimelineRebuildResponse)
def rebuild_timeline(
    req: TimelineRebuildRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Re-correlate artifacts and reconstruct full chronological timeline with automated gap/contradiction detection."""
    return TimelineService.rebuild_timeline(
        db=db,
        case_id=req.case_id,
        user=current_user,
        auto_detect_gaps=req.auto_detect_gaps,
        auto_detect_contradictions=req.auto_detect_contradictions,
        auto_generate_recommendations=req.auto_generate_recommendations
    )
