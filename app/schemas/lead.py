from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
    first_name: str = Field(..., description="Prospect's first name")
    last_name: str = Field(..., description="Prospect's last name")
    email_id: EmailStr = Field(..., description="Prospect's email address (must be unique)")


class LeadRead(BaseModel):
    id: str = Field(..., description="Lead UUID")
    first_name: str
    last_name: str
    email_id: str = Field(..., description="Prospect's email address")
    resume_filename: str = Field(..., description="Original filename of the uploaded resume")
    lead_state_id: str = Field(..., description="Current state: PENDING or REACHED_OUT")
    handled_by_user_id: str | None = Field(None, description="ID of the attorney assigned to this lead")
    attorney_notes: str | None = Field(None, description="Internal notes added by the attorney")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadUpdate(BaseModel):
    lead_state_id: str | None = Field(None, description="New state: PENDING or REACHED_OUT")
    attorney_notes: str | None = Field(None, description="Internal notes to set or update")
