"""
Create tables and seed initial data (roles, states, default attorney).
Safe to run multiple times (idempotent).
"""

import asyncio
import sys
from pathlib import Path

# Ensure project root is on the path when run directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.dependencies.auth import hash_password
from app.models.base import Base
from app.models.lead import Lead, LeadState  # noqa: F401 — register models with Base
from app.models.notification import LeadNotification, NotificationType  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401


async def create_tables(engine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created (or already exist).")


async def seed(session: AsyncSession) -> None:
    # Seed UserRole rows
    for role_id, role_name in [
        ("ATTORNEY", "Attorney"),
        ("PARA_LEGAL", "Paralegal"),
        ("CLERK", "Clerk"),
    ]:
        existing = await session.execute(
            select(UserRole).where(UserRole.role_id == role_id)
        )
        if not existing.scalar_one_or_none():
            session.add(UserRole(role_id=role_id, role_name=role_name))

    # Seed NotificationType rows
    for type_id, type_name in [
        ("email_new_lead_submission", "Email — New Lead Submission"),
    ]:
        existing = await session.execute(
            select(NotificationType).where(NotificationType.notification_type_id == type_id)
        )
        if not existing.scalar_one_or_none():
            session.add(NotificationType(notification_type_id=type_id, notification_type_name=type_name))

    # Seed LeadState rows
    for state_id, state_name in [
        ("PENDING", "Pending"),
        ("REACHED_OUT", "Reached Out"),
    ]:
        existing = await session.execute(
            select(LeadState).where(LeadState.lead_state_id == state_id)
        )
        if not existing.scalar_one_or_none():
            session.add(LeadState(lead_state_id=state_id, lead_state_name=state_name))

    await session.commit()

    # Seed default attorney user
    existing_user = await session.execute(
        select(User).where(User.email == settings.admin_email)
    )
    if not existing_user.scalar_one_or_none():
        session.add(
            User(
                name=settings.admin_name,
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                user_role_id="ATTORNEY",
            )
        )
        await session.commit()
        print(f"Created default attorney: {settings.admin_email}")
    else:
        print(f"Default attorney already exists: {settings.admin_email}")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    await create_tables(engine)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
    print("Init DB complete.")
