"""Tests for the CDS Hooks 2.0 discovery + patient-view service.

Covers: discovery response shape (public, no auth), a real critical-sepsis
card for MPI-DEMO-001 (severity/indicator/summary/detail/source/links per
the CDS Hooks 2.0 spec), a patient with no active pathways getting an
empty card list, and 422 on an invalid request body.
"""

from __future__ import annotations

import httpx

from intensicare.api.v1.cds_hooks import SERVICE_ID, SERVICE_PATH
from intensicare.config import settings

DEMO_MPI_PREFIX = "MPI-DEMO-"
SEPSE_PATHWAY_ID = 2  # _work/alerts/pathways/sepse.yaml -> pathway.id


# ===========================================================================
# GET /cds-services — discovery (public, no auth header sent)
# ===========================================================================


class TestDiscovery:
    async def test_discovery_shape(self, client: httpx.AsyncClient) -> None:
        resp = await client.get("/cds-services")
        assert resp.status_code == 200, resp.text
        body = resp.json()

        assert "services" in body
        assert isinstance(body["services"], list)
        assert len(body["services"]) == 1

        service = body["services"][0]
        assert service["hook"] == "patient-view"
        assert service["id"] == SERVICE_ID
        assert service["title"]
        assert service["description"]

    async def test_discovery_requires_no_auth(self, client: httpx.AsyncClient) -> None:
        """Discovery must be reachable with zero Authorization header — a CDS
        Client has no auth context yet at discovery time (CDS Hooks 2.0
        spec)."""
        resp = await client.get("/cds-services", headers={})
        assert resp.status_code == 200, resp.text


# ===========================================================================
# POST /cds-services/intensicare-pathway-alerts — patient-view
# ===========================================================================


class TestPatientViewService:
    async def test_demo_001_critical_sepsis_card(
        self,
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
        demo_patients: object,
    ) -> None:
        """MPI-DEMO-001 is seeded active + critical in the sepsis pathway
        (pam=58 critical band) — must surface exactly one card, CRITICAL
        indicator, with all CDS Hooks 2.0-required fields populated."""
        mpi_id = f"{DEMO_MPI_PREFIX}001"
        resp = await client.post(
            SERVICE_PATH,
            json={
                "hook": "patient-view",
                "hookInstance": "test-hook-instance-001",
                "context": {"patientId": mpi_id},
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()

        assert "cards" in body
        cards = body["cards"]
        assert len(cards) >= 1

        sepse_cards = [c for c in cards if "Sepse" in c["summary"]]
        assert len(sepse_cards) == 1, cards
        card = sepse_cards[0]

        # CDS Hooks 2.0-required card fields.
        assert card["uuid"]
        assert card["summary"]
        assert len(card["summary"]) <= 140
        assert card["indicator"] == "critical"
        assert card["source"]["label"] == "IntensiCare"
        assert card["links"]
        assert card["links"][0]["url"].startswith(
            f"{settings.frontend_base_url}/patient/{mpi_id}/pathway/"
        )
        assert card["links"][0]["type"] == "absolute"
        assert "Sepse" in card["summary"]
        assert "CRITICAL" in card["summary"]
        assert card["detail"] is not None and "critérios" in card["detail"].lower()

    async def test_patient_without_pathways_returns_empty_cards(
        self,
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        resp = await client.post(
            SERVICE_PATH,
            json={
                "hook": "patient-view",
                "hookInstance": "test-hook-instance-002",
                "context": {"patientId": "MPI-NOBODY-HOME-999"},
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"cards": []}

    async def test_demo_003_no_enrollment_returns_empty_cards(
        self,
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
        demo_patients: object,
    ) -> None:
        """MPI-DEMO-003/004 receive no pathway enrollment in the demo seed
        (per scripts/dev/seed_demo.py) — must yield an empty card list, not
        an error."""
        mpi_id = f"{DEMO_MPI_PREFIX}003"
        resp = await client.post(
            SERVICE_PATH,
            json={
                "hook": "patient-view",
                "hookInstance": "test-hook-instance-003",
                "context": {"patientId": mpi_id},
            },
            headers=admin_headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json() == {"cards": []}

    async def test_missing_context_returns_422(
        self,
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        resp = await client.post(
            SERVICE_PATH,
            json={"hook": "patient-view", "hookInstance": "test-hook-instance-004"},
            headers=admin_headers,
        )
        assert resp.status_code == 422

    async def test_missing_patient_id_returns_422(
        self,
        client: httpx.AsyncClient,
        admin_headers: dict[str, str],
    ) -> None:
        resp = await client.post(
            SERVICE_PATH,
            json={
                "hook": "patient-view",
                "hookInstance": "test-hook-instance-005",
                "context": {},
            },
            headers=admin_headers,
        )
        assert resp.status_code == 422

    async def test_requires_authentication(
        self,
        client: httpx.AsyncClient,
        no_auth_headers: dict[str, str],
    ) -> None:
        """Unlike discovery, the actual service call carries patient context
        and requires a valid IntensiCare bearer token in this deployment
        (see api/v1/cds_hooks.py module docstring for the documented
        deviation from the base CDS Hooks spec)."""
        resp = await client.post(
            SERVICE_PATH,
            json={
                "hook": "patient-view",
                "hookInstance": "test-hook-instance-006",
                "context": {"patientId": "MPI-DEMO-001"},
            },
            headers=no_auth_headers,
        )
        assert resp.status_code in (401, 403)
