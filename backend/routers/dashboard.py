from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Assignment, AssignmentStatus, Course, StudyGoal, StudySession, User
from backend.routers.goals import _goal_out
from backend.schemas import AssignmentOut, DashboardOut

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    base = db.query(Assignment).join(Course).filter(Course.user_id == current_user.id)

    upcoming = (
        base.filter(
            Assignment.due_date >= today,
            Assignment.status != AssignmentStatus.DONE,
        )
        .order_by(Assignment.due_date.asc())
        .limit(10)
        .all()
    )

    overdue = (
        base.filter(
            Assignment.due_date < today,
            Assignment.status != AssignmentStatus.DONE,
        )
        .order_by(Assignment.due_date.asc())
        .all()
    )

    all_assignments = base.all()
    total = len(all_assignments)
    done = sum(1 for a in all_assignments if a.status == AssignmentStatus.DONE)
    completion_rate = round(100 * done / total, 1) if total else 0.0

    today_minutes = (
        db.query(func.coalesce(func.sum(StudySession.minutes), 0))
        .join(Course)
        .filter(Course.user_id == current_user.id, StudySession.date == today)
        .scalar()
    )

    weekly_minutes = (
        db.query(func.coalesce(func.sum(StudySession.minutes), 0))
        .join(Course)
        .filter(Course.user_id == current_user.id, StudySession.date >= week_start)
        .scalar()
    )

    goals = (
        db.query(StudyGoal)
        .options(joinedload(StudyGoal.course))
        .filter(StudyGoal.user_id == current_user.id)
        .all()
    )

    return DashboardOut(
        upcoming_deadlines=[AssignmentOut.model_validate(a) for a in upcoming],
        overdue_assignments=[AssignmentOut.model_validate(a) for a in overdue],
        today_study_minutes=int(today_minutes or 0),
        weekly_study_minutes=int(weekly_minutes or 0),
        assignments_total=total,
        assignments_done=done,
        completion_rate=completion_rate,
        study_goals=[_goal_out(db, g) for g in goals],
    )
