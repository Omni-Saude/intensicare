"""
Aplicação principal FastAPI — Intensicare.

Inicializa a aplicação, registra rotas, middlewares e handlers de ciclo de vida.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from intensicare.api.clinical_forms import router as clinical_forms_router
from intensicare.api.reference_ranges import router as reference_ranges_router
from intensicare.api.thresholds import router as thresholds_router
from intensicare.api.v1 import (
    admin_router,
    alert_routing_router,
    alerts_router,
    antimicrobial_router,
    auth_router,
    dashboard_router,
    deterioration_router,
    documentacao_router,
    efficiency_router,
    events_router,
    evolucoes_router,
    formularios_router,
    health_router,
    indicators_router,
    movimentacao_router,
    pathways_router,
    patients_router,
    prescricao_router,
    prophylaxis_router,
    registry_router,
    sedacao_router,
    stability_router,
    ventilation_router,
    vitals_router,
    ws_router,
)
from intensicare.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia o ciclo de vida da aplicação.

    - Startup: inicializa conexões com banco e Redis.
    - Shutdown: fecha conexões gracefulmente.
    """
    from intensicare.core.database import dispose_engine, get_engine
    from intensicare.core.redis import close_redis, get_redis

    # Startup
    # Força inicialização do engine SQLAlchemy e do pool Redis.
    get_engine()
    get_redis()

    # Inicializa telemetria OpenTelemetry (traces + métricas) — ADR-001 / CON-0006.
    # Em dev local sem OTEL SDK, a inicialização é no-op com log de warning.
    from intensicare.core.telemetry import init_telemetry

    init_telemetry()

    app.state.started = True

    yield

    # Shutdown
    await dispose_engine()
    await close_redis()
    app.state.started = False


def create_app() -> FastAPI:
    """Factory que cria e configura a aplicação FastAPI."""

    app = FastAPI(
        title="Intensicare API",
        description="Plataforma de monitoramento contínuo para UTI",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting — prevents brute-force attacks on auth endpoints
    from intensicare.core.rate_limit import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)

    # Health check — redirect /health to /api/v1/health for backward compat
    from fastapi.responses import RedirectResponse

    @app.get("/health", tags=["system"], include_in_schema=False)
    async def health_legacy() -> RedirectResponse:
        return RedirectResponse(url="/api/v1/health")

    # Metrics — Prometheus exposition endpoint (CON-0006 / observability-slo.md)
    from intensicare.core.metrics import setup_metrics_endpoint

    setup_metrics_endpoint(app)

    # Routers. Some already carry a full prefix (auth → /auth, alerts →
    # /api/v1/alerts, dashboard → /api/v1, thresholds → /api/v1/thresholds);
    # patients/vitals are unprefixed and mounted under /api/v1.
    # New domain routers (antimicrobial, prophylaxis, alert-routing, events)
    # carry their own prefix internally.
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(alerts_router)
    app.include_router(antimicrobial_router)
    app.include_router(dashboard_router)
    app.include_router(deterioration_router)
    app.include_router(documentacao_router)
    app.include_router(efficiency_router)
    app.include_router(evolucoes_router)
    app.include_router(formularios_router)
    app.include_router(indicators_router)
    app.include_router(movimentacao_router)
    app.include_router(pathways_router)
    app.include_router(prescricao_router)
    app.include_router(sedacao_router)
    app.include_router(stability_router)
    app.include_router(ventilation_router)
    app.include_router(clinical_forms_router)
    app.include_router(reference_ranges_router)
    app.include_router(thresholds_router)
    app.include_router(prophylaxis_router)
    app.include_router(registry_router)
    app.include_router(alert_routing_router)
    app.include_router(events_router)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(patients_router, prefix="/api/v1")
    app.include_router(vitals_router, prefix="/api/v1")
    app.include_router(ws_router)

    return app


app = create_app()
