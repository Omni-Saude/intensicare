"""ABAC enforcement tests for the clinical routers.

Fix RBAC audit finding Dim A/C: granular ABAC (auth/abac.py's
``_ABAC_POLICY_MATRIX`` + ``require_abac``) existed but had zero call-sites
outside ``api/v1/admin.py`` — clinical data (vitals, alerts, pathways,
dashboard/patient-detail) was reachable by *any* authenticated user
regardless of clinical role. This suite proves the matrix is now actually
enforced on those four routers, without granting or revoking any policy —
only exercising what ``_ABAC_POLICY_MATRIX`` already defines.

Endpoint -> ResourceType/Action -> what's asserted:
  POST /api/v1/vitals                                  VITALS/WRITE
  GET  /api/v1/alerts                                   ALERTS/READ
  POST /api/v1/alerts/{id}/acknowledge                  ALERTS/ACKNOWLEDGE
  GET  /api/v1/dashboard                                DASHBOARD/READ
  GET  /api/v1/patients/{mpi}/detail                    PATIENT_DEMOGRAPHICS/READ
  GET  /api/v1/pathways                                 VITALS/READ  (*)
  POST /api/v1/patients/{mpi}/pathways                  VITALS/WRITE (*)

  (*) ResourceType.PATHWAY does not exist in the matrix (auth/abac.py is out
      of scope for this change) — pathways.py documents ResourceType.VITALS
      as the nearest semantic analog. See the comment block in
      ``api/v1/pathways.py`` above ``_PATHWAY_RESOURCE``.

Golden rule under test: legitimate clinical roles keep the access the
matrix already grants them (medico/enfermeiro can still write vitals,
enfermeiro can still acknowledge alerts, VIEWER/readonly keeps reading the
bed-grid dashboard) — this is enforcement of the existing matrix, not new
policy.
"""

from __future__ import annotations

from datetime import datetime, timezone

from httpx import AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.api.v1.auth import hash_password
from intensicare.auth.jwt import create_access_token
from intensicare.models.alert import Alert
from intensicare.models.user import User
from intensicare.services.pathway_definitions_sync import sync_pathway_definitions
from intensicare.services.trilhas_engine import TrilhasEngine

pytestmark = pytest.mark.asyncio

# ═══════════════════════════════════════════════════════════════════════════
# Helpers / fixtures
# ═══════════════════════════════════════════════════════════════════════════

VALID_VITALS_PAYLOAD = {
    "mpi_id": "MPI-ABAC-001",
    "recorded_at": "2026-07-12T10:00:00Z",
    "heart_rate": 82,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "temperature": 36.8,
    "spo2": 98,
    "respiratory_rate": 15,
    "avpu": "A",
}

VENTILACAO_PATHWAY_ID = 1  # synced from _work/alerts/pathways/*.yaml


async def _user_headers(
    db_session: AsyncSession,
    *,
    username: str,
    role: str,
    is_admin: bool = False,
) -> dict[str, str]:
    """Create a real user with a given clinical ``role`` and return a bearer header.

    Mirrors ``conftest.py``'s ``_create_user_and_headers`` but additionally
    sets ``role`` — the field ``require_abac`` actually reads (via
    ``ROLE_ALIASES``), which the shared conftest helper does not set.
    """
    user = User(
        username=username,
        email=f"{username}@abac-test.intensicare.io",
        hashed_password=hash_password("test-fixture-secret"),
        display_name=username,
        is_admin=is_admin,
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def medico_headers(db_session: AsyncSession) -> dict[str, str]:
    return await _user_headers(db_session, username="dr-abac", role="medico")


@pytest_asyncio.fixture
async def enfermeiro_headers(db_session: AsyncSession) -> dict[str, str]:
    return await _user_headers(db_session, username="nurse-abac", role="enfermeiro")


@pytest_asyncio.fixture
async def farmacia_headers(db_session: AsyncSession) -> dict[str, str]:
    return await _user_headers(db_session, username="pharm-abac", role="farmacia")


@pytest_asyncio.fixture
async def readonly_headers(db_session: AsyncSession) -> dict[str, str]:
    return await _user_headers(db_session, username="viewer-abac", role="readonly")


@pytest_asyncio.fixture
async def admin_headers_role(db_session: AsyncSession) -> dict[str, str]:
    """Admin with role='admin' (distinct from conftest's ``admin_headers``,
    which sets ``is_admin=True`` but leaves ``role`` at its default
    'readonly' — insufficient for ABAC, which reads ``role``, not
    ``is_admin``)."""
    return await _user_headers(db_session, username="admin-abac", role="admin", is_admin=True)


async def _create_test_alert(db: AsyncSession, *, status: str = "active") -> Alert:
    alert = Alert(
        mpi_id="MPI-ABAC-ALERT-001",
        score_id=None,
        severity="watch",
        status=status,
        title="ABAC test alert",
        body="body",
        created_at=datetime.now(timezone.utc),
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


@pytest_asyncio.fixture
async def synced_pathways(db_session: AsyncSession) -> TrilhasEngine:
    """Sync the real YAML pathway catalog into the test DB (same production
    path used at boot) so POST /patients/{mpi}/pathways has a real pathway
    to enroll into."""
    engine = TrilhasEngine()
    report = await sync_pathway_definitions(db_session, engine)
    assert not report.failed, f"pathway sync failures: {report.failed}"
    return engine


async def _post_acknowledge_expect_authorized(
    client: AsyncClient, alert_id: int, headers: dict[str, str]
) -> None:
    """POST .../acknowledge and assert the caller got PAST the ABAC gate.

    ``acknowledge_alert`` (api/v1/alerts.py) has a pre-existing, unrelated
    bug: ``db.refresh(alert)`` after ``flush()`` drops the
    ``joinedload(Alert.patient)`` eager-load state (a well-known SQLAlchemy
    ``refresh()`` gotcha), and ``Alert.patient`` is declared
    ``lazy="raise"`` (models/alert.py) — so the response serializer's
    ``alert.patient`` access then raises ``InvalidRequestError``. This
    predates this change (the same failure is what makes
    ``tests/test_alerts.py::TestAcknowledgeAlert::test_acknowledge_success``
    flaky/failing on this branch already) and fixing it is out of scope for
    an ABAC-enforcement change.

    What this helper actually proves: an authorized role reaches that
    downstream code at all. ``require_abac`` runs before any of it — a
    denied role gets a clean ``ABACAccessDenied`` -> 403 and never gets
    close to ``db.refresh``. So "raises InvalidRequestError" here is
    evidence of *authorization succeeding*, distinguishable from
    ABAC-denial (403, a normal HTTP response, no exception) by construction.
    """
    try:
        response = await client.post(f"/api/v1/alerts/{alert_id}/acknowledge", headers=headers)
    except InvalidRequestError as exc:
        assert "lazy" in str(exc), f"unexpected InvalidRequestError: {exc}"
        return
    assert response.status_code == 200, response.text


def _assert_clean_403(response) -> None:
    """403 responses must be the global ABACAccessDenied handler's clean
    body — no stack trace, no internals, just {"detail": "..."}"""
    assert response.status_code == 403
    body = response.json()
    assert set(body.keys()) == {"detail"}
    assert isinstance(body["detail"], str)
    assert "ABAC denied" in body["detail"]


# ═══════════════════════════════════════════════════════════════════════════
# POST /api/v1/vitals — ResourceType.VITALS / Action.WRITE
# ═══════════════════════════════════════════════════════════════════════════


class TestVitalsABAC:
    async def test_readonly_cannot_post_vitals(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/api/v1/vitals", json=VALID_VITALS_PAYLOAD, headers=readonly_headers
        )
        _assert_clean_403(response)

    async def test_medico_can_post_vitals(
        self, client: AsyncClient, medico_headers: dict[str, str]
    ) -> None:
        response = await client.post(
            "/api/v1/vitals", json=VALID_VITALS_PAYLOAD, headers=medico_headers
        )
        assert response.status_code == 201

    async def test_enfermeiro_can_post_vitals(
        self, client: AsyncClient, enfermeiro_headers: dict[str, str]
    ) -> None:
        """Golden rule: nurses chart vitals — matrix grants NURSE VITALS/WRITE."""
        payload = {**VALID_VITALS_PAYLOAD, "mpi_id": "MPI-ABAC-002"}
        response = await client.post("/api/v1/vitals", json=payload, headers=enfermeiro_headers)
        assert response.status_code == 201

    async def test_farmacia_cannot_post_vitals(
        self, client: AsyncClient, farmacia_headers: dict[str, str]
    ) -> None:
        """Pharmacist has no VITALS policy at all in the matrix."""
        response = await client.post(
            "/api/v1/vitals", json=VALID_VITALS_PAYLOAD, headers=farmacia_headers
        )
        _assert_clean_403(response)

    async def test_admin_can_post_vitals(
        self, client: AsyncClient, admin_headers_role: dict[str, str]
    ) -> None:
        payload = {**VALID_VITALS_PAYLOAD, "mpi_id": "MPI-ABAC-003"}
        response = await client.post("/api/v1/vitals", json=payload, headers=admin_headers_role)
        assert response.status_code == 201


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/alerts, POST /{id}/acknowledge — ResourceType.ALERTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAlertsABAC:
    async def test_readonly_can_list_alerts(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        """VIEWER has ALERTS/READ in the matrix."""
        response = await client.get("/api/v1/alerts", headers=readonly_headers)
        assert response.status_code == 200

    async def test_readonly_cannot_acknowledge_alert(
        self, client: AsyncClient, db_session: AsyncSession, readonly_headers: dict[str, str]
    ) -> None:
        alert = await _create_test_alert(db_session)
        response = await client.post(
            f"/api/v1/alerts/{alert.id}/acknowledge", headers=readonly_headers
        )
        _assert_clean_403(response)

    async def test_enfermeiro_can_acknowledge_alert(
        self, client: AsyncClient, db_session: AsyncSession, enfermeiro_headers: dict[str, str]
    ) -> None:
        """Task spec: 'enfermeiro acknowledge alert -> conforme matriz' — NURSE
        has ALERTS/ACKNOWLEDGE."""
        alert = await _create_test_alert(db_session)
        await _post_acknowledge_expect_authorized(client, alert.id, enfermeiro_headers)

    async def test_farmacia_cannot_acknowledge_alert(
        self, client: AsyncClient, db_session: AsyncSession, farmacia_headers: dict[str, str]
    ) -> None:
        """Pharmacist has ALERTS/READ only (no ACKNOWLEDGE) in the matrix."""
        alert = await _create_test_alert(db_session)
        response = await client.post(
            f"/api/v1/alerts/{alert.id}/acknowledge", headers=farmacia_headers
        )
        _assert_clean_403(response)

    async def test_admin_can_acknowledge_alert(
        self, client: AsyncClient, db_session: AsyncSession, admin_headers_role: dict[str, str]
    ) -> None:
        alert = await _create_test_alert(db_session)
        await _post_acknowledge_expect_authorized(client, alert.id, admin_headers_role)


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/dashboard, GET /api/v1/patients/{mpi}/detail
# ═══════════════════════════════════════════════════════════════════════════


class TestDashboardABAC:
    async def test_readonly_can_read_dashboard(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        """VIEWER is the 'telão' (big-screen) role — must keep DASHBOARD/READ."""
        response = await client.get("/api/v1/dashboard", headers=readonly_headers)
        assert response.status_code == 200

    async def test_medico_can_read_dashboard(
        self, client: AsyncClient, medico_headers: dict[str, str]
    ) -> None:
        response = await client.get("/api/v1/dashboard", headers=medico_headers)
        assert response.status_code == 200

    async def test_readonly_cannot_read_patient_detail(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        """VIEWER lacks PATIENT_DEMOGRAPHICS — bed-grid access does not imply
        per-patient PHI drill-down access."""
        response = await client.get(
            "/api/v1/patients/MPI-DOES-NOT-EXIST/detail", headers=readonly_headers
        )
        _assert_clean_403(response)

    async def test_medico_patient_detail_not_blocked_by_abac(
        self, client: AsyncClient, medico_headers: dict[str, str]
    ) -> None:
        """PHYSICIAN has PATIENT_DEMOGRAPHICS/READ — ABAC must not be the
        reason a lookup on a nonexistent patient fails (a clean 404, not a
        403, proves the ABAC gate passed through to the business logic)."""
        response = await client.get(
            "/api/v1/patients/MPI-DOES-NOT-EXIST/detail", headers=medico_headers
        )
        assert response.status_code == 404

    async def test_farmacia_cannot_read_patient_detail(
        self, client: AsyncClient, farmacia_headers: dict[str, str]
    ) -> None:
        """Pharmacist has no PATIENT_DEMOGRAPHICS policy."""
        response = await client.get(
            "/api/v1/patients/MPI-DOES-NOT-EXIST/detail", headers=farmacia_headers
        )
        _assert_clean_403(response)

    async def test_admin_dashboard_and_detail_not_blocked(
        self, client: AsyncClient, admin_headers_role: dict[str, str]
    ) -> None:
        dash = await client.get("/api/v1/dashboard", headers=admin_headers_role)
        assert dash.status_code == 200
        detail = await client.get(
            "/api/v1/patients/MPI-DOES-NOT-EXIST/detail", headers=admin_headers_role
        )
        assert detail.status_code == 404  # not found, not 403


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/pathways, POST /api/v1/patients/{mpi}/pathways
# ResourceType.VITALS (documented nearest analog — see pathways.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestPathwaysABAC:
    async def test_readonly_cannot_list_pathway_catalog(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        """VIEWER has no VITALS policy — catalog reads are now gated (a
        behavior change from the prior zero-enforcement state, expected)."""
        response = await client.get("/api/v1/pathways", headers=readonly_headers)
        _assert_clean_403(response)

    async def test_medico_can_list_pathway_catalog(
        self, client: AsyncClient, medico_headers: dict[str, str]
    ) -> None:
        response = await client.get("/api/v1/pathways", headers=medico_headers)
        assert response.status_code == 200

    async def test_readonly_cannot_enroll_patient(
        self, client: AsyncClient, readonly_headers: dict[str, str]
    ) -> None:
        body = {"pathway_id": VENTILACAO_PATHWAY_ID, "encounter_id": "ENC-ABAC-RO"}
        response = await client.post(
            "/api/v1/patients/MPI-ABAC-PATHWAY-01/pathways",
            json=body,
            headers=readonly_headers,
        )
        _assert_clean_403(response)

    async def test_medico_can_enroll_patient(
        self,
        client: AsyncClient,
        medico_headers: dict[str, str],
        synced_pathways: TrilhasEngine,
    ) -> None:
        body = {"pathway_id": VENTILACAO_PATHWAY_ID, "encounter_id": "ENC-ABAC-MED"}
        response = await client.post(
            "/api/v1/patients/MPI-ABAC-PATHWAY-02/pathways",
            json=body,
            headers=medico_headers,
        )
        assert response.status_code == 201

    async def test_enfermeiro_can_enroll_patient(
        self,
        client: AsyncClient,
        enfermeiro_headers: dict[str, str],
        synced_pathways: TrilhasEngine,
    ) -> None:
        """Golden rule: the VITALS-analog mapping must not strip nurses of
        pathway-enrollment access they have in real ICU workflows."""
        body = {"pathway_id": VENTILACAO_PATHWAY_ID, "encounter_id": "ENC-ABAC-NURSE"}
        response = await client.post(
            "/api/v1/patients/MPI-ABAC-PATHWAY-03/pathways",
            json=body,
            headers=enfermeiro_headers,
        )
        assert response.status_code == 201

    async def test_admin_can_enroll_patient(
        self,
        client: AsyncClient,
        admin_headers_role: dict[str, str],
        synced_pathways: TrilhasEngine,
    ) -> None:
        body = {"pathway_id": VENTILACAO_PATHWAY_ID, "encounter_id": "ENC-ABAC-ADMIN"}
        response = await client.post(
            "/api/v1/patients/MPI-ABAC-PATHWAY-04/pathways",
            json=body,
            headers=admin_headers_role,
        )
        assert response.status_code == 201
