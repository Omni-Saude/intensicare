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


async def _reader_headers(db: AsyncSession, username: str = "alerts-reader") -> dict[str, str]:
    """Auth headers for a role='readonly' user — VIEWER has ALERTS/READ in the
    ABAC matrix (see test_abac_clinical.py::test_readonly_can_list_alerts,
    and TestAlertsPHIDecryption's _phi_reader_headers below, same pattern)."""
    user = User(
        username=username,
        email=f"{username}@test.com",
        hashed_password=hash_password("test-fixture-secret"),
        role="readonly",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


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

    @pytest.mark.asyncio
    async def test_list_alerts_status_resolved_filters_only_resolved(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """BUG-F5-01: status=resolved should return only resolved alerts —
        before the fix, `status` was declared but the frontend's non-"active"
        values were the ones silently dropped from visibility; this pins the
        expanded status contract (active/acknowledged/escalated/resolved/all)
        for the case that matters most for audit trail: resolved alerts."""
        await create_test_alert(db_session, status="active", severity="watch")
        await create_test_alert(db_session, status="acknowledged", severity="urgent")
        await create_test_alert(db_session, status="resolved", severity="critical")
        headers = await _reader_headers(db_session, "reader-resolved")

        response = await client.get("/api/v1/alerts?status=resolved", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["mpi_id"] == "MPI-1001"

    @pytest.mark.asyncio
    async def test_list_alerts_status_all_returns_all_statuses(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """BUG-F5-01: status=all must apply no status predicate — this is the
        escape hatch that lets the Alerts page (or an auditor) see the full
        lifecycle instead of only the default active-only view."""
        mpi = "MPI-STATUS-ALL"
        for i, alert_status in enumerate(["active", "acknowledged", "escalated", "resolved"]):
            alert = Alert(
                mpi_id=mpi,
                score_id=None,
                severity="watch",
                status=alert_status,
                title=f"All-status alert {i}",
                body="test",
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(alert)
        await db_session.flush()
        headers = await _reader_headers(db_session, "reader-all")

        response = await client.get(
            f"/api/v1/alerts?status=all&mpi_id={mpi}&limit=200", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 4
        assert {a["mpi_id"] for a in data["items"]} == {mpi}
        # only the default (status=active) would have returned 1; all=4 proves
        # the predicate was actually dropped, not just widened.

    @pytest.mark.asyncio
    async def test_list_alerts_severity_critical_filters(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """BUG-F5-01: severity=critical should filter Alert.severity — this
        query param did not exist before the fix and was silently ignored
        by FastAPI."""
        mpi = "MPI-SEVERITY-CRIT"
        for sev in ["normal", "watch", "urgent", "critical"]:
            alert = Alert(
                mpi_id=mpi,
                score_id=None,
                severity=sev,
                status="active",
                title=f"Severity alert {sev}",
                body="test",
                created_at=datetime.now(timezone.utc),
            )
            db_session.add(alert)
        await db_session.flush()
        headers = await _reader_headers(db_session, "reader-severity")

        response = await client.get(
            f"/api/v1/alerts?status=active&severity=critical&mpi_id={mpi}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_list_alerts_invalid_status_is_422(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """status is Literal-validated (BUG-F5-01 contract) — a value outside
        active/acknowledged/escalated/resolved/all is rejected, not silently
        treated as an empty-result no-op filter."""
        headers = await _reader_headers(db_session, "reader-bad-status")

        response = await client.get("/api/v1/alerts?status=bogus", headers=headers)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_alerts_invalid_severity_is_422(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """severity is Literal-validated against Alert.severity's canonical
        set (normal/watch/urgent/critical) — bad input 422s instead of
        silently matching zero rows."""
        headers = await _reader_headers(db_session, "reader-bad-severity")

        response = await client.get("/api/v1/alerts?severity=bogus", headers=headers)

        assert response.status_code == 422


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
            # role="medico" (PHYSICIAN) — ABAC (auth/abac.py) requires a
            # clinical role granting Action.ACKNOWLEDGE on ResourceType.ALERTS;
            # the User.role default ("readonly" -> VIEWER) is read-only and
            # 403s here since commit cebb239 wired require_abac() into this
            # router. Matches the house convention in conftest.py's
            # user_headers fixture (role="medico").
            role="medico",
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
    async def test_resolve_success_acknowledged(
        self, client: AsyncClient, db_session: AsyncSession
    ):
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
    async def test_escalate_success_from_active(
        self, client: AsyncClient, db_session: AsyncSession
    ):
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
    async def test_escalate_success_from_acknowledged(
        self, client: AsyncClient, db_session: AsyncSession
    ):
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


# ---------------------------------------------------------------------------
# PHI dual-schema — patient_name resolution via pgcrypto (encrypted path)
#
# DRILL: same pattern as test_dashboard.py's
# test_get_dashboard_decrypts_encrypted_display_name — proves the fix for
# the bug where alerts._to_alert_response() did a raw
# ``.decode("utf-8")`` on ``alert.patient.display_name`` instead of routing
# through ``patient_encryption.resolve_display_name`` (pgp_sym_decrypt).
# Against a real pgcrypto-encrypted BYTEA column, the old code produced
# mojibake/garbage or raised UnicodeDecodeError — never the real name.
# ---------------------------------------------------------------------------

TENANT_PHI_ALERTS = "tenant-phi-alerts-test"


async def _ensure_pgcrypto(db: AsyncSession) -> None:
    from sqlalchemy import text

    await db.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA public"))


async def _set_dev_encryption_key(db: AsyncSession, tenant_id: str) -> None:
    """Sets app.encryption_key using the same local DEK derivation dev/test
    uses when no real KMS is configured (KMSEngine._derive_dek_local) —
    the same helper test_dashboard.py's phi_dashboard_session fixture uses."""
    from sqlalchemy import text

    from intensicare.services.kms_keys import KMSEngine

    dek = KMSEngine._derive_dek_local(tenant_id)
    await db.execute(
        text("SELECT set_config('app.encryption_key', :key, false)"),
        {"key": dek.plaintext.hex()},
    )


@pytest.fixture
async def phi_alerts_session(db_session: AsyncSession) -> AsyncSession:
    """Real Postgres session with pgcrypto enabled and the dev-local DEK
    loaded into app.encryption_key for TENANT_PHI_ALERTS."""
    await _ensure_pgcrypto(db_session)
    await _set_dev_encryption_key(db_session, TENANT_PHI_ALERTS)
    return db_session


async def _phi_reader_headers(db: AsyncSession) -> dict[str, str]:
    """Real user with role='readonly' (VIEWER has ALERTS/READ in the ABAC
    matrix, see test_abac_clinical.py::test_readonly_can_list_alerts) plus
    the X-Tenant-ID header matching TENANT_PHI_ALERTS (get_current_tenant_id
    reads X-Tenant-ID with precedence over the IAM/default fallback)."""
    user = User(
        username="phi-alerts-reader",
        email="phi-alerts-reader@test.com",
        hashed_password=hash_password("test-fixture-secret"),
        display_name="phi-alerts-reader",
        role="readonly",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"Authorization": f"Bearer {token}", "X-Tenant-ID": TENANT_PHI_ALERTS}


class TestAlertsPHIDecryption:
    """DRILL: patient_name in alert responses must come back decrypted from
    real pgcrypto ciphertext, not raw bytes / mojibake / a 500."""

    @pytest.mark.asyncio
    async def test_list_alerts_decrypts_encrypted_patient_name(
        self, client: AsyncClient, phi_alerts_session: AsyncSession
    ) -> None:
        from intensicare.models.patient_cache import PatientCache
        from intensicare.services.patient_encryption import encrypt_phi

        plaintext_name = "DEMO Sepse Crítica"
        enc_name = await encrypt_phi(phi_alerts_session, plaintext_name)
        assert isinstance(enc_name, bytes)

        patient = PatientCache(
            mpi_id="MPI-PHI-ALERTS-001",
            tenant_id=TENANT_PHI_ALERTS,
            display_name=enc_name,
            bed_id="B-PHI-01",
            unit="UTI-PHI-ALERTS-TEST",
            is_active=True,
        )
        phi_alerts_session.add(patient)

        alert = Alert(
            mpi_id="MPI-PHI-ALERTS-001",
            score_id=None,
            severity="watch",
            status="active",
            title="PHI decrypt test alert",
            body="body",
            created_at=datetime.now(timezone.utc),
        )
        phi_alerts_session.add(alert)
        await phi_alerts_session.flush()

        headers = await _phi_reader_headers(phi_alerts_session)
        response = await client.get(
            "/api/v1/alerts?status=active&mpi_id=MPI-PHI-ALERTS-001", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        matching = [a for a in data["items"] if a["mpi_id"] == "MPI-PHI-ALERTS-001"]
        assert len(matching) == 1
        assert matching[0]["patient_name"] == plaintext_name

    @pytest.mark.asyncio
    async def test_trace_alert_decrypts_encrypted_patient_name(
        self, client: AsyncClient, phi_alerts_session: AsyncSession
    ) -> None:
        from intensicare.models.patient_cache import PatientCache
        from intensicare.services.patient_encryption import encrypt_phi

        plaintext_name = "DEMO Choque Séptico"
        enc_name = await encrypt_phi(phi_alerts_session, plaintext_name)

        patient = PatientCache(
            mpi_id="MPI-PHI-ALERTS-002",
            tenant_id=TENANT_PHI_ALERTS,
            display_name=enc_name,
            bed_id="B-PHI-02",
            unit="UTI-PHI-ALERTS-TEST",
            is_active=True,
        )
        phi_alerts_session.add(patient)

        alert = Alert(
            mpi_id="MPI-PHI-ALERTS-002",
            score_id=None,
            severity="urgent",
            status="active",
            title="PHI decrypt trace test alert",
            body="body",
            created_at=datetime.now(timezone.utc),
        )
        phi_alerts_session.add(alert)
        await phi_alerts_session.flush()
        await phi_alerts_session.refresh(alert)

        headers = await _phi_reader_headers(phi_alerts_session)
        response = await client.get(f"/api/v1/alerts/{alert.id}/trace", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["patient_name"] == plaintext_name
