from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies.auth import create_access_token, verify_password
from ..models.user import User
from ..schemas.user import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    responses={
        401: {"description": "Incorrect email or password"},
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticates an internal user and returns a Bearer JWT.

    Submit as `application/x-www-form-urlencoded` with `username` (email) and `password`.
    Use the returned `access_token` in the `Authorization: Bearer <token>` header for protected endpoints.
    """
    result = await db.execute(
        select(User).where(User.email == form_data.username, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": user.id, "role": user.user_role_id})
    return TokenResponse(access_token=token)
