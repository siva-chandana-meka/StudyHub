# StudyHub

Personal study planner: courses, assignments, study sessions, and deadlines in one place.

## Stack

| Layer    | Technology              |
| -------- | ----------------------- |
| Backend  | FastAPI                 |
| Frontend | HTML, CSS, JavaScript   |
| Database | SQLite (dev) or PostgreSQL (prod) |

## Features

- Login / register with JWT
- Dashboard: deadlines, overdue, study time, completion rate, weekly goals
- Courses list + detail (edit details, syllabus link, assignments, sessions)
- Assignments with categories (exam, homework, reading), filters, edit/delete
- Study log + weekly chart + **CSV export**
- **Calendar** month view with due dates
- **Profile**: name, password, email reminders toggle
- **Study goals**: weekly minutes per course with progress bars
- **Dark / light theme**
- **Mobile-friendly** collapsible sidebar
- **Email reminders** (optional SMTP; runs daily via scheduler)
- **API tests** (pytest)

## Setup

```bash
cd StudyHub
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # optional
```

## Run

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- App: http://127.0.0.1:8000/login.html
- API docs: http://127.0.0.1:8000/docs

## PostgreSQL

In `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/studyhub
```

## Email reminders

Configure SMTP in `.env` (see `.env.example`). Reminders run daily at `REMINDER_HOUR_UTC` for assignments due tomorrow. Users can disable them in Profile.

## Tests

```bash
pytest
```

## Project layout

```
StudyHub/
├── backend/
├── frontend/
├── tests/
├── requirements.txt
└── .env.example
```
