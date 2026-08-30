from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.evidence import EvidenceResponse, EvidenceListResponse, EvidenceUploadResponse
from app.models.evidence import EvidenceSourceType
from app.services.evidence_service import EvidenceService
from app.auth.dependencies import get_current_user, require_investigator, require_admin
from app.models.user import User

router = APIRouter(prefix="/evidence", tags=["Evidence Collection"])

@router.post("/upload", response_model=EvidenceUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    case_id: int = Form(...),
    device: str = Form("Unknown Device"),
    source_type: Optional[EvidenceSourceType] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """
    Ingest, compute SHA-256 hash, safely store, and normalize evidence file (CSV, JSON, LOG, TXT, XML).
    """
    return await EvidenceService.upload_evidence(
        db=db,
        case_id=case_id,
        file=file,
        source_type=source_type,
        device=device,
        user=current_user
    )

@router.get("", response_model=EvidenceListResponse)
def get_evidence(
    case_id: int = Query(..., description="ID of the case to filter evidence for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all ingested evidence for a case."""
    return EvidenceService.get_case_evidence(db=db, case_id=case_id)

@router.get("/{id}", response_model=EvidenceResponse)
def get_evidence_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve single evidence record by ID."""
    return EvidenceService.get_evidence_by_id(db=db, evidence_id=id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evidence(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Remove evidence item (Admin only)."""
    EvidenceService.delete_evidence(db=db, evidence_id=id, user=current_user)
    return None
