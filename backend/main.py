from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.reminders import send_due_assignment_reminders
from backend.routers import assignments, auth, calendar, courses, dashboard, goals, profile, sessions

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.add_job(
        send_due_assignment_reminders,
        "cron",
        hour=settings.reminder_hour_utc,
        minute=0,
        id="assignment_reminders",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(sessions.router)
app.include_router(dashboard.router)
app.include_router(goals.router)
app.include_router(calendar.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "email_reminders": settings.email_enabled,
        "database": "postgresql" if settings.database_url.startswith("postgresql") else "sqlite",
    }


if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
