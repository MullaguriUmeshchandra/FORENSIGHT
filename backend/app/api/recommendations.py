from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.recommendation import RecommendationListResponse, RecommendationResponse, RecommendationUpdate
from app.services.recommendation_service import RecommendationService
from app.auth.dependencies import get_current_user, require_investigator
from app.models.user import User

router = APIRouter(prefix="/recommendations", tags=["Investigative Recommendations"])

@router.get("", response_model=RecommendationListResponse)
def get_recommendations(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve prioritized investigative recommendations for missing sources and gap resolution."""
    return RecommendationService.get_case_recommendations(db=db, case_id=case_id)

@router.post("/generate", response_model=RecommendationListResponse)
def generate_recommendations(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Formulate actionable forensic recommendations from detected gaps and contradictions."""
    RecommendationService.generate_recommendations_for_case(db=db, case_id=case_id, user=current_user)
    return RecommendationService.get_case_recommendations(db=db, case_id=case_id)

@router.put("/{id}", response_model=RecommendationResponse)
def update_recommendation(
    id: int,
    update_in: RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Update recommendation status (PENDING -> REVIEWED -> ACTIONED) or priority."""
    return RecommendationService.update_recommendation(db=db, recommendation_id=id, update_in=update_in, user=current_user)
