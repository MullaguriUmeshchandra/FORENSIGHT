from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.case import CaseStatus

class CaseBase(BaseModel):
    case_number: str
    case_name: str
    description: Optional[str] = None
    status: CaseStatus = CaseStatus.OPEN

class CaseCreate(CaseBase):
    pass

class CaseUpdate(BaseModel):
    case_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CaseStatus] = None

class CaseResponse(CaseBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    evidence_count: Optional[int] = 0
    artifacts_count: Optional[int] = 0
    gaps_count: Optional[int] = 0
    contradictions_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class CaseListResponse(BaseModel):
    total: int
    cases: List[CaseResponse]
