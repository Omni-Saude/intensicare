"""Admin API endpoints — user CRUD (admin-only).

Endpoints:
  GET  /admin/users        — list all users with roles
  POST /admin/users        — create new user (admin only)
  PUT  /admin/users/{id}   — update user role/status
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import require_admin
from intensicare.core.database import get_db
from intensicare.models.audit_trail import AuditTrail
from intensicare.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

USERNAME_MIN_LENGTH = 3
PASSWORD_MIN_LENGTH = 8


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class UserOut(BaseModel):
    """Public-safe user representation."""

    id: int
    username: str
    email: str
    display_name: str | None
    is_admin: bool
    is_active: bool
    created_at: str | None = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Wrapped list response for users."""

    users: list[UserOut]
    total: int


class UserCreate(BaseModel):
    """Request body for creating a user."""

    username: str = Field(..., min_length=USERNAME_MIN_LENGTH, max_length=64)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    display_name: str | None = Field(None, max_length=255)
    is_admin: bool = False
    is_active: bool = True

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


class UserUpdate(BaseModel):
    """Partial update for a user (role, status, display name)."""

    display_name: str | None = Field(None, max_length=255)
    is_admin: bool | None = None
    is_active: bool | None = None
    email: str | None = Field(None, max_length=255)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _user_to_out(user: User) -> UserOut:
    """Convert a User ORM instance to a UserOut schema."""
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


async def _get_user_or_404(session: AsyncSession, user_id: int) -> User:
    """Fetch a user by ID or raise 404."""
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found",
        )
    return user


async def _write_audit(
    session: AsyncSession,
    *,
    action: str,
    target_user: User,
    actor: str,
    before_state: bytes | None = None,
    after_state: bytes | None = None,
    request_id: str | None = None,
) -> None:
    """Create an audit trail entry for user admin mutations."""
    entry = AuditTrail(
        event_ts=datetime.now(timezone.utc),
        tenant_id="default",
        actor=actor,
        action=action,
        entity_table="users",
        entity_id=str(target_user.id),
        before_state=before_state,
        after_state=after_state,
        request_id=request_id,
    )
    session.add(entry)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List all users",
    dependencies=[Depends(require_admin)],
)
async def list_users(
    session: AsyncSession = Depends(get_db),
) -> UserListResponse:
    """List all registered users with their roles and statuses (admin-only)."""
    result = await session.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return UserListResponse(
        users=[_user_to_out(u) for u in users],
        total=len(users),
    )


@router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    body: UserCreate,
    session: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
    request: Request = None,  # type: ignore[assignment]  # noqa: ARG001
) -> UserOut:
    """Create a new user (admin-only)."""
    # Check for duplicate username
    result = await session.execute(
        select(User).where(User.username == body.username)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # Check for duplicate email
    result = await session.execute(
        select(User).where(User.email == body.email)
    )
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=_hash_password(body.password),
        display_name=body.display_name or body.username,
        is_admin=body.is_admin,
        is_active=body.is_active,
        created_at=datetime.now(timezone.utc),
    )
    session.add(user)
    await session.flush()  # flush to generate the ID

    # Audit
    after_state = json.dumps(
        {
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
        },
        default=str,
    ).encode()
    req_id = request.headers.get("x-request-id") if request else None
    await _write_audit(
        session,
        action="user.create",
        target_user=user,
        actor=current_admin.username,
        after_state=after_state,
        request_id=req_id,
    )

    await session.commit()
    await session.refresh(user)
    return _user_to_out(user)


@router.put(
    "/users/{user_id}",
    response_model=UserOut,
    summary="Update user role/status",
)
async def update_user(
    user_id: int,
    body: UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_admin: User = Depends(require_admin),
    request: Request = None,  # type: ignore[assignment]  # noqa: ARG001
) -> UserOut:
    """Update a user's role, active status, or display name (admin-only)."""
    user = await _get_user_or_404(session, user_id)

    # Serialize before-state for audit
    before_state = json.dumps(
        {
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
        },
        default=str,
    ).encode()

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(user, field, value)

    # Audit
    after_state = json.dumps(
        {
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
        },
        default=str,
    ).encode()
    req_id = request.headers.get("x-request-id") if request else None

    await session.flush()
    await _write_audit(
        session,
        action="user.update",
        target_user=user,
        actor=current_admin.username,
        before_state=before_state,
        after_state=after_state,
        request_id=req_id,
    )

    await session.commit()
    await session.refresh(user)
    return _user_to_out(user)
