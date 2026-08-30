from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.dashboard import DashboardSummaryResponse, DashboardActivityResponse, ActivityLogResponse
from app.models.evidence import Evidence, EvidenceSourceType
from app.models.artifact import Artifact
from app.models.gap import Gap, GapType
from app.models.contradiction import Contradiction
from app.models.recommendation import Recommendation, RecommendationPriority
from app.models.report import Report
from app.models.activity_log import ActivityLog
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Metrics"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    case_id: Optional[int] = Query(None, description="Optional Case ID to filter summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return real database-computed summary metrics matching the dashboard stat cards and breakdown widgets:
    - Evidence Sources (total & today)
    - Artifacts Processed
    - Gaps Detected (and unexplained count)
    - Recommendations (and high priority count)
    - Reports Generated
    - Contradictions Count
    - Gap Detection Summary breakdown
    - Evidence Sources breakdown
    """
    ev_query = db.query(Evidence)
    art_query = db.query(Artifact)
    gap_query = db.query(Gap)
    contra_query = db.query(Contradiction)
    rec_query = db.query(Recommendation)
    rep_query = db.query(Report)

    if case_id:
        ev_query = ev_query.filter(Evidence.case_id == case_id)
        art_query = art_query.filter(Artifact.case_id == case_id)
        gap_query = gap_query.filter(Gap.case_id == case_id)
        contra_query = contra_query.filter(Contradiction.case_id == case_id)
        rec_query = rec_query.filter(Recommendation.case_id == case_id)
        rep_query = rep_query.filter(Report.case_id == case_id)

    total_evidence = ev_query.count()
    total_artifacts = art_query.count()
    total_gaps = gap_query.count()
    total_contradictions = contra_query.count()
    total_recommendations = rec_query.count()
    total_reports = rep_query.count()

    # Evidence uploaded today
    today_utc = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    evidence_today = ev_query.filter(Evidence.uploaded_at >= today_utc).count()

    # Gap breakdown
    all_gaps = gap_query.all()
    unexplained_count = sum(1 for g in all_gaps if g.gap_type == GapType.UNEXPLAINED_TIME_GAP)
    missing_exp_count = sum(1 for g in all_gaps if g.gap_type == GapType.MISSING_EXPECTED_EVENT)
    inconsistencies_count = sum(1 for g in all_gaps if g.gap_type == GapType.TIMESTAMP_INCONSISTENCY)

    gap_summary = {
        "Unexplained Time Gaps": unexplained_count,
        "Missing Expected Events": missing_exp_count,
        "Timestamp Inconsistencies": inconsistencies_count
    }

    # Recommendation breakdown
    all_recs = rec_query.all()
    high_priority_recs = sum(1 for r in all_recs if r.priority == RecommendationPriority.HIGH)

    # Source breakdown
    all_ev = ev_query.all()
    source_breakdown = {
        "System Logs": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.SYSTEM_LOGS),
        "Browser Artifacts": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.BROWSER_ARTIFACTS),
        "File Metadata": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.FILE_METADATA),
        "USB / Device Logs": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.USB_LOGS),
        "Network Logs": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.NETWORK_LOGS),
        "Cloud Activity": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.CLOUD_ACTIVITY),
        "Other": sum(1 for e in all_ev if e.source_type == EvidenceSourceType.OTHER),
    }

    return DashboardSummaryResponse(
        case_id=case_id,
        evidence_sources=total_evidence,
        evidence_sources_today=evidence_today,
        artifacts_processed=total_artifacts,
        gaps_detected=total_gaps,
        unexplained_gaps_count=unexplained_count,
        recommendations_count=total_recommendations,
        high_priority_recommendations_count=high_priority_recs,
        reports_generated=total_reports,
        contradictions_count=total_contradictions,
        gap_summary=gap_summary,
        source_breakdown=source_breakdown
    )

@router.get("/activity", response_model=DashboardActivityResponse)
def get_dashboard_activity(
    case_id: Optional[int] = Query(None, description="Case ID"),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve actual forensic audit and activity stream logs."""
    query = db.query(ActivityLog)
    if case_id:
        query = query.filter(ActivityLog.case_id == case_id)
    
    logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()

    action_label_map = {
        "EVIDENCE_UPLOADED": "System logs imported",
        "EVIDENCE_PROCESSED": "Evidence processed",
        "TIMELINE_REBUILT": "Timeline updated",
        "GAP_DETECTED": "Gap detected in event sequence",
        "CONTRADICTION_DETECTED": "Contradiction identified",
        "RECOMMENDATION_GENERATED": "Recommendation generated",
        "REPORT_GENERATED": "Report generated",
        "REPORT_DOWNLOADED": "Report downloaded",
        "CASE_CREATED": "Case created",
        "USER_LOGIN": "User logged in",
    }

    resp_logs = []
    for l in logs:
        r = ActivityLogResponse.model_validate(l)
        r.formatted_time = l.created_at.strftime("%I:%M %p")
        r.action_label = action_label_map.get(l.action, l.action.replace("_", " ").title())
        resp_logs.append(r)

    return DashboardActivityResponse(
        total=len(resp_logs),
        activities=resp_logs
    )
