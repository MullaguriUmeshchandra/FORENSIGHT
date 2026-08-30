from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class ArtifactBase(BaseModel):
    timestamp: datetime
    device: str = "Unknown Device"
    event_type: str
    event_description: str
    source: str
    source_record_id: Optional[str] = None
    metadata_json: Dict[str, Any] = {}
    confidence: float = 1.0

class ArtifactCreate(ArtifactBase):
    evidence_id: int
    case_id: int

class ArtifactResponse(ArtifactBase):
    id: int
    evidence_id: int
    case_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArtifactListResponse(BaseModel):
    total: int
    artifacts: List[ArtifactResponse]
