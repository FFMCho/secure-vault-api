"""User-Schemas – für API-Responses und spätere Auth-Requests."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    """Basis-Schema für User."""

    email: EmailStr
    role: UserRole


class UserResponse(UserBase):
    """User-Response (ohne Passwort)."""

    id: UUID
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}
