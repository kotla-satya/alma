from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies.auth import hash_password
from ..models.user import User
from ..schemas.user import UserCreate, UserRead


async def create_user(db: AsyncSession, body: UserCreate) -> UserRead:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),
        user_role_id=body.user_role_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserRead.model_validate(user)
