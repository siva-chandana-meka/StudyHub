from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Assignment, AssignmentStatus, Course, User
from backend.schemas import AssignmentCreate, AssignmentOut, AssignmentUpdate

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


@router.get("", response_model=list[AssignmentOut])
def list_assignments(
    course_id: int | None = None,
    status_filter: AssignmentStatus | None = Query(default=None, alias="status"),
    due_before: date | None = None,
    due_after: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        db.query(Assignment)
        .join(Course)
        .filter(Course.user_id == current_user.id)
        .order_by(Assignment.due_date.asc().nullslast())
    )
    if course_id is not None:
        q = q.filter(Assignment.course_id == course_id)
    if status_filter is not None:
        q = q.filter(Assignment.status == status_filter)
    if due_before is not None:
        q = q.filter(Assignment.due_date <= due_before)
    if due_after is not None:
        q = q.filter(Assignment.due_date >= due_after)
    return q.all()


@router.post("", response_model=AssignmentOut, status_code=status.HTTP_201_CREATED)
def create_assignment(
    body: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_user_course(db, body.course_id, current_user.id)
    assignment = Assignment(**body.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentOut)
def update_assignment(
    assignment_id: int,
    body: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = _get_user_assignment(db, assignment_id, current_user.id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(assignment, key, value)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = _get_user_assignment(db, assignment_id, current_user.id)
    db.delete(assignment)
    db.commit()


def _require_user_course(db: Session, course_id: int, user_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def _get_user_assignment(db: Session, assignment_id: int, user_id: int) -> Assignment:
    assignment = (
        db.query(Assignment)
        .join(Course)
        .filter(Assignment.id == assignment_id, Course.user_id == user_id)
        .first()
    )
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")
    return assignment
