"""Configuração do banco de dados — SQLAlchemy async engine + session."""

from collections.abc import AsyncGenerator

from sqlalchemy import event
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
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=settings.postgres_min_connections,
        max_overflow=settings.postgres_max_connections - settings.postgres_min_connections,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # H14: statement_timeout — prevents runaway queries (DoS protection)
    _STATEMENT_TIMEOUT_MS = 30_000  # 30 seconds

    @event.listens_for(engine.sync_engine, "connect")
    def _set_statement_timeout(dbapi_connection, _connection_record):
        """Enforce query timeout on every new connection."""
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute(f"SET statement_timeout = {_STATEMENT_TIMEOUT_MS}")
        finally:
            cursor.close()

    return engine


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

# ── F-CODE-001: In dev mode, raise on lazy loads to detect N+1 issues early ──
if settings.environment == "development":
    from sqlalchemy.orm import Session, raiseload

    @event.listens_for(Session, "do_orm_execute")
    def _dev_raiseload(orm_execute_state):  # noqa: E306
        """Apply raiseload('*') to every ORM query in development.

        This catches accidental lazy loads at the point they occur,
        forcing developers to add explicit selectinload/joinedload options.
        """
        if orm_execute_state.execution_options.get("_raiseload_applied"):
            return
        orm_execute_state.statement = orm_execute_state.statement.options(
            raiseload("*")
        )
        orm_execute_state.update_execution_options(_raiseload_applied=True)


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
