import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.models.evidence import Evidence, EvidenceSourceType, EvidenceStatus
from app.models.case import Case
from app.models.user import User
from app.models.artifact import Artifact
from app.schemas.evidence import EvidenceResponse, EvidenceListResponse, EvidenceUploadResponse
from app.utils.hasher import compute_sha256_bytes
from app.services.normalization_service import NormalizationService
from app.services.activity_service import ActivityService
from app.graph.graph_service import GraphService
from app.utils.logger import logger

ALLOWED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson", ".txt", ".log", ".xml"}

class EvidenceService:
    """Service for evidence intake, SHA-256 verification, safe storage, and normalization."""

    @staticmethod
    def get_upload_directory() -> Path:
        upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads"))
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    @staticmethod
    def detect_source_type_from_filename(filename: str) -> EvidenceSourceType:
        fn = filename.lower()
        if "browser" in fn or "chrome" in fn or "firefox" in fn or "edge" in fn or "history" in fn:
            return EvidenceSourceType.BROWSER_ARTIFACTS
        elif "usb" in fn or "device" in fn or "removable" in fn:
            return EvidenceSourceType.USB_LOGS
        elif "network" in fn or "pcap" in fn or "socket" in fn or "conn" in fn or "traffic" in fn:
            return EvidenceSourceType.NETWORK_LOGS
        elif "file" in fn or "mft" in fn or "usnjrnl" in fn or "metadata" in fn:
            return EvidenceSourceType.FILE_METADATA
        elif "cloud" in fn or "aws" in fn or "azure" in fn or "gcp" in fn:
            return EvidenceSourceType.CLOUD_ACTIVITY
        elif "system" in fn or "syslog" in fn or "auth" in fn or "event" in fn or "security" in fn or "windows" in fn:
            return EvidenceSourceType.SYSTEM_LOGS
        return EvidenceSourceType.OTHER

    @staticmethod
    async def upload_evidence(
        db: Session,
        case_id: int,
        file: UploadFile,
        source_type: Optional[EvidenceSourceType] = None,
        device: str = "Unknown Device",
        user: Optional[User] = None
    ) -> EvidenceUploadResponse:
        # Verify Case exists
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )

        filename = file.filename or "unknown_evidence.log"
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext}'. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file contents securely in memory
        content = await file.read()
        file_size = len(content)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        # Compute SHA-256 hash (Forensic Chain of Custody)
        file_hash = compute_sha256_bytes(content)

        # Determine source type
        resolved_source_type = source_type or EvidenceService.detect_source_type_from_filename(filename)

        # Save immutable file to disk
        upload_dir = EvidenceService.get_upload_directory()
        safe_filename = f"{case_id}_{file_hash[:12]}_{Path(filename).name}"
        save_path = upload_dir / safe_filename
        with open(save_path, "wb") as f:
            f.write(content)

        # Create Evidence record in DB
        db_evidence = Evidence(
            case_id=case_id,
            source_type=resolved_source_type,
            filename=filename,
            original_filename=filename,
            file_path=str(save_path),
            file_hash=file_hash,
            file_size=file_size,
            uploaded_at=datetime.now(timezone.utc),
            collected_at=datetime.now(timezone.utc),
            device=device,
            investigator_id=user.id if user else None,
            status=EvidenceStatus.PROCESSING
        )
        db.add(db_evidence)
        db.commit()
        db.refresh(db_evidence)

        # Normalize artifacts from evidence
        try:
            artifacts, errors = NormalizationService.normalize_evidence_file(db, db_evidence, content)
            db_evidence.status = EvidenceStatus.PROCESSED
            db.commit()
            db.refresh(db_evidence)

            # Sync to Neo4j graph
            GraphService.sync_evidence_to_graph(db_evidence, artifacts)

        except Exception as e:
            db_evidence.status = EvidenceStatus.FAILED
            db_evidence.error_message = str(e)
            db.commit()
            db.refresh(db_evidence)
            logger.error(f"Evidence processing failed for {filename}: {e}")
            artifacts = []

        ActivityService.log_activity(
            db=db,
            action="EVIDENCE_UPLOADED",
            case_id=case_id,
            user_id=user.id if user else None,
            details={
                "evidence_id": db_evidence.id,
                "filename": filename,
                "file_hash": file_hash,
                "source_type": str(db_evidence.source_type),
                "artifacts_created": len(artifacts)
            }
        )

        resp = EvidenceResponse.model_validate(db_evidence)
        resp.artifacts_count = len(artifacts)

        return EvidenceUploadResponse(
            evidence=resp,
            artifacts_created=len(artifacts),
            message=f"Evidence '{filename}' successfully ingested and normalized ({len(artifacts)} artifacts generated)."
        )

    @staticmethod
    def get_case_evidence(db: Session, case_id: int) -> EvidenceListResponse:
        items = db.query(Evidence).filter(Evidence.case_id == case_id).all()
        result = []
        for item in items:
            art_count = db.query(Artifact).filter(Artifact.evidence_id == item.id).count()
            resp = EvidenceResponse.model_validate(item)
            resp.artifacts_count = art_count
            result.append(resp)
        return EvidenceListResponse(total=len(result), evidence=result)

    @staticmethod
    def get_evidence_by_id(db: Session, evidence_id: int) -> EvidenceResponse:
        item = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )
        art_count = db.query(Artifact).filter(Artifact.evidence_id == item.id).count()
        resp = EvidenceResponse.model_validate(item)
        resp.artifacts_count = art_count
        return resp

    @staticmethod
    def delete_evidence(db: Session, evidence_id: int, user: Optional[User] = None) -> bool:
        item = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence {evidence_id} not found"
            )
        case_id = item.case_id
        fn = item.filename
        db.delete(item)
        db.commit()

        ActivityService.log_activity(
            db=db,
            action="EVIDENCE_DELETED",
            case_id=case_id,
            user_id=user.id if user else None,
            details={"evidence_id": evidence_id, "filename": fn}
        )
        return True
