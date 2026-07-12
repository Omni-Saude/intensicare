"""
Testes de idempotência de ingestão — WO-006 (INV-2).

Padrão DRILL-DUPLICATE-REPLAY:
  - DRILL: envia os mesmos dados duas vezes (mesmo MSH-10 ou mesma chave natural)
  - DUPLICATE: o sistema detecta duplicação (via IdempotencyStore ou UNIQUE constraint)
  - REPLAY: retorna o mesmo resultado sem criar nova linha no banco

Cobre:
  - MSH-10 idempotency (X-Idempotency-Key) — in-memory IdempotencyStore
  - Gold-poll natural key (mpi_id, recorded_at, source_system) — DB UNIQUE constraint
  - Defesa em profundidade: ambas as camadas atuando juntas
"""

from __future__ import annotations

from httpx import AsyncClient
import pytest

# ── Helpers ────────────────────────────────────────────────────────────────

GOLD_POLL_PAYLOAD = {
    "mpi_id": "MPI-GOLD-001",
    "recorded_at": "2026-07-05T10:00:00Z",
    "heart_rate": 88,
    "systolic_bp": 125,
    "diastolic_bp": 80,
    "temperature": 37.0,
    "spo2": 97,
    "respiratory_rate": 16,
    "avpu": "A",
    "source_system": "gold_poll",
}

MSH10_PAYLOAD = {
    "mpi_id": "MPI-MSH10-001",
    "recorded_at": "2026-07-05T10:00:00Z",
    "heart_rate": 72,
    "systolic_bp": 118,
    "diastolic_bp": 78,
    "temperature": 36.5,
    "spo2": 99,
    "respiratory_rate": 14,
    "avpu": "A",
    "source_system": "philips_monitor",
}


# ═════════════════════════════════════════════════════════════════════════════
# DRILL-DUPLICATE-REPLAY: MSH-10 (X-Idempotency-Key)
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_drill_duplicate_replay_msh10(client: AsyncClient):
    """DRILL-DUPLICATE-REPLAY: envia mesma MSH-10 duas vezes → uma linha."""
    idem_key = "msh10-drill-001"
    headers = {"X-Idempotency-Key": idem_key}

    # DRILL: primeira ingestão
    resp1 = await client.post(
        "/api/v1/vitals",
        json=MSH10_PAYLOAD,
        headers=headers,
    )
    assert resp1.status_code == 201
    data1 = resp1.json()
    vital_id1 = data1["id"]
    assert data1["mews_score"] is not None

    # DUPLICATE: segunda ingestão com mesma chave
    resp2 = await client.post(
        "/api/v1/vitals",
        json=MSH10_PAYLOAD,
        headers=headers,
    )
    assert resp2.status_code == 200  # 200 = idempotent replay, não 201
    data2 = resp2.json()

    # REPLAY: mesmo ID, mesmo score, mensagem indica replay
    assert data2["id"] == vital_id1
    assert data2["mews_score"] == data1["mews_score"]
    assert data2["news2_score"] == data1["news2_score"]
    assert "idempotent" in data2["message"].lower()
    assert data2["message"] != data1["message"]  # mensagem diferente (replay vs created)


@pytest.mark.asyncio
async def test_drill_duplicate_replay_msh10_different_payload_same_key(client: AsyncClient):
    """Mesma chave MSH-10 com payload diferente → retorna o primeiro registro
    (o segundo payload é ignorado por idempotência)."""
    idem_key = "msh10-drill-002"
    headers = {"X-Idempotency-Key": idem_key}

    # DRILL: primeiro payload
    resp1 = await client.post(
        "/api/v1/vitals",
        json={**MSH10_PAYLOAD, "heart_rate": 72},
        headers=headers,
    )
    assert resp1.status_code == 201
    data1 = resp1.json()

    # DUPLICATE: mesmo idempotency key, mas heart_rate diferente
    # (valor válido: 110, mas diferente do original 72)
    resp2 = await client.post(
        "/api/v1/vitals",
        json={**MSH10_PAYLOAD, "heart_rate": 110},
        headers=headers,
    )
    assert resp2.status_code == 200
    data2 = resp2.json()

    # REPLAY: retorna o primeiro registro (heart_rate=72), não o novo
    assert data2["id"] == data1["id"]
    # O MEWS do registro original é baseado em heart_rate=72
    assert data2["mews_score"] == data1["mews_score"]


@pytest.mark.asyncio
async def test_drill_duplicate_replay_msh10_only_one_row_in_db(client: AsyncClient):
    """DRILL-DUPLICATE-REPLAY: verifica que há exatamente 1 linha no banco
    após duas requisições com mesma MSH-10."""
    idem_key = "msh10-drill-003"
    headers = {"X-Idempotency-Key": idem_key}
    mpi_id = "MPI-MSH10-003"

    # DRILL
    resp1 = await client.post(
        "/api/v1/vitals",
        json={**MSH10_PAYLOAD, "mpi_id": mpi_id},
        headers=headers,
    )
    assert resp1.status_code == 201

    # DUPLICATE
    resp2 = await client.post(
        "/api/v1/vitals",
        json={**MSH10_PAYLOAD, "mpi_id": mpi_id},
        headers=headers,
    )
    assert resp2.status_code == 200

    # Verifica que só existe 1 registro no status do paciente
    status_resp = await client.get(f"/api/v1/patients/{mpi_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    # O trend deve ter no máximo 1 valor (se só houve 1 ingestão real)
    assert status_data["latest_vitals"] is not None
    assert len(status_data["trend"]["values"]) == 1


# ═════════════════════════════════════════════════════════════════════════════
# DRILL-DUPLICATE-REPLAY: Gold-poll natural key (DB UNIQUE constraint)
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_drill_duplicate_replay_gold_poll_natural_key(client: AsyncClient):
    """DRILL-DUPLICATE-REPLAY via chave natural Gold-poll.

    Sem X-Idempotency-Key, o DB UNIQUE (mpi_id, recorded_at, source_system)
    impede duplicação e retorna o registro existente.
    """
    # DRILL: primeira ingestão SEM idempotency key
    resp1 = await client.post("/api/v1/vitals", json=GOLD_POLL_PAYLOAD)
    assert resp1.status_code == 201
    data1 = resp1.json()
    vital_id1 = data1["id"]

    # DUPLICATE: segunda ingestão com mesmos (mpi_id, recorded_at, source_system)
    # sem idempotency key → o DB UNIQUE constraint bloqueia
    resp2 = await client.post("/api/v1/vitals", json=GOLD_POLL_PAYLOAD)
    # Deve retornar 200 (idempotent replay via DB constraint)
    assert resp2.status_code == 200
    data2 = resp2.json()

    # REPLAY: mesmo ID
    assert data2["id"] == vital_id1
    assert "idempotent" in data2["message"].lower()
    assert "DB unique constraint" in data2["message"]


@pytest.mark.asyncio
async def test_gold_poll_natural_key_allows_different_sources(client: AsyncClient):
    """Mesmo (mpi_id, recorded_at) de fontes diferentes → dois registros."""
    payload_philips = {**GOLD_POLL_PAYLOAD, "source_system": "philips_monitor"}
    payload_gold = {**GOLD_POLL_PAYLOAD, "source_system": "gold_poll"}

    resp1 = await client.post("/api/v1/vitals", json=payload_philips)
    resp2 = await client.post("/api/v1/vitals", json=payload_gold)

    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["id"] != resp2.json()["id"]


@pytest.mark.asyncio
async def test_gold_poll_natural_key_allows_different_timestamps(client: AsyncClient):
    """Mesmo (mpi_id, source_system) com recorded_at diferente → dois registros."""
    payload1 = {**GOLD_POLL_PAYLOAD, "recorded_at": "2026-07-05T10:00:00Z"}
    payload2 = {**GOLD_POLL_PAYLOAD, "recorded_at": "2026-07-05T10:05:00Z"}

    resp1 = await client.post("/api/v1/vitals", json=payload1)
    resp2 = await client.post("/api/v1/vitals", json=payload2)

    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["id"] != resp2.json()["id"]


@pytest.mark.asyncio
async def test_gold_poll_natural_key_null_source_system(client: AsyncClient):
    """source_system=NULL não conflita entre si (comportamento SQL padrão)."""
    payload_sem_source = {
        **GOLD_POLL_PAYLOAD,
        "mpi_id": "MPI-NULL-SOURCE",
        "source_system": None,
    }

    resp1 = await client.post("/api/v1/vitals", json=payload_sem_source)
    resp2 = await client.post("/api/v1/vitals", json=payload_sem_source)

    # NULL != NULL em SQL → ambos criam registros novos (sem UNIQUE conflito)
    assert resp1.status_code == 201
    assert resp2.status_code == 201
    assert resp1.json()["id"] != resp2.json()["id"]


# ═════════════════════════════════════════════════════════════════════════════
# Defesa em profundidade: IdempotencyStore + DB UNIQUE
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_idempotency_store_and_db_unique_together(client: AsyncClient):
    """IdempotencyStore (MSH-10) atua primeiro; DB UNIQUE é safety net.

    Com X-Idempotency-Key, o IdempotencyStore captura antes do DB.
    A mensagem de replay vem da camada de aplicação.
    """
    idem_key = "msh10-plus-natural-key"
    headers = {"X-Idempotency-Key": idem_key}
    payload = {
        **GOLD_POLL_PAYLOAD,
        "mpi_id": "MPI-DEFENSE-01",
    }

    # DRILL: com idempotency key
    resp1 = await client.post("/api/v1/vitals", json=payload, headers=headers)
    assert resp1.status_code == 201

    # DUPLICATE: mesma key → IdempotencyStore captura primeiro
    resp2 = await client.post("/api/v1/vitals", json=payload, headers=headers)
    assert resp2.status_code == 200
    data2 = resp2.json()

    # REPLAY: mensagem da camada de aplicação (não do DB)
    assert "idempotent replay" in data2["message"].lower()
    # Não deve mencionar "DB unique constraint" porque o IdempotencyStore
    # interceptou antes do DB
    assert "DB unique constraint" not in data2["message"]


@pytest.mark.asyncio
async def test_gold_poll_natural_key_only_one_row_in_db(client: AsyncClient):
    """DRILL-DUPLICATE-REPLAY: verifica que Gold-poll natural key resulta
    em exatamente 1 linha no banco."""
    mpi_id = "MPI-GOLD-ONEROW"

    payload = {**GOLD_POLL_PAYLOAD, "mpi_id": mpi_id}

    # DRILL
    resp1 = await client.post("/api/v1/vitals", json=payload)
    assert resp1.status_code == 201

    # DUPLICATE (sem idempotency key → depende do DB UNIQUE)
    resp2 = await client.post("/api/v1/vitals", json=payload)
    assert resp2.status_code == 200

    # Verifica que há apenas 1 registro
    status_resp = await client.get(f"/api/v1/patients/{mpi_id}/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["latest_vitals"] is not None
    assert len(status_data["trend"]["values"]) == 1
