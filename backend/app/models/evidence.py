import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class EvidenceSourceType(str, enum.Enum):
    SYSTEM_LOGS = "SYSTEM_LOGS"
    BROWSER_ARTIFACTS = "BROWSER_ARTIFACTS"
    FILE_METADATA = "FILE_METADATA"
    USB_LOGS = "USB_LOGS"
    NETWORK_LOGS = "NETWORK_LOGS"
    CLOUD_ACTIVITY = "CLOUD_ACTIVITY"
    OTHER = "OTHER"

class EvidenceStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    source_type = Column(Enum(EvidenceSourceType), default=EvidenceSourceType.OTHER, index=True, nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256 hash (64 hex chars)
    file_size = Column(BigInteger, nullable=False)  # File size in bytes
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    collected_at = Column(DateTime, nullable=True)
    device = Column(String(100), default="Unknown Device", nullable=False)
    investigator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)

    # Relationships
    case = relationship("Case", back_populates="evidence_list")
    investigator = relationship("User", back_populates="evidence_items")
    artifacts = relationship("Artifact", back_populates="evidence", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="evidence")
