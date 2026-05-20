from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")

    app_name: str = "StudyHub"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24 * 7

    # sqlite:///./studyhub.db  or  postgresql://user:pass@localhost/studyhub
    database_url: str = f"sqlite:///{ROOT_DIR / 'studyhub.db'}"

    # Email reminders (optional — leave SMTP_HOST empty to disable sending)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "studyhub@localhost"
    smtp_tls: bool = True
    reminder_days_ahead: int = 1
    reminder_hour_utc: int = 8

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_host and self.smtp_user)


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
