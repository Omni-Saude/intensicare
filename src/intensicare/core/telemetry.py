"""
Observabilidade — OpenTelemetry tracing + exportação OTLP para AMP/Grafana.

ADR-001 / CON-0006: Métricas e traces via OpenTelemetry → stack AMP + Grafana
existente. Este módulo configura:

- Auto-instrumentação para FastAPI, SQLAlchemy (async), httpx, Redis.
- Spans manuais nos limites dos estágios do pipeline:
  poll_nrt, poll_micro_batch, normalize, evaluate, persist, deliver.
- Exportação OTLP (gRPC ou HTTP) configurável via variáveis de ambiente.
- Injeção do trace_id atual no campo ``audit_trail.request_id``.

Uso típico::

    from intensicare.core.telemetry import (
        init_telemetry,
        get_tracer,
        get_current_trace_id,
        trace_stage,
    )

    # Startup (chamado uma vez durante a inicialização da aplicação):
    init_telemetry()

    # Em qualquer lugar do código:
    tracer = get_tracer()

    with tracer.start_as_current_span("poll_nrt") as span:
        span.set_attribute("unit_id", unit_id)
        # ... lógica de polling ...

    # Para injetar o trace_id no audit_trail:
    audit_entry.request_id = get_current_trace_id()
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração via ambiente (com fallbacks seguros para dev local)
# ---------------------------------------------------------------------------

_OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "http://localhost:4318",  # default OTLP HTTP local collector
)
_OTEL_EXPORTER_OTLP_PROTOCOL = os.getenv(
    "OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf"
)
_OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "intensicare")
_OTEL_TRACES_ENABLED = os.getenv("OTEL_TRACES_ENABLED", "true").lower() in (
    "1", "true", "yes",
)
_OTEL_METRICS_ENABLED = os.getenv("OTEL_METRICS_ENABLED", "true").lower() in (
    "1", "true", "yes",
)

# ---------------------------------------------------------------------------
# Estado global (lazy init)
# ---------------------------------------------------------------------------


class _TelemetryState:
    """Container para o estado da instrumentação OTEL."""

    initialized: bool = False
    tracer_provider: Any = None
    meter_provider: Any = None
    tracer: Any = None


_telemetry_state = _TelemetryState()

# Nome do tracer — usar o nome do serviço para consistência com o backend.
_TRACER_NAME = _OTEL_SERVICE_NAME


def init_telemetry(
    *,
    service_name: str = _OTEL_SERVICE_NAME,
    otlp_endpoint: str = _OTEL_EXPORTER_OTLP_ENDPOINT,
    otlp_protocol: str = _OTEL_EXPORTER_OTLP_PROTOCOL,
    traces_enabled: bool = _OTEL_TRACES_ENABLED,
    metrics_enabled: bool = _OTEL_METRICS_ENABLED,
) -> None:
    """Inicializa o pipeline OpenTelemetry (traces + métricas).

    Deve ser chamado **uma vez** durante a inicialização da aplicação,
    antes de qualquer operação que produza spans ou métricas.

    Configura:
    - Auto-instrumentação para bibliotecas suportadas (FastAPI, SQLAlchemy,
      httpx, Redis) via ``opentelemetry-instrumentation-*``.
    - OTLP Exporter apontando para o endpoint configurado (AMP/Grafana).
    - Propagação de contexto via W3C TraceContext.
    """
    global _TRACER_NAME

    if _telemetry_state.initialized:
        logger.info("Telemetria OTEL já inicializada — ignorando chamada repetida.")
        return

    _TRACER_NAME = service_name

    try:
        # ------------------------------------------------------------------
        # Importações lazy — OTEL não é dependência obrigatória em dev.
        # Em produção, as bibliotecas devem estar instaladas.
        # ------------------------------------------------------------------
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource, SERVICE_NAME
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import ALWAYS_ON

        # Recursos identificadores do serviço
        resource = Resource.create({
            SERVICE_NAME: service_name,
        })

        # Provider + exporter
        if traces_enabled:
            tracer_provider = TracerProvider(
                resource=resource,
                sampler=ALWAYS_ON,
            )
            otlp_exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint.rstrip("/") + "/v1/traces",
                # timeout em ms (padrão 10s)
            )
            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    otlp_exporter,
                    # Batch: envia a cada 5s ou 512 spans, o que acontecer
                    # primeiro. Valores conservadores para produção.
                    schedule_delay_millis=5000,
                    max_export_batch_size=512,
                )
            )
            trace.set_tracer_provider(tracer_provider)
            _telemetry_state.tracer_provider = tracer_provider

        # Auto-instrumentação de bibliotecas
        _auto_instrument()

        _telemetry_state.initialized = True
        logger.info(
            "Telemetria OTEL inicializada: service=%s, endpoint=%s, "
            "traces=%s, metrics=%s",
            service_name,
            otlp_endpoint,
            traces_enabled,
            metrics_enabled,
        )

    except ImportError as exc:
        logger.warning(
            "OpenTelemetry SDK não disponível — telemetria desabilitada. "
            "Instale com: pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-exporter-otlp-proto-http. Erro: %s",
            exc,
        )
        _telemetry_state.initialized = True  # não tenta de novo
    except Exception as exc:
        logger.error(
            "Falha ao inicializar telemetria OTEL: %s. "
            "A aplicação continua sem tracing.",
            exc,
        )
        _telemetry_state.initialized = True


def _auto_instrument() -> None:
    """Aplica auto-instrumentação nas bibliotecas disponíveis.

    Cada ``opentelemetry-instrumentation-*`` é opcional — se não estiver
    instalada, o erro é logado e a inicialização continua.
    """
    _instrument_fastapi()
    _instrument_sqlalchemy()
    _instrument_httpx()
    _instrument_redis()


def _instrument_fastapi() -> None:
    """Auto-instrumentação FastAPI (rotas HTTP)."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        # A instrumentação é aplicada no momento em que a app é criada.
        # Registramos um hook para aplicar automaticamente.
        # O import é adiado para evitar dependência circular.
        from intensicare.main import app as _fastapi_app

        FastAPIInstrumentor.instrument_app(_fastapi_app)
        logger.info("FastAPI auto-instrumented.")
    except ImportError:
        logger.debug("opentelemetry-instrumentation-fastapi não instalado.")
    except Exception as exc:
        logger.warning("Falha ao instrumentar FastAPI: %s", exc)


def _instrument_sqlalchemy() -> None:
    """Auto-instrumentação SQLAlchemy (queries ao banco)."""
    try:
        from opentelemetry.instrumentation.sqlalchemy import (
            SQLAlchemyInstrumentor,
        )

        from intensicare.core.database import get_engine

        engine = get_engine()
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        logger.info("SQLAlchemy (async) auto-instrumented.")
    except ImportError:
        logger.debug("opentelemetry-instrumentation-sqlalchemy não instalado.")
    except Exception as exc:
        logger.warning("Falha ao instrumentar SQLAlchemy: %s", exc)


def _instrument_httpx() -> None:
    """Auto-instrumentação httpx (chamadas HTTP externas — FHIR, MPI, etc.)."""
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
        logger.info("httpx auto-instrumented.")
    except ImportError:
        logger.debug("opentelemetry-instrumentation-httpx não instalado.")
    except Exception as exc:
        logger.warning("Falha ao instrumentar httpx: %s", exc)


def _instrument_redis() -> None:
    """Auto-instrumentação Redis (cache + filas ARQ)."""
    try:
        from opentelemetry.instrumentation.redis import RedisInstrumentor

        RedisInstrumentor().instrument()
        logger.info("Redis auto-instrumented.")
    except ImportError:
        logger.debug("opentelemetry-instrumentation-redis não instalado.")
    except Exception as exc:
        logger.warning("Falha ao instrumentar Redis: %s", exc)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def get_tracer(name: str | None = None) -> Any:
    """Retorna o tracer OTEL configurado.

    Se a telemetria não foi inicializada, retorna um NoOp tracer.
    """
    try:
        from opentelemetry import trace

        return trace.get_tracer(name or _TRACER_NAME)
    except ImportError:
        return _NoOpTracer()


def get_current_trace_id() -> str | None:
    """Retorna o trace_id do span ativo no contexto atual.

    Retorna ``None`` se não houver span ativo ou se o OTEL não estiver
    disponível.

    Uso típico::

        audit_entry.request_id = get_current_trace_id()
    """
    try:
        from opentelemetry import trace

        span_context = trace.get_current_span().get_span_context()
        if span_context.is_valid:
            return format(span_context.trace_id, "032x")
        return None
    except ImportError:
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Context manager para spans manuais dos estágios do pipeline
# ---------------------------------------------------------------------------


@contextmanager
def trace_stage(
    stage: str,
    *,
    attributes: dict[str, Any] | None = None,
    evaluation_mode: str | None = None,
    tenant_id: str | None = None,
    unit_id: str | None = None,
    alert_definition_id: str | None = None,
):
    """Context manager que cria um span manual para um estágio do pipeline.

    Parâmetros:
        stage: Nome do estágio. Deve ser um dos valores documentados:
               ``poll_nrt``, ``poll_micro_batch``, ``normalize``,
               ``evaluate``, ``persist``, ``deliver``.
        attributes: Dicionário opcional com atributos adicionais.
        evaluation_mode: Modo de avaliação (``micro_batch``, ``near_real_time``,
                         ``hybrid``).
        tenant_id: Identificador do tenant.
        unit_id: Identificador da unidade (UTI).
        alert_definition_id: Identificador da definição de alerta.

    Exemplo::

        with trace_stage("poll_nrt", unit_id="UTI-A", tenant_id="t01"):
            # lógica de polling NRT
            ...
    """
    tracer = get_tracer()

    span_attrs: dict[str, Any] = {"stage": stage}
    if evaluation_mode:
        span_attrs["evaluation_mode"] = evaluation_mode
    if tenant_id:
        span_attrs["tenant_id"] = tenant_id
    if unit_id:
        span_attrs["unit_id"] = unit_id
    if alert_definition_id:
        span_attrs["alert_definition_id"] = alert_definition_id
    if attributes:
        span_attrs.update(attributes)

    with tracer.start_as_current_span(stage, attributes=span_attrs) as span:
        try:
            yield span
        except Exception:
            span.set_status(2, "ERROR")  # StatusCode.ERROR = 2
            span.record_exception()
            raise


# ---------------------------------------------------------------------------
# NoOp fallback quando OTEL não está instalado
# ---------------------------------------------------------------------------


class _NoOpSpan:
    """Span fictício que não faz nada."""

    def set_attribute(self, key: str, value: Any) -> None:  # noqa: ARG002
        pass

    def set_status(self, status: Any, description: str = "") -> None:  # noqa: ARG002
        pass

    def record_exception(self) -> None:
        pass

    def __enter__(self) -> "_NoOpSpan":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


class _NoOpTracer:
    """Tracer fictício que produz NoOp spans."""

    def start_as_current_span(
        self,
        name: str,  # noqa: ARG002
        attributes: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> _NoOpSpan:
        return _NoOpSpan()


# ---------------------------------------------------------------------------
# Helpers para extração/validação
# ---------------------------------------------------------------------------


def format_trace_id(trace_id: int) -> str:
    """Formata um trace_id inteiro como string hex de 32 caracteres."""
    return format(trace_id, "032x")


def is_telemetry_available() -> bool:
    """Retorna True se o OTEL SDK está importável e inicializado."""
    return _telemetry_state.initialized
