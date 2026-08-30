from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseListResponse
from app.services.case_service import CaseService
from app.auth.dependencies import get_current_user, require_investigator, require_admin
from app.models.user import User

router = APIRouter(prefix="/cases", tags=["Case Management"])

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_in: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Create a new forensic case."""
    return CaseService.create_case(db=db, case_in=case_in, user=current_user)

@router.get("", response_model=CaseListResponse)
def get_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all cases."""
    return CaseService.get_cases(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=CaseResponse)
def get_case(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get case details by ID."""
    return CaseService.get_case(db=db, case_id=id)

@router.put("/{id}", response_model=CaseResponse)
def update_case(
    id: int,
    case_update: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Update case metadata or status."""
    return CaseService.update_case(db=db, case_id=id, case_update=case_update, user=current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete case (Admin only)."""
    CaseService.delete_case(db=db, case_id=id, user=current_user)
    return None
