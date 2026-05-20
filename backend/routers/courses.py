from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Assignment, Course, StudySession, User
from backend.schemas import CourseCreate, CourseDetailOut, CourseOut, CourseUpdate

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Course).filter(Course.user_id == current_user.id).order_by(Course.name).all()


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    body: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = Course(user_id=current_user.id, **body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_user_course(db, course_id, current_user.id)
    return course


@router.get("/{course_id}/detail", response_model=CourseDetailOut)
def get_course_detail(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_user_course(db, course_id, current_user.id)
    assignments = (
        db.query(Assignment)
        .filter(Assignment.course_id == course_id)
        .order_by(Assignment.due_date.asc().nullslast())
        .all()
    )
    sessions = (
        db.query(StudySession)
        .filter(StudySession.course_id == course_id)
        .order_by(StudySession.date.desc())
        .limit(20)
        .all()
    )
    study_minutes_total = (
        db.query(func.coalesce(func.sum(StudySession.minutes), 0))
        .filter(StudySession.course_id == course_id)
        .scalar()
    )
    return CourseDetailOut(
        id=course.id,
        user_id=course.user_id,
        name=course.name,
        color=course.color,
        teacher=course.teacher,
        room=course.room,
        schedule=course.schedule,
        description=course.description,
        syllabus_url=course.syllabus_url,
        assignment_count=len(assignments),
        study_minutes_total=int(study_minutes_total or 0),
        assignments=assignments,
        study_sessions=sessions,
    )


@router.patch("/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int,
    body: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_user_course(db, course_id, current_user.id)
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = _get_user_course(db, course_id, current_user.id)
    db.delete(course)
    db.commit()


def _get_user_course(db: Session, course_id: int, user_id: int) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course
