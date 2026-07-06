"""Configuração do banco de dados — SQLAlchemy async engine + session."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from intensicare.config import settings


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos SQLAlchemy."""


def create_engine() -> AsyncEngine:
    """Cria engine assíncrona para PostgreSQL/TimescaleDB."""
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.postgres_min_connections,
        max_overflow=settings.postgres_max_connections - settings.postgres_min_connections,
        pool_pre_ping=True,
        pool_recycle=3600,
    )


# Engine global (inicializada lazy no primeiro acesso).
# Armazenada como atributo de um container para evitar o uso de `global`.
class _EngineState:
    """Container para a engine assíncrona compartilhada."""

    engine: AsyncEngine | None = None


_engine_state = _EngineState()


def get_engine() -> AsyncEngine:
    """Retorna a engine assíncrona (lazy init)."""
    engine = _engine_state.engine
    if engine is None:
        engine = create_engine()
        _engine_state.engine = engine
    return engine


# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)


async def dispose_engine() -> None:
    """Fecha (dispose) a engine assíncrona e limpa o estado global."""
    engine = _engine_state.engine
    if engine is not None:
        await engine.dispose()
        _engine_state.engine = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency que fornece uma sessão de banco por request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
