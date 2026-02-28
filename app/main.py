import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from .routers import auth, leads, users
from .services.notification_service import process_pending_notifications

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(process_pending_notifications, "interval", seconds=30, id="lead_notifications")
    scheduler.start()
    logger.info("Scheduler started — lead notifications run every 30 seconds.")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="Alma Lead Management API",
    version="1.0.0",
    description=(
        "Backend API for managing law firm leads.\n\n"
        "**Prospects** submit leads (with resume) via `POST /leads` — no authentication required.\n\n"
        "**Attorneys** manage the lead lifecycle (view, update state, download resume) "
        "using a JWT obtained from `POST /auth/login`.\n\n"
        "Email notifications are sent to the assigned attorney and the prospect "
        "automatically via a background job running every 30 seconds."
    ),
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(users.router)


@app.get("/health", tags=["health"], summary="Health check")
async def health() -> dict:
    """Returns 200 if the service is running."""
    return {"status": "ok"}
