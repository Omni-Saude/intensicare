"""Authentication endpoints — login, register, logout."""

from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user, require_admin
from intensicare.auth.jwt import blacklist_token, create_access_token, create_refresh_token
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
    token_type: str = "bearer"  # noqa: S105  # OAuth2 token-type label, not a credential


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    display_name: str | None
    is_admin: bool
    is_active: bool


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    # --- Account lockout check (F-SEC-009) ---
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
        # Increment failed count with 15-minute expiry
        await redis_client.incr(lockout_key)
        await redis_client.expire(lockout_key, 900)  # 15 minutes
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is deactivated"
        )

    # Successful login — reset failed attempt counter
    await redis_client.delete(lockout_key)

    token_data = {"sub": user.username, "user_id": user.id}
    return TokenResponse(
        access_token=create_access_token(token_data), refresh_token=create_refresh_token(token_data)
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
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
    return user


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),  # noqa: ARG001  # auth enforced via dependency; identity unused
) -> dict[str, str]:
    """Log out by blacklisting the current access token in Redis."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        redis_client = get_redis()
        await blacklist_token(token, redis_client)
    return {"detail": "Logged out successfully"}
