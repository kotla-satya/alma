from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies.auth import require_attorney
from ..models.user import User
from ..schemas.user import UserCreate, UserRead
from ..services import user_service

router = APIRouter(prefix="/user", tags=["users"])


@router.post(
    "",
    response_model=UserRead,
    status_code=201,
    summary="Create an internal user",
    responses={
        201: {"description": "User created successfully"},
        401: {"description": "Missing or invalid token"},
        403: {"description": "Attorney role required"},
        409: {"description": "Email already registered"},
    },
)
async def create_user(
    body: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_attorney)],
) -> UserRead:
    """
    Creates a new internal user (attorney, paralegal, or clerk). Requires an attorney JWT.

    Valid values for `user_role_id`: `ATTORNEY`, `PARA_LEGAL`, `CLERK`.
    """
    return await user_service.create_user(db, body)
