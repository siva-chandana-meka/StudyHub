import calendar as cal_mod
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Assignment, Course, User
from backend.schemas import CalendarAssignmentOut, CalendarOut

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("", response_model=CalendarOut)
def get_calendar(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = date(year, month, 1)
    last_day = cal_mod.monthrange(year, month)[1]
    end = date(year, month, last_day)

    rows = (
        db.query(Assignment, Course)
        .join(Course)
        .filter(
            Course.user_id == current_user.id,
            Assignment.due_date >= start,
            Assignment.due_date <= end,
        )
        .order_by(Assignment.due_date)
        .all()
    )

    days: dict[str, list[CalendarAssignmentOut]] = {}
    for assignment, course in rows:
        if assignment.due_date is None:
            continue
        key = assignment.due_date.isoformat()
        days.setdefault(key, []).append(
            CalendarAssignmentOut(
                id=assignment.id,
                course_id=assignment.course_id,
                title=assignment.title,
                due_date=assignment.due_date,
                priority=assignment.priority,
                status=assignment.status,
                category=assignment.category,
                course_name=course.name,
                course_color=course.color,
            )
        )

    return CalendarOut(year=year, month=month, days=days)
