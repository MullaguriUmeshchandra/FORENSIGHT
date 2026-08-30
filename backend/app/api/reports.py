from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.report import ReportCreate, ReportResponse, ReportListResponse
from app.services.report_service import ReportService
from app.auth.dependencies import get_current_user, require_investigator
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["Forensic Reports"])

@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_investigator)
):
    """Generate comprehensive forensic findings report for a case."""
    return ReportService.generate_case_report(db=db, report_in=report_in, user=current_user)

@router.get("", response_model=ReportListResponse)
def get_reports(
    case_id: int = Query(..., description="Case ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all generated forensic reports for a case."""
    return ReportService.get_case_reports(db=db, case_id=case_id)

@router.get("/{id}/download")
def download_report(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download raw report artifact file (Markdown / Text)."""
    file_path = ReportService.get_report_file(db=db, report_id=id, user=current_user)
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="text/markdown"
    )
