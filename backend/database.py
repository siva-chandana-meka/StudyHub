from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings

_connect_args = {}
if settings.database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _add_columns(table: str, columns: dict[str, str]):
    inspector = inspect(engine)
    if table not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns(table)}
    with engine.begin() as conn:
        for name, col_type in columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}"))


def _run_migrations():
    _add_columns("courses", {
        "room": "VARCHAR(120)",
        "schedule": "VARCHAR(200)",
        "description": "TEXT",
        "syllabus_url": "VARCHAR(500)",
    })
    _add_columns("assignments", {"category": "VARCHAR(20) DEFAULT 'other'"})
    _add_columns("users", {"email_reminders_enabled": "BOOLEAN DEFAULT 1"})

    if "assignments" in inspect(engine).get_table_names():
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE assignments SET category = 'other' "
                    "WHERE category IS NULL OR category = ''"
                )
            )
            # Normalize legacy enum names (HIGH) to values (high) for SQLite
            for col, mapping in (
                ("priority", {"LOW": "low", "MEDIUM": "medium", "HIGH": "high"}),
                (
                    "status",
                    {"TODO": "todo", "IN_PROGRESS": "in_progress", "DONE": "done"},
                ),
                (
                    "category",
                    {"EXAM": "exam", "HOMEWORK": "homework", "READING": "reading", "OTHER": "other"},
                ),
            ):
                for old, new in mapping.items():
                    conn.execute(
                        text(f"UPDATE assignments SET {col} = :new WHERE {col} = :old"),
                        {"old": old, "new": new},
                    )


def init_db():
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _run_migrations()
