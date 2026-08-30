from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.recommendation import RecommendationType, RecommendationPriority, RecommendationStatus

class RecommendationBase(BaseModel):
    recommendation_type: RecommendationType = RecommendationType.MISSING_SOURCE
    title: str
    description: str
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    status: RecommendationStatus = RecommendationStatus.PENDING
    confidence: float = 1.0

class RecommendationCreate(RecommendationBase):
    case_id: int
    gap_id: Optional[int] = None
    contradiction_id: Optional[int] = None

class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None
    priority: Optional[RecommendationPriority] = None

class RecommendationResponse(RecommendationBase):
    id: int
    case_id: int
    gap_id: Optional[int] = None
    contradiction_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RecommendationListResponse(BaseModel):
    case_id: int
    total_recommendations: int
    high_priority_count: int
    recommendations: List[RecommendationResponse]
