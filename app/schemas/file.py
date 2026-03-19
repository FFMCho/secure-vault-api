"""File-Schemas – für API-Responses und Upload-Requests."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FileBase(BaseModel):
    """Basis-Schema für File-Metadaten."""

    original_filename: str
    content_type: str
    size_bytes: int


class FileResponse(FileBase):
    """File-Response (Metadaten, kein Object-Key nach außen)."""

    id: UUID
    owner_id: UUID
    created_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}
