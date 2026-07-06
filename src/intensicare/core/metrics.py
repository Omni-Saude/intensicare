"""
Métricas Prometheus — contadores, histogramas e gauges para observabilidade.

ADR-001 / CON-0006: Métricas emitidas via OpenTelemetry → AMP (Prometheus
remote-write). Este módulo expõe:

- Contadores: ``ingested_rows``, ``alerts_raised``, ``retries_total``,
  ``dlq_arrivals``.
- Histogramas: latência por estágio (matching observability-slo.md §3),
  ``alert_evaluation_duration``.
- Gauges: ``last_poll_success_at``, ``last_score_at`` por ``(unit, domain)``.
- Endpoint ``/metrics`` no formato Prometheus (text/plain).

Uso típico::

    from intensicare.core.metrics import (
        setup_metrics_endpoint,
        INGESTED_ROWS,
        ALERTS_RAISED,
        STAGE_LATENCY,
    )

    # Na inicialização da app FastAPI:
    setup_metrics_endpoint(app)

    # Durante o processamento:
    INGESTED_ROWS.add(1, {"domain": "hemodynamics", "unit_id": "UTI-A"})
    STAGE_LATENCY.record(0.450, {"stage": "normalize"})
"""

from __future__ import annotations

import logging
import time
from typing import Any

from fastapi import FastAPI, Response

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tipos para rótulos (labels)
# ---------------------------------------------------------------------------

_DomainLabels = dict[str, str]  # ex: {"domain": "sepsis", "unit_id": "UTI-A"}
_StageLabels = dict[str, str]  # ex: {"stage": "evaluate"}

# ---------------------------------------------------------------------------
# Contadores (Counter)
# ---------------------------------------------------------------------------


class _PrometheusCounter:
    """Contador monotônico no estilo Prometheus.

    Suporta múltiplos conjuntos de labels. Thread-safe.
    Thread-safe via dict interno (sem lock — adequado para single-thread
    async FastAPI + múltiplos workers; se necessário, migrar para
    threading.Lock ou prometheus_client oficial).
    """

    def __init__(self, name: str, help_: str, label_names: list[str] | None = None):
        self.name = name
        self.help = help_
        self.label_names = label_names or []
        self._values: dict[tuple[tuple[str, str], ...], float] = {}
        self._created_at = time.time()

    def add(self, amount: float = 1, labels: dict[str, str] | None = None) -> None:
        """Incrementa o contador em ``amount``."""
        key = _labels_to_key(labels or {}, self.label_names)
        self._values[key] = self._values.get(key, 0.0) + amount

    def get(self, labels: dict[str, str] | None = None) -> float:
        """Retorna o valor atual do contador para os labels fornecidos."""
        key = _labels_to_key(labels or {}, self.label_names)
        return self._values.get(key, 0.0)

    def collect(self) -> list[str]:
        """Gera as linhas no formato de exposição Prometheus."""
        lines: list[str] = []
        lines.append(f"# HELP {self.name} {self.help}")
        lines.append(f"# TYPE {self.name} counter")
        for label_tuple, value in self._values.items():
            label_str = _format_labels(dict(label_tuple))
            lines.append(f"{self.name}{label_str} {_format_value(value)}")
        return lines


class _PrometheusGauge:
    """Gauge no estilo Prometheus — valor que sobe e desce."""

    def __init__(self, name: str, help_: str, label_names: list[str] | None = None):
        self.name = name
        self.help = help_
        self.label_names = label_names or []
        self._values: dict[tuple[tuple[str, str], ...], float] = {}

    def set(self, value: float, labels: dict[str, str] | None = None) -> None:
        """Define o valor do gauge."""
        key = _labels_to_key(labels or {}, self.label_names)
        self._values[key] = value

    def get(self, labels: dict[str, str] | None = None) -> float:
        """Retorna o valor atual."""
        key = _labels_to_key(labels or {}, self.label_names)
        return self._values.get(key, 0.0)

    def collect(self) -> list[str]:
        """Gera as linhas no formato Prometheus."""
        lines: list[str] = []
        lines.append(f"# HELP {self.name} {self.help}")
        lines.append(f"# TYPE {self.name} gauge")
        for label_tuple, value in self._values.items():
            label_str = _format_labels(dict(label_tuple))
            lines.append(f"{self.name}{label_str} {_format_value(value)}")
        return lines


class _PrometheusHistogram:
    """Histograma no estilo Prometheus com buckets configuráveis.

    Acumula contagem, soma e buckets.
    """

    def __init__(
        self,
        name: str,
        help_: str,
        label_names: list[str] | None = None,
        buckets: list[float] | None = None,
    ):
        self.name = name
        self.help = help_
        self.label_names = label_names or []
        self.buckets = sorted(buckets or _default_latency_buckets())
        self._count: dict[tuple[tuple[str, str], ...], float] = {}
        self._sum: dict[tuple[tuple[str, str], ...], float] = {}
        self._bucket_counts: dict[
            tuple[tuple[tuple[str, str], ...], float], float
        ] = {}
        self._created_at = time.time()

    def observe(self, amount: float, labels: dict[str, str] | None = None) -> None:
        """Registra uma observação no histograma."""
        key = _labels_to_key(labels or {}, self.label_names)

        # count
        self._count[key] = self._count.get(key, 0.0) + 1.0

        # sum
        self._sum[key] = self._sum.get(key, 0.0) + amount

        # buckets
        for bucket in self.buckets:
            if amount <= bucket:
                bk = (key, bucket)
                self._bucket_counts[bk] = self._bucket_counts.get(bk, 0.0) + 1.0

    def record(self, amount: float, labels: dict[str, str] | None = None) -> None:
        """Alias para ``observe`` — compatível com a API OTEL."""
        self.observe(amount, labels)

    def collect(self) -> list[str]:
        """Gera as linhas no formato Prometheus."""
        lines: list[str] = []
        lines.append(f"# HELP {self.name} {self.help}")
        lines.append(f"# TYPE {self.name} histogram")

        for key, count_val in self._count.items():
            label_str = _format_labels(dict(key))
            sum_val = self._sum.get(key, 0.0)
            lines.append(f"{self.name}_count{label_str} {_format_value(count_val)}")
            lines.append(f"{self.name}_sum{label_str} {_format_value(sum_val)}")
            lines.append(
                f"{self.name}_created{label_str} {_format_value(self._created_at)}"
            )

            cumulative = 0.0
            for bucket in self.buckets:
                bk = (key, bucket)
                cumulative += self._bucket_counts.get(bk, 0.0)
                bucket_label_str = _format_labels(
                    dict(key) | {"le": str(bucket)}
                )
                lines.append(
                    f"{self.name}_bucket{bucket_label_str} {_format_value(cumulative)}"
                )
            # +Inf bucket
            inf_label = _format_labels(dict(key) | {"le": "+Inf"})
            lines.append(
                f"{self.name}_bucket{inf_label} {_format_value(cumulative)}"
            )

        return lines


# ---------------------------------------------------------------------------
# Helpers para labels
# ---------------------------------------------------------------------------


def _labels_to_key(
    labels: dict[str, str], label_names: list[str]
) -> tuple[tuple[str, str], ...]:
    """Converte labels para uma tupla determinística."""
    return tuple(
        (name, labels.get(name, ""))
        for name in sorted(label_names or labels.keys())
    )


def _format_labels(labels: dict[str, str]) -> str:
    """Formata labels no estilo Prometheus: {key="value",...}."""
    if not labels:
        return ""
    parts = []
    for k, v in sorted(labels.items()):
        # Escapa aspas duplas e backslashes
        v_escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        parts.append(f'{k}="{v_escaped}"')
    return "{" + ",".join(parts) + "}"


def _format_value(value: float) -> str:
    """Formata valor como string, evitando notação científica quando possível."""
    if value == int(value):
        return str(int(value))
    return f"{value:.6g}"


def _default_latency_buckets() -> list[float]:
    """Buckets padrão para histogramas de latência (segundos).

    Cobre de 1ms até 30s — alinhado ao SLO de 30s (VIS-C-09).
    """
    return [
        0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5,
        1.0, 2.5, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0,
    ]


# ---------------------------------------------------------------------------
# Métricas instanciadas (singletons a nível de módulo)
# ---------------------------------------------------------------------------

# Contadores
INGESTED_ROWS = _PrometheusCounter(
    "intensicare_ingested_rows_total",
    "Total de registros vitais ingeridos pelo pipeline.",
    label_names=["domain", "unit_id", "evaluation_mode"],
)

ALERTS_RAISED = _PrometheusCounter(
    "intensicare_alerts_raised_total",
    "Total de alertas clínicos disparados.",
    label_names=["domain", "unit_id", "severity", "alert_definition_id"],
)

RETRIES_TOTAL = _PrometheusCounter(
    "intensicare_retries_total",
    "Total de tentativas de reentrega de notificações.",
    label_names=["channel", "severity"],
)

DLQ_ARRIVALS = _PrometheusCounter(
    "intensicare_dlq_arrivals_total",
    "Total de notificações que esgotaram retentativas e foram para a DLQ.",
    label_names=["channel", "severity"],
)

# Histogramas
STAGE_LATENCY = _PrometheusHistogram(
    "intensicare_stage_latency_seconds",
    "Latência por estágio do pipeline (observability-slo.md §3).",
    label_names=["stage", "evaluation_mode", "domain"],
    buckets=_default_latency_buckets(),
)

ALERT_EVALUATION_DURATION = _PrometheusHistogram(
    "intensicare_alert_evaluation_duration_seconds",
    "Duração da avaliação de alertas (evaluate stage).",
    label_names=["domain", "alert_definition_id"],
    buckets=_default_latency_buckets(),
)

# Gauges
LAST_POLL_SUCCESS_AT = _PrometheusGauge(
    "intensicare_last_poll_success_at_seconds",
    "Timestamp Unix do último poll bem-sucedido por (unit, domain).",
    label_names=["unit_id", "domain"],
)

LAST_SCORE_AT = _PrometheusGauge(
    "intensicare_last_score_at_seconds",
    "Timestamp Unix do último score computado por (unit, domain).",
    label_names=["unit_id", "domain"],
)

# ---------------------------------------------------------------------------
# Coleta e exposição via endpoint /metrics
# ---------------------------------------------------------------------------

# Registro central de todos os coletores.
_ALL_COLLECTORS: list[Any] = [
    INGESTED_ROWS,
    ALERTS_RAISED,
    RETRIES_TOTAL,
    DLQ_ARRIVALS,
    STAGE_LATENCY,
    ALERT_EVALUATION_DURATION,
    LAST_POLL_SUCCESS_AT,
    LAST_SCORE_AT,
]


def collect_all_metrics() -> str:
    """Gera a saída completa no formato de exposição Prometheus (text/plain)."""
    lines: list[str] = []
    for collector in _ALL_COLLECTORS:
        lines.extend(collector.collect())
    lines.append("# EOF")
    return "\n".join(lines) + "\n"


def setup_metrics_endpoint(app: FastAPI, path: str = "/metrics") -> None:
    """Registra o endpoint ``/metrics`` na aplicação FastAPI.

    Exemplo::

        from fastapi import FastAPI
        from intensicare.core.metrics import setup_metrics_endpoint

        app = FastAPI()
        setup_metrics_endpoint(app)

    Args:
        app: Instância da aplicação FastAPI.
        path: Caminho do endpoint (default: ``/metrics``).
    """

    @app.get(path, include_in_schema=False)
    async def metrics_endpoint() -> Response:
        """Endpoint Prometheus — expõe métricas no formato text/plain."""
        output = collect_all_metrics()
        return Response(
            content=output,
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    logger.info("Endpoint /metrics registrado em %s", path)


# ---------------------------------------------------------------------------
# Registro de latência de estágio — helper de conveniência
# ---------------------------------------------------------------------------


def record_stage_latency(
    stage: str,
    duration_seconds: float,
    *,
    evaluation_mode: str = "",
    domain: str = "",
) -> None:
    """Registra a latência de um estágio do pipeline.

    Args:
        stage: Nome do estágio (``poll_nrt``, ``normalize``, etc.).
        duration_seconds: Duração em segundos.
        evaluation_mode: Modo de avaliação (opcional).
        domain: Domínio clínico (opcional).
    """
    labels: dict[str, str] = {"stage": stage}
    if evaluation_mode:
        labels["evaluation_mode"] = evaluation_mode
    if domain:
        labels["domain"] = domain
    STAGE_LATENCY.record(duration_seconds, labels)


def record_poll_success(unit_id: str, domain: str) -> None:
    """Registra um poll bem-sucedido, atualizando o gauge de timestamp."""
    LAST_POLL_SUCCESS_AT.set(time.time(), {"unit_id": unit_id, "domain": domain})


def record_score(unit_id: str, domain: str) -> None:
    """Registra um score computado, atualizando o gauge de timestamp."""
    LAST_SCORE_AT.set(time.time(), {"unit_id": unit_id, "domain": domain})
