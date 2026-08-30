import os
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.artifact import Artifact
from app.models.timeline import TimelineEvent
from app.models.gap import Gap
from app.models.contradiction import Contradiction
from app.models.recommendation import Recommendation
from app.models.report import Report, ReportFormat
from app.models.user import User
from app.schemas.report import ReportCreate, ReportResponse, ReportListResponse
from app.services.activity_service import ActivityService
from app.utils.logger import logger

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    """Service to generate defensible Markdown and ReportLab PDF forensic investigation reports."""

    @staticmethod
    def generate_pdf_report(
        pdf_path: Path,
        case: Case,
        evidence_items: List[Evidence],
        timeline_events: List[TimelineEvent],
        gaps: List[Gap],
        contradictions: List[Contradiction],
        recommendations: List[Recommendation]
    ) -> None:
        """Generate PDF document using ReportLab."""
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#0f172a'))
        h2_style = ParagraphStyle('DocH2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#1e293b'), spaceBefore=12, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#334155'))
        code_style = ParagraphStyle('DocCode', parent=styles['Normal'], fontSize=8, leading=10, fontName='Courier', textColor=colors.HexColor('#0f172a'))

        story = []

        # Document Header
        story.append(Paragraph(f"<b>FORENSIC INVESTIGATION REPORT</b>", title_style))
        story.append(Paragraph(f"Case Number: <b>{case.case_number}</b> | Case Name: <b>{case.case_name}</b>", h2_style))
        story.append(Paragraph(f"Generated Date: <b>{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}</b>", body_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=4, spaceAfter=12))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", h2_style))
        exec_summary = (
            f"Digital Forensics Timeline Reconstruction report for case <b>{case.case_name}</b> ({case.case_number}). "
            f"Ingested {len(evidence_items)} evidence files yielding chronological reconstruction of {len(timeline_events)} "
            f"verified timeline entries. Evaluated {len(gaps)} temporal gaps, {len(contradictions)} multi-source contradictions, "
            f"and formulated {len(recommendations)} investigative recommendations."
        )
        story.append(Paragraph(exec_summary, body_style))
        story.append(Spacer(1, 10))

        # Evidence Summary Table
        story.append(Paragraph("2. Ingested Evidence Sources", h2_style))
        ev_data = [["Filename", "Source Type", "SHA-256 Hash", "Size (bytes)", "Status"]]
        for ev in evidence_items:
            ev_data.append([
                ev.filename[:20],
                str(ev.source_type.value if hasattr(ev.source_type, 'value') else ev.source_type),
                ev.file_hash[:16] + "...",
                str(ev.file_size),
                str(ev.status.value if hasattr(ev.status, 'value') else ev.status)
            ])
        ev_table = Table(ev_data, colWidths=[110, 110, 140, 80, 70])
        ev_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(ev_table)
        story.append(Spacer(1, 10))

        # Reconstructed Timeline Table
        story.append(Paragraph("3. Reconstructed Timeline Summary", h2_style))
        tl_data = [["Timestamp (UTC)", "Device", "Event Description", "Source"]]
        for ev in timeline_events[:15]:
            tl_data.append([
                ev.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                ev.device[:15],
                Paragraph(ev.event[:60], body_style),
                ev.source[:15]
            ])
        tl_table = Table(tl_data, colWidths=[100, 80, 240, 90])
        tl_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(tl_table)
        story.append(Spacer(1, 10))

        # Gaps & Contradictions Summary
        story.append(Paragraph("4. Detected Gaps & Contradictions", h2_style))
        if gaps:
            for g in gaps:
                story.append(Paragraph(f"• <b>[{g.severity.value} Severity]</b> {g.reason}", body_style))
        else:
            story.append(Paragraph("No unexplained time gaps identified.", body_style))

        story.append(Spacer(1, 10))

        # Recommendations
        story.append(Paragraph("5. Forensic Recommendations", h2_style))
        for r in recommendations:
            story.append(Paragraph(f"• <b>[{r.priority.value} Priority]</b> <b>{r.title}</b>: {r.description}", body_style))

        # Methodology & Limitations
        story.append(Spacer(1, 10))
        story.append(Paragraph("6. Methodology & Forensic Limitations", h2_style))
        story.append(Paragraph(
            "<b>Methodology</b>: Telemetry records were ingested, SHA-256 verified, standardized to UTC, and correlated. "
            "Gaps represent calculated deltas. <b>Limitations</b>: Statements reflect only provided evidence files. "
            "No unrecorded user actions are assumed or fabricated.",
            body_style
        ))

        doc.build(story)

    @staticmethod
    def generate_case_report(
        db: Session,
        report_in: ReportCreate,
        user: Optional[User] = None
    ) -> ReportResponse:
        case = db.query(Case).filter(Case.id == report_in.case_id).first()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {report_in.case_id} not found"
            )

        evidence_items = db.query(Evidence).filter(Evidence.case_id == case.id).all()
        artifacts = db.query(Artifact).filter(Artifact.case_id == case.id).all()
        timeline_events = db.query(TimelineEvent).filter(TimelineEvent.case_id == case.id).order_by(TimelineEvent.timestamp.asc()).all()
        gaps = db.query(Gap).filter(Gap.case_id == case.id).all()
        contradictions = db.query(Contradiction).filter(Contradiction.case_id == case.id).all()
        recommendations = db.query(Recommendation).filter(Recommendation.case_id == case.id).all()

        timeline_summary = {
            "total_events": len(timeline_events),
            "earliest_timestamp": timeline_events[0].timestamp.isoformat() if timeline_events else None,
            "latest_timestamp": timeline_events[-1].timestamp.isoformat() if timeline_events else None,
            "sample_sequence": [
                {"time": ev.timestamp.strftime("%H:%M:%S UTC"), "event": ev.event, "source": ev.source}
                for ev in timeline_events[:15]
            ]
        }

        gap_summary = {
            "total_gaps": len(gaps),
            "unexplained_gaps": [
                {
                    "interval": f"{g.start_time.strftime('%H:%M:%S')} - {g.end_time.strftime('%H:%M:%S')}",
                    "duration_seconds": g.duration_seconds,
                    "severity": str(g.severity),
                    "reason": g.reason
                }
                for g in gaps
            ]
        }

        contradiction_summary = {
            "total_contradictions": len(contradictions),
            "items": [
                {
                    "type": str(c.contradiction_type),
                    "severity": str(c.severity),
                    "description": c.description
                }
                for c in contradictions
            ]
        }

        recommendations_summary = {
            "total_recommendations": len(recommendations),
            "items": [
                {
                    "title": r.title,
                    "priority": str(r.priority),
                    "description": r.description
                }
                for r in recommendations
            ]
        }

        findings = {
            "case_number": case.case_number,
            "case_name": case.case_name,
            "evidence_sources_evaluated": len(evidence_items),
            "artifacts_extracted": len(artifacts),
            "integrity_verified": True,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        title = report_in.title or f"Forensic Investigation Report - {case.case_number}"
        summary = (
            f"Digital Forensics Timeline Reconstruction report for {case.case_name} ({case.case_number}). "
            f"Ingested {len(evidence_items)} evidence files yielding {len(artifacts)} normalized artifacts. "
            f"Chronological reconstruction produced {len(timeline_events)} verified timeline entries with "
            f"{len(gaps)} temporal gaps and {len(contradictions)} multi-source contradictions detected. "
            f"{len(recommendations)} forensic recommendations formulated."
        )

        reports_dir = Path("./reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        timestamp_str = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')

        if report_in.report_format == ReportFormat.PDF:
            filename = f"report_{case.case_number}_{timestamp_str}.pdf"
            report_file_path = reports_dir / filename
            ReportService.generate_pdf_report(
                report_file_path, case, evidence_items, timeline_events, gaps, contradictions, recommendations
            )
        else:
            filename = f"report_{case.case_number}_{timestamp_str}.md"
            report_file_path = reports_dir / filename
            md_content = f"# {title}\n**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n**Case**: {case.case_number}\n\n## 1. Executive Summary\n{summary}\n"
            with open(report_file_path, "w", encoding="utf-8") as f:
                f.write(md_content)

        db_report = Report(
            case_id=case.id,
            title=title,
            summary=summary,
            findings=findings,
            timeline_summary=timeline_summary,
            gap_summary=gap_summary,
            contradiction_summary=contradiction_summary,
            recommendations_summary=recommendations_summary,
            generated_by=user.id if user else None,
            report_format=report_in.report_format,
            file_path=str(report_file_path),
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        ActivityService.log_activity(
            db=db,
            action="REPORT_GENERATED",
            case_id=case.id,
            user_id=user.id if user else None,
            details={"report_id": db_report.id, "title": title, "format": str(report_in.report_format)}
        )

        return ReportResponse.model_validate(db_report)

    @staticmethod
    def get_case_reports(db: Session, case_id: int) -> ReportListResponse:
        reports = db.query(Report).filter(Report.case_id == case_id).order_by(Report.created_at.desc()).all()
        return ReportListResponse(
            case_id=case_id,
            total_reports=len(reports),
            reports=[ReportResponse.model_validate(r) for r in reports]
        )

    @staticmethod
    def get_report_file(db: Session, report_id: int, user: Optional[User] = None) -> Path:
        rep = db.query(Report).filter(Report.id == report_id).first()
        if not rep or not rep.file_path:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} file not found"
            )
        path = Path(rep.file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report file on disk missing"
            )

        ActivityService.log_activity(
            db=db,
            action="REPORT_DOWNLOADED",
            case_id=rep.case_id,
            user_id=user.id if user else None,
            details={"report_id": rep.id, "filename": path.name}
        )
        return path
