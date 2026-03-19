"""FastAPI Dependencies – DB-Session, Auth (später)."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# Re-export für einfachen Import in Routern
__all__ = ["get_db"]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Alias für get_db – konsistente Benennung."""
    async for session in get_db():
        yield session
