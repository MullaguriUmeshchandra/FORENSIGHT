import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class GapSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class GapType(str, enum.Enum):
    UNEXPLAINED_TIME_GAP = "UNEXPLAINED_TIME_GAP"
    MISSING_EXPECTED_EVENT = "MISSING_EXPECTED_EVENT"
    TIMESTAMP_INCONSISTENCY = "TIMESTAMP_INCONSISTENCY"

class Gap(Base):
    __tablename__ = "gaps"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    previous_event_id = Column(Integer, ForeignKey("timeline_events.id", ondelete="SET NULL"), nullable=True)
    next_event_id = Column(Integer, ForeignKey("timeline_events.id", ondelete="SET NULL"), nullable=True)
    severity = Column(Enum(GapSeverity), nullable=False)
    gap_type = Column(Enum(GapType), default=GapType.UNEXPLAINED_TIME_GAP, nullable=False)
    reason = Column(Text, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="gaps")
    previous_event = relationship("TimelineEvent", foreign_keys=[previous_event_id])
    next_event = relationship("TimelineEvent", foreign_keys=[next_event_id])
    recommendations = relationship("Recommendation", back_populates="gap", cascade="all, delete-orphan")
