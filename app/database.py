from typing import AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from .config import settings

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session
