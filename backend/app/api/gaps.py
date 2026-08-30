from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.gap import GapSummaryResponse
from app.services.gap_service import GapService
from app.auth.dependencies import get_current_user, require_investigator
from app.models.user import User

router = APIRouter(prefix="/gaps", tags=["Gap Detection"])

@router.get("", response_model=GapSummaryResponse)
def get_gaps(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve detected unexplained time gaps, missing expected events, and summary counts."""
    return GapService.get_gaps_summary(db=db, case_id=case_id)

@router.post("/detect", response_model=GapSummaryResponse)
def detect_gaps(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Run mathematical gap analysis and sequence discontinuity detection on case timeline."""
    GapService.detect_gaps_for_case(db=db, case_id=case_id, user=current_user)
    return GapService.get_gaps_summary(db=db, case_id=case_id)
