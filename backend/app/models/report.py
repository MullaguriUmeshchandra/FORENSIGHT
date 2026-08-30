import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base

class ReportFormat(str, enum.Enum):
    JSON = "JSON"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    PDF = "PDF"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    findings = Column(JSON, default=dict, nullable=False)
    timeline_summary = Column(JSON, default=dict, nullable=False)
    gap_summary = Column(JSON, default=dict, nullable=False)
    contradiction_summary = Column(JSON, default=dict, nullable=False)
    recommendations_summary = Column(JSON, default=dict, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    report_format = Column(Enum(ReportFormat), default=ReportFormat.JSON, nullable=False)
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    case = relationship("Case", back_populates="reports")
    generator = relationship("User", back_populates="reports")
