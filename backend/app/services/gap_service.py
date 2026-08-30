from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.timeline import TimelineEvent
from app.models.gap import Gap, GapType
from app.models.user import User
from app.schemas.gap import GapResponse, GapSummaryResponse, GapSummaryItem
from app.ml.gap_analyzer import GapAnalyzer, format_duration
from app.services.activity_service import ActivityService
from app.utils.logger import logger

class GapService:
    """Service to calculate and detect temporal gaps and sequence discontinuities from real timeline data."""

    @staticmethod
    def detect_gaps_for_case(db: Session, case_id: int, user: Optional[User] = None) -> List[Gap]:
        # 1. Fetch timeline events
        events = db.query(TimelineEvent).filter(
            TimelineEvent.case_id == case_id
        ).order_by(TimelineEvent.timestamp.asc()).all()

        if len(events) < 2:
            return []

        # 2. Clear previous gaps for this case
        db.query(Gap).filter(Gap.case_id == case_id).delete()
        db.commit()

        # 3. Detect time gaps using actual timestamps
        detected_time_gaps = GapAnalyzer.detect_time_gaps(events)
        
        # 4. Detect sequence anomalies (missing expected events)
        detected_seq_gaps = GapAnalyzer.detect_sequence_anomalies(events)

        all_gap_dicts = detected_time_gaps + detected_seq_gaps
        db_gaps: List[Gap] = []

        for gd in all_gap_dicts:
            gap = Gap(
                case_id=case_id,
                start_time=gd["start_time"],
                end_time=gd["end_time"],
                duration_seconds=gd["duration_seconds"],
                previous_event_id=gd.get("previous_event_id"),
                next_event_id=gd.get("next_event_id"),
                severity=gd["severity"],
                gap_type=gd.get("gap_type", GapType.UNEXPLAINED_TIME_GAP),
                reason=gd["reason"],
                confidence=gd.get("confidence", 1.0)
            )
            db_gaps.append(gap)

        if db_gaps:
            db.add_all(db_gaps)
            db.commit()
            for g in db_gaps:
                db.refresh(g)

            ActivityService.log_activity(
                db=db,
                action="GAP_DETECTED",
                case_id=case_id,
                user_id=user.id if user else None,
                details={"gaps_count": len(db_gaps)}
            )

        logger.info(f"Detected {len(db_gaps)} gaps for Case {case_id}")
        return db_gaps

    @staticmethod
    def get_gaps_summary(db: Session, case_id: int) -> GapSummaryResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        gaps = db.query(Gap).filter(Gap.case_id == case_id).order_by(Gap.start_time.asc()).all()

        unexplained_count = sum(1 for g in gaps if g.gap_type == GapType.UNEXPLAINED_TIME_GAP)
        missing_exp_count = sum(1 for g in gaps if g.gap_type == GapType.MISSING_EXPECTED_EVENT)
        inconsistency_count = sum(1 for g in gaps if g.gap_type == GapType.TIMESTAMP_INCONSISTENCY)

        summary_items = [
            GapSummaryItem(type="Unexplained Time Gaps", count=unexplained_count, status="High" if unexplained_count > 0 else "Normal"),
            GapSummaryItem(type="Missing Expected Events", count=missing_exp_count, status="Medium" if missing_exp_count > 0 else "Normal"),
            GapSummaryItem(type="Timestamp Inconsistencies", count=inconsistency_count, status="Low" if inconsistency_count > 0 else "Normal"),
        ]

        resp_gaps: List[GapResponse] = []
        for g in gaps:
            r = GapResponse.model_validate(g)
            r.formatted_duration = format_duration(g.duration_seconds)
            resp_gaps.append(r)

        return GapSummaryResponse(
            case_id=case_id,
            total_gaps=len(gaps),
            unexplained_time_gaps=unexplained_count,
            missing_expected_events=missing_exp_count,
            timestamp_inconsistencies=inconsistency_count,
            summary_items=summary_items,
            gaps=resp_gaps
        )
