from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class ActivityLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    case_id: Optional[int] = None
    action: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    created_at: datetime
    formatted_time: Optional[str] = None
    action_label: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class DashboardSummaryResponse(BaseModel):
    case_id: Optional[int] = None
    evidence_sources: int
    evidence_sources_today: int
    artifacts_processed: int
    gaps_detected: int
    unexplained_gaps_count: int
    recommendations_count: int
    high_priority_recommendations_count: int
    reports_generated: int
    contradictions_count: int
    gap_summary: Dict[str, int]
    source_breakdown: Dict[str, int]

class DashboardActivityResponse(BaseModel):
    total: int
    activities: List[ActivityLogResponse]
