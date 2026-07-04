"""
Aplicação principal FastAPI — Intensicare.

Inicializa a aplicação, registra rotas, middlewares e handlers de ciclo de vida.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from intensicare.api.thresholds import router as thresholds_router
from intensicare.api.v1 import (
    alerts_router,
    auth_router,
    dashboard_router,
    patients_router,
    vitals_router,
)
from intensicare.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia o ciclo de vida da aplicação.

    - Startup: inicializa conexões com banco e Redis.
    - Shutdown: fecha conexões gracefulmente.
    """
    # Startup
    # TODO: Inicializar pool de conexões (engine SQLAlchemy, Redis client)
    app.state.started = True

    yield

    # Shutdown
    # TODO: Fechar pool de conexões
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

    # Health check
    @app.get("/health", tags=["system"])
    async def health_check() -> JSONResponse:
        return JSONResponse(
            content={
                "status": "healthy",
                "version": "0.1.0",
                "environment": settings.environment,
            }
        )

    # Routers. Some already carry a full prefix (auth → /auth, alerts →
    # /api/v1/alerts, dashboard → /api/v1, thresholds → /api/v1/thresholds);
    # patients/vitals are unprefixed and mounted under /api/v1.
    app.include_router(auth_router)
    app.include_router(alerts_router)
    app.include_router(dashboard_router)
    app.include_router(thresholds_router)
    app.include_router(patients_router, prefix="/api/v1")
    app.include_router(vitals_router, prefix="/api/v1")

    return app


app = create_app()
