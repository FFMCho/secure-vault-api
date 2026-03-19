"""V1 Router – aggregiert alle API-Router."""

from fastapi import APIRouter

from app.api.v1 import auth, health, users

api_router = APIRouter(prefix="/api/v1", tags=["v1"])

api_router.include_router(health.router, prefix="/health")
api_router.include_router(auth.router)
api_router.include_router(users.router)
