import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class TimelineEventStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    INFERRED = "INFERRED"
    MISSING = "MISSING"
    CONTRADICTION = "CONTRADICTION"

class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    device = Column(String(100), default="Unknown Device", nullable=False)
    event = Column(Text, nullable=False)
    source = Column(String(100), nullable=False)
    evidence_id = Column(Integer, ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)
    status = Column(Enum(TimelineEventStatus), default=TimelineEventStatus.CONFIRMED, nullable=False)
    related_artifacts = Column(JSON, default=list, nullable=False)  # List of artifact IDs
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="timeline_events")
    evidence = relationship("Evidence", back_populates="timeline_events")
