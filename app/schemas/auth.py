"""Auth-Schemas – Register, Login, Token."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request für User-Registrierung."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Request für Login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT Access Token Response."""

    access_token: str
    token_type: str = "bearer"
