from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.email_service import send_reminder_email
from backend.models import Assignment, AssignmentStatus, Course, User


def send_due_assignment_reminders():
    db: Session = SessionLocal()
    try:
        today = date.today()
        target = today + timedelta(days=1)
        users = db.query(User).filter(User.email_reminders_enabled.is_(True)).all()
        for user in users:
            due_items = (
                db.query(Assignment, Course)
                .join(Course)
                .filter(
                    Course.user_id == user.id,
                    Assignment.due_date == target,
                    Assignment.status != AssignmentStatus.DONE,
                )
                .all()
            )
            if not due_items:
                continue
            lines = []
            for assignment, course in due_items:
                lines.append(f"  • {assignment.title} ({course.name})")
            body = (
                f"Hi {user.name},\n\n"
                f"You have {len(lines)} assignment(s) due tomorrow ({target}):\n\n"
                + "\n".join(lines)
                + "\n\n— StudyHub"
            )
            send_reminder_email(
                user.email,
                f"StudyHub: {len(lines)} assignment(s) due tomorrow",
                body,
            )
    finally:
        db.close()
