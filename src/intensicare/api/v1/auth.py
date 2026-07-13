"""Authentication endpoints — login, register, logout."""

from __future__ import annotations

from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user, require_admin
from intensicare.auth.jwt import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    is_token_blacklisted,
)
from intensicare.config import settings
from intensicare.core.database import get_db
from intensicare.core.redis import get_redis
from intensicare.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

USERNAME_MIN_LENGTH = 3
PASSWORD_MIN_LENGTH = 8


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None

    @field_validator("username")
    @classmethod
    def username_min_length(cls, v: str) -> str:
        if len(v) < USERNAME_MIN_LENGTH:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError("Password must be at least 8 characters")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 — OAuth2 token type literal, not a secret
    user: UserResponse


class UserResponse(BaseModel):
    # NOTE: `id` stays `int` here (matches the DB PK). frontend-v3's TS type
    # declares `id: string`, but a JSON number is assignable at runtime; the
    # type-side fix belongs in the frontend, not here (would be a breaking
    # wire-format change for other consumers of this endpoint).
    id: int
    username: str
    email: str
    display_name: str | None
    is_admin: bool
    is_active: bool
    # Added for AUTH-1: frontend-v3 (lib/api.ts LoginResponse.user) expects
    # `name` and `role`. Additive only — existing fields kept for backward
    # compatibility with other consumers.
    name: str
    role: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _user_to_response(user: User) -> UserResponse:
    """Convert a User model instance to a UserResponse."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        name=user.display_name or user.username,
        role=user.role,
    )


def _build_login_response(user: User, access_token: str, refresh_token: str) -> JSONResponse:
    """Build a JSONResponse with tokens, user info, and dual cookies."""
    user_resp = _user_to_response(user)
    response = JSONResponse(
        content=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_resp,
        ).model_dump(),
    )
    # Cookie for HttpOnly access (legacy name)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=1800,
        path="/",
    )
    # Cookie for frontend middleware (expects 'token')
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=1800,
        path="/",
    )
    # HttpOnly refresh_token cookie — enables session bootstrap on reload/
    # deep-link (POST /auth/refresh reads this cookie; the in-memory-only
    # access token is otherwise lost on every full page load, see
    # frontend-v3 lib/auth.tsx AuthProvider). Lifetime matches the refresh
    # JWT's own `exp` claim (jwt_refresh_expire_days), not the short-lived
    # access token cookies above.
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="strict",
        max_age=settings.jwt_refresh_expire_days * 24 * 60 * 60,
        path="/",
    )
    return response


async def _refresh_from_cookie(request: Request, db: AsyncSession) -> JSONResponse:
    """Bootstrap a session from the HttpOnly ``refresh_token`` cookie.

    Used by the frontend on mount (page reload / deep-link) to recover the
    in-memory-only access token, which is intentionally never persisted to
    localStorage/sessionStorage (XSS hardening — see lib/api.ts). The
    browser sends the HttpOnly cookie automatically; this endpoint validates
    it and re-issues a fresh access/refresh pair via the same code path as
    login, so the response shape is identical to ``TokenResponse``.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token ausente"
        )

    redis_client = get_redis()
    if await is_token_blacklisted(refresh_token, redis_client):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revogado"
        )

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido"
        )

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_admin": user.is_admin,
        "role": user.role,
        "name": user.display_name or user.username,
        "email": user.email,
    }
    new_access_token = create_access_token(token_data)
    # Rotate the refresh token on every use (standard refresh-token-rotation
    # practice); the old one is left to expire naturally rather than
    # blacklisted, since it was single-use only insofar as the client
    # always receives (and the browser overwrites the cookie with) the new
    # one on success.
    new_refresh_token = create_refresh_token(token_data)

    return _build_login_response(user, new_access_token, new_refresh_token)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    redis_client = get_redis()
    lockout_key = f"lockout:failed:{request.username}"
    failed_attempts = await redis_client.get(lockout_key)
    if failed_attempts and int(failed_attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts. Please try again in 15 minutes.",
        )

    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(request.password, user.hashed_password):
        await redis_client.incr(lockout_key)
        await redis_client.expire(lockout_key, 900)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated"
        )

    await redis_client.delete(lockout_key)

    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_admin": user.is_admin,
        "role": user.role,
        "name": user.display_name or user.username,
        "email": user.email,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return _build_login_response(user, access_token, refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, db: AsyncSession = Depends(get_db)):
    """Bootstrap/renew a session from the HttpOnly ``refresh_token`` cookie.

    Called by the frontend on mount to recover the in-memory-only access
    token lost on full page reload / deep-link navigation (JWT is never
    persisted client-side). Returns 401 if the cookie is missing/invalid.
    """
    return await _refresh_from_cookie(request, db)


# ---------------------------------------------------------------------------
# Compat router: /api/v1/auth/login accepting form-urlencoded
# (frontend-v3 sends Content-Type: application/x-www-form-urlencoded)
# ---------------------------------------------------------------------------
api_v1_auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@api_v1_auth_router.post("/login", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login via form-urlencoded (compatibilidade com frontend-v3)."""
    redis_client = get_redis()
    lockout_key = f"lockout:failed:{form_data.username}"
    failed_attempts = await redis_client.get(lockout_key)
    if failed_attempts and int(failed_attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed attempts. Please try again in 15 minutes.",
        )

    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        await redis_client.incr(lockout_key)
        await redis_client.expire(lockout_key, 900)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated"
        )

    await redis_client.delete(lockout_key)

    token_data = {
        "sub": user.username,
        "user_id": user.id,
        "is_admin": user.is_admin,
        "role": user.role,
        "name": user.display_name or user.username,
        "email": user.email,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return _build_login_response(user, access_token, refresh_token)


@api_v1_auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_v1(request: Request, db: AsyncSession = Depends(get_db)):
    """Bootstrap/renew a session from the HttpOnly ``refresh_token`` cookie.

    API v1 compat alias — see ``refresh()`` above for details. This is the
    path frontend-v3 actually calls (proxied through Next.js at
    ``/api/v1/auth/refresh``).
    """
    return await _refresh_from_cookie(request, db)


@api_v1_auth_router.post("/logout")
async def logout_v1(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """Log out (API v1 compat) — see ``_perform_logout`` for details."""
    return await _perform_logout(request)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")

    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        display_name=request.display_name or request.username,
        is_admin=False,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    # Build the response explicitly (rather than returning the ORM object and
    # relying on FastAPI's from_attributes auto-serialization): UserResponse.name
    # has no 1:1 attribute on the User model (it derives from display_name/username).
    return _user_to_response(user)


async def _perform_logout(request: Request) -> JSONResponse:
    """Blacklist the current access + refresh tokens and clear all session cookies.

    Clearing the cookies server-side (``delete_cookie``) is required now
    that ``POST /auth/refresh`` exists to bootstrap a session from the
    HttpOnly ``refresh_token`` cookie (see ``_refresh_from_cookie`` above):
    without also blacklisting that refresh token and deleting the cookie
    here, a "logged out" session would be silently resurrected the next
    time the frontend calls ``/auth/refresh`` on mount, since the cookie
    would still be valid until its natural expiry (up to
    ``jwt_refresh_expire_days``).
    """
    redis_client = get_redis()

    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        access_token = auth_header[7:].strip()
        await blacklist_token(access_token, redis_client)

    refresh_cookie = request.cookies.get("refresh_token")
    if refresh_cookie:
        await blacklist_token(refresh_cookie, redis_client)

    response = JSONResponse(content={"detail": "Logged out successfully"})
    for cookie_name in ("access_token", "token", "refresh_token"):
        response.delete_cookie(key=cookie_name, path="/")
    return response


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    """Log out — see ``_perform_logout`` for details."""
    return await _perform_logout(request)
