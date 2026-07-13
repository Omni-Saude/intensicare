"""E2E: pathway enrollment persistence survives a process "restart".

Sprint 1 patient-safety audit finding: the care-pathway engine used to keep
enrollment/state in an in-memory dict (``trilhas_state.PathwayStore``), which
meant every enrollment was lost on process restart/redeploy — clinically
unacceptable for an ICU pathway tracker. The fix moved enrollment/state onto
Postgres (``pathway_repository`` / ``pathway_enrollment``), with the YAML
pathway *definitions* synced into the DB at boot
(``pathway_definitions_sync.sync_pathway_definitions``).

This module proves the fix actually holds:
  1. An enrollment created via the real ASGI app survives a simulated
     "restart" — a brand-new ``TrilhasEngine`` instance plus a fresh
     boot-time sync run on the *same* DB session (the old process/module
     state is discarded; only the DB persists across the "restart").
  2. Criteria updates / state transitions persist the same way and are
     visible to a subsequent, independent request.
  3. The deprecated in-memory ``trilhas_state.PathwayStore`` is never
     touched anywhere in the enroll → update-criteria → list → progress
     flow.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services import domain_trilhas_engine
from intensicare.services.pathway_definitions_sync import sync_pathway_definitions
from intensicare.services.trilhas_engine import TrilhasEngine

SEPSE_PATHWAY_ID = 2  # _work/alerts/pathways/sepse.yaml -> pathway.id


async def _boot_sync(db_session: AsyncSession) -> TrilhasEngine:
    """Simulate a fresh process boot: a brand-new TrilhasEngine instance plus
    a fresh YAML->DB sync pass, run on the SAME db session/transaction so the
    test can assert the enrollment made before this call is still there
    after it.

    Mirrors exactly what ``intensicare.main.lifespan`` does at real boot
    (see ``TrilhasEngine()`` + ``sync_pathway_definitions`` there) — nothing
    module-level/global is reused across calls, only the DB.
    """
    engine = TrilhasEngine()
    await sync_pathway_definitions(db_session, engine)
    await db_session.flush()
    return engine


class _ExplodingLegacyStore:
    """Sentinel installed in place of the deprecated in-memory PathwayStore
    singleton (``domain_trilhas_engine._default_store``). Raises on ANY
    attribute access, so if the enroll/evaluate/list/progress API flow ever
    touches the legacy store again (a regression back toward in-memory
    state), this fails loudly instead of silently reintroducing the
    restart-survival bug.
    """

    def __getattribute__(self, name: str) -> Any:
        raise AssertionError(
            f"Legacy trilhas_state.PathwayStore was accessed (attribute "
            f"{name!r}) during the pathway API flow — enrollment/state must "
            "be Postgres-backed only (ADR-0020/0021)."
        )


async def test_enrollment_survives_new_engine_and_resync(
    client: httpx.AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
) -> None:
    mpi_id = "MPI-TEST-E2E-PATHWAY-001"

    # ── "Boot 1" — populate pathways/pathway_criteria before enrolling. ──
    await _boot_sync(db_session)

    # ── Enroll via the real ASGI app (POST -> 201). ──
    enroll_resp = await client.post(
        f"/api/v1/patients/{mpi_id}/pathways",
        json={
            "pathway_id": SEPSE_PATHWAY_ID,
            "encounter_id": "ENC-E2E-001",
            "bed_id": "E2E-01",
            "unit": "UTI-E2E",
        },
        headers=admin_headers,
    )
    assert enroll_resp.status_code == 201, enroll_resp.text
    enrolled_body = enroll_resp.json()
    pp_id = enrolled_body["id"]
    assert enrolled_body["current_state"]["id"] == "initial"
    assert enrolled_body["severity"] == "normal"
    assert enrolled_body["status"] == "active"
    pathway_criteria = enrolled_body["pathway"]["criteria"]
    assert pathway_criteria, "Sepse pathway deve ter critérios carregados"

    # ── "Restart" — brand-new TrilhasEngine + fresh sync, same DB session. ──
    # Simulates a new process boot: any in-process/module state from before
    # this point is considered gone. Only Postgres carries state forward.
    restarted_engine = await _boot_sync(db_session)
    assert restarted_engine.get_pathway(SEPSE_PATHWAY_ID) is not None

    # ── A brand-new request must still see the enrollment, state intact. ──
    list_resp = await client.get(
        f"/api/v1/patients/{mpi_id}/pathways",
        headers=admin_headers,
    )
    assert list_resp.status_code == 200
    items = list_resp.json()["items"]
    matches = [it for it in items if it["id"] == pp_id]
    assert len(matches) == 1, f"enrollment {pp_id} not found after restart: {items}"
    survived = matches[0]
    assert survived["mpi_id"] == mpi_id
    assert survived["pathway"]["id"] == SEPSE_PATHWAY_ID
    assert survived["current_state"]["id"] == "initial"
    assert survived["severity"] == "normal"
    assert survived["status"] == "active"

    # ── Drive a criteria update (all criteria met) -> forces a state ──
    # transition; confirms transitions persist across the "restart" too.
    update_resp = await client.put(
        f"/api/v1/patients/{mpi_id}/pathways/{pp_id}/criteria",
        json={"criteria": [{"id": c["id"], "met": True, "value": "1"} for c in pathway_criteria]},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200, update_resp.text
    updated_body = update_resp.json()
    assert updated_body["current_state"]["id"] == "confirmacao"
    assert updated_body["severity"] == "critical"

    # ── Progress endpoint reflects the persisted transition history. ──
    progress_resp = await client.get(
        f"/api/v1/patients/{mpi_id}/pathways/{pp_id}/progress",
        headers=admin_headers,
    )
    assert progress_resp.status_code == 200
    progress = progress_resp.json()
    assert progress["current_state"]["id"] == "confirmacao"
    assert progress["criteria_summary"]["total"] == len(pathway_criteria)
    assert progress["criteria_summary"]["met"] == len(pathway_criteria)
    assert progress["criteria_summary"]["not_met"] == 0
    history = progress["state_history"]
    assert len(history) == 1
    assert history[0]["from_state"] == "initial"
    assert history[0]["to_state"] == "confirmacao"


async def test_pathway_flow_never_touches_legacy_pathway_store(
    client: httpx.AsyncClient,
    admin_headers: dict[str, str],
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bonus: prove ``trilhas_state.PathwayStore`` is dead code on this path.

    Installs an exploding sentinel in place of the module-level
    ``domain_trilhas_engine._default_store`` singleton (the only remaining
    live instance of the deprecated legacy store) and drives the full
    enroll -> update-criteria -> list -> progress flow through the real
    ASGI app. httpx's ``ASGITransport`` re-raises unhandled app exceptions
    by default, so any hidden access to the legacy store would blow up this
    test instead of silently reintroducing the in-memory persistence bug.
    """
    monkeypatch.setattr(domain_trilhas_engine, "_default_store", _ExplodingLegacyStore())

    mpi_id = "MPI-TEST-E2E-PATHWAY-002"
    await _boot_sync(db_session)

    enroll_resp = await client.post(
        f"/api/v1/patients/{mpi_id}/pathways",
        json={
            "pathway_id": SEPSE_PATHWAY_ID,
            "encounter_id": "ENC-E2E-002",
            "bed_id": "E2E-02",
            "unit": "UTI-E2E",
        },
        headers=admin_headers,
    )
    assert enroll_resp.status_code == 201, enroll_resp.text
    pp_id = enroll_resp.json()["id"]

    list_resp = await client.get(f"/api/v1/patients/{mpi_id}/pathways", headers=admin_headers)
    assert list_resp.status_code == 200

    update_resp = await client.put(
        f"/api/v1/patients/{mpi_id}/pathways/{pp_id}/criteria",
        json={"criteria": [{"id": "crit-sep-qsofa", "met": True, "value": "0"}]},
        headers=admin_headers,
    )
    assert update_resp.status_code == 200

    progress_resp = await client.get(
        f"/api/v1/patients/{mpi_id}/pathways/{pp_id}/progress", headers=admin_headers
    )
    assert progress_resp.status_code == 200
    # Reaching this line without an AssertionError bubbling out of
    # _ExplodingLegacyStore proves the legacy PathwayStore was never
    # accessed by the enrollment API flow.
