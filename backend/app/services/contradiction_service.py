from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.artifact import Artifact
from app.models.contradiction import Contradiction
from app.models.user import User
from app.schemas.contradiction import ContradictionResponse, ContradictionListResponse
from app.schemas.artifact import ArtifactResponse
from app.ml.contradiction_detector import ContradictionDetector
from app.services.activity_service import ActivityService
from app.utils.logger import logger

class ContradictionService:
    """Service to evaluate multi-source forensic evidence for inconsistencies and contradictions."""

    @staticmethod
    def detect_contradictions_for_case(db: Session, case_id: int, user: Optional[User] = None) -> List[Contradiction]:
        # 1. Fetch artifacts for case
        artifacts = db.query(Artifact).filter(Artifact.case_id == case_id).all()
        if len(artifacts) < 2:
            return []

        # 2. Clear old contradictions for this case
        db.query(Contradiction).filter(Contradiction.case_id == case_id).delete()
        db.commit()

        # 3. Detect contradictions using detector
        detected_dicts = ContradictionDetector.detect_contradictions(artifacts)
        db_contradictions: List[Contradiction] = []

        for cd in detected_dicts:
            contra = Contradiction(
                case_id=case_id,
                artifact_a_id=cd["artifact_a_id"],
                artifact_b_id=cd["artifact_b_id"],
                contradiction_type=cd["contradiction_type"],
                description=cd["description"],
                severity=cd["severity"],
                confidence=cd.get("confidence", 1.0)
            )
            db_contradictions.append(contra)

        if db_contradictions:
            db.add_all(db_contradictions)
            db.commit()
            for c in db_contradictions:
                db.refresh(c)

            ActivityService.log_activity(
                db=db,
                action="CONTRADICTION_DETECTED",
                case_id=case_id,
                user_id=user.id if user else None,
                details={"contradictions_count": len(db_contradictions)}
            )

        logger.info(f"Detected {len(db_contradictions)} contradictions for Case {case_id}")
        return db_contradictions

    @staticmethod
    def get_case_contradictions(db: Session, case_id: int) -> ContradictionListResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        contras = db.query(Contradiction).filter(Contradiction.case_id == case_id).all()
        responses: List[ContradictionResponse] = []

        for c in contras:
            art_a = db.query(Artifact).filter(Artifact.id == c.artifact_a_id).first()
            art_b = db.query(Artifact).filter(Artifact.id == c.artifact_b_id).first()

            resp = ContradictionResponse.model_validate(c)
            if art_a:
                resp.artifact_a = ArtifactResponse.model_validate(art_a)
            if art_b:
                resp.artifact_b = ArtifactResponse.model_validate(art_b)
            responses.append(resp)

        return ContradictionListResponse(
            case_id=case_id,
            total_contradictions=len(responses),
            contradictions=responses
        )
