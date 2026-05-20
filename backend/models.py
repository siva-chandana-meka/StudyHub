import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def _enum_values(enum_cls: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_cls]


class AssignmentStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class AssignmentPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AssignmentCategory(str, enum.Enum):
    EXAM = "exam"
    HOMEWORK = "homework"
    READING = "reading"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email_reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    courses: Mapped[list["Course"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    study_goals: Mapped[list["StudyGoal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#3b82f6")
    teacher: Mapped[str | None] = mapped_column(String(120), nullable=True)
    room: Mapped[str | None] = mapped_column(String(120), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    syllabus_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="courses")
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    study_goal: Mapped["StudyGoal | None"] = relationship(
        back_populates="course", uselist=False, cascade="all, delete-orphan"
    )


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[AssignmentPriority] = mapped_column(
        Enum(AssignmentPriority, values_callable=_enum_values, native_enum=False),
        default=AssignmentPriority.MEDIUM,
    )
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus, values_callable=_enum_values, native_enum=False),
        default=AssignmentStatus.TODO,
    )
    category: Mapped[AssignmentCategory] = mapped_column(
        Enum(AssignmentCategory, values_callable=_enum_values, native_enum=False),
        default=AssignmentCategory.OTHER,
    )

    course: Mapped["Course"] = relationship(back_populates="assignments")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped["Course"] = relationship(back_populates="study_sessions")


class StudyGoal(Base):
    __tablename__ = "study_goals"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course_goal"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False, index=True)
    weekly_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="study_goals")
    course: Mapped["Course"] = relationship(back_populates="study_goal")
