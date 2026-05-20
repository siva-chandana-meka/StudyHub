from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Course, StudyGoal, StudySession, User
from backend.schemas import StudyGoalCreate, StudyGoalOut, StudyGoalUpdate

router = APIRouter(prefix="/api/goals", tags=["goals"])


def _goal_out(db: Session, goal: StudyGoal) -> StudyGoalOut:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    minutes = (
        db.query(func.coalesce(func.sum(StudySession.minutes), 0))
        .filter(
            StudySession.course_id == goal.course_id,
            StudySession.date >= week_start,
        )
        .scalar()
    )
    mins = int(minutes or 0)
    pct = min(100.0, round(100 * mins / goal.weekly_minutes, 1)) if goal.weekly_minutes else 0
    return StudyGoalOut(
        id=goal.id,
        course_id=goal.course_id,
        weekly_minutes=goal.weekly_minutes,
        course_name=goal.course.name,
        course_color=goal.course.color,
        minutes_this_week=mins,
        progress_percent=pct,
    )


@router.get("", response_model=list[StudyGoalOut])
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goals = db.query(StudyGoal).filter(StudyGoal.user_id == current_user.id).all()
    return [_goal_out(db, g) for g in goals]


@router.post("", response_model=StudyGoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(
    body: StudyGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == body.course_id, Course.user_id == current_user.id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = (
        db.query(StudyGoal)
        .filter(StudyGoal.user_id == current_user.id, StudyGoal.course_id == body.course_id)
        .first()
    )
    if existing:
        existing.weekly_minutes = body.weekly_minutes
        db.commit()
        db.refresh(existing)
        return _goal_out(db, existing)
    goal = StudyGoal(user_id=current_user.id, course_id=body.course_id, weekly_minutes=body.weekly_minutes)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    goal = (
        db.query(StudyGoal)
        .options(joinedload(StudyGoal.course))
        .filter(StudyGoal.id == goal.id)
        .one()
    )
    return _goal_out(db, goal)


@router.patch("/{goal_id}", response_model=StudyGoalOut)
def update_goal(
    goal_id: int,
    body: StudyGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(StudyGoal).filter(StudyGoal.id == goal_id, StudyGoal.user_id == current_user.id).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal.weekly_minutes = body.weekly_minutes
    db.commit()
    db.refresh(goal)
    return _goal_out(db, goal)


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = db.query(StudyGoal).filter(StudyGoal.id == goal_id, StudyGoal.user_id == current_user.id).first()
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    db.delete(goal)
    db.commit()
