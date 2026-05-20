from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field

from backend.models import AssignmentCategory, AssignmentPriority, AssignmentStatus


# --- Auth / Profile ---


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=120)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    email_reminders_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email_reminders_enabled: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Courses ---


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    color: str = Field(default="#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$")
    teacher: str | None = Field(default=None, max_length=120)
    room: str | None = Field(default=None, max_length=120)
    schedule: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    syllabus_url: str | None = Field(default=None, max_length=500)


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    color: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$")
    teacher: str | None = Field(default=None, max_length=120)
    room: str | None = Field(default=None, max_length=120)
    schedule: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    syllabus_url: str | None = Field(default=None, max_length=500)


class CourseOut(BaseModel):
    id: int
    user_id: int
    name: str
    color: str
    teacher: str | None
    room: str | None
    schedule: str | None
    description: str | None
    syllabus_url: str | None

    model_config = {"from_attributes": True}


# --- Assignments ---


class AssignmentCreate(BaseModel):
    course_id: int
    title: str = Field(min_length=1, max_length=200)
    due_date: date | None = None
    priority: AssignmentPriority = AssignmentPriority.MEDIUM
    status: AssignmentStatus = AssignmentStatus.TODO
    category: AssignmentCategory = AssignmentCategory.OTHER


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    due_date: date | None = None
    priority: AssignmentPriority | None = None
    status: AssignmentStatus | None = None
    category: AssignmentCategory | None = None


class AssignmentOut(BaseModel):
    id: int
    course_id: int
    title: str
    due_date: date | None
    priority: AssignmentPriority
    status: AssignmentStatus
    category: AssignmentCategory

    model_config = {"from_attributes": True}


class CalendarAssignmentOut(AssignmentOut):
    course_name: str
    course_color: str


class CalendarOut(BaseModel):
    year: int
    month: int
    days: dict[str, list[CalendarAssignmentOut]]


# --- Study sessions ---


class StudySessionCreate(BaseModel):
    course_id: int
    minutes: int = Field(gt=0, le=24 * 60)
    date: date
    notes: str | None = None


class StudySessionOut(BaseModel):
    id: int
    course_id: int
    minutes: int
    date: date
    notes: str | None

    model_config = {"from_attributes": True}


# --- Study goals ---


class StudyGoalCreate(BaseModel):
    course_id: int
    weekly_minutes: int = Field(gt=0, le=7 * 24 * 60)


class StudyGoalUpdate(BaseModel):
    weekly_minutes: int = Field(gt=0, le=7 * 24 * 60)


class StudyGoalOut(BaseModel):
    id: int
    course_id: int
    weekly_minutes: int
    course_name: str
    course_color: str
    minutes_this_week: int
    progress_percent: float

    model_config = {"from_attributes": True}


# --- Dashboard ---


class DashboardOut(BaseModel):
    upcoming_deadlines: list[AssignmentOut]
    overdue_assignments: list[AssignmentOut]
    today_study_minutes: int
    weekly_study_minutes: int
    assignments_total: int
    assignments_done: int
    completion_rate: float
    study_goals: list[StudyGoalOut]


class CourseDetailOut(CourseOut):
    assignment_count: int
    study_minutes_total: int
    assignments: list[AssignmentOut]
    study_sessions: list[StudySessionOut]
