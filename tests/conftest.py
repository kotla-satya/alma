import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.dependencies.auth import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.lead import LeadState
from app.models.notification import NotificationType
from app.models.user import User, UserRole

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session_factory(db_engine):
    return async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        # Seed roles
        for role_id, role_name in [
            ("ATTORNEY", "Attorney"),
            ("PARA_LEGAL", "Paralegal"),
            ("CLERK", "Clerk"),
        ]:
            session.add(UserRole(role_id=role_id, role_name=role_name))
        # Seed lead states
        for state_id, state_name in [
            ("PENDING", "Pending"),
            ("REACHED_OUT", "Reached Out"),
        ]:
            session.add(LeadState(lead_state_id=state_id, lead_state_name=state_name))
        # Seed notification types
        session.add(
            NotificationType(
                notification_type_id="email_new_lead_submission",
                notification_type_name="Email — New Lead Submission",
            )
        )
        # Seed default admin attorney (matches settings.admin_email for lead assignment)
        session.add(
            User(
                name=settings.admin_name,
                email=settings.admin_email,
                hashed_password=hash_password(settings.admin_password),
                user_role_id="ATTORNEY",
            )
        )
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def attorney_user(db_session):
    user = User(
        name="Test Attorney",
        email="attorney@test.com",
        hashed_password=hash_password("password123"),
        user_role_id="ATTORNEY",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
def attorney_token(attorney_user):
    return create_access_token({"sub": attorney_user.id, "role": attorney_user.user_role_id})
