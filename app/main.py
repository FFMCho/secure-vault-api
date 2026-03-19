"""FastAPI-Anwendung – Einstiegspunkt und Router-Mount."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: Startup/Shutdown-Hooks."""
    # Startup
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Factory für die FastAPI-App."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )

    # Root-Healthcheck (z.B. für Docker Healthcheck) – prüft auch DB
    @app.get("/health", tags=["Health"])
    async def health():
        from fastapi.responses import JSONResponse

        from app.db.session import check_db_connection

        db_ok = await check_db_connection()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "service": settings.app_name,
            "database": "connected" if db_ok else "disconnected",
        }
        if not db_ok:
            return JSONResponse(status_code=503, content=payload)
        return payload

    # Versionierte API
    app.include_router(api_router)

    return app


app = create_app()
