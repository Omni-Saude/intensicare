"""Tests for alert CRUD endpoints — AUDIT-007 wrapped response + lifecycle."""

from datetime import datetime, timezone

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.api.v1.auth import hash_password
from intensicare.auth.jwt import create_access_token
from intensicare.models.alert import Alert
from intensicare.models.user import User


async def create_test_alert(db: AsyncSession, status="active", severity="watch") -> Alert:
    """Helper to create a test alert."""
    alert = Alert(
        mpi_id="MPI-1001",
        score_id=None,
        severity=severity,
        status=status,
        title=f"Test Alert - {severity}",
        body="Test alert body",
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


class TestListAlerts:
    """Tests for GET /api/v1/alerts (AUDIT-007: {alerts, total} response)."""

    @pytest.mark.asyncio
    async def test_list_active_alerts_wrapped(self, client: AsyncClient, db_session: AsyncSession):
        """Should return {alerts, total} instead of bare array."""
        await create_test_alert(db_session, status="active", severity="watch")
        await create_test_alert(db_session, status="acknowledged", severity="urgent")

        response = await client.get("/api/v1/alerts?status=active")

        assert response.status_code == 200
        data = response.json()
        # AUDIT-007: response is {alerts, total}, not bare array
        assert "alerts" in data
        assert "total" in data
        assert isinstance(data["alerts"], list)
        assert isinstance(data["total"], int)
        assert data["total"] >= 1
        assert all(a["status"] == "active" for a in data["alerts"])

    @pytest.mark.asyncio
    async def test_list_alerts_with_mpi_filter(self, client: AsyncClient, db_session: AsyncSession):
        """Should filter by mpi_id and return wrapped shape."""
        await create_test_alert(db_session, status="active")

        response = await client.get("/api/v1/alerts?status=active&mpi_id=MPI-1001")

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert data["total"] >= 1
        assert all(a["mpi_id"] == "MPI-1001" for a in data["alerts"])

    @pytest.mark.asyncio
    async def test_list_alerts_empty(self, client: AsyncClient):
        """Should return {alerts: [], total: 0} when no alerts."""
        response = await client.get("/api/v1/alerts?status=active")

        assert response.status_code == 200
        data = response.json()
        assert data == {"alerts": [], "total": 0}

    @pytest.mark.asyncio
    async def test_list_alerts_respects_limit(self, client: AsyncClient, db_session: AsyncSession):
        """Should respect the limit parameter."""
        for i in range(5):
            alert = Alert(
                mpi_id=f"MPI-{1000 + i}",
                severity="watch",
                status="active",
                title=f"Alert {i}",
                body="test",
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(alert)
        await db_session.flush()

        response = await client.get("/api/v1/alerts?status=active&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["alerts"]) <= 2
        # total should be the unfiltered count
        assert data["total"] >= 5


class TestAcknowledgeAlert:
    """Tests for POST /api/v1/alerts/{alert_id}/acknowledge."""

    @pytest.mark.asyncio
    async def test_acknowledge_requires_auth(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 401 without auth."""
        alert = await create_test_alert(db_session)

        response = await client.post(f"/api/v1/alerts/{alert.id}/acknowledge")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_acknowledge_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 404 for non-existent alert."""
        user = User(
            username="nurse",
            email="nurse@test.com",
            hashed_password=hash_password("nurse1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            "/api/v1/alerts/99999/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_acknowledge_already_acknowledged(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Should return 409 if already acknowledged."""
        alert = await create_test_alert(db_session, status="acknowledged")
        user = User(
            username="nurse",
            email="nurse@test.com",
            hashed_password=hash_password("nurse1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_acknowledge_success(self, client: AsyncClient, db_session: AsyncSession):
        """Should successfully acknowledge an active alert."""
        alert = await create_test_alert(db_session, status="active")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/acknowledge",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "acknowledged"
        assert data["acknowledged_by"] == "doctor"
        assert data["acknowledged_at"] is not None


class TestResolveAlert:
    """Tests for POST /api/v1/alerts/{alert_id}/resolve (lifecycle)."""

    @pytest.mark.asyncio
    async def test_resolve_requires_auth(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 401 without auth."""
        alert = await create_test_alert(db_session, status="acknowledged")

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/resolve",
            json={"resolution": "true_positive"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_resolve_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 404 for non-existent alert."""
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            "/api/v1/alerts/99999/resolve",
            json={"resolution": "true_positive"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_resolve_success_acknowledged(self, client: AsyncClient, db_session: AsyncSession):
        """Should resolve an acknowledged alert."""
        alert = await create_test_alert(db_session, status="acknowledged")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/resolve",
            json={"resolution": "true_positive"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolution"] == "true_positive"
        assert data["resolved_at"] is not None

    @pytest.mark.asyncio
    async def test_resolve_invalid_resolution(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 422 for invalid resolution value."""
        alert = await create_test_alert(db_session, status="acknowledged")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/resolve",
            json={"resolution": "bad_value"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_resolve_already_resolved(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 409 if already resolved."""
        alert = await create_test_alert(db_session, status="resolved")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/resolve",
            json={"resolution": "true_positive"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_resolve_from_active_invalid(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 409 — cannot resolve directly from active."""
        alert = await create_test_alert(db_session, status="active")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/resolve",
            json={"resolution": "true_positive"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409


class TestEscalateAlert:
    """Tests for POST /api/v1/alerts/{alert_id}/escalate (lifecycle)."""

    @pytest.mark.asyncio
    async def test_escalate_requires_auth(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 401 without auth."""
        alert = await create_test_alert(db_session, status="active")

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/escalate",
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_escalate_not_found(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 404 for non-existent alert."""
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            "/api/v1/alerts/99999/escalate",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_escalate_success_from_active(self, client: AsyncClient, db_session: AsyncSession):
        """Should escalate an active alert."""
        alert = await create_test_alert(db_session, status="active")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/escalate",
            json={"reason": "Patient deteriorating rapidly"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "escalated"

    @pytest.mark.asyncio
    async def test_escalate_success_from_acknowledged(self, client: AsyncClient, db_session: AsyncSession):
        """Should escalate an acknowledged alert."""
        alert = await create_test_alert(db_session, status="acknowledged")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/escalate",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "escalated"

    @pytest.mark.asyncio
    async def test_escalate_already_resolved(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 409 if already resolved."""
        alert = await create_test_alert(db_session, status="resolved")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/escalate",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_escalate_already_escalated(self, client: AsyncClient, db_session: AsyncSession):
        """Should return 409 if already escalated."""
        alert = await create_test_alert(db_session, status="escalated")
        user = User(
            username="doctor",
            email="doctor@test.com",
            hashed_password=hash_password("doctor1234"),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(user)
        await db_session.flush()
        token = create_access_token({"sub": user.username, "user_id": user.id})

        response = await client.post(
            f"/api/v1/alerts/{alert.id}/escalate",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409


class TestTraceAlert:
    """Tests for GET /api/v1/alerts/{alert_id}/trace."""

    @pytest.mark.asyncio
    async def test_trace_alert_success(self, client: AsyncClient, db_session: AsyncSession):
        """Should return alert details."""
        alert = await create_test_alert(db_session)

        response = await client.get(f"/api/v1/alerts/{alert.id}/trace")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == alert.id
        assert data["mpi_id"] == alert.mpi_id
        assert data["severity"] == alert.severity
        assert data["status"] == alert.status

    @pytest.mark.asyncio
    async def test_trace_alert_not_found(self, client: AsyncClient):
        """Should return 404 for non-existent alert."""
        response = await client.get("/api/v1/alerts/99999/trace")

        assert response.status_code == 404
