"""Audit-Service – Logging sicherheitsrelevanter Aktionen."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def log_audit(
    session: AsyncSession,
    *,
    action: str,
    user_id: UUID | None = None,
    file_id: UUID | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    status: str = "success",
    detail: str | None = None,
) -> AuditLog:
    """Schreibt Audit-Log-Eintrag."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        file_id=file_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        detail=detail,
    )
    session.add(entry)
    await session.flush()  # damit ID verfügbar ist
    return entry
