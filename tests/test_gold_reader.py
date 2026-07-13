"""Tests for Gold Reader (WO-019) — Athena Poller.

Covers:
- High-watermark: avança após poll bem-sucedido
- Backpressure: polls concorrentes são bloqueados
- Unit normalization at edge: unidades convertidas conforme registry
- Mocked Athena responses
- Domain cadence configuration
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from intensicare.clients.athena_client import AthenaClient, AthenaQueryResult
from intensicare.services.gold_reader import (
    AthenaPoller,
    DomainConfigError,
    poll_all_domains,
)
from intensicare.services.gold_schema import DOMAIN_CADENCE
from intensicare.services.units_normalizer import UnitNormalizationError, normalize_value

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_athena_client() -> AthenaClient:
    """Retorna um AthenaClient com métodos mockados."""
    client = MagicMock(spec=AthenaClient)
    client.execute_query = AsyncMock()
    return client


@pytest.fixture
def sample_rows() -> list[dict[str, str]]:
    """Linhas de exemplo simulando resposta Athena."""
    return [
        {
            "id": "1",
            "patient_id": "P-001",
            "tenant_id": "austa",
            "unit": "ICU-1",
            "parameter": "fio2",
            "value": "0.40",
            "unit_canonical": "fraction",
            "recorded_at": "2026-07-05T10:00:00Z",
            "ingested_at": "2026-07-05T10:05:00Z",
        },
        {
            "id": "2",
            "patient_id": "P-002",
            "tenant_id": "austa",
            "unit": "ICU-1",
            "parameter": "lactato_arterial",
            "value": "2.5",
            "unit_canonical": "mmol/L",
            "recorded_at": "2026-07-05T10:01:00Z",
            "ingested_at": "2026-07-05T10:05:30Z",
        },
        {
            "id": "3",
            "patient_id": "P-003",
            "tenant_id": "austa",
            "unit": "ICU-2",
            "parameter": "creatinina",
            "value": "1.2",
            "unit_canonical": "mg/dL",
            "recorded_at": "2026-07-05T10:02:00Z",
            "ingested_at": "2026-07-05T10:06:00Z",
        },
    ]


@pytest.fixture
def sample_rows_with_conversion() -> list[dict[str, str]]:
    """Linhas que exigem conversão de unidades (fio2 percent, lactato mg/dL)."""
    return [
        {
            "id": "1",
            "patient_id": "P-001",
            "tenant_id": "austa",
            "unit": "ICU-1",
            "parameter": "fio2",
            "value": "40",
            "unit_canonical": "percent",
            "recorded_at": "2026-07-05T10:00:00Z",
            "ingested_at": "2026-07-05T10:05:00Z",
        },
        {
            "id": "2",
            "patient_id": "P-002",
            "tenant_id": "austa",
            "unit": "ICU-1",
            "parameter": "lactato_arterial",
            "value": "27",
            "unit_canonical": "mg/dL",
            "recorded_at": "2026-07-05T10:01:00Z",
            "ingested_at": "2026-07-05T10:05:30Z",
        },
    ]


# ---------------------------------------------------------------------------
# Test: High-watermark advance
# ---------------------------------------------------------------------------


class TestHighWatermark:
    """Verifica que o watermark avança após poll bem-sucedido."""

    @pytest.mark.asyncio
    async def test_watermark_advances_after_poll(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Após um poll com resultados, o watermark deve avançar para o maior ingested_at."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "ventilation"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        # Garante que não há watermark prévio
        await redis.delete(watermark_key)

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows,
            column_names=[
                "id",
                "patient_id",
                "parameter",
                "value",
                "unit_canonical",
                "ingested_at",
            ],
            total_rows=3,
            query_execution_id="test-exec-001",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain(domain, tenant_id)

        assert result["status"] == "ok"
        assert result["rows_processed"] == 3
        assert result["new_watermark"] == "2026-07-05T10:06:00Z"

        # Verifica que o watermark foi persistido no Redis
        stored_watermark = await redis.get(watermark_key)
        assert stored_watermark == "2026-07-05T10:06:00Z"

    @pytest.mark.asyncio
    async def test_watermark_unchanged_on_empty_poll(self, mock_athena_client: AthenaClient):
        """Poll sem resultados não deve alterar o watermark."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "ventilation"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        # Define watermark inicial
        await redis.set(watermark_key, "2026-07-04T00:00:00Z")

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=[],
            column_names=[],
            total_rows=0,
            query_execution_id="test-exec-empty",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain(domain, tenant_id)

        assert result["status"] == "empty"
        assert result["rows_processed"] == 0
        assert result["new_watermark"] == "2026-07-04T00:00:00Z"

        # Watermark não foi alterado
        stored = await redis.get(watermark_key)
        assert stored == "2026-07-04T00:00:00Z"

    @pytest.mark.asyncio
    async def test_get_last_watermark(self):
        """get_last_watermark retorna o valor armazenado no Redis."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "sepsis"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        await redis.set(watermark_key, "2026-07-05T08:00:00Z")

        poller = AthenaPoller(athena_client=mock_athena_client)
        wm = await poller.get_last_watermark(tenant_id, domain)
        assert wm == "2026-07-05T08:00:00Z"

        # Domínio sem watermark → None
        wm2 = await poller.get_last_watermark(tenant_id, "aki")
        assert wm2 is None

    @pytest.mark.asyncio
    async def test_reset_watermark(self):
        """reset_watermark remove o watermark do Redis."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "sepsis"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        await redis.set(watermark_key, "2026-07-05T08:00:00Z")

        poller = AthenaPoller(athena_client=mock_athena_client)
        await poller.reset_watermark(tenant_id, domain)

        stored = await redis.get(watermark_key)
        assert stored is None

    @pytest.mark.asyncio
    async def test_force_full_load_ignores_watermark(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """force_full_load=True deve ignorar watermark existente e fazer full load."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "ventilation"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        # Define watermark antigo
        await redis.set(watermark_key, "2026-07-05T10:00:00Z")

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows[:1],  # apenas 1 linha
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=1,
            query_execution_id="test-exec-full",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain(domain, tenant_id, force_full_load=True)

        assert result["status"] == "ok"
        # O watermark nos resultados é 10:05, deve avançar
        assert result["new_watermark"] == "2026-07-05T10:05:00Z"


# ---------------------------------------------------------------------------
# Test: Backpressure — concurrent polls blocked
# ---------------------------------------------------------------------------


class TestBackpressure:
    """Verifica que polls concorrentes para o mesmo domínio/tenant são bloqueados."""

    @pytest.mark.asyncio
    async def test_concurrent_polls_blocked(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Segundo poll para mesmo domínio/tenant deve ser skipped (backpressure)."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows,
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=3,
            query_execution_id="test-exec-bp",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)

        # Simula poll concorrente: adquire o lock manualmente antes
        from intensicare.core.redis import get_redis

        redis = get_redis()
        lock_key = "gold:lock:austa:ventilation"
        await redis.set(lock_key, "1", ex=60)

        # Agora o poll deve ser skipped
        result = await poller.poll_domain("ventilation", "austa")

        assert result["status"] == "skipped"
        assert result["reason"] == "backpressure"
        assert result["rows_processed"] == 0

        # Athena NÃO foi chamado
        mock_athena_client.execute_query.assert_not_called()

        # Limpa lock
        await redis.delete(lock_key)

    @pytest.mark.asyncio
    async def test_different_domains_not_blocked(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Domínios diferentes para o mesmo tenant NÃO devem se bloquear."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows[:1],
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=1,
            query_execution_id="test-exec-diff",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)

        # Bloqueia apenas o domínio "ventilation"
        from intensicare.core.redis import get_redis

        redis = get_redis()
        lock_key_vent = "gold:lock:austa:ventilation"
        await redis.set(lock_key_vent, "1", ex=60)

        # "sepsis" deve rodar normalmente
        result = await poller.poll_domain("sepsis", "austa")

        assert result["status"] == "ok"
        assert result["rows_processed"] == 1
        mock_athena_client.execute_query.assert_called_once()

        # Limpa lock
        await redis.delete(lock_key_vent)

    @pytest.mark.asyncio
    async def test_different_tenants_not_blocked(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Tenants diferentes para o mesmo domínio NÃO devem se bloquear."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows[:1],
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=1,
            query_execution_id="test-exec-tenant",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)

        # Bloqueia tenant "austa"
        from intensicare.core.redis import get_redis

        redis = get_redis()
        lock_key_austa = "gold:lock:austa:ventilation"
        await redis.set(lock_key_austa, "1", ex=60)

        # Tenant "bradesco" deve rodar normalmente
        result = await poller.poll_domain("ventilation", "bradesco")

        assert result["status"] == "ok"
        mock_athena_client.execute_query.assert_called_once()

        # Limpa lock
        await redis.delete(lock_key_austa)

    @pytest.mark.asyncio
    async def test_lock_released_after_poll(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Após um poll bem-sucedido, o lock deve ser liberado."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows,
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=3,
            query_execution_id="test-exec-release",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)

        # Primeiro poll — deve passar
        result1 = await poller.poll_domain("ventilation", "austa")
        assert result1["status"] == "ok"

        # Segundo poll — deve passar também (lock foi liberado)
        result2 = await poller.poll_domain("ventilation", "austa")
        assert result2["status"] == "ok"


# ---------------------------------------------------------------------------
# Test: Unit normalization at edge
# ---------------------------------------------------------------------------


class TestUnitNormalization:
    """Verifica normalização de unidades canônicas na borda (edge)."""

    def test_fio2_percent_to_fraction(self):
        """FiO2 de percent (40) deve converter para fraction (0.4)."""
        result = normalize_value("fio2", 40, "percent")
        assert result == pytest.approx(0.4)

    def test_fio2_percent_symbol(self):
        """FiO2 com símbolo '%' deve converter."""
        result = normalize_value("fio2", 21, "%")
        assert result == pytest.approx(0.21)

    def test_fio2_already_canonical(self):
        """FiO2 já em fraction não deve ser alterado."""
        result = normalize_value("fio2", 0.21, "fraction")
        assert result == 0.21

    def test_lactate_mgdl_to_mmol(self):
        """Lactato de mg/dL (27) deve converter para mmol/L (~3.0)."""
        result = normalize_value("lactato_arterial", 27, "mg/dL")
        assert result == pytest.approx(27 * 0.111, rel=1e-3)

    def test_lactate_already_canonical(self):
        """Lactato já em mmol/L não deve ser alterado."""
        result = normalize_value("lactato_arterial", 2.5, "mmol/L")
        assert result == 2.5

    def test_creatinine_umol_to_mgdl(self):
        """Creatinina de umol/L (88.4) deve converter para mg/dL (~1.0)."""
        result = normalize_value("creatinina", 88.4, "umol/L")
        assert result == pytest.approx(1.0, rel=1e-2)

    def test_pao2_kpa_to_mmhg(self):
        """PaO2 de kPa (12) deve converter para mmHg (~90)."""
        result = normalize_value("pao2", 12, "kPa")
        assert result == pytest.approx(12 * 7.50062, rel=1e-3)

    def test_case_insensitive_units(self):
        """Unidades devem ser case-insensitive."""
        result = normalize_value("fio2", 50, "PERCENT")
        assert result == pytest.approx(0.5)

        result2 = normalize_value("pao2", 12, "KPA")
        assert result2 == pytest.approx(12 * 7.50062, rel=1e-3)

    def test_alias_units(self):
        """Aliases devem ser aceitos (ex: 'mmhg' para mmHg)."""
        result = normalize_value("pao2", 90, "mmhg")
        assert result == 90  # alias, same unit

    def test_affine_conversion_raises_error(self):
        """Conversão affine (degF → degC) deve levantar erro (factor=null)."""
        with pytest.raises(UnitNormalizationError, match="NÃO é um fator fixo"):
            normalize_value("temperatura", 98.6, "degF")

    def test_unknown_parameter_raises_error(self):
        """Parâmetro desconhecido deve levantar erro."""
        with pytest.raises(UnitNormalizationError, match="Parâmetro desconhecido"):
            normalize_value("param_inexistente", 100, "units")

    def test_unknown_unit_raises_error(self):
        """Unidade não reconhecida deve levantar erro."""
        with pytest.raises(UnitNormalizationError, match="não reconhecida"):
            normalize_value("fio2", 40, "furlongs")

    def test_get_canonical_unit(self):
        """get_canonical_unit retorna a unidade canônica."""
        from intensicare.services.units_normalizer import get_canonical_unit

        assert get_canonical_unit("fio2") == "fraction"
        assert get_canonical_unit("lactato_arterial") == "mmol/L"
        assert get_canonical_unit("creatinina") == "mg/dL"
        assert get_canonical_unit("inexistente") is None

    def test_list_parameters(self):
        """list_parameters retorna lista de parâmetros."""
        from intensicare.services.units_normalizer import list_parameters

        params = list_parameters()
        assert len(params) > 0
        assert "fio2" in params
        assert "lactato_arterial" in params
        assert "creatinina" in params

    @pytest.mark.asyncio
    async def test_normalization_in_poll(
        self,
        mock_athena_client: AthenaClient,
        sample_rows_with_conversion: list[dict[str, str]],
    ):
        """Poll deve normalizar unidades nos resultados (fio2 percent→fraction, lactato mg/dL→mmol/L)."""
        from intensicare.core.redis import get_redis

        get_redis()
        tenant_id = "austa"
        domain = "sepsis"

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows_with_conversion,
            column_names=[
                "id",
                "patient_id",
                "parameter",
                "value",
                "unit_canonical",
                "ingested_at",
            ],
            total_rows=2,
            query_execution_id="test-exec-norm",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain(domain, tenant_id)

        assert result["status"] == "ok"
        assert result["rows_processed"] == 2
        assert result["normalization_errors"] == 0

        # Verifica que o Athena foi chamado
        mock_athena_client.execute_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_normalization_error_counted(self, mock_athena_client: AthenaClient):
        """Erros de normalização devem ser contados mas não devem quebrar o poll."""
        bad_rows = [
            {
                "id": "1",
                "patient_id": "P-001",
                "tenant_id": "austa",
                "parameter": "fio2",
                "value": "40",
                "unit_canonical": "invalid_unit",
                "ingested_at": "2026-07-05T10:05:00Z",
            },
        ]

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=bad_rows,
            column_names=[
                "id",
                "patient_id",
                "parameter",
                "value",
                "unit_canonical",
                "ingested_at",
            ],
            total_rows=1,
            query_execution_id="test-exec-err",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain("sepsis", "austa")

        assert result["status"] == "ok"
        assert result["rows_processed"] == 1
        assert result["normalization_errors"] == 1


# ---------------------------------------------------------------------------
# Test: Domain configuration
# ---------------------------------------------------------------------------


class TestDomainConfig:
    """Verifica configuração de domínios e cadências."""

    def test_valid_domains(self):
        """Domínios padrão devem ser reconhecidos."""
        poller = AthenaPoller(athena_client=mock_athena_client)
        for domain in [
            "sepsis",
            "electrolytes",
            "aki",
            "ventilation",
            "hemodynamics",
            "neurology",
            "medication",
        ]:
            cadence = poller.get_cadence(domain)
            assert cadence > 0, f"Domain {domain} should have positive cadence"

    def test_invalid_domain_raises_error(self):
        """Domínio inválido deve levantar DomainConfigError."""
        poller = AthenaPoller(athena_client=mock_athena_client)

        with pytest.raises(DomainConfigError, match="não reconhecido"):
            poller.get_cadence("invalid_domain")

    @pytest.mark.asyncio
    async def test_invalid_domain_poll_raises_error(self, mock_athena_client: AthenaClient):
        """Poll em domínio inválido deve levantar DomainConfigError."""
        poller = AthenaPoller(athena_client=mock_athena_client)

        with pytest.raises(DomainConfigError, match="não reconhecido"):
            await poller.poll_domain("invalid_domain", "austa")

    def test_cadence_overrides(self):
        """Cadências podem ser sobrescritas no construtor."""
        poller = AthenaPoller(
            athena_client=mock_athena_client,
            cadence_overrides={"sepsis": 60, "aki": 7200},
        )
        assert poller.get_cadence("sepsis") == 60
        assert poller.get_cadence("aki") == 7200
        # Domínio não sobrescrito mantém padrão
        assert poller.get_cadence("electrolytes") == DOMAIN_CADENCE["electrolytes"]

    def test_cadence_values(self):
        """Verifica cadências padrão documentadas."""
        assert DOMAIN_CADENCE["sepsis"] == 300  # 5 min
        assert DOMAIN_CADENCE["electrolytes"] == 120  # 2 min (expedited)
        assert DOMAIN_CADENCE["aki"] == 3600  # 1 h


# ---------------------------------------------------------------------------
# Test: Athena error handling
# ---------------------------------------------------------------------------


class TestAthenaErrorHandling:
    """Verifica tratamento de erros do Athena durante o poll."""

    @pytest.mark.asyncio
    async def test_athena_error_returns_status_error(self, mock_athena_client: AthenaClient):
        """Erro do Athena não deve quebrar o poll, apenas reportar status=error."""
        mock_athena_client.execute_query.side_effect = RuntimeError("Athena indisponível")

        poller = AthenaPoller(athena_client=mock_athena_client)

        result = await poller.poll_domain("sepsis", "austa")

        assert result["status"] == "error"
        assert "Athena indisponível" in result["error"]
        assert result["rows_processed"] == 0


# ---------------------------------------------------------------------------
# Test: poll_all_domains
# ---------------------------------------------------------------------------


class TestPollAllDomains:
    """Verifica a função de conveniência poll_all_domains."""

    @pytest.mark.asyncio
    async def test_poll_all_domains(self, mock_athena_client: AthenaClient):
        """poll_all_domains deve executar todos os domínios."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=[],
            column_names=[],
            total_rows=0,
            query_execution_id="test-exec-all",
        )

        results = await poll_all_domains(
            "austa", poller=AthenaPoller(athena_client=mock_athena_client)
        )

        # Todos os domínios devem estar no resultado
        for domain in DOMAIN_CADENCE:
            assert domain in results, f"Domain {domain} missing from results"
            assert results[domain]["status"] in ("ok", "empty", "error")


# ---------------------------------------------------------------------------
# Test: Per-tenant workgroup isolation
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """Verifica que queries usam o workgroup correto por tenant."""

    @pytest.mark.asyncio
    async def test_workgroup_isolation(
        self, mock_athena_client: AthenaClient, sample_rows: list[dict[str, str]]
    ):
        """Cada tenant deve usar seu próprio workgroup Athena."""
        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=sample_rows[:1],
            column_names=["id", "patient_id", "parameter", "value", "ingested_at"],
            total_rows=1,
            query_execution_id="test-exec-wg",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)

        await poller.poll_domain("ventilation", "tenant-hopsital")

        # Verifica que o workgroup contém o tenant_id
        call_kwargs = mock_athena_client.execute_query.call_args
        assert call_kwargs is not None
        # O argumento 'workgroup' deve ser passado
        _, kwargs = call_kwargs
        assert "workgroup" in kwargs
        assert "tenant-hopsital" in kwargs["workgroup"]


# ---------------------------------------------------------------------------
# Test: Edge-case — watermark missing column
# ---------------------------------------------------------------------------


class TestWatermarkEdgeCases:
    """Edge cases para watermark."""

    @pytest.mark.asyncio
    async def test_rows_without_watermark_column(self, mock_athena_client: AthenaClient):
        """Se as linhas não tiverem a coluna de watermark, mantém watermark atual."""
        from intensicare.core.redis import get_redis

        redis = get_redis()
        tenant_id = "austa"
        domain = "ventilation"
        watermark_key = f"gold:watermark:{tenant_id}:{domain}"

        await redis.set(watermark_key, "2026-07-04T12:00:00Z")

        rows_no_wm = [
            {
                "id": "1",
                "patient_id": "P-001",
                "parameter": "fio2",
                "value": "0.4",
                "unit_canonical": "fraction",
                # sem ingested_at
            },
        ]

        mock_athena_client.execute_query.return_value = AthenaQueryResult(
            rows=rows_no_wm,
            column_names=["id", "patient_id", "parameter", "value", "unit_canonical"],
            total_rows=1,
            query_execution_id="test-exec-nowm",
        )

        poller = AthenaPoller(athena_client=mock_athena_client)
        result = await poller.poll_domain(domain, tenant_id)

        assert result["status"] == "ok"
        # Watermark não avança porque não há coluna de timestamp
        assert result["new_watermark"] == "2026-07-04T12:00:00Z"

        stored = await redis.get(watermark_key)
        assert stored == "2026-07-04T12:00:00Z"
