from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.investigation import InvestigationOverviewResponse, GraphDataResponse
from app.services.investigation_service import InvestigationService
from app.graph.graph_service import GraphService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/investigation", tags=["Investigation Workflow & Knowledge Graph"])

@router.get("/overview", response_model=InvestigationOverviewResponse)
def get_investigation_overview(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve 5-step investigative workflow status (Collect -> Normalize -> Build Timeline -> Detect Gaps -> Recommend)."""
    return InvestigationService.get_investigation_overview(db=db, case_id=case_id)

@router.get("/relationships", response_model=GraphDataResponse)
def get_investigation_relationships(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve complete Neo4j node-link graph model of forensic entities and timeline relationships."""
    return GraphService.get_case_graph(db=db, case_id=case_id)
