"""V1 Router – aggregiert alle API-Router."""

from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Health unter /api/v1/health, weitere Router in Phase 2+
api_router.include_router(health.router, prefix="/health")
