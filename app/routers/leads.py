from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..dependencies.auth import require_attorney
from ..models.user import User
from ..schemas.lead import LeadCreate, LeadRead, LeadUpdate
from ..services import lead_service

router = APIRouter(tags=["leads"])


@router.post(
    "/leads",
    response_model=LeadRead,
    status_code=201,
    summary="Submit a lead",
    responses={
        201: {"description": "Lead created successfully"},
        409: {"description": "A lead with this email already exists"},
    },
)
async def submit_lead(
    first_name: Annotated[str, Form(description="Prospect's first name")],
    last_name: Annotated[str, Form(description="Prospect's last name")],
    email_id: Annotated[str, Form(description="Prospect's email address (must be unique)")],
    resume: Annotated[UploadFile, File(description="Resume file (PDF, DOCX, etc.)")],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeadRead:
    """
    Publicly accessible. Accepts multipart/form-data with prospect details and a resume file.

    On success, a notification row is created and the assigned attorney is emailed
    within 30 seconds by the background job.
    """
    data = LeadCreate(first_name=first_name, last_name=last_name, email_id=email_id)
    return await lead_service.create_lead(db, data, resume)


@router.get(
    "/leads/",
    response_model=dict,
    summary="List all leads",
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Attorney role required"},
    },
)
async def list_leads(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_attorney)],
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> dict:
    """
    Returns a paginated list of all leads. Requires a valid attorney JWT.

    Response shape: `{ "total": int, "items": [LeadRead] }`
    """
    leads, total = await lead_service.list_leads(db, skip, limit)
    return {"total": total, "items": leads}


@router.get(
    "/leads/{lead_id}",
    response_model=LeadRead,
    summary="Get a lead by ID",
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Attorney role required"},
        404: {"description": "Lead not found"},
    },
)
async def get_lead(
    lead_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_attorney)],
) -> LeadRead:
    """Returns the full detail of a single lead. Requires a valid attorney JWT."""
    return await lead_service.get_lead(db, lead_id)


@router.patch(
    "/leads/{lead_id}",
    response_model=LeadRead,
    summary="Update a lead",
    responses={
        401: {"description": "Missing or invalid token"},
        403: {"description": "Attorney role required"},
        404: {"description": "Lead not found"},
    },
)
async def update_lead(
    lead_id: str,
    body: LeadUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_attorney)],
) -> LeadRead:
    """
    Updates `lead_state_id` and/or `attorney_notes` on a lead. Requires a valid attorney JWT.

    """
    return await lead_service.update_lead(db, lead_id, body)


@router.get(
    "/leads/{lead_id}/resume",
    summary="Download resume",
    response_class=Response,
    responses={
        200: {
            "description": "Resume file download",
            "content": {"application/octet-stream": {}},
        },
        401: {"description": "Missing or invalid token"},
        403: {"description": "Attorney role required"},
        404: {"description": "Lead not found"},
    },
)
async def download_resume(
    lead_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_attorney)],
) -> Response:
    """
    Streams the resume file for a lead as an attachment.
    The original filename is preserved in the `Content-Disposition` header.
    Requires a valid attorney JWT.
    """
    resume_bytes, filename = await lead_service.get_lead_resume(db, lead_id)
    return Response(
        content=resume_bytes,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
