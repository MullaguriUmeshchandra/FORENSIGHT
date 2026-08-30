from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.report import ReportFormat

class ReportBase(BaseModel):
    title: str
    summary: str
    report_format: ReportFormat = ReportFormat.JSON

class ReportCreate(BaseModel):
    case_id: int
    title: Optional[str] = None
    report_format: ReportFormat = ReportFormat.JSON

class ReportResponse(ReportBase):
    id: int
    case_id: int
    findings: Dict[str, Any]
    timeline_summary: Dict[str, Any]
    gap_summary: Dict[str, Any]
    contradiction_summary: Dict[str, Any]
    recommendations_summary: Dict[str, Any]
    generated_by: Optional[int] = None
    file_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportListResponse(BaseModel):
    case_id: int
    total_reports: int
    reports: List[ReportResponse]
