import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config import settings

logger = logging.getLogger(__name__)


def send_reminder_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.email_enabled:
        logger.info("Email disabled (SMTP not configured). Would send to %s: %s", to_email, subject)
        return False
    msg = MIMEMultipart()
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        if settings.smtp_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from, [to_email], msg.as_string())
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return False
