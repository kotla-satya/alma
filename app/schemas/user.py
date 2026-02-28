from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., description="Full name of the user")
    email: EmailStr = Field(..., description="Login email (must be unique)")
    password: str = Field(..., description="Plain-text password (will be hashed)")
    user_role_id: str = Field("ATTORNEY", description="Role: ATTORNEY, PARA_LEGAL, or CLERK")


class UserRead(BaseModel):
    id: str = Field(..., description="User UUID")
    name: str
    email: EmailStr
    user_role_id: str = Field(..., description="Role: ATTORNEY, PARA_LEGAL, or CLERK")
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Bearer token")
    token_type: str = Field("bearer", description="Always 'bearer'")
