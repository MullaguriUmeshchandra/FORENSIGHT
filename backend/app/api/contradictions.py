from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.contradiction import ContradictionListResponse
from app.services.contradiction_service import ContradictionService
from app.auth.dependencies import get_current_user, require_investigator
from app.models.user import User

router = APIRouter(prefix="/contradictions", tags=["Contradiction Detection"])

@router.get("", response_model=ContradictionListResponse)
def get_contradictions(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve cross-source contradictions and discrepancies for a case."""
    return ContradictionService.get_case_contradictions(db=db, case_id=case_id)

@router.post("/detect", response_model=ContradictionListResponse)
def detect_contradictions(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Run contradiction detection algorithm across normalized artifacts."""
    ContradictionService.detect_contradictions_for_case(db=db, case_id=case_id, user=current_user)
    return ContradictionService.get_case_contradictions(db=db, case_id=case_id)
