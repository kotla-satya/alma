import io

import pytest
from sqlalchemy import select

from app.models.notification import LeadNotification


@pytest.mark.asyncio
async def test_submit_lead_creates_notification(client, db_session):
    response = await client.post(
        "/leads",
        data={
            "first_name": "Jane",
            "last_name": "Doe",
            "email_id": "jane@example.com",
        },
        files={"resume": ("resume.pdf", io.BytesIO(b"%PDF-1.4 fake content"), "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email_id"] == "jane@example.com"
    assert body["lead_state_id"] == "PENDING"
    assert body["resume_filename"] == "resume.pdf"

    # Notification row created, not yet sent
    result = await db_session.execute(
        select(LeadNotification).where(LeadNotification.lead_id == body["id"])
    )
    notif = result.scalar_one_or_none()
    assert notif is not None
    assert notif.is_lead_notified is False
    assert notif.is_attorney_notified is False
    assert notif.notification_type_id == "email_new_lead_submission"


@pytest.mark.asyncio
async def test_list_leads_without_auth(client):
    response = await client.get("/leads/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_leads_non_attorney_forbidden(client, db_session):
    from app.dependencies.auth import create_access_token, hash_password
    from app.models.user import User

    clerk = User(
        name="Test Clerk",
        email="clerk@test.com",
        hashed_password=hash_password("password123"),
        user_role_id="CLERK",
    )
    db_session.add(clerk)
    await db_session.commit()
    await db_session.refresh(clerk)

    token = create_access_token({"sub": clerk.id, "role": clerk.user_role_id})
    response = await client.get("/leads/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_leads_with_auth(client, attorney_token):
    await client.post(
        "/leads",
        data={
            "first_name": "John",
            "last_name": "Smith",
            "email_id": "john@example.com",
        },
        files={"resume": ("cv.pdf", io.BytesIO(b"resume data"), "application/pdf")},
    )

    response = await client.get(
        "/leads/",
        headers={"Authorization": f"Bearer {attorney_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert len(body["items"]) >= 1


@pytest.mark.asyncio
async def test_update_lead_state(client, attorney_token):
    create_resp = await client.post(
        "/leads",
        data={
            "first_name": "Alice",
            "last_name": "Wonder",
            "email_id": "alice@example.com",
        },
        files={"resume": ("resume.pdf", io.BytesIO(b"data"), "application/pdf")},
    )
    lead_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/leads/{lead_id}",
        json={"lead_state_id": "REACHED_OUT", "attorney_notes": "Called and left voicemail."},
        headers={"Authorization": f"Bearer {attorney_token}"},
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["lead_state_id"] == "REACHED_OUT"
    assert body["attorney_notes"] == "Called and left voicemail."


@pytest.mark.asyncio
async def test_download_resume(client, attorney_token):
    resume_content = b"%PDF-1.4 test resume"
    create_resp = await client.post(
        "/leads",
        data={
            "first_name": "Bob",
            "last_name": "Builder",
            "email_id": "bob@example.com",
        },
        files={"resume": ("bob_resume.pdf", io.BytesIO(resume_content), "application/pdf")},
    )
    lead_id = create_resp.json()["id"]

    resume_resp = await client.get(
        f"/leads/{lead_id}/resume",
        headers={"Authorization": f"Bearer {attorney_token}"},
    )
    assert resume_resp.status_code == 200
    assert resume_resp.content == resume_content
    assert "bob_resume.pdf" in resume_resp.headers["content-disposition"]


@pytest.mark.asyncio
async def test_notification_service_sends_emails(client, db_session, db_session_factory):
    """Cron job processes pending notifications and marks them sent."""
    from unittest.mock import patch

    from app.services.notification_service import process_pending_notifications

    await client.post(
        "/leads",
        data={
            "first_name": "Carol",
            "last_name": "Test",
            "email_id": "carol@example.com",
        },
        files={"resume": ("r.pdf", io.BytesIO(b"data"), "application/pdf")},
    )

    with patch("app.services.notification_service.email_service._send") as mock_send:
        await process_pending_notifications(session_factory=db_session_factory)

    assert mock_send.call_count == 2  # attorney + prospect

    db_session.expire_all()
    result = await db_session.execute(select(LeadNotification))
    notif = result.scalar_one()
    assert notif.is_attorney_notified is True
    assert notif.is_lead_notified is True
    assert notif.attorney_notified_at is not None
    assert notif.lead_notified_at is not None
