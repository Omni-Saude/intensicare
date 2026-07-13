"""Cliente assíncrono para Amazon Athena via boto3 com retry e paginação.

Fornece:
- ``AthenaClient``: execução assíncrona de queries Athena com backoff exponencial
- Paginação automática de resultados
- Timeout e retry configuráveis
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
from typing import Any

import boto3
from botocore.config import Config as BotoCoreConfig

from intensicare.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração de retry / backoff
# ---------------------------------------------------------------------------

# Backoff exponencial (segundos): 1 → 2 → 4 → 8 → 16 → 32
BACKOFF_SCHEDULE: list[int] = [1, 2, 4, 8, 16, 32]
MAX_RETRIES: int = len(BACKOFF_SCHEDULE)
MAX_CONNECTIONS: int = 10


@dataclass
class AthenaQueryResult:
    """Resultado de uma query Athena."""

    rows: list[dict[str, Any]]
    column_names: list[str]
    total_rows: int
    query_execution_id: str


class AthenaThrottledError(Exception):
    """Erro levantado quando Athena retorna throttling (TooManyRequestsException)."""


class AthenaQueryTimeoutError(Exception):
    """Erro levantado quando a query excede o timeout."""


class AthenaClient:
    """Cliente assíncrono para Amazon Athena.

    Encapsula boto3 Athena client com:
    - Execução assíncrona de queries com polling
    - Retry automático em throttling (TooManyRequestsException)
    - Paginação de resultados
    - Timeout configurável

    Uso::

        client = AthenaClient()
        result = await client.execute_query(
            "SELECT * FROM vital_sign WHERE tenant_id = ?",
            parameters=["tenant-1"],
        )
    """

    def __init__(
        self,
        *,
        database: str | None = None,
        workgroup: str | None = None,
        output_location: str | None = None,
        region: str | None = None,
        max_retries: int = MAX_RETRIES,
        query_timeout: int = 300,
        poll_interval: float = 1.0,
    ) -> None:
        self.database = database or settings.athena_database
        self.workgroup = workgroup or settings.athena_workgroup
        self.output_location = output_location or settings.athena_output_location
        self.region = region or settings.athena_region
        self.max_retries = max_retries
        self.query_timeout = query_timeout
        self.poll_interval = poll_interval

        boto_config = BotoCoreConfig(
            max_pool_connections=MAX_CONNECTIONS,
            retries={"max_attempts": 3, "mode": "adaptive"},
        )
        self._client = boto3.client(
            "athena",
            region_name=self.region,
            config=boto_config,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute_query(
        self,
        query: str,
        *,
        parameters: list[str] | None = None,
        database: str | None = None,
        workgroup: str | None = None,
        max_rows: int = 10_000,
    ) -> AthenaQueryResult:
        """Executa uma query Athena e retorna o resultado paginado.

        Args:
            query: SQL a ser executada.
            parameters: Parâmetros posicionais (substituem ``?`` na query).
            database: Override do database padrão.
            workgroup: Override do workgroup padrão.
            max_rows: Número máximo de linhas a retornar.

        Returns:
            AthenaQueryResult com as linhas e metadados.

        Raises:
            AthenaThrottledError: Quando throttling persiste após retries.
            AthenaQueryTimeoutError: Quando a query excede o timeout.
        """
        # Passa a query com placeholders ? diretamente para o Athena;
        # os ExecutionParameters são enviados como parâmetros posicionais
        # (não fazemos substituição client-side — F-INT-001).
        db = database or self.database
        wg = workgroup or self.workgroup

        # Inicia a execução com retry em throttling
        query_execution_id = await self._start_query_execution(query, db, wg, parameters)

        # Aguarda conclusão com timeout
        await self._wait_for_completion(query_execution_id)

        # Coleta resultados paginados
        rows, column_names = await self._collect_results(query_execution_id, max_rows)

        return AthenaQueryResult(
            rows=rows,
            column_names=column_names,
            total_rows=len(rows),
            query_execution_id=query_execution_id,
        )

    async def get_query_status(self, query_execution_id: str) -> str:
        """Retorna o estado de uma execução Athena.

        Estados: QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED
        """
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.get_query_execution(QueryExecutionId=query_execution_id),
        )
        return response["QueryExecution"]["Status"]["State"]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    async def _start_query_execution(
        self,
        query: str,
        database: str,
        workgroup: str,
        parameters: list[str] | None = None,
    ) -> str:
        """Inicia a execução de uma query com retry em throttling."""
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                loop = asyncio.get_running_loop()
                kwargs: dict[str, Any] = {
                    "QueryString": query,
                    "QueryExecutionContext": {"Database": database},
                    "WorkGroup": workgroup,
                }
                if parameters:
                    kwargs["ExecutionParameters"] = parameters
                if self.output_location:
                    kwargs["ResultConfiguration"] = {"OutputLocation": self.output_location}

                # kwargs is rebuilt fresh each retry iteration and this lambda
                # is awaited (not stored/escaped) before the next iteration
                # reassigns it — the late-binding closure is safe here.
                response = await loop.run_in_executor(
                    None,
                    lambda: self._client.start_query_execution(**kwargs),  # noqa: B023
                )
                return response["QueryExecutionId"]

            except self._client.exceptions.TooManyRequestsException as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    delay = BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]
                    logger.warning(
                        "Athena throttled — retry %d/%d after %ds",
                        attempt + 1,
                        self.max_retries,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    raise AthenaThrottledError(
                        f"Athena throttling persistiu após {self.max_retries} retries"
                    ) from exc

            except Exception as exc:
                last_exception = exc
                if attempt < self.max_retries:
                    delay = BACKOFF_SCHEDULE[min(attempt, len(BACKOFF_SCHEDULE) - 1)]
                    logger.warning(
                        "Athena query start failed — retry %d/%d: %s",
                        attempt + 1,
                        self.max_retries,
                        exc,
                    )
                    await asyncio.sleep(delay)
                else:
                    raise

        # Unreachable — but keep mypy happy
        raise RuntimeError("Unexpected retry exhaustion") from last_exception

    async def _wait_for_completion(self, query_execution_id: str) -> None:
        """Aguarda a conclusão da query com polling."""
        elapsed = 0.0
        while elapsed < self.query_timeout:
            status = await self.get_query_status(query_execution_id)

            if status == "SUCCEEDED":
                return
            if status in ("FAILED", "CANCELLED"):
                # Busca detalhes do erro
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self._client.get_query_execution(QueryExecutionId=query_execution_id),
                )
                reason = response["QueryExecution"]["Status"].get("StateChangeReason", "Unknown")
                raise RuntimeError(f"Athena query {status}: {reason}")

            await asyncio.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise AthenaQueryTimeoutError(
            f"Query {query_execution_id} excedeu timeout de {self.query_timeout}s"
        )

    async def _collect_results(
        self, query_execution_id: str, max_rows: int
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Coleta resultados paginados da query."""
        rows: list[dict[str, Any]] = []
        column_names: list[str] = []
        next_token: str | None = None

        loop = asyncio.get_running_loop()

        while len(rows) < max_rows:
            kwargs: dict[str, Any] = {
                "QueryExecutionId": query_execution_id,
                "MaxResults": min(max_rows - len(rows), 1000),
            }
            if next_token:
                kwargs["NextToken"] = next_token

            # kwargs is rebuilt fresh each poll iteration and this lambda is
            # awaited (not stored/escaped) before the next iteration
            # reassigns it — the late-binding closure is safe here.
            response = await loop.run_in_executor(
                None,
                lambda: self._client.get_query_results(**kwargs),  # noqa: B023
            )

            result_set = response["ResultSet"]

            # Extrai nomes das colunas na primeira página
            if not column_names and "Rows" in result_set:
                header_row = result_set["Rows"][0]
                column_names = [
                    col.get("VarCharValue", col.get("Name", ""))
                    for col in header_row.get("Data", [])
                ]

            # Extrai linhas de dados
            data_rows = result_set.get("Rows", [])
            if len(data_rows) <= 1 and not next_token:
                # Apenas header, sem dados
                break

            start = 1 if not next_token else 0  # skip header on first page
            for row_data in data_rows[start:]:
                row: dict[str, Any] = {}
                for i, col in enumerate(row_data.get("Data", [])):
                    col_name = column_names[i] if i < len(column_names) else f"col_{i}"
                    row[col_name] = col.get("VarCharValue")
                rows.append(row)

            next_token = response.get("NextToken")
            if not next_token:
                break

        return rows, column_names
