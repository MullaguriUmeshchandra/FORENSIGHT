from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.utils.logger import logger

class ActivityService:
    """Service for forensic audit trails and activity logging."""

    @staticmethod
    def log_activity(
        db: Session,
        action: str,
        case_id: Optional[int] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> ActivityLog:
        """Create an immutable activity log entry."""
        log_entry = ActivityLog(
            action=action,
            case_id=case_id,
            user_id=user_id,
            details=details or {},
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        logger.info(f"Audit Log: [{action}] Case={case_id} User={user_id} Details={details}")
        return log_entry

    @staticmethod
    def get_activities(
        db: Session,
        case_id: Optional[int] = None,
        limit: int = 50
    ) -> List[ActivityLog]:
        """Fetch chronological activity logs."""
        query = db.query(ActivityLog)
        if case_id:
            query = query.filter(ActivityLog.case_id == case_id)
        return query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
