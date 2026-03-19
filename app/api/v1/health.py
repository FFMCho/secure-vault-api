"""Health-Endpunkt – für Docker/K8s und Load-Balancer."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db.session import check_db_connection

router = APIRouter(tags=["Health"])


@router.get("")
async def health_check():
    """Healthcheck inkl. DB-Verbindungsprüfung."""
    settings = get_settings()
    db_ok = await check_db_connection()
    payload = {
        "status": "ok" if db_ok else "degraded",
        "service": settings.app_name,
        "database": "connected" if db_ok else "disconnected",
    }
    if not db_ok:
        return JSONResponse(status_code=503, content=payload)
    return payload
