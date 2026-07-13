"""Testes para a projeção determinística de tendência de deterioração
(services/deterioration_trend.py) e o endpoint
GET /api/v1/patients/{mpi_id}/deterioration-trend.

Cobre:
  - série sintética subindo com slope conhecido -> hours_to_threshold
    determinístico (matemática conferida manualmente no comentário do teste);
  - série estável (slope~0) -> sem projeção (projected_threshold/
    hours_to_threshold None), mas o objeto ainda é retornado (pontos
    disponíveis para auditoria);
  - menos de 3 pontos na janela de 12h -> None ("sem dado, sem previsão");
  - R² baixo -> confidence "low" mesmo com slope>0;
  - endpoint: 404 paciente inexistente, 200 com projections=[] sem dados,
    200 com projeções reais para o paciente demo (MPI-DEMO-001).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.patient_cache import PatientCache
from intensicare.services.deterioration_trend import (
    MAX_HOURS_TO_THRESHOLD,
    compute_deterioration_trend,
)

MPI_ID = "MPI-TREND-TEST-001"


async def _insert_scores(
    db_session: AsyncSession,
    *,
    mpi_id: str,
    score_type: str,
    algorithm_version: str,
    base_time: datetime,
    hourly_offsets: list[float],
    values: list[int],
) -> None:
    """Insere linhas de ClinicalScore em ``base_time + offset_hours``."""
    for offset, value in zip(hourly_offsets, values, strict=True):
        db_session.add(
            ClinicalScore(
                mpi_id=mpi_id,
                score_type=score_type,
                score_value=value,
                algorithm_version=algorithm_version,
                calculated_at=base_time + timedelta(hours=offset),
            )
        )
    await db_session.flush()


# ---------------------------------------------------------------------------
# Série subindo — slope conhecido, hours_to_threshold determinístico
# ---------------------------------------------------------------------------


class TestRisingTrend:
    async def test_known_slope_projects_deterministic_hours_to_threshold(
        self, db_session: AsyncSession
    ) -> None:
        """4 pontos MEWS perfeitamente lineares: t=[0,1,2,3]h, score=[1,2,3,4].

        Matemática (regressão OLS manual, x=t em horas desde o 1º ponto):
          mean_x = 1.5, mean_y = 2.5
          Sxy = sum((x-1.5)(y-2.5)) para (0,1),(1,2),(2,3),(3,4):
            (0-1.5)(1-2.5)=(-1.5)(-1.5)=2.25
            (1-1.5)(2-2.5)=(-0.5)(-0.5)=0.25
            (2-1.5)(3-2.5)=(0.5)(0.5)=0.25
            (3-1.5)(4-2.5)=(1.5)(1.5)=2.25
            Sxy = 2.25+0.25+0.25+2.25 = 5.0
          Sxx = sum((x-1.5)^2) = 2.25+0.25+0.25+2.25 = 5.0
          slope = Sxy/Sxx = 5.0/5.0 = 1.0 pt/h
          intercept = 2.5 - 1.0*1.5 = 1.0 -> y_hat == y em todos os pontos
          ss_res = 0, ss_tot = sum((y-2.5)^2) = 2.25+0.25+0.25+2.25=5.0
          r_squared = 1 - 0/5.0 = 1.0 (ajuste perfeito)

          current_score = último ponto observado = 4.
          Fallback MEWS thresholds (watch=3, urgent=4, critical=5) — nenhum
          threshold_config seedado para MPI_ID, então cai no fallback 0038.
          Próximo threshold > 4 -> 5 (watch=3 e urgent=4 já foram
          igualados/ultrapassados).
          hours_to_threshold = (5 - 4) / 1.0 = 1.0h exatamente.

          n_points=4 >= 4 e r_squared=1.0 >= 0.6 -> confidence == "moderate".
        """
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=3)  # first point at now-3h
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 1, 2, 3],
            values=[1, 2, 3, 4],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is not None
        assert projection.n_points == 4
        assert projection.slope_per_hour == pytest.approx(1.0)
        assert projection.r_squared == pytest.approx(1.0)
        assert projection.current_score == 4
        assert projection.confidence == "moderate"
        assert projection.projected_threshold == 5
        assert projection.hours_to_threshold == pytest.approx(1.0)
        assert projection.window_hours == 12.0
        assert "não substitui julgamento clínico" in projection.disclaimer
        # Explicabilidade: os 4 pontos brutos devem estar presentes.
        assert len(projection.points) == 4
        assert [p.score for p in projection.points] == [1, 2, 3, 4]

    async def test_low_r_squared_yields_low_confidence(self, db_session: AsyncSession) -> None:
        """4 pontos MEWS dispersos mas com tendência de alta: t=[0,1,2,3]h,
        score=[1,3,1,4].

        Matemática (mesma x que o teste acima, logo mean_x=1.5, Sxx=5.0):
          mean_y = (1+3+1+4)/4 = 2.25
          Sxy = sum((x-1.5)(y-2.25)):
            (0-1.5)(1-2.25)=(-1.5)(-1.25)=1.875
            (1-1.5)(3-2.25)=(-0.5)(0.75)=-0.375
            (2-1.5)(1-2.25)=(0.5)(-1.25)=-0.625
            (3-1.5)(4-2.25)=(1.5)(1.75)=2.625
            Sxy = 1.875-0.375-0.625+2.625 = 3.5
          slope = 3.5/5.0 = 0.7 pt/h
          intercept = 2.25 - 0.7*1.5 = 1.2
          y_hat = [1.2, 1.9, 2.6, 3.3]
          ss_res = (1-1.2)^2+(3-1.9)^2+(1-2.6)^2+(4-3.3)^2
                 = 0.04+1.21+2.56+0.49 = 4.3
          ss_tot = (1-2.25)^2+(3-2.25)^2+(1-2.25)^2+(4-2.25)^2
                 = 1.5625+0.5625+1.5625+3.0625 = 6.75
          r_squared = 1 - 4.3/6.75 = 1 - 0.637037... = 0.362962... (< 0.6)

          current_score = 4 (último ponto). Próximo threshold MEWS > 4 -> 5.
          hours_to_threshold = (5-4)/0.7 = 1.428571... h (< 24h cap, ainda
          projetado — só a *confiança* é baixa, a projeção não é omitida).
          O serviço arredonda slope/hours para exibição (4/2 casas
          decimais respectivamente) — os asserts abaixo comparam contra os
          valores já arredondados (1.43h).
        """
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=3)
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 1, 2, 3],
            values=[1, 3, 1, 4],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is not None
        assert projection.slope_per_hour == pytest.approx(0.7)
        assert projection.r_squared == pytest.approx(0.362963, abs=1e-4)
        assert projection.r_squared < 0.6
        assert projection.confidence == "low"
        assert projection.projected_threshold == 5
        # Serviço arredonda hours_to_threshold para 2 casas decimais.
        assert projection.hours_to_threshold == pytest.approx(round(1 / 0.7, 2), abs=1e-9)


# ---------------------------------------------------------------------------
# Série estável — sem projeção
# ---------------------------------------------------------------------------


class TestStableTrend:
    async def test_flat_series_has_no_projection(self, db_session: AsyncSession) -> None:
        """4 pontos MEWS constantes (score=2 sempre) -> slope=0.0 exatamente,
        logo nenhuma projeção é feita (spec: 'se slope > 0' é a única
        condição de projeção). O objeto ainda é retornado com os pontos
        disponíveis para auditoria — 'sem projeção' != 'sem dado'."""
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=3)
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 1, 2, 3],
            values=[2, 2, 2, 2],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is not None
        assert projection.slope_per_hour == pytest.approx(0.0)
        assert projection.projected_threshold is None
        assert projection.hours_to_threshold is None
        assert projection.n_points == 4
        assert projection.current_score == 2


# ---------------------------------------------------------------------------
# Menos de 3 pontos -> None
# ---------------------------------------------------------------------------


class TestInsufficientData:
    async def test_two_points_returns_none(self, db_session: AsyncSession) -> None:
        """Apenas 2 pontos na janela de 12h -> sem dado, sem previsão (None)."""
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=1)
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 1],
            values=[3, 4],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is None

    async def test_no_points_returns_none(self, db_session: AsyncSession) -> None:
        """Nenhum score persistido -> None."""
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)

        projection = await compute_deterioration_trend(db_session, "MPI-NEVER-SCORED", now, "MEWS")

        assert projection is None

    async def test_points_outside_window_are_excluded(self, db_session: AsyncSession) -> None:
        """Pontos com mais de 12h de idade não contam para a janela."""
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=20)  # bem fora da janela de 12h
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 1, 2],
            values=[3, 4, 5],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is None


# ---------------------------------------------------------------------------
# Cap de 24h
# ---------------------------------------------------------------------------


class TestHorizonCap:
    async def test_slow_rise_beyond_24h_horizon_is_not_projected(
        self, db_session: AsyncSession
    ) -> None:
        """4 pontos MEWS espalhados por quase toda a janela de 12h, subindo
        muito devagar: t=[0,4,8,11]h (desde base_time = now-11h), score=[0,0,0,1].

        Matemática (regressão OLS manual):
          mean_x = (0+4+8+11)/4 = 5.75, mean_y = (0+0+0+1)/4 = 0.25
          Sxy = sum((x-5.75)(y-0.25)):
            (0-5.75)(0-0.25)   = (-5.75)(-0.25) = 1.4375
            (4-5.75)(0-0.25)   = (-1.75)(-0.25) = 0.4375
            (8-5.75)(0-0.25)   = (2.25)(-0.25)  = -0.5625
            (11-5.75)(1-0.25)  = (5.25)(0.75)   = 3.9375
            Sxy = 1.4375+0.4375-0.5625+3.9375 = 5.25
          Sxx = sum((x-5.75)^2) = 33.0625+3.0625+5.0625+27.5625 = 68.75
          slope = 5.25/68.75 = 21/275 = 0.076363... pt/h (positivo, subindo)

          current_score = 1 (último ponto). Fallback MEWS (watch=3, urgent=4,
          critical=5) -> próximo threshold > 1 é watch=3 (gap=2).
          hours_to_threshold_bruto = 2 / (21/275) = 550/21 = 26.190476...h
          > 24h (MAX_HOURS_TO_THRESHOLD) -> cap: projeção reportada como
          None em vez de um número especulativo além do horizonte seguro.
        """
        now = datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc)
        base_time = now - timedelta(hours=11)  # first point at now-11h (inside the 12h window)
        await _insert_scores(
            db_session,
            mpi_id=MPI_ID,
            score_type="MEWS",
            algorithm_version="MEWS-v3.0.0",
            base_time=base_time,
            hourly_offsets=[0, 4, 8, 11],
            values=[0, 0, 0, 1],
        )

        projection = await compute_deterioration_trend(db_session, MPI_ID, now, "MEWS")

        assert projection is not None
        # Serviço arredonda slope_per_hour para 4 casas decimais.
        assert projection.slope_per_hour == pytest.approx(round(21 / 275, 4), abs=1e-9)
        raw_hours = 2 / (21 / 275)
        assert raw_hours > MAX_HOURS_TO_THRESHOLD  # confirms this scenario needs the cap
        # (threshold - current_score) / slope exceeds the 24h cap.
        assert projection.hours_to_threshold is None
        assert projection.projected_threshold is None
        assert MAX_HOURS_TO_THRESHOLD == 24.0


# ---------------------------------------------------------------------------
# Endpoint — GET /api/v1/patients/{mpi_id}/deterioration-trend
# ---------------------------------------------------------------------------


class TestDeteriorationTrendEndpoint:
    async def test_404_when_patient_does_not_exist(
        self, client: httpx.AsyncClient, user_headers: dict[str, str]
    ) -> None:
        resp = await client.get(
            "/api/v1/patients/MPI-DOES-NOT-EXIST/deterioration-trend",
            headers=user_headers,
        )
        assert resp.status_code == 404

    async def test_401_without_auth(
        self, client: httpx.AsyncClient, no_auth_headers: dict[str, str]
    ) -> None:
        resp = await client.get(
            "/api/v1/patients/MPI-ANYTHING/deterioration-trend", headers=no_auth_headers
        )
        assert resp.status_code == 401

    async def test_200_empty_projections_when_patient_exists_without_scores(
        self, client: httpx.AsyncClient, user_headers: dict[str, str], db_session: AsyncSession
    ) -> None:
        """Paciente existe (patient_cache) mas não tem ClinicalScore algum ->
        200 com projections=[] (não 404 — a ausência de dado clínico não é
        a mesma coisa que a ausência do paciente)."""
        db_session.add(
            PatientCache(
                mpi_id="MPI-NO-SCORES-001",
                tenant_id="default",
                display_name=b"synthetic-test-bytes",
                is_active=True,
            )
        )
        await db_session.flush()

        resp = await client.get(
            "/api/v1/patients/MPI-NO-SCORES-001/deterioration-trend",
            headers=user_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["mpi_id"] == "MPI-NO-SCORES-001"
        assert body["projections"] == []

    async def test_200_real_projections_for_demo_patient(
        self,
        client: httpx.AsyncClient,
        user_headers: dict[str, str],
        demo_patients,
    ) -> None:
        """MPI-DEMO-001 ('DEMO Sepse Crítica') tem 10 pontos de vitals
        (portanto ClinicalScore MEWS/NEWS2) ingeridos via o caminho real de
        produção, com piora monotônica -> deve produzir ao menos 1 projeção
        real, com pontos e disclaimer corretamente preenchidos end-to-end
        através do router/schemas/serviço reais (sem mocks).

        Nota: ``scripts/dev/seed_demo.py`` grava ``VitalSign.recorded_at``
        retroativo (~6h atrás até agora), mas ``ClinicalScore.calculated_at``
        reflete o instante real de ingestão (``vitals.py`` sempre usa
        ``now()`` da chamada, não o ``recorded_at`` do vital) — os 10 pontos
        acabam com timestamps próximos entre si em vez de espalhados por 6h.
        Isso é um comportamento pré-existente do seeder/pipeline de ingestão
        (fora do escopo desta mudança), não deste serviço: dado o
        score_type já estar acima do threshold crítico (perfil "Sepse
        Crítica"), o resultado esperado (`projected_threshold`/
        `hours_to_threshold` = None, pois não há próximo threshold acima do
        score atual) é o mesmo independentemente da compressão temporal.
        """
        resp = await client.get(
            "/api/v1/patients/MPI-DEMO-001/deterioration-trend",
            headers=user_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["mpi_id"] == "MPI-DEMO-001"
        assert isinstance(body["projections"], list)
        # Deve haver exatamente 2 projeções (MEWS e NEWS2) — o perfil DEMO
        # Sepse Crítica seeda 10 pontos de vitals, todos dentro da janela
        # de 12h (>= 3 pontos mínimos exigidos por score_type).
        assert len(body["projections"]) == 2
        by_type = {p["score_type"]: p for p in body["projections"]}
        assert set(by_type) == {"MEWS", "NEWS2"}
        # Perfil "Sepse Crítica" termina acima do critical threshold em
        # ambos os scores (MEWS fallback critical=5, NEWS2 fallback
        # critical=7) -> não há "próximo" threshold a projetar.
        assert by_type["MEWS"]["current_score"] >= 5
        assert by_type["NEWS2"]["current_score"] >= 7
        assert by_type["MEWS"]["projected_threshold"] is None
        assert by_type["NEWS2"]["projected_threshold"] is None
        for proj in body["projections"]:
            assert proj["confidence"] in ("low", "moderate")
            assert proj["n_points"] >= 3
            assert proj["window_hours"] == 12.0
            assert "não substitui julgamento clínico" in proj["disclaimer"]
            assert len(proj["points"]) == proj["n_points"]
