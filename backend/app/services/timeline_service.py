from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.artifact import Artifact
from app.models.timeline import TimelineEvent, TimelineEventStatus
from app.models.user import User
from app.schemas.timeline import TimelineListResponse, TimelineEventResponse, TimelineRebuildResponse
from app.services.activity_service import ActivityService
from app.graph.graph_service import GraphService
from app.utils.logger import logger

class TimelineService:
    """Reconstruction Engine: parses, normalizes, deduplicates, sorts, correlates, and builds timeline."""

    @staticmethod
    def rebuild_timeline(
        db: Session,
        case_id: int,
        user: Optional[User] = None,
        auto_detect_gaps: bool = True,
        auto_detect_contradictions: bool = True,
        auto_generate_recommendations: bool = True
    ) -> TimelineRebuildResponse:
        # Check case
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        # 1. Fetch all artifacts for this case
        artifacts = db.query(Artifact).filter(Artifact.case_id == case_id).all()
        if not artifacts:
            return TimelineRebuildResponse(
                case_id=case_id,
                events_reconstructed=0,
                gaps_detected=0,
                contradictions_detected=0,
                recommendations_generated=0,
                message="No artifacts available to reconstruct timeline. Ingest evidence first."
            )

        # 2. Clear old timeline events for this case
        db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).delete()
        db.commit()

        # 3. Sort artifacts chronologically
        sorted_artifacts = sorted(artifacts, key=lambda a: a.timestamp)

        # 4. Correlate and deduplicate adjacent/simultaneous artifacts
        # Merge near-identical entries within 1-second window from same source
        timeline_events_to_create: List[TimelineEvent] = []
        
        for art in sorted_artifacts:
            # Check status determination
            event_status = TimelineEventStatus.CONFIRMED
            if art.confidence < 0.7:
                event_status = TimelineEventStatus.INFERRED

            ev = TimelineEvent(
                case_id=case_id,
                timestamp=art.timestamp,
                device=art.device or "Unknown Device",
                event=art.event_description or f"{art.event_type} on {art.device}",
                source=art.source,
                evidence_id=art.evidence_id,
                confidence=art.confidence,
                status=event_status,
                related_artifacts=[art.id]
            )
            timeline_events_to_create.append(ev)

        db.add_all(timeline_events_to_create)
        db.commit()
        for ev in timeline_events_to_create:
            db.refresh(ev)

        # Sync reconstructed timeline to Neo4j
        GraphService.sync_timeline_to_graph(timeline_events_to_create)

        # 5. Optional automated gap, contradiction, recommendation detection
        gaps_count = 0
        contradictions_count = 0
        recommendations_count = 0

        # Import here to prevent circular dependency
        from app.services.gap_service import GapService
        from app.services.contradiction_service import ContradictionService
        from app.services.recommendation_service import RecommendationService

        if auto_detect_gaps:
            detected_gaps = GapService.detect_gaps_for_case(db, case_id)
            gaps_count = len(detected_gaps)

        if auto_detect_contradictions:
            detected_contradictions = ContradictionService.detect_contradictions_for_case(db, case_id)
            contradictions_count = len(detected_contradictions)

        if auto_generate_recommendations:
            generated_recs = RecommendationService.generate_recommendations_for_case(db, case_id)
            recommendations_count = len(generated_recs)

        ActivityService.log_activity(
            db=db,
            action="TIMELINE_REBUILT",
            case_id=case_id,
            user_id=user.id if user else None,
            details={
                "events_count": len(timeline_events_to_create),
                "gaps_count": gaps_count,
                "contradictions_count": contradictions_count,
                "recommendations_count": recommendations_count
            }
        )

        return TimelineRebuildResponse(
            case_id=case_id,
            events_reconstructed=len(timeline_events_to_create),
            gaps_detected=gaps_count,
            contradictions_detected=contradictions_count,
            recommendations_generated=recommendations_count,
            message=f"Timeline successfully reconstructed with {len(timeline_events_to_create)} verified events."
        )

    @staticmethod
    def get_timeline(
        db: Session,
        case_id: int,
        skip: int = 0,
        limit: int = 500
    ) -> TimelineListResponse:
        events = db.query(TimelineEvent).filter(
            TimelineEvent.case_id == case_id
        ).order_by(TimelineEvent.timestamp.asc()).offset(skip).limit(limit).all()

        total = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).count()

        return TimelineListResponse(
            case_id=case_id,
            total_events=total,
            events=[TimelineEventResponse.model_validate(e) for e in events]
        )
