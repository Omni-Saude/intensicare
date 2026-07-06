"""Gold Reader — Athena Poller incremental com high-watermark e backpressure.

WO-019: Implementa o poller Athena que lê dados Gold incrementalmente,
aplica normalização de unidades canônicas na borda (edge) e gerencia
backpressure para evitar polls concorrentes.

Arquitetura:
- High-watermark por domínio/tenant via Redis (``last_polled_at``)
- Cadência configurável por domínio (sepsis=5min, aki=1h, electrolytes=2min)
- Per-tenant Athena workgroup isolation
- Cadence backpressure: skip poll se anterior ainda em execução
- Canonical-unit normalization na borda usando units_normalizer
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from intensicare.clients.athena_client import AthenaClient, AthenaQueryResult
from intensicare.core.redis import get_redis
from intensicare.services.gold_schema import (
    DOMAIN_CADENCE,
    DOMAIN_WATERMARK_COLUMN,
    build_domain_query,
)
from intensicare.services.units_normalizer import normalize_value, UnitNormalizationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes Redis
# ---------------------------------------------------------------------------

# Prefixo para chaves de watermark: "gold:watermark:{tenant}:{domain}"
WATERMARK_KEY_PREFIX = "gold:watermark"

# Prefixo para lock de backpressure: "gold:lock:{tenant}:{domain}"
LOCK_KEY_PREFIX = "gold:lock"

# TTL do lock de backpressure (segundos) — evita lock eterno se crash
LOCK_TTL = 600  # 10 minutos

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------


class BackpressureError(Exception):
    """Levantado quando um poll é ignorado por backpressure (poll anterior em execução)."""


class DomainConfigError(Exception):
    """Levantado quando um domínio não é reconhecido."""


# ---------------------------------------------------------------------------
# AthenaPoller
# ---------------------------------------------------------------------------


class AthenaPoller:
    """Poller Athena incremental com high-watermark e backpressure.

    Responsável por:
    1. Verificar se o poll anterior para o mesmo domínio/tenant ainda está
       em execução (backpressure) — se sim, skip.
    2. Obter o último watermark (timestamp) processado do Redis.
    3. Executar query Athena incremental (``WHERE ingested_at > watermark``).
    4. Normalizar unidades dos resultados usando o registry canônico.
    5. Atualizar o watermark no Redis com o maior timestamp encontrado.

    Uso::

        poller = AthenaPoller(athena_client=AthenaClient())
        results = await poller.poll_domain("sepsis", "tenant-austa")
    """

    def __init__(
        self,
        *,
        athena_client: AthenaClient | None = None,
        cadence_overrides: dict[str, int] | None = None,
        lock_ttl: int = LOCK_TTL,
    ) -> None:
        """
        Args:
            athena_client: Cliente Athena. Se None, cria um default.
            cadence_overrides: Overrides de cadência por domínio (segundos).
            lock_ttl: TTL do lock de backpressure (segundos).
        """
        self._athena = athena_client or AthenaClient()
        self._cadence = {**DOMAIN_CADENCE, **(cadence_overrides or {})}
        self._lock_ttl = lock_ttl

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def poll_domain(
        self,
        domain: str,
        tenant_id: str,
        *,
        limit: int = 10_000,
        force_full_load: bool = False,
    ) -> dict[str, Any]:
        """Executa um poll incremental para um domínio e tenant.

        Fluxo completo:
        1. Backpressure check — adquire lock, skip se já em execução.
        2. Lê watermark do Redis.
        3. Executa query Athena incremental.
        4. Normaliza unidades dos resultados.
        5. Atualiza watermark.
        6. Libera lock.

        Args:
            domain: Domínio clínico (ex: ``"sepsis"``, ``"electrolytes"``).
            tenant_id: Tenant para isolamento de workgroup.
            limit: Máximo de linhas por poll.
            force_full_load: Se True, ignora watermark (full reload).

        Returns:
            Dict com:
            - ``status``: ``"ok"``, ``"skipped"`` (backpressure), ``"empty"``
            - ``rows_processed``: número de linhas processadas
            - ``new_watermark``: novo watermark (ISO-8601) ou None
            - ``normalization_errors``: contagem de erros de normalização

        Raises:
            BackpressureError: Se poll ignorado por backpressure.
            DomainConfigError: Se domínio não reconhecido.
        """
        if domain not in self._cadence:
            raise DomainConfigError(
                f"Domínio '{domain}' não reconhecido. "
                f"Disponíveis: {sorted(self._cadence.keys())}"
            )

        redis = get_redis()
        lock_key = f"{LOCK_KEY_PREFIX}:{tenant_id}:{domain}"

        # 1. Backpressure: tenta adquirir lock
        acquired = await redis.set(lock_key, "1", nx=True, ex=self._lock_ttl)
        if not acquired:
            logger.info(
                "Backpressure: poll ignorado para %s/%s — anterior em execução",
                tenant_id, domain,
            )
            return {
                "status": "skipped",
                "reason": "backpressure",
                "domain": domain,
                "tenant_id": tenant_id,
                "rows_processed": 0,
                "new_watermark": None,
                "normalization_errors": 0,
            }

        try:
            return await self._execute_poll(
                domain, tenant_id, redis, limit, force_full_load
            )
        finally:
            # Libera o lock (apenas se ainda for nosso)
            await redis.delete(lock_key)

    async def get_last_watermark(
        self, tenant_id: str, domain: str
    ) -> str | None:
        """Retorna o último watermark (timestamp ISO-8601) para um domínio/tenant.

        Returns:
            Timestamp ISO-8601 ou None se nunca foi processado.
        """
        redis = get_redis()
        key = f"{WATERMARK_KEY_PREFIX}:{tenant_id}:{domain}"
        return await redis.get(key)

    async def reset_watermark(self, tenant_id: str, domain: str) -> None:
        """Reseta o watermark para forçar full reload no próximo poll."""
        redis = get_redis()
        key = f"{WATERMARK_KEY_PREFIX}:{tenant_id}:{domain}"
        await redis.delete(key)
        logger.info("Watermark resetado: %s/%s", tenant_id, domain)

    def get_cadence(self, domain: str) -> int:
        """Retorna a cadência (segundos) para um domínio."""
        if domain not in self._cadence:
            raise DomainConfigError(f"Domínio '{domain}' não reconhecido")
        return self._cadence[domain]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _execute_poll(
        self,
        domain: str,
        tenant_id: str,
        redis: Any,
        limit: int,
        force_full_load: bool,
    ) -> dict[str, Any]:
        """Executa o poll real (dentro do lock)."""
        watermark_key = f"{WATERMARK_KEY_PREFIX}:{tenant_id}:{domain}"

        # 2. Lê watermark
        last_watermark: str | None = None
        if not force_full_load:
            last_watermark = await redis.get(watermark_key)

        logger.info(
            "Poll iniciado: domain=%s tenant=%s watermark=%s",
            domain, tenant_id, last_watermark or "(full load)",
        )

        # 3. Query Athena
        query = build_domain_query(
            domain, tenant_id, last_watermark, limit=limit
        )
        logger.debug("Athena query: %s", query)

        try:
            result: AthenaQueryResult = await self._athena.execute_query(
                query, workgroup=f"{tenant_id}-{domain}"
            )
        except Exception as exc:
            logger.error("Athena query falhou: domain=%s tenant=%s error=%s",
                         domain, tenant_id, exc)
            return {
                "status": "error",
                "domain": domain,
                "tenant_id": tenant_id,
                "error": str(exc),
                "rows_processed": 0,
                "new_watermark": last_watermark,
                "normalization_errors": 0,
            }

        if not result.rows:
            logger.info("Poll vazio: domain=%s tenant=%s", domain, tenant_id)
            return {
                "status": "empty",
                "domain": domain,
                "tenant_id": tenant_id,
                "rows_processed": 0,
                "new_watermark": last_watermark,
                "normalization_errors": 0,
            }

        # 4. Normaliza unidades na borda
        normalized_rows, norm_errors = self._normalize_rows(
            result.rows,
            domain,
            watermark_column=DOMAIN_WATERMARK_COLUMN.get(domain, "ingested_at"),
        )

        # 5. Determina novo watermark (maior timestamp nos resultados)
        new_watermark = self._compute_new_watermark(
            normalized_rows,
            domain,
            last_watermark,
        )

        # 6. Atualiza watermark no Redis
        if new_watermark and new_watermark != last_watermark:
            await redis.set(watermark_key, new_watermark)
            logger.info(
                "Watermark avançado: domain=%s tenant=%s %s → %s",
                domain, tenant_id, last_watermark, new_watermark,
            )

        logger.info(
            "Poll concluído: domain=%s tenant=%s rows=%d errors=%d",
            domain, tenant_id, len(normalized_rows), norm_errors,
        )

        return {
            "status": "ok",
            "domain": domain,
            "tenant_id": tenant_id,
            "rows_processed": len(normalized_rows),
            "new_watermark": new_watermark,
            "normalization_errors": norm_errors,
            "query_execution_id": result.query_execution_id,
        }

    def _normalize_rows(
        self,
        rows: list[dict[str, Any]],
        domain: str,  # noqa: ARG002 — reservado para normalização domain-specific
        *,
        watermark_column: str = "ingested_at",
    ) -> tuple[list[dict[str, Any]], int]:
        """Normaliza unidades canônicas nos resultados da query.

        Para cada linha que contém ``parameter`` e ``unit_canonical``,
        aplica ``normalize_value`` para garantir que o ``value`` está
        na unidade canônica.

        Returns:
            Tuple de (rows normalizadas, contagem de erros).
        """
        normalized: list[dict[str, Any]] = []
        errors = 0

        for row in rows:
            parameter = row.get("parameter")
            value_str = row.get("value")
            unit = row.get("unit_canonical")

            if parameter and value_str is not None and unit:
                try:
                    value = float(value_str)
                    canonical_value = normalize_value(parameter, value, unit)
                    row["value"] = str(canonical_value)
                    row["unit_canonical"] = unit  # mantém unidade canônica
                except (ValueError, UnitNormalizationError) as exc:
                    logger.warning(
                        "Normalização falhou: param=%s value=%s unit=%s error=%s",
                        parameter, value_str, unit, exc,
                    )
                    errors += 1
                    # Mantém a linha original, mas marca o erro
                    row["_normalization_error"] = str(exc)

            normalized.append(row)

        return normalized, errors

    def _compute_new_watermark(
        self,
        rows: list[dict[str, Any]],
        domain: str,
        current_watermark: str | None,
    ) -> str | None:
        """Calcula o novo watermark como o maior timestamp nos resultados.

        Usa a coluna de watermark do domínio (ex: ``ingested_at``).
        Se não houver timestamps nos resultados, mantém o watermark atual.
        """
        wm_col = DOMAIN_WATERMARK_COLUMN.get(domain, "ingested_at")

        max_ts: str | None = current_watermark
        for row in rows:
            ts = row.get(wm_col)
            if ts and (max_ts is None or ts > max_ts):
                max_ts = ts

        return max_ts


# ---------------------------------------------------------------------------
# Função de conveniência para polling agendado
# ---------------------------------------------------------------------------


async def poll_all_domains(
    tenant_id: str,
    *,
    poller: AthenaPoller | None = None,
    limit: int = 10_000,
) -> dict[str, dict[str, Any]]:
    """Executa poll em todos os domínios para um tenant.

    Cada domínio é executado sequencialmente; se um domínio estiver em
    backpressure, é ignorado (skip) sem bloquear os demais.

    Args:
        tenant_id: Tenant alvo.
        poller: Instância de AthenaPoller. Se None, cria default.
        limit: Máximo de linhas por domínio.

    Returns:
        Dict mapeando domínio → resultado do poll.
    """
    p = poller or AthenaPoller()
    results: dict[str, dict[str, Any]] = {}

    for domain in sorted(p._cadence.keys()):
        try:
            results[domain] = await p.poll_domain(domain, tenant_id, limit=limit)
        except Exception as exc:
            logger.error("Poll falhou: domain=%s error=%s", domain, exc)
            results[domain] = {
                "status": "error",
                "domain": domain,
                "error": str(exc),
            }

    return results
