import csv
import io
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Course, StudySession, User
from backend.schemas import StudySessionCreate, StudySessionOut
router = APIRouter(prefix="/api/sessions", tags=["study_sessions"])


@router.get("", response_model=list[StudySessionOut])
def list_sessions(
    course_id: int | None = None,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(StudySession)
        .join(Course)
        .filter(Course.user_id == current_user.id)
        .order_by(StudySession.date.desc())
    )
    if course_id is not None:
        q = q.filter(StudySession.course_id == course_id)
    if from_date is not None:
        q = q.filter(StudySession.date >= from_date)
    if to_date is not None:
        q = q.filter(StudySession.date <= to_date)
    return q.all()


@router.post("", response_model=StudySessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    body: StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == body.course_id, Course.user_id == current_user.id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    session = StudySession(**body.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/stats/weekly", response_model=dict)
def weekly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    rows = (
        db.query(StudySession.date, func.sum(StudySession.minutes))
        .join(Course)
        .filter(Course.user_id == current_user.id, StudySession.date >= week_start)
        .group_by(StudySession.date)
        .all()
    )
    by_day = {str(d): int(m or 0) for d, m in rows}
    return {"week_start": str(week_start), "minutes_by_day": by_day, "total_minutes": sum(by_day.values())}


@router.get("/export.csv")
def export_sessions_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(StudySession, Course)
        .join(Course)
        .filter(Course.user_id == current_user.id)
        .order_by(StudySession.date.desc())
        .all()
    )
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["date", "course", "minutes", "hours", "notes"])
    for session, course in rows:
        writer.writerow([
            session.date.isoformat(),
            course.name,
            session.minutes,
            round(session.minutes / 60, 2),
            session.notes or "",
        ])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=studyhub_sessions.csv"},
    )
