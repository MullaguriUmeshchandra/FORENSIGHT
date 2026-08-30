from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case, CaseStatus
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.models.gap import Gap
from app.models.contradiction import Contradiction
from app.models.user import User
from app.schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseListResponse
from app.services.activity_service import ActivityService

class CaseService:
    """Case management service."""

    @staticmethod
    def create_case(db: Session, case_in: CaseCreate, user: Optional[User] = None) -> CaseResponse:
        # Check uniqueness of case_number
        existing = db.query(Case).filter(Case.case_number == case_in.case_number).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Case with number '{case_in.case_number}' already exists"
            )

        db_case = Case(
            case_number=case_in.case_number,
            case_name=case_in.case_name,
            description=case_in.description,
            status=case_in.status,
            created_by=user.id if user else None
        )
        db.add(db_case)
        db.commit()
        db.refresh(db_case)

        ActivityService.log_activity(
            db=db,
            action="CASE_CREATED",
            case_id=db_case.id,
            user_id=user.id if user else None,
            details={"case_number": db_case.case_number, "case_name": db_case.case_name}
        )

        return CaseService._to_case_response(db, db_case)

    @staticmethod
    def get_cases(db: Session, skip: int = 0, limit: int = 100) -> CaseListResponse:
        total = db.query(Case).count()
        cases = db.query(Case).offset(skip).limit(limit).all()
        return CaseListResponse(
            total=total,
            cases=[CaseService._to_case_response(db, c) for c in cases]
        )

    @staticmethod
    def get_case(db: Session, case_id: int) -> CaseResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        return CaseService._to_case_response(db, case)

    @staticmethod
    def update_case(db: Session, case_id: int, case_update: CaseUpdate, user: Optional[User] = None) -> CaseResponse:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        if case_update.case_name is not None:
            case.case_name = case_update.case_name
        if case_update.description is not None:
            case.description = case_update.description
        if case_update.status is not None:
            case.status = case_update.status

        db.commit()
        db.refresh(case)

        ActivityService.log_activity(
            db=db,
            action="CASE_UPDATED",
            case_id=case.id,
            user_id=user.id if user else None,
            details={"case_number": case.case_number, "status": str(case.status)}
        )

        return CaseService._to_case_response(db, case)

    @staticmethod
    def delete_case(db: Session, case_id: int, user: Optional[User] = None) -> bool:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        case_num = case.case_number
        db.delete(case)
        db.commit()

        ActivityService.log_activity(
            db=db,
            action="CASE_DELETED",
            case_id=case_id,
            user_id=user.id if user else None,
            details={"case_number": case_num}
        )
        return True

    @staticmethod
    def _to_case_response(db: Session, case: Case) -> CaseResponse:
        ev_count = db.query(Evidence).filter(Evidence.case_id == case.id).count()
        art_count = db.query(Artifact).filter(Artifact.case_id == case.id).count()
        gap_count = db.query(Gap).filter(Gap.case_id == case.id).count()
        contra_count = db.query(Contradiction).filter(Contradiction.case_id == case.id).count()

        resp = CaseResponse.model_validate(case)
        resp.evidence_count = ev_count
        resp.artifacts_count = art_count
        resp.gaps_count = gap_count
        resp.contradictions_count = contra_count
        return resp
