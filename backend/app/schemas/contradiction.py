from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.contradiction import ContradictionType, ContradictionSeverity
from app.schemas.artifact import ArtifactResponse

class ContradictionBase(BaseModel):
    contradiction_type: ContradictionType = ContradictionType.TIMESTAMP_CONFLICT
    description: str
    severity: ContradictionSeverity = ContradictionSeverity.MEDIUM
    confidence: float = 1.0

class ContradictionCreate(ContradictionBase):
    case_id: int
    artifact_a_id: int
    artifact_b_id: int

class ContradictionResponse(ContradictionBase):
    id: int
    case_id: int
    artifact_a_id: int
    artifact_b_id: int
    created_at: datetime
    artifact_a: Optional[ArtifactResponse] = None
    artifact_b: Optional[ArtifactResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ContradictionListResponse(BaseModel):
    case_id: int
    total_contradictions: int
    contradictions: List[ContradictionResponse]
