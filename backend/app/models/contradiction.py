import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class ContradictionType(str, enum.Enum):
    TIMESTAMP_CONFLICT = "TIMESTAMP_CONFLICT"
    DEVICE_CONFLICT = "DEVICE_CONFLICT"
    EVENT_ORDER_CONFLICT = "EVENT_ORDER_CONFLICT"
    INCONSISTENT_USER_ACTIVITY = "INCONSISTENT_USER_ACTIVITY"
    OTHER = "OTHER"

class ContradictionSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class Contradiction(Base):
    __tablename__ = "contradictions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    artifact_a_id = Column(Integer, ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False)
    artifact_b_id = Column(Integer, ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False)
    contradiction_type = Column(Enum(ContradictionType), default=ContradictionType.TIMESTAMP_CONFLICT, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(ContradictionSeverity), default=ContradictionSeverity.MEDIUM, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="contradictions")
    artifact_a = relationship("Artifact", foreign_keys=[artifact_a_id])
    artifact_b = relationship("Artifact", foreign_keys=[artifact_b_id])
    recommendations = relationship("Recommendation", back_populates="contradiction", cascade="all, delete-orphan")
