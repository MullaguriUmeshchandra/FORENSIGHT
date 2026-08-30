from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.evidence import EvidenceSourceType, EvidenceStatus

class EvidenceBase(BaseModel):
    source_type: EvidenceSourceType = EvidenceSourceType.OTHER
    device: str = "Unknown Device"
    collected_at: Optional[datetime] = None

class EvidenceCreate(EvidenceBase):
    case_id: int

class EvidenceResponse(EvidenceBase):
    id: int
    case_id: int
    filename: str
    original_filename: str
    file_path: str
    file_hash: str
    file_size: int
    uploaded_at: datetime
    investigator_id: Optional[int] = None
    status: EvidenceStatus
    error_message: Optional[str] = None
    artifacts_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class EvidenceListResponse(BaseModel):
    total: int
    evidence: List[EvidenceResponse]

class EvidenceUploadResponse(BaseModel):
    evidence: EvidenceResponse
    artifacts_created: int
    message: str
