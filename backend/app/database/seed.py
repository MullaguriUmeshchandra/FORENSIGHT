import os
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.case import Case, CaseStatus
from app.models.evidence import Evidence, EvidenceSourceType, EvidenceStatus
from app.models.user import User
from app.models.report import Report, ReportFormat
from app.schemas.report import ReportCreate
from app.utils.hasher import compute_sha256_bytes
from app.services.normalization_service import NormalizationService
from app.services.timeline_service import TimelineService
from app.services.report_service import ReportService
from app.services.activity_service import ActivityService
from app.utils.logger import logger


from app.models.gap import Gap

SAMPLE_EVIDENCE = [
    {
        "filename": "sample_auth_logs.csv",
        "device": "WORKSTATION-01",
        "source_type": EvidenceSourceType.SYSTEM_LOGS,
        "content": (
            "timestamp,event_type,device,event_description,source_ip,user_account\n"
            "2026-08-30T10:00:00Z,USER_LOGON,WORKSTATION-01,Standard user authentication succeeded,192.168.1.45,jdoe\n"
            "2026-08-30T10:15:00Z,PRIVILEGE_ELEVATION,WORKSTATION-01,User requested elevated administrative session,192.168.1.45,jdoe\n"
            "2026-08-30T10:20:00Z,CREDENTIAL_ACCESS,WORKSTATION-01,Local security authority subsystem read access,192.168.1.45,SYSTEM\n"
        ).encode("utf-8")
    },
    {
        "filename": "sample_system_logs.csv",
        "device": "WORKSTATION-01",
        "source_type": EvidenceSourceType.USB_LOGS,
        "content": (
            "timestamp,event_type,device,event_description,artifact_path,file_hash\n"
            "2026-08-30T10:21:00Z,PROCESS_EXECUTION,WORKSTATION-01,PowerShell launched with encoded parameters,C:\\Windows\\System32\\powershell.exe,e3b0c44298fc1c149afbf4c8996fb924\n"
            "2026-08-30T10:28:00Z,USB_ATTACH,WORKSTATION-01,Removable USB storage attached (Kingston DataTraveler 3.0),USBSTOR\\DiskKingston_00187D,00187D6B9921\n"
            "2026-08-30T10:41:00Z,FILE_ACCESS,WORKSTATION-01,Sensitive document accessed and read (Q3_Ledger_Confidential.xlsx),C:\\Finance\\Q3_Ledger_Confidential.xlsx,8f4b23a789bcde21\n"
            "2026-08-30T10:43:00Z,FILE_MODIFICATION,WORKSTATION-01,Archive container created in temporary directory,C:\\Users\\jdoe\\AppData\\Local\\Temp\\vault_backup.zip,90218734bcfe8923\n"
        ).encode("utf-8")
    },
    {
        "filename": "sample_domain_controller.csv",
        "device": "LAPTOP-02",
        "source_type": EvidenceSourceType.SYSTEM_LOGS,
        "content": (
            "timestamp,event_type,device,event_description,source_ip,user_account\n"
            "2026-08-30T10:28:15Z,USER_LOGON,LAPTOP-02,Concurrent interactive user session initiated,192.168.1.188,jdoe\n"
        ).encode("utf-8")
    },
    {
        "filename": "sample_network_traffic.csv",
        "device": "WORKSTATION-01",
        "source_type": EvidenceSourceType.NETWORK_LOGS,
        "content": (
            "timestamp,event_type,device,event_description,destination_ip,bytes_transferred\n"
            "2026-08-30T10:46:00Z,NETWORK_OUTBOUND,WORKSTATION-01,High-volume HTTPS connection to unknown external IP,198.51.100.77:443,48291040\n"
            "2026-08-30T10:50:00Z,DNS_QUERY,WORKSTATION-01,DNS lookup for suspicious staging domain vault-sync-c2.net,1.1.1.1,512\n"
            "2026-08-30T10:55:00Z,LOG_CLEAR,WORKSTATION-01,Windows Security Event Log 1102 (Audit log cleared),WORKSTATION-01,0\n"
        ).encode("utf-8")
    }
]


def seed_initial_demo_case(db: Session) -> Case:
    """
    Seeds the baseline CASE-001 demonstration forensic case with verified multi-source
    evidence, normalized artifacts, reconstructed timeline with calculated 13-minute gap,
    cross-source contradiction signals, investigative recommendations, and report artifacts.
    """
    existing_case = db.query(Case).filter(Case.case_number == "CASE-001").first()
    if existing_case:
        ev_count = db.query(Evidence).filter(Evidence.case_id == existing_case.id).count()
        gap_count = db.query(Gap).filter(Gap.case_id == existing_case.id).count()
        if ev_count >= 3 and gap_count >= 1:
            logger.info("CASE-001 already has complete evidence and calculated gaps. Skipping seed.")
            return existing_case
        else:
            logger.info("CASE-001 exists but is incomplete. Refreshing demonstration case...")
            db.query(Evidence).filter(Evidence.case_id == existing_case.id).delete()
            db.commit()
            demo_case = existing_case
    else:
        admin_user = db.query(User).filter(User.username == "investigator").first()
        user_id = admin_user.id if admin_user else None

        logger.info("Creating baseline forensic demonstration case (CASE-001)...")
        demo_case = Case(
            case_number="CASE-001",
            case_name="Operation RedDelta — Sensitive Data Exfiltration Investigation",
            description=(
                "Multi-source forensic reconstruction analyzing unauthorized USB connection, "
                "temporal blindspots, sensitive finance file access, and high-volume outbound network exfiltration."
            ),
            status=CaseStatus.OPEN,
            created_by=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(demo_case)
        db.commit()
        db.refresh(demo_case)

    admin_user = db.query(User).filter(User.username == "investigator").first()
    user_id = admin_user.id if admin_user else None

    upload_dir = Path(os.getenv("UPLOAD_DIR", "./uploads")) / demo_case.case_number
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Ingest evidence items
    for item in SAMPLE_EVIDENCE:
        filename = item["filename"]
        raw_content = item["content"]
        file_hash = compute_sha256_bytes(raw_content)
        file_path = upload_dir / filename

        with open(file_path, "wb") as f:
            f.write(raw_content)

        evidence = Evidence(
            case_id=demo_case.id,
            filename=filename,
            original_filename=filename,
            file_path=str(file_path),
            file_size=len(raw_content),
            file_hash=file_hash,
            source_type=item["source_type"],
            device=item["device"],
            status=EvidenceStatus.PROCESSED,
            investigator_id=user_id,
            uploaded_at=datetime.now(timezone.utc),
            collected_at=datetime(2026, 8, 30, 10, 0, 0, tzinfo=timezone.utc),
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)

        # Normalize into artifacts
        artifacts, errors = NormalizationService.normalize_evidence_file(
            db=db,
            evidence=evidence,
            raw_content=raw_content
        )

        ActivityService.log_activity(
            db=db,
            action="EVIDENCE_UPLOADED",
            case_id=demo_case.id,
            user_id=user_id,
            details={"filename": filename, "sha256": file_hash[:16] + "...", "artifacts": len(artifacts)}
        )

    # Rebuild timeline & trigger gap detection, contradictions, and recommendations
    logger.info(f"Rebuilding timeline and computing gaps for case {demo_case.case_number}...")
    TimelineService.rebuild_timeline(
        db=db,
        case_id=demo_case.id,
        user=admin_user,
        auto_detect_gaps=True,
        auto_detect_contradictions=True,
        auto_generate_recommendations=True
    )

    # Generate initial sample report
    try:
        ReportService.generate_case_report(
            db=db,
            report_in=ReportCreate(
                case_id=demo_case.id,
                title=f"Initial Incident Findings — {demo_case.case_number}",
                report_format=ReportFormat.MARKDOWN
            ),
            user=admin_user
        )
    except Exception as e:
        logger.warning(f"Could not generate initial report for demo case: {e}")

    logger.info(f"CASE-001 seeded successfully with {len(SAMPLE_EVIDENCE)} evidence sources!")
    return demo_case
