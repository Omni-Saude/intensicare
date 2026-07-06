"""
Tests for authentication dependencies: get_current_user and require_admin.

Covers:
  - JWT token validation and user resolution
  - Token blacklist enforcement
  - Admin privilege gate
  - IAM fallback paths (when iam_enabled=False)
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from intensicare.api.v1.auth import hash_password
from intensicare.auth.dependencies import get_current_user, require_admin
from intensicare.auth.jwt import create_access_token
from intensicare.models.user import User


# ─── Test helpers ────────────────────────────────────────────────────────────


def _make_cred(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _make_user(username: str = "testuser", is_admin: bool = False) -> User:
    return User(
        id=1,
        username=username,
        email=f"{username}@intensicare.io",
        hashed_password=hash_password("secret1234"),
        display_name=username,
        is_admin=is_admin,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )


# ─── get_current_user tests ──────────────────────────────────────────────────


class TestGetCurrentUser:
    """Tests for the get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_valid_jwt_returns_user(self, db_session):
        """A valid JWT token should resolve the corresponding user from the DB."""
        user = _make_user(username="nurse_jane")
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": "nurse_jane", "user_id": user.id})
        cred = _make_cred(token)

        with patch(
            "intensicare.auth.dependencies.is_token_blacklisted",
            new_callable=AsyncMock,
        ) as mock_blacklisted:
            mock_blacklisted.return_value = False
            result = await get_current_user(credentials=cred, db=db_session)
            assert result.username == "nurse_jane"
            assert result.id == user.id

    @pytest.mark.asyncio
    async def test_blacklisted_token_raises_401(self, db_session):
        """A blacklisted token must raise 401 Unauthorized."""
        token = create_access_token({"sub": "nurse_jane", "user_id": 1})
        cred = _make_cred(token)

        with patch(
            "intensicare.auth.dependencies.is_token_blacklisted",
            new_callable=AsyncMock,
        ) as mock_blacklisted:
            mock_blacklisted.return_value = True
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=cred, db=db_session)
            assert exc_info.value.status_code == 401
            assert "revoked" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self, db_session):
        """An invalid (garbage) token must raise 401."""
        cred = _make_cred("invalid_token_garbage")

        with patch(
            "intensicare.auth.dependencies.is_token_blacklisted",
            new_callable=AsyncMock,
        ) as mock_blacklisted:
            mock_blacklisted.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=cred, db=db_session)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_user_not_in_db_raises_401(self, db_session):
        """A valid token whose subject does not match any DB user must raise 401."""
        token = create_access_token({"sub": "ghost_user", "user_id": 999})
        cred = _make_cred(token)

        with patch(
            "intensicare.auth.dependencies.is_token_blacklisted",
            new_callable=AsyncMock,
        ) as mock_blacklisted:
            mock_blacklisted.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=cred, db=db_session)
            assert exc_info.value.status_code == 401
            assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_inactive_user_raises_401(self, db_session):
        """A disabled user account must result in 401."""
        user = _make_user(username="inactive_user")
        user.is_active = False
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": "inactive_user", "user_id": user.id})
        cred = _make_cred(token)

        with patch(
            "intensicare.auth.dependencies.is_token_blacklisted",
            new_callable=AsyncMock,
        ) as mock_blacklisted:
            mock_blacklisted.return_value = False
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials=cred, db=db_session)
            assert exc_info.value.status_code == 401


# ─── require_admin tests ─────────────────────────────────────────────────────


class TestRequireAdmin:
    """Tests for the require_admin dependency."""

    def test_admin_user_passes(self):
        """An admin user should pass the admin gate."""
        admin = _make_user(username="admin_user", is_admin=True)
        result = require_admin(current_user=admin)
        assert result is admin

    def test_non_admin_user_raises_403(self):
        """A non-admin user must raise 403 Forbidden."""
        nurse = _make_user(username="nurse", is_admin=False)
        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=nurse)
        assert exc_info.value.status_code == 403
        assert "admin" in str(exc_info.value.detail).lower()


# ─── IAM fallback tests ──────────────────────────────────────────────────────


class TestGetCurrentUserWithIAM:
    """Tests that the IAM identity path is exercised when `iam_enabled` is True."""

    @pytest.mark.asyncio
    async def test_iam_enabled_resolves_via_iam(self, db_session):
        """When iam_enabled=True, the IAM validate_iam_token path is tried first."""
        user = _make_user(username="iam_user")
        db_session.add(user)
        await db_session.flush()

        token = "fake-iam-token"
        cred = _make_cred(token)

        mock_identity = MagicMock()
        mock_identity.username = "iam_user"

        with patch(
            "intensicare.auth.dependencies.settings.iam_enabled", True
        ), patch(
            "intensicare.auth.dependencies.validate_iam_token",
            new_callable=AsyncMock,
        ) as mock_validate:
            mock_validate.return_value = mock_identity
            result = await get_current_user(credentials=cred, db=db_session)
            assert result.username == "iam_user"
            mock_validate.assert_awaited_once_with(token)

    @pytest.mark.asyncio
    async def test_iam_fails_falls_back_to_jwt(self, db_session):
        """When IAM validation fails, the dependency falls back to JWT."""
        user = _make_user(username="jwt_fallback_user")
        db_session.add(user)
        await db_session.flush()

        jwt_token = create_access_token({"sub": "jwt_fallback_user", "user_id": user.id})
        cred = _make_cred(jwt_token)

        with patch(
            "intensicare.auth.dependencies.settings.iam_enabled", True
        ), patch(
            "intensicare.auth.dependencies.validate_iam_token",
            new_callable=AsyncMock,
        ) as mock_validate:
            mock_validate.side_effect = Exception("IAM unavailable")

            with patch(
                "intensicare.auth.dependencies.is_token_blacklisted",
                new_callable=AsyncMock,
            ) as mock_blacklisted:
                mock_blacklisted.return_value = False
                result = await get_current_user(credentials=cred, db=db_session)
                assert result.username == "jwt_fallback_user"
