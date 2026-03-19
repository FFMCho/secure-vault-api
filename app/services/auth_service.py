"""Auth-Service – Registrierung, Login."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.services.audit_service import log_audit


class AuthError(Exception):
    """Auth-Fehler (z.B. E-Mail bereits vergeben, falsches Passwort)."""

    pass


async def register(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> User:
    """Registriert neuen User. Wirft AuthError wenn E-Mail existiert."""
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none():
        await log_audit(
            session,
            action="register_failed",
            ip_address=ip_address,
            user_agent=user_agent,
            status="failure",
            detail="email_already_exists",
        )
        raise AuthError("E-Mail bereits registriert")

    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.USER,
    )
    session.add(user)
    await session.flush()

    await log_audit(
        session,
        action="register",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return user


async def login(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> tuple[User, str]:
    """
    Login. Gibt (User, access_token) zurück.
    Wirft AuthError bei falschem Passwort oder unbekannter E-Mail.
    """
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        await log_audit(
            session,
            action="login_failed",
            ip_address=ip_address,
            user_agent=user_agent,
            status="failure",
            detail="invalid_credentials",
        )
        raise AuthError("Ungültige Anmeldedaten")

    from datetime import datetime, timezone

    user.last_login_at = datetime.now(timezone.utc)
    token = create_access_token(subject=user.id)

    await log_audit(
        session,
        action="login",
        user_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return user, token
