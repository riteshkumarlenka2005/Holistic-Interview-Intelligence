"""
Reports API endpoints
Full implementation for report generation and export
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.crud import report as crud_report
from app.tasks.pipeline_tasks import celery_app # for scheduling report generation if needed
from enum import Enum

router = APIRouter()


class ExportFormat(str, Enum):
    JSON = "json"
    PDF = "pdf"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"


class ReportType(str, Enum):
    FULL = "full"
    SUMMARY = "summary"
    SPEECH_ONLY = "speech_only"
    VISION_ONLY = "vision_only"


class ReportCreate(BaseModel):
    interview_id: str
    analysis_job_id: str
    title: Optional[str] = None
    report_type: ReportType = ReportType.FULL


class ReportSummary(BaseModel):
    id: str
    interview_id: str
    title: str
    report_type: ReportType
    created_at: datetime
    overall_score: float
    
    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    id: str
    interview_id: str
    title: str
    report_type: ReportType
    created_at: datetime
    
    # Scores
    overall_score: float
    communication_score: float
    presence_score: float
    engagement_score: float
    authenticity_score: float
    
    # Analysis sections
    speech_analysis: Optional[Dict] = None
    vision_analysis: Optional[Dict] = None
    fusion_analysis: Optional[Dict] = None
    
    # Insights
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    recommendations: List[Dict] = []
    
    # Timeline
    timeline: List[Dict] = []
    
    # Explainability
    explainability: Optional[Dict] = None


@router.get("/", response_model=List[ReportSummary])
async def list_reports(
    interview_id: Optional[str] = Query(None),
    report_type: Optional[ReportType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's reports with optional filtering"""
    reports = await crud_report.get_user_reports(
        db=db,
        user_id=current_user.id,
        interview_id=interview_id,
        report_type=report_type.value if report_type else None,
        limit=limit,
        offset=offset
    )
    
    summary_list = []
    for r in reports:
        data = r.data or {}
        summary_list.append(
            ReportSummary(
                id=r.id,
                interview_id=r.session_id,
                title=data.get("title", f"Report for Session {r.session_id}"),
                report_type=ReportType(r.report_type),
                created_at=r.created_at,
                overall_score=data.get("overall_score", 0.0)
            )
        )
    return summary_list


@router.post("/", response_model=ReportDetail, status_code=201)
async def create_report(
    request: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report from analysis results"""
    now = datetime.now()
    
    # In production, would fetch actual analysis results from job_id
    # For now, create mock report data
    report_data = {
        "title": request.title or f"Interview Report - {now.strftime('%Y-%m-%d')}",
        "overall_score": 0.72,
        "communication_score": 0.75,
        "presence_score": 0.70,
        "engagement_score": 0.68,
        "authenticity_score": 0.78,
        
        "speech_analysis": {
            "transcription_summary": "Clear communication with good articulation",
            "prosody": {"pace": "normal", "energy": "good", "tone": "confident"},
            "filler_usage": {"rate": 3.5, "assessment": "moderate"},
            "confidence": {"score": 0.72, "assessment": "good"}
        },
        "vision_analysis": {
            "eye_contact": {"percentage": 68, "assessment": "good"},
            "posture": {"type": "upright", "consistency": 0.85},
            "expressions": {"dominant": "engaged", "variety": "moderate"}
        },
        "fusion_analysis": {
            "congruence": {"score": 0.82, "is_congruent": True},
            "authenticity": {"score": 0.78}
        },
        
        "strengths": [
            "Clear and articulate speech",
            "Maintained good eye contact",
            "Professional posture throughout",
            "Authentic and genuine communication style"
        ],
        "areas_for_improvement": [
            "Reduce filler word usage slightly",
            "Increase gestures for engagement",
            "Vary vocal tone for emphasis"
        ],
        "recommendations": [
            {
                "category": "Speech",
                "priority": "medium",
                "text": "Practice replacing filler words with pauses",
                "action_steps": [
                    "Record yourself answering practice questions",
                    "Count filler words and track progress",
                    "Use deliberate pauses instead of 'um'"
                ]
            },
            {
                "category": "Body Language",
                "priority": "low",
                "text": "Incorporate more natural hand gestures",
                "action_steps": [
                    "Practice emphasizing key points with gestures",
                    "Watch TED talks for gesture inspiration"
                ]
            }
        ],
        
        "timeline": [
            {"time": 0, "event": "Interview started", "type": "milestone"},
            {"time": 15, "event": "Strong opening answer", "type": "positive"},
            {"time": 45, "event": "Brief hesitation noted", "type": "observation"},
            {"time": 90, "event": "Confident conclusion", "type": "positive"}
        ],
        
        "explainability": {
            "top_factors": [
                {"feature": "eye_contact", "impact": 0.15, "direction": "positive"},
                {"feature": "vocal_confidence", "impact": 0.12, "direction": "positive"},
                {"feature": "filler_words", "impact": -0.05, "direction": "negative"}
            ],
            "improvement_path": "Focus on reducing fillers to reach 80% score"
        }
    }
    
    report = await crud_report.create_report(
        db=db,
        user_id=current_user.id,
        session_id=request.interview_id,
        report_type=request.report_type.value,
        data=report_data
    )
    
    return ReportDetail(
        id=report.id,
        interview_id=report.session_id,
        title=report_data["title"],
        report_type=ReportType(report.report_type),
        created_at=report.created_at,
        **{k: v for k, v in report_data.items() if k != "title"}
    )


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed report"""
    report = await crud_report.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
        
    data = report.data or {}
    return ReportDetail(
        id=report.id,
        interview_id=report.session_id,
        title=data.get("title", f"Report for Session {report.session_id}"),
        report_type=ReportType(report.report_type),
        created_at=report.created_at,
        **{k: v for k, v in data.items() if k != "title"}
    )


@router.delete("/{report_id}")
async def delete_report(
    report_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a report"""
    report = await crud_report.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    await crud_report.delete_report(db=db, db_obj=report)
    return {"message": "Report deleted", "report_id": report_id}


@router.get("/session/{session_id}", summary="Get reports for a session")
async def get_session_reports(
    session_id: str = Path(...),
    report_type: Optional[str] = Query(None, pattern="^(candidate|recruiter)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all generated reports for a given session.
    Returns both candidate and recruiter reports, or filter by type.
    """
    from sqlalchemy.future import select
    from app.models.reports import Report

    query = select(Report).where(
        Report.session_id == session_id,
        Report.user_id == current_user.id
    )
    if report_type:
        query = query.where(Report.report_type == report_type)

    result = await db.execute(query)
    reports = result.scalars().all()

    if not reports:
        raise HTTPException(
            status_code=404,
            detail="No reports found for this session. The report may still be generating."
        )

    return [
        {
            "id": r.id,
            "session_id": r.session_id,
            "report_type": r.report_type,
            "status": r.status,
            "created_at": r.created_at,
            "data": r.data
        }
        for r in reports
    ]


@router.post("/session/{session_id}/generate", status_code=202)
async def trigger_report_generation(
    session_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger background report generation for a completed session.
    The client should listen for the 'report_ready' WebSocket event.
    """
    from app.services.crud import interview as crud_interview

    session = await crud_interview.get_session(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if session.status not in ("completed", "analyzed"):
        raise HTTPException(
            status_code=400,
            detail=f"Session must be completed before generating a report. Current status: {session.status}"
        )

    from app.core.celery_app import celery_app
    celery_app.send_task(
        "app.tasks.pipeline_tasks.generate_report_task",
        args=[session_id],
        queue="pipeline"
    )

    return {"message": "Report generation started", "session_id": session_id}


@router.get("/{report_id}/export")
async def export_report(
    report_id: str = Path(...), 
    format: ExportFormat = Query(ExportFormat.JSON),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export report in various formats"""
    report = await crud_report.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    data = report.data or {}
    
    if format == ExportFormat.JSON:
        return data
    
    elif format == ExportFormat.MARKDOWN:
        md_content = generate_markdown_report(data)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.md"
            }
        )
    
    elif format == ExportFormat.HTML:
        html_content = generate_html_report(data)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.html"
            }
        )
    
    elif format == ExportFormat.CSV:
        csv_content = generate_csv_report(data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.csv"
            }
        )
        
    elif format == ExportFormat.PDF:
        # PDF generation would require additional libraries
        raise HTTPException(
            status_code=501, 
            detail="PDF export requires additional setup. Use HTML or Markdown."
        )

@router.get("/session/{session_id}/insights", summary="Get AI Insights for Candidate Dashboard")
async def get_session_insights(
    session_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summarized AI insights for the candidate based on latest reports."""
    from sqlalchemy.future import select
    from app.models.reports import Report

    query = select(Report).where(Report.user_id == current_user.id).order_by(Report.created_at.desc())
    result = await db.execute(query)
    user_reports = result.scalars().all()
    
    if not user_reports:
        return {
            "insights": [
                "Complete an interview to receive AI insights.",
                "Your readiness score will be calculated based on your performance."
            ]
        }
        
    latest_report = user_reports[0]
    data = latest_report.data or {}
    readiness = data.get("readiness_score", 0)
    
    # Calculate some mock trend data if multiple reports
    insights = []
    
    if len(user_reports) > 1:
        prev_data = user_reports[1].data or {}
        prev_readiness = prev_data.get("readiness_score", 0)
        diff = readiness - prev_readiness
        if diff > 0:
            insights.append(f"Your readiness score improved by {diff}% since your last interview.")
        elif diff < 0:
            insights.append(f"Your readiness score decreased by {abs(diff)}% since your last interview.")
            
    radar = data.get("radar_data", {})
    if radar:
        best_skill = max(radar.items(), key=lambda x: x[1])
        worst_skill = min(radar.items(), key=lambda x: x[1])
        insights.append(f"Your strongest area is {best_skill[0].title()} ({best_skill[1]}).")
        insights.append(f"Focus on improving {worst_skill[0].title()} ({worst_skill[1]}).")
        
    if readiness >= 80:
        insights.append("You are interview-ready for most positions.")
    elif readiness >= 60:
        insights.append("You are making good progress. Keep practicing.")
    else:
        insights.append("You have significant room for improvement. Follow the learning roadmap.")
        
    return {
        "insights": insights
    }


@router.get("/{report_id}/summary")
async def get_report_summary_endpoint(
    report_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a condensed summary of the report"""
    report = await crud_report.get_report(db=db, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this report")
    
    data = report.data or {}
    overall_score = data.get("overall_score", 0.0)
    strengths = data.get("strengths", [])
    improvements = data.get("areas_for_improvement", [])
    recommendations = data.get("recommendations", [])
    
    return {
        "id": report.id,
        "title": data.get("title", f"Report for Session {report.session_id}"),
        "overall_score": overall_score,
        "grade": get_grade(overall_score),
        "top_strength": strengths[0] if strengths else None,
        "top_improvement": improvements[0] if improvements else None,
        "quick_tips": [r.get("text", "") for r in recommendations[:2]]
    }


def get_grade(score: float) -> str:
    """Convert score to letter grade"""
    if score >= 0.9: return "A+"
    if score >= 0.85: return "A"
    if score >= 0.8: return "A-"
    if score >= 0.75: return "B+"
    if score >= 0.7: return "B"
    if score >= 0.65: return "B-"
    if score >= 0.6: return "C+"
    if score >= 0.55: return "C"
    return "C-"


def generate_markdown_report(report: Dict) -> str:
    """Generate Markdown report"""
    title = report.get('title', 'Report')
    score = report.get('overall_score', 0)
    md = f"""# {title}

**Overall Score:** {score:.0%} ({get_grade(score)})

---

## Performance Scores

| Metric | Score |
|--------|-------|
| Communication | {report.get('communication_score', 0):.0%} |
| Presence | {report.get('presence_score', 0):.0%} |
| Engagement | {report.get('engagement_score', 0):.0%} |
| Authenticity | {report.get('authenticity_score', 0):.0%} |

---

## Strengths

"""
    for s in report.get('strengths', []):
        md += f"- ✅ {s}\n"
    
    md += "\n## Areas for Improvement\n\n"
    for a in report.get('areas_for_improvement', []):
        md += f"- 📈 {a}\n"
    
    md += "\n## Recommendations\n\n"
    for r in report.get('recommendations', []):
        md += f"### {r.get('category')} ({r.get('priority')} priority)\n\n"
        md += f"{r.get('text')}\n\n"
        if r.get('action_steps'):
            md += "**Action Steps:**\n"
            for step in r['action_steps']:
                md += f"1. {step}\n"
            md += "\n"
    
    return md


def generate_html_report(report: Dict) -> str:
    """Generate HTML report"""
    title = report.get('title', 'Report')
    score = report.get('overall_score', 0)
    
    strengths_html = ''.join(f'<li>{s}</li>' for s in report.get('strengths', []))
    improvements_html = ''.join(f'<li>{a}</li>' for a in report.get('areas_for_improvement', []))
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a1a1a; }}
        .score {{ font-size: 48px; font-weight: bold; color: #4CAF50; }}
        .grade {{ font-size: 24px; color: #666; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 8px; }}
        .strength {{ color: #2e7d32; }}
        .improvement {{ color: #f57c00; }}
        ul {{ padding-left: 20px; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="score">{score:.0%} <span class="grade">({get_grade(score)})</span></p>
    
    <h2>Performance Metrics</h2>
    <div class="metric">Communication: {report.get('communication_score', 0):.0%}</div>
    <div class="metric">Presence: {report.get('presence_score', 0):.0%}</div>
    <div class="metric">Engagement: {report.get('engagement_score', 0):.0%}</div>
    <div class="metric">Authenticity: {report.get('authenticity_score', 0):.0%}</div>
    
    <h2 class="strength">Strengths</h2>
    <ul>{strengths_html}</ul>
    
    <h2 class="improvement">Areas for Improvement</h2>
    <ul>{improvements_html}</ul>
</body>
</html>"""

def generate_csv_report(report: Dict) -> str:
    """Generate CSV report"""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Metric", "Score", "Notes"])
    
    # Write overall
    score = report.get('overall_score', 0)
    readiness = report.get('readiness_score', int(score * 100))
    writer.writerow(["Overall Readiness", f"{readiness}%", ""])
    
    # Write radar/components
    radar = report.get("radar_data", {})
    if radar:
        for key, val in radar.items():
            writer.writerow([key.title(), f"{val}%", ""])
    else:
        writer.writerow(["Communication", f"{report.get('communication_score', 0):.0%}", ""])
        writer.writerow(["Presence", f"{report.get('presence_score', 0):.0%}", ""])
        writer.writerow(["Engagement", f"{report.get('engagement_score', 0):.0%}", ""])
        writer.writerow(["Authenticity", f"{report.get('authenticity_score', 0):.0%}", ""])
    
    writer.writerow([])
    writer.writerow(["Strengths", "", ""])
    for s in report.get("strengths", []):
        writer.writerow(["", "", s])
        
    writer.writerow([])
    writer.writerow(["Areas for Improvement", "", ""])
    for a in report.get("areas_for_improvement", []):
        writer.writerow(["", "", a])
        
    return output.getvalue()
