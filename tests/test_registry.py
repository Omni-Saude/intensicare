"""Tests for api/v1/registry.py endpoints and domain_tenancy registry CRUD functions.

Covers:
  - GET    /api/v1/registry/empresas              (list, search)
  - POST   /api/v1/registry/empresas              (create, CNPJ duplicate)
  - GET    /api/v1/registry/empresas/{id}         (get, 404)
  - PUT    /api/v1/registry/empresas/{id}         (update, 404)
  - DELETE /api/v1/registry/empresas/{id}         (delete, 404)
  - GET    /api/v1/registry/estabelecimentos      (list)
  - domain_tenancy: create_estabelecimento, get_estabelecimento
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.domain_tenancy import (
    create_estabelecimento,
    get_estabelecimento,
)


# ============================================================================
# Helpers
# ============================================================================

def _empresa_payload(
    razao_social: str = "Hospital Teste Ltda",
    nome_fantasia: str = "Hospital Teste",
    cnpj: str = "12345678000199",
) -> dict:
    return {
        "razao_social": razao_social,
        "nome_fantasia": nome_fantasia,
        "cnpj": cnpj,
    }


def _estabelecimento_payload(
    empresa_id: str,
    nome: str = "UTI Central",
    cnes: str | None = "1234567",
) -> dict:
    return {
        "empresa_id": empresa_id,
        "nome": nome,
        "cnes": cnes,
    }


# ============================================================================
# Empresa endpoint tests
# ============================================================================

class TestCreateEmpresa:
    """POST /api/v1/registry/empresas"""

    @pytest.mark.asyncio
    async def test_create_empresa_returns_201(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Creating a valid empresa returns 201 with EmpresaResponse."""
        payload = _empresa_payload(
            razao_social="Hospital São Lucas S.A.",
            nome_fantasia="São Lucas",
            cnpj="11222333000144",
        )
        resp = await client.post(
            "/api/v1/registry/empresas", json=payload, headers=admin_headers
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["razao_social"] == payload["razao_social"]
        assert data["nome_fantasia"] == payload["nome_fantasia"]
        assert data["cnpj"] == payload["cnpj"]
        assert data["ativo"] is True
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_empresa_duplicate_cnpj_returns_409(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Creating an empresa with an already-registered CNPJ returns 409."""
        payload = _empresa_payload(cnpj="99988877700155")
        # First creation
        resp1 = await client.post(
            "/api/v1/registry/empresas", json=payload, headers=admin_headers
        )
        assert resp1.status_code == 201

        # Duplicate — same CNPJ
        payload2 = _empresa_payload(
            razao_social="Outra Empresa S.A.",
            nome_fantasia="Outra",
            cnpj="99988877700155",
        )
        resp2 = await client.post(
            "/api/v1/registry/empresas", json=payload2, headers=admin_headers
        )
        assert resp2.status_code == 409
        assert "CNPJ" in resp2.json()["detail"]


class TestListEmpresas:
    """GET /api/v1/registry/empresas"""

    @pytest.mark.asyncio
    async def test_list_empresas_returns_200_with_items(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Listing empresas returns paginated response."""
        # Seed one empresa
        await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="55566677000188"),
            headers=admin_headers,
        )

        resp = await client.get(
            "/api/v1/registry/empresas", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_empresas_search_filters_by_nome(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Search param filters by nome_fantasia or razao_social."""
        # Seed two empresas
        await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(
                razao_social="Alpha Med Ltda",
                nome_fantasia="Alpha Med",
                cnpj="11111111000101",
            ),
            headers=admin_headers,
        )
        await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(
                razao_social="Beta Saúde S.A.",
                nome_fantasia="Beta Saúde",
                cnpj="22222222000102",
            ),
            headers=admin_headers,
        )

        # Search for "Alpha"
        resp = await client.get(
            "/api/v1/registry/empresas",
            params={"search": "Alpha"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        names = [item["nome_fantasia"] for item in data["items"]]
        assert any("Alpha" in n for n in names)

    @pytest.mark.asyncio
    async def test_list_empresas_search_filters_by_cnpj(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Search param also matches CNPJ."""
        await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="33333333000103"),
            headers=admin_headers,
        )

        resp = await client.get(
            "/api/v1/registry/empresas",
            params={"search": "33333333000103"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        cnjps = [item["cnpj"] for item in data["items"]]
        assert "33333333000103" in cnjps


class TestGetEmpresa:
    """GET /api/v1/registry/empresas/{id}"""

    @pytest.mark.asyncio
    async def test_get_empresa_by_id_returns_200(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Getting an existing empresa by ID returns it."""
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="44444444000104"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        resp = await client.get(
            f"/api/v1/registry/empresas/{empresa_id}", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == empresa_id
        assert data["cnpj"] == "44444444000104"

    @pytest.mark.asyncio
    async def test_get_empresa_nonexistent_returns_404(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Getting a non-existent empresa returns 404."""
        fake_id = str(uuid4())
        resp = await client.get(
            f"/api/v1/registry/empresas/{fake_id}", headers=admin_headers
        )
        assert resp.status_code == 404
        assert "não encontrada" in resp.json()["detail"]


class TestUpdateEmpresa:
    """PUT /api/v1/registry/empresas/{id}"""

    @pytest.mark.asyncio
    async def test_update_empresa_returns_200(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Updating an empresa changes its fields."""
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="66666666000106"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        update = {"nome_fantasia": "Hospital Renovado", "ativo": False}
        resp = await client.put(
            f"/api/v1/registry/empresas/{empresa_id}",
            json=update,
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["nome_fantasia"] == "Hospital Renovado"
        assert data["ativo"] is False
        assert data["cnpj"] == "66666666000106"  # unchanged

    @pytest.mark.asyncio
    async def test_update_empresa_nonexistent_returns_404(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Updating a non-existent empresa returns 404."""
        fake_id = str(uuid4())
        resp = await client.put(
            f"/api/v1/registry/empresas/{fake_id}",
            json={"nome_fantasia": "Nope"},
            headers=admin_headers,
        )
        assert resp.status_code == 404


class TestDeleteEmpresa:
    """DELETE /api/v1/registry/empresas/{id}"""

    @pytest.mark.asyncio
    async def test_delete_empresa_returns_204(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Deleting an existing empresa returns 204 No Content."""
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="77777777000107"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        resp = await client.delete(
            f"/api/v1/registry/empresas/{empresa_id}", headers=admin_headers
        )
        assert resp.status_code == 204

        # Verify it's gone
        get_resp = await client.get(
            f"/api/v1/registry/empresas/{empresa_id}", headers=admin_headers
        )
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_empresa_nonexistent_returns_404(
        self, client: AsyncClient, admin_headers: dict
    ) -> None:
        """Deleting a non-existent empresa returns 404."""
        fake_id = str(uuid4())
        resp = await client.delete(
            f"/api/v1/registry/empresas/{fake_id}", headers=admin_headers
        )
        assert resp.status_code == 404


# ============================================================================
# Estabelecimento endpoint tests
# ============================================================================

class TestListEstabelecimentos:
    """GET /api/v1/registry/estabelecimentos"""

    @pytest.mark.asyncio
    async def test_list_estabelecimentos_returns_200(
        self, client: AsyncClient, admin_headers: dict, db_session: AsyncSession
    ) -> None:
        """Listing estabelecimentos returns paginated response."""
        # Create an empresa first
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="88888888000108"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        # Create an estabelecimento via service layer
        estab_data = _estabelecimento_payload(
            empresa_id=empresa_id, nome="Pronto Socorro Central", cnes="7654321"
        )
        await create_estabelecimento(db_session, estab_data)

        resp = await client.get(
            "/api/v1/registry/estabelecimentos", headers=admin_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_estabelecimentos_filter_by_empresa(
        self, client: AsyncClient, admin_headers: dict, db_session: AsyncSession
    ) -> None:
        """Filter estabelecimentos by empresa_id."""
        # Create empresa
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="99999999000109"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        # Create estabelecimento
        await create_estabelecimento(
            db_session,
            _estabelecimento_payload(
                empresa_id=empresa_id, nome="UTI Neo Natal", cnes="1111111"
            ),
        )

        resp = await client.get(
            "/api/v1/registry/estabelecimentos",
            params={"empresa_id": empresa_id},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        estab_ids = {item["empresa_id"] for item in data["items"]}
        assert empresa_id in estab_ids


# ============================================================================
# Domain service tests (create_estabelecimento / get_estabelecimento)
# ============================================================================

class TestEstabelecimentoService:
    """Direct tests for domain_tenancy registry CRUD functions."""

    @pytest.mark.asyncio
    async def test_create_estabelecimento_service(
        self, client: AsyncClient, admin_headers: dict, db_session: AsyncSession
    ) -> None:
        """create_estabelecimento() persists and returns an Estabelecimento."""
        # Create an empresa first
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="10101010000110"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        payload = _estabelecimento_payload(
            empresa_id=empresa_id,
            nome="Centro Cirúrgico",
            cnes="2222222",
        )
        estab = await create_estabelecimento(db_session, payload)

        assert estab.id is not None
        assert estab.nome == "Centro Cirúrgico"
        assert estab.empresa_id == empresa_id
        assert estab.cnes == "2222222"
        assert estab.ativo is True

    @pytest.mark.asyncio
    async def test_get_estabelecimento_service(
        self, client: AsyncClient, admin_headers: dict, db_session: AsyncSession
    ) -> None:
        """get_estabelecimento() returns the correct record or None."""
        # Create empresa + estabelecimento
        create_resp = await client.post(
            "/api/v1/registry/empresas",
            json=_empresa_payload(cnpj="20202020000120"),
            headers=admin_headers,
        )
        empresa_id = create_resp.json()["id"]

        estab = await create_estabelecimento(
            db_session,
            _estabelecimento_payload(
                empresa_id=empresa_id, nome="Enfermaria Geral", cnes="3333333"
            ),
        )

        # Positive lookup
        found = await get_estabelecimento(db_session, estab.id)
        assert found is not None
        assert found.id == estab.id
        assert found.nome == "Enfermaria Geral"

        # Nonexistent ID
        missing = await get_estabelecimento(db_session, str(uuid4()))
        assert missing is None
