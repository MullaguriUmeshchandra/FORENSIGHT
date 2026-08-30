from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.gap import GapSeverity, GapType

class GapBase(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    severity: GapSeverity
    gap_type: GapType = GapType.UNEXPLAINED_TIME_GAP
    reason: str
    confidence: float = 1.0

class GapCreate(GapBase):
    case_id: int
    previous_event_id: Optional[int] = None
    next_event_id: Optional[int] = None

class GapResponse(GapBase):
    id: int
    case_id: int
    previous_event_id: Optional[int] = None
    next_event_id: Optional[int] = None
    created_at: datetime
    formatted_duration: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GapSummaryItem(BaseModel):
    type: str
    count: int
    status: str  # High, Medium, Low

class GapSummaryResponse(BaseModel):
    case_id: int
    total_gaps: int
    unexplained_time_gaps: int
    missing_expected_events: int
    timestamp_inconsistencies: int
    summary_items: List[GapSummaryItem]
    gaps: List[GapResponse]
