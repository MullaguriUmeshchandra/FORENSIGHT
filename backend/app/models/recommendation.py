import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base

class RecommendationType(str, enum.Enum):
    MISSING_SOURCE = "MISSING_SOURCE"
    DEEPER_INSPECTION = "DEEPER_INSPECTION"
    CLOUD_LOGS = "CLOUD_LOGS"
    MEMORY_DUMP = "MEMORY_DUMP"
    MFT_PARSING = "MFT_PARSING"
    NETWORK_PCAP = "NETWORK_PCAP"
    REGISTRY_HIVE = "REGISTRY_HIVE"
    OTHER = "OTHER"

class RecommendationPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RecommendationStatus(str, enum.Enum):
    PENDING = "PENDING"
    REVIEWED = "REVIEWED"
    ACTIONED = "ACTIONED"

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    gap_id = Column(Integer, ForeignKey("gaps.id", ondelete="CASCADE"), nullable=True)
    contradiction_id = Column(Integer, ForeignKey("contradictions.id", ondelete="CASCADE"), nullable=True)
    recommendation_type = Column(Enum(RecommendationType), default=RecommendationType.MISSING_SOURCE, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM, nullable=False)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="recommendations")
    gap = relationship("Gap", back_populates="recommendations")
    contradiction = relationship("Contradiction", back_populates="recommendations")
