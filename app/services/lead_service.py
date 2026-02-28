from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.lead import Lead
from ..models.notification import LeadNotification
from ..models.user import User
from ..schemas.lead import LeadCreate, LeadRead, LeadUpdate


async def create_lead(db: AsyncSession, data: LeadCreate, resume: UploadFile) -> LeadRead:
    existing = await db.execute(select(Lead).where(Lead.email_id == data.email_id))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A lead with this email already exists",
        )

    # Assign default attorney on creation, to optimize this value can be cached
    attorney_result = await db.execute(
        select(User).where(User.email == settings.admin_email, User.is_active == True)
    )
    default_attorney = attorney_result.scalar_one_or_none()

    resume_bytes = await resume.read()
    lead = Lead(
        first_name=data.first_name,
        last_name=data.last_name,
        email_id=data.email_id,
        resume=resume_bytes,
        resume_filename=resume.filename or "resume",
        handled_by_user_id=default_attorney.id if default_attorney else None,
    )
    db.add(lead)
    await db.flush()  # get lead.id before commit

    notification = LeadNotification(
        lead_id=lead.id,
        notification_type_id="email_new_lead_submission",
    )
    db.add(notification)
    await db.commit()
    await db.refresh(lead)
    return LeadRead.model_validate(lead)


async def list_leads(db: AsyncSession, skip: int, limit: int) -> tuple[list[LeadRead], int]:
    count_result = await db.execute(select(func.count()).select_from(Lead))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    )
    leads = result.scalars().all()
    return [LeadRead.model_validate(l) for l in leads], total


async def get_lead(db: AsyncSession, lead_id: str) -> LeadRead:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadRead.model_validate(lead)


async def update_lead(db: AsyncSession, lead_id: str, body: LeadUpdate) -> LeadRead:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(lead, key, value)

    await db.commit()
    await db.refresh(lead)
    return LeadRead.model_validate(lead)


async def get_lead_resume(db: AsyncSession, lead_id: str) -> tuple[bytes, str]:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead.resume, lead.resume_filename
