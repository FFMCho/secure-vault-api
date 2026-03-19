"""Audit-Schemas – für Admin-Audit-Logs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    """Audit-Log-Eintrag für API-Response."""

    id: UUID
    user_id: UUID | None
    action: str
    file_id: UUID | None
    ip_address: str | None
    user_agent: str | None
    status: str
    detail: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
