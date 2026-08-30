from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.gap import Gap, GapSeverity, GapType
from app.models.contradiction import Contradiction, ContradictionType
from app.models.recommendation import Recommendation, RecommendationType, RecommendationPriority, RecommendationStatus
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse, RecommendationListResponse, RecommendationUpdate
from app.services.activity_service import ActivityService
from app.utils.logger import logger

class RecommendationService:
    """Service to generate defensible investigative recommendations based on detected gaps and contradictions."""

    @staticmethod
    def generate_recommendations_for_case(db: Session, case_id: int, user: Optional[User] = None) -> List[Recommendation]:
        # Fetch gaps and contradictions
        gaps = db.query(Gap).filter(Gap.case_id == case_id).all()
        contradictions = db.query(Contradiction).filter(Contradiction.case_id == case_id).all()

        # Clear existing pending recommendations for this case to refresh
        db.query(Recommendation).filter(
            Recommendation.case_id == case_id,
            Recommendation.status == RecommendationStatus.PENDING
        ).delete()
        db.commit()

        recs_to_create: List[Recommendation] = []

        # 1. Recommendations from Gaps
        for gap in gaps:
            t1_str = gap.start_time.strftime("%H:%M:%S")
            t2_str = gap.end_time.strftime("%H:%M:%S")

            if gap.gap_type == GapType.UNEXPLAINED_TIME_GAP:
                prio = RecommendationPriority.HIGH if gap.severity == GapSeverity.HIGH else (
                    RecommendationPriority.MEDIUM if gap.severity == GapSeverity.MEDIUM else RecommendationPriority.LOW
                )
                rec = Recommendation(
                    case_id=case_id,
                    gap_id=gap.id,
                    recommendation_type=RecommendationType.MFT_PARSING,
                    title=f"Acquire File System Journal & Prefetch for {t1_str}–{t2_str} Transition",
                    description=(
                        f"An unexplained interval of {gap.duration_seconds // 60} minutes exists between {t1_str} and {t2_str} UTC. "
                        f"Recommended investigative action: Collect and parse NTFS $MFT, $LogFile, and Windows Prefetch / BAM "
                        f"to determine whether user processes or file modifications occurred during this unrecorded interval."
                    ),
                    priority=prio,
                    status=RecommendationStatus.PENDING,
                    confidence=0.9
                )
                recs_to_create.append(rec)

            elif gap.gap_type == GapType.MISSING_EXPECTED_EVENT:
                rec = Recommendation(
                    case_id=case_id,
                    gap_id=gap.id,
                    recommendation_type=RecommendationType.MISSING_SOURCE,
                    title="Ingest Security Logon Records (Event ID 4624/4625)",
                    description=(
                        "Observed forensic artifacts show privileged or interactive operations without preceding authentication records. "
                        "Recommended investigative action: Acquire Windows Security Event logs or PAM authentication records to verify initial logon telemetry."
                    ),
                    priority=RecommendationPriority.HIGH,
                    status=RecommendationStatus.PENDING,
                    confidence=0.95
                )
                recs_to_create.append(rec)

        # 2. Recommendations from Contradictions
        for contra in contradictions:
            if contra.contradiction_type == ContradictionType.DEVICE_CONFLICT:
                rec = Recommendation(
                    case_id=case_id,
                    contradiction_id=contra.id,
                    recommendation_type=RecommendationType.NETWORK_PCAP,
                    title="Correlate Network DHCP Leases & RADIUS Logs",
                    description=(
                        "Cross-source telemetry shows concurrent actions across separate devices. "
                        "Recommended action: Query DHCP server leases and network switch MAC tables to authenticate device identity at the recorded timestamps."
                    ),
                    priority=RecommendationPriority.HIGH,
                    status=RecommendationStatus.PENDING,
                    confidence=0.9
                )
                recs_to_create.append(rec)

            elif contra.contradiction_type == ContradictionType.TIMESTAMP_CONFLICT:
                rec = Recommendation(
                    case_id=case_id,
                    contradiction_id=contra.id,
                    recommendation_type=RecommendationType.DEEPER_INSPECTION,
                    title="Perform NTP / Clock Drift Analysis on Evidence Sources",
                    description=(
                        "Conflicting timestamps were observed across distinct evidence files for identical records. "
                        "Recommended action: Review local timezone offsets and CMOS clock synchronization logs on the respective host systems."
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    status=RecommendationStatus.PENDING,
                    confidence=0.85
                )
                recs_to_create.append(rec)

        if recs_to_create:
            db.add_all(recs_to_create)
            db.commit()
            for r in recs_to_create:
                db.refresh(r)

            ActivityService.log_activity(
                db=db,
                action="RECOMMENDATION_GENERATED",
                case_id=case_id,
                user_id=user.id if user else None,
                details={"recommendations_count": len(recs_to_create)}
            )

        logger.info(f"Generated {len(recs_to_create)} recommendations for Case {case_id}")
        return recs_to_create

    @staticmethod
    def get_case_recommendations(db: Session, case_id: int) -> RecommendationListResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        recs = db.query(Recommendation).filter(Recommendation.case_id == case_id).all()
        high_prio = sum(1 for r in recs if r.priority == RecommendationPriority.HIGH)

        return RecommendationListResponse(
            case_id=case_id,
            total_recommendations=len(recs),
            high_priority_count=high_prio,
            recommendations=[RecommendationResponse.model_validate(r) for r in recs]
        )

    @staticmethod
    def update_recommendation(
        db: Session,
        recommendation_id: int,
        update_in: RecommendationUpdate,
        user: Optional[User] = None
    ) -> RecommendationResponse:
        rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found"
            )
        if update_in.status is not None:
            rec.status = update_in.status
        if update_in.priority is not None:
            rec.priority = update_in.priority

        db.commit()
        db.refresh(rec)
        return RecommendationResponse.model_validate(rec)
