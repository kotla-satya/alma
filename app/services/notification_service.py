import logging
from datetime import datetime, timezone
from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import AsyncSessionLocal
from ..models.lead import Lead
from ..models.notification import LeadNotification
from . import email_service

logger = logging.getLogger(__name__)


async def process_pending_notifications(
    session_factory: Callable[[], AsyncSession] | None = None,
) -> None:
    """
    Called by the scheduler every x minutes based on the cron job.
    Finds unsent LeadNotification rows, sends the emails, and marks them done.
    Accepts an optional session_factory for testability.
    """
    factory = session_factory or AsyncSessionLocal
    logger.info("Processing pending lead notifications...")
    try:
        async with factory() as session:
            result = await session.execute(
                select(LeadNotification)
                .where(
                    (LeadNotification.is_lead_notified == False)  # noqa: E712
                    | (LeadNotification.is_attorney_notified == False)  # noqa: E712
                )
                .options(selectinload(LeadNotification.lead).selectinload(Lead.handler))
            )
            notifications = result.scalars().all()

            if not notifications:
                logger.info("No pending notifications.")
                return

            now = datetime.now(timezone.utc)
            for notif in notifications:
                lead = notif.lead
                if lead is None:
                    continue

                if not notif.is_attorney_notified:
                    if lead.handler is None:
                        logger.warning(
                            "Lead %s has no assigned attorney — skipping attorney notification.", lead.id
                        )
                    else:
                        email_service._send(
                            to_email=lead.handler.email,
                            subject="New lead received",
                            body=(
                                f"A new lead has been submitted.\n\n"
                                f"Name: {lead.first_name} {lead.last_name}\n"
                                f"Email: {lead.email_id}\n"
                            ),
                        )
                    notif.is_attorney_notified = True
                    notif.attorney_notified_at = now

                if not notif.is_lead_notified:
                    email_service._send(
                        to_email=lead.email_id,
                        subject="We received your submission",
                        body=(
                            f"Dear {lead.first_name},\n\n"
                            "Thank you for reaching out. We have received your submission "
                            "and will be in touch shortly.\n\n"
                            "Best regards,\nAlma Law"
                        ),
                    )
                    notif.is_lead_notified = True
                    notif.lead_notified_at = now

            await session.commit()
            logger.info("Processed %d notification(s).", len(notifications))
    except Exception:
        logger.exception("Error processing pending notifications")
