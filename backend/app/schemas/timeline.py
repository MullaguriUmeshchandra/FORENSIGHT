from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
from app.models.timeline import TimelineEventStatus

class TimelineEventBase(BaseModel):
    timestamp: datetime
    device: str = "Unknown Device"
    event: str
    source: str
    confidence: float = 1.0
    status: TimelineEventStatus = TimelineEventStatus.CONFIRMED
    related_artifacts: List[Any] = []

class TimelineEventCreate(TimelineEventBase):
    case_id: int
    evidence_id: Optional[int] = None

class TimelineEventResponse(TimelineEventBase):
    id: int
    case_id: int
    evidence_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TimelineListResponse(BaseModel):
    case_id: int
    total_events: int
    events: List[TimelineEventResponse]

class TimelineRebuildRequest(BaseModel):
    case_id: int
    auto_detect_gaps: bool = True
    auto_detect_contradictions: bool = True
    auto_generate_recommendations: bool = True

class TimelineRebuildResponse(BaseModel):
    case_id: int
    events_reconstructed: int
    gaps_detected: int
    contradictions_detected: int
    recommendations_generated: int
    message: str
