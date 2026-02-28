import logging

import resend

from ..config import settings

logger = logging.getLogger(__name__)


def _send(to_email: str, subject: str, body: str) -> None:
    if not settings.resend_api_key:
        logger.info("Resend API key not set — skipping email to %s: %s", to_email, subject)
        return
    try:
        resend.api_key = settings.resend_api_key
        resend.Emails.send({
            "from": settings.from_email,
            "to": [to_email],
            "subject": subject,
            "text": body,
        })
        logger.info("Email sent to %s: %s", to_email, subject)
    except Exception:
        logger.exception("Failed to send email to %s", to_email)

