from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.models.timeline import TimelineEvent
from app.models.gap import Gap
from app.models.contradiction import Contradiction
from app.models.recommendation import Recommendation
from app.models.report import Report
from app.schemas.investigation import InvestigationOverviewResponse, InvestigationStep

class InvestigationService:
    """Service to track end-to-end investigation phase progress."""

    @staticmethod
    def get_investigation_overview(db: Session, case_id: int) -> InvestigationOverviewResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        evidence_count = db.query(Evidence).filter(Evidence.case_id == case_id).count()
        artifacts_count = db.query(Artifact).filter(Artifact.case_id == case_id).count()
        timeline_count = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).count()
        gaps_count = db.query(Gap).filter(Gap.case_id == case_id).count()
        contradictions_count = db.query(Contradiction).filter(Contradiction.case_id == case_id).count()
        recommendations_count = db.query(Recommendation).filter(Recommendation.case_id == case_id).count()
        reports_count = db.query(Report).filter(Report.case_id == case_id).count()

        step1_status = "completed" if evidence_count > 0 else "pending"
        step2_status = "completed" if artifacts_count > 0 else ("in_progress" if evidence_count > 0 else "pending")
        step3_status = "completed" if timeline_count > 0 else ("in_progress" if artifacts_count > 0 else "pending")
        step4_status = "completed" if (gaps_count > 0 or contradictions_count > 0 or (timeline_count > 0 and gaps_count == 0)) else "pending"
        step5_status = "completed" if reports_count > 0 else ("in_progress" if recommendations_count > 0 else "pending")

        steps = [
            InvestigationStep(
                step_number=1,
                title="Collect Evidence",
                description="Import system logs, files, and device data.",
                status=step1_status,
                count=evidence_count
            ),
            InvestigationStep(
                step_number=2,
                title="Normalize Artifacts",
                description="Convert formats and standardize timestamps.",
                status=step2_status,
                count=artifacts_count
            ),
            InvestigationStep(
                step_number=3,
                title="Build Timeline",
                description="Arrange events chronologically.",
                status=step3_status,
                count=timeline_count
            ),
            InvestigationStep(
                step_number=4,
                title="Detect Gaps & Contradictions",
                description="Find missing or conflicting events.",
                status=step4_status,
                count=gaps_count + contradictions_count
            ),
            InvestigationStep(
                step_number=5,
                title="Recommend & Report",
                description="Suggest evidence and generate reports.",
                status=step5_status,
                count=recommendations_count + reports_count
            )
        ]

        return InvestigationOverviewResponse(
            case_id=case_id,
            steps=steps
        )
