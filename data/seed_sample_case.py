"""
Automated seeding and analysis script for CASE-001 with realistic forensic evidence files.
"""
import sys
import os
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi import UploadFile
from app.database.session import init_db, SessionLocal
from app.models.user import User, UserRole
from app.models.case import Case, CaseStatus
from app.services.evidence_service import EvidenceService
from app.services.timeline_service import TimelineService
from app.services.gap_service import GapService
from app.services.contradiction_service import ContradictionService
from app.services.recommendation_service import RecommendationService
from app.auth.security import get_password_hash
from app.utils.logger import logger

def seed_sample_case():
    print("=" * 60)
    print("Starting AI Forensics Case Seeding & Analysis (CASE-001)...")
    print("=" * 60)

    init_db()
    db = SessionLocal()

    try:
        # 1. Ensure investigator user
        investigator = db.query(User).filter(User.username == "investigator").first()
        if not investigator:
            investigator = User(
                username="investigator",
                email="investigator@forensics.local",
                hashed_password=get_password_hash("Investigator123!"),
                full_name="Senior Digital Investigator",
                role=UserRole.INVESTIGATOR,
                is_active=True
            )
            db.add(investigator)
            db.commit()
            db.refresh(investigator)
            print("[OK] Investigator user verified.")

        # 2. Ensure or create CASE-001
        case = db.query(Case).filter(Case.case_number == "CASE-001").first()
        if not case:
            case = Case(
                case_number="CASE-001",
                case_name="Insider Threat & Financial Exfiltration Investigation",
                description="Investigation regarding suspicious credential use, unauthorized data exfiltration, and intentional log deletion.",
                status=CaseStatus.IN_PROGRESS,
                created_by=investigator.id
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            print(f"[OK] Created Case: {case.case_number} - {case.case_name}")
        else:
            print(f"[OK] Found existing Case: {case.case_number} (ID: {case.id})")

        # 3. Ingest Sample Files
        samples_dir = Path(__file__).resolve().parent / "samples"
        sample_files = [
            ("sample_system_logs.csv", "WORKSTATION-01"),
            ("sample_browser_history.json", "WORKSTATION-01"),
            ("sample_usb_logs.csv", "WORKSTATION-01"),
            ("sample_auth_syslog.log", "DC-SRV-01"),
            ("sample_network_connections.csv", "WORKSTATION-01")
        ]

        import asyncio

        async def ingest_files():
            for filename, device in sample_files:
                file_path = samples_dir / filename
                if not file_path.exists():
                    print(f"[WARN] Sample file {filename} not found, skipping.")
                    continue

                with open(file_path, "rb") as f:
                    content = f.read()

                # Mock an UploadFile
                from io import BytesIO
                upload_file = UploadFile(
                    file=BytesIO(content),
                    size=len(content),
                    filename=filename,
                    headers={"content-type": "text/plain"}
                )

                res = await EvidenceService.upload_evidence(
                    db=db,
                    case_id=case.id,
                    file=upload_file,
                    device=device,
                    user=investigator
                )
                print(f"[OK] Ingested '{filename}': {res.artifacts_created} artifacts created (SHA-256: {res.evidence.file_hash[:12]}...)")

        asyncio.run(ingest_files())

        # 4. Rebuild Chronological Timeline & Auto-Analyze
        print("\nReconstructing chronological event timeline and running anomaly analytics...")
        rebuild_res = TimelineService.rebuild_timeline(db, case_id=case.id, user=investigator)
        print(f"[OK] Reconstructed {rebuild_res.events_reconstructed} verified timeline events.")
        print(f"[OK] Detected {rebuild_res.gaps_detected} temporal gaps.")
        print(f"[OK] Identified {rebuild_res.contradictions_detected} multi-source contradictions.")
        print(f"[OK] Formulated {rebuild_res.recommendations_generated} defensible recommendations.")

        print("\n" + "=" * 60)
        print("CASE-001 Seeding & Analysis Completed Successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        print(f"\n[ERROR] Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_case()
