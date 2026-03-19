"""Auth-Endpunkte – Register, Login."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthError, login, register

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_client_ip(request: Request) -> str | None:
    """Extrahiert Client-IP (X-Forwarded-For oder direkter Client)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _get_user_agent(request: Request) -> str | None:
    """Extrahiert User-Agent (gekürzt für DB)."""
    ua = request.headers.get("user-agent")
    return ua[:512] if ua else None


@router.post("/register", response_model=UserResponse)
async def register_user(
    data: RegisterRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """Registriert neuen User."""
    try:
        user = await register(
            session,
            email=data.email,
            password=data.password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        await session.refresh(user)
        return user
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login_user(
    data: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    """Login – gibt JWT Access Token zurück."""
    try:
        _, token = await login(
            session,
            email=data.email,
            password=data.password,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
        return TokenResponse(access_token=token)
    except AuthError:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
