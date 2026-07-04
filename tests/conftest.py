"""
Fixtures e configurações compartilhadas para todos os testes.

Fornece:
- Cliente HTTP assíncrono (httpx.AsyncClient)
- Banco de dados de teste isolado (transação externa + SAVEPOINT por teste)
- Fixtures de autenticação (usuários reais + JWT reais)
- Mocks para testes unitários da camada de serviço

Modelo de event loop (pytest-asyncio 0.26):
    Não definimos mais uma fixture ``event_loop`` custom (removida/depreciada).
    Em vez disso, ``asyncio_default_fixture_loop_scope`` e
    ``asyncio_default_test_loop_scope`` são fixados em ``session`` no pyproject,
    e as fixtures assíncronas declaram ``loop_scope="session"``. Assim a engine,
    as tabelas, as sessões e os próprios testes compartilham UM único event loop
    coerente — eliminando o ``InterfaceError: another operation is in progress``
    (conexões asyncpg presas a loops diferentes) e o modo de deadlock.
"""

from collections.abc import AsyncGenerator, Generator
from datetime import datetime, timezone
import os
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import pytest_asyncio
import redis
import redis.asyncio as aioredis
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine

from intensicare.api.v1.auth import hash_password
from intensicare.auth.jwt import create_access_token
from intensicare.config import get_settings, settings
from intensicare.core import redis as app_redis
from intensicare.core.database import Base, get_db
from intensicare.main import app
from intensicare.models.user import User

# ═══════════════════════════════════════════════════════════════════════════
# Configuração de teste
# ═══════════════════════════════════════════════════════════════════════════

# A URL do banco de teste vem de DATABASE_URL (ambiente de execução/CI). Caso
# ausente, cai para a URL derivada das settings da aplicação. Em qualquer caso,
# garantimos que o banco termine em "_test" (nunca tocar no banco de dev/prod).
_raw_db_url = os.environ.get("DATABASE_URL") or settings.database_url
_url = make_url(_raw_db_url)
if not (_url.database or "").endswith("_test"):
    _url = _url.set(database=f"{_url.database}_test")
TEST_DATABASE_URL = _url.render_as_string(hide_password=False)

# Redis for tests comes from REDIS_URL (run/CI environment), falling back to the
# app's configured URL. The app's get_redis() is a lazy singleton, so we point
# it at this URL (below) and flush the DB per test — Redis side effects (alert
# rate-limit/cooldown keys) are NOT covered by the DB transaction rollback and
# would otherwise leak between tests and across repeated suite runs.
REDIS_TEST_URL = os.environ.get("REDIS_URL") or settings.redis_url


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    """Engine assíncrona para o banco de testes (uma por sessão, um único loop)."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def create_tables(engine: AsyncEngine) -> AsyncGenerator[None, None]:
    """Cria um schema limpo antes da sessão e o remove ao final.

    O ``drop_all`` inicial garante estado prístino mesmo que uma execução
    anterior tenha deixado dados/tabelas para trás (importante para a exigência
    de rodar a suíte duas vezes seguidas de forma verde).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Sessão de banco isolada por teste via transação externa + SAVEPOINT.

    Abrimos uma conexão, iniciamos uma transação externa e vinculamos a sessão
    a ela com ``join_transaction_mode="create_savepoint"``. Assim, mesmo que o
    código sob teste (endpoints, serviços) chame ``commit()``, apenas o SAVEPOINT
    é liberado — a transação externa permanece aberta e é revertida no teardown,
    revertendo TODAS as escritas do teste. Isolamento real por teste.
    """
    connection: AsyncConnection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Cliente HTTP assíncrono para testar a API, ligado à sessão de teste."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════
# Redis — apontar o singleton da app para o Redis de teste e isolar por teste
# ═══════════════════════════════════════════════════════════════════════════


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def _app_redis_client() -> AsyncGenerator[None, None]:
    """Faz o get_redis() da aplicação usar o Redis de teste (REDIS_URL).

    Criado uma única vez no loop de sessão (mesmo loop dos testes async), então a
    conexão asyncpg/redis nunca cruza loops.
    """
    client = aioredis.from_url(REDIS_TEST_URL, encoding="utf-8", decode_responses=True)
    app_redis._redis_state.client = client
    yield
    await client.aclose()
    app_redis._redis_state.client = None


@pytest.fixture(autouse=True)
def _isolate_redis() -> Generator[None, None, None]:
    """Limpa o Redis de teste antes e depois de cada teste (isolamento de estado).

    Usa um cliente síncrono (independente de event loop), seguro para testes
    asyncio e anyio. Sem isso, chaves de rate-limit/cooldown do alert engine
    vazariam entre testes e quebrariam a exigência de rodar a suíte duas vezes.
    """
    sync_client = redis.from_url(REDIS_TEST_URL)
    sync_client.flushdb()
    try:
        yield
    finally:
        sync_client.flushdb()
        sync_client.close()


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures de autenticação — usuários reais + JWT reais
# ═══════════════════════════════════════════════════════════════════════════


async def _create_user_and_headers(
    db_session: AsyncSession,
    *,
    username: str,
    email: str,
    is_admin: bool,
) -> dict[str, str]:
    """Cria um usuário real e devolve o header Authorization com um JWT válido."""
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password("test-fixture-secret"),
        display_name=username,
        is_admin=is_admin,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    token = create_access_token({"sub": user.username, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(loop_scope="session")
async def admin_headers(db_session: AsyncSession) -> dict[str, str]:
    """Authorization header para um usuário admin real (username: testadmin)."""
    return await _create_user_and_headers(
        db_session, username="testadmin", email="testadmin@intensicare.io", is_admin=True
    )


@pytest_asyncio.fixture(loop_scope="session")
async def user_headers(db_session: AsyncSession) -> dict[str, str]:
    """Authorization header para um usuário comum (não-admin) real."""
    return await _create_user_and_headers(
        db_session, username="testuser", email="testuser@intensicare.io", is_admin=False
    )


@pytest.fixture
def no_auth_headers() -> dict[str, str]:
    """Ausência de credenciais — o HTTPBearer deve responder 401."""
    return {}


# ═══════════════════════════════════════════════════════════════════════════
# Mocks para testes unitários da camada de serviço / API
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """AsyncSession mockada que devolve resultados vazios.

    ``await session.execute(...)`` resolve para um resultado cujo
    ``scalar_one_or_none()`` é None e ``fetchall()``/``scalars().all()`` são [].
    Suficiente para exercitar a lógica de ``get_patient_status`` sem banco real.
    """
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    result.fetchall.return_value = []
    result.scalars.return_value.all.return_value = []
    session.execute.return_value = result
    return session


@pytest_asyncio.fixture(loop_scope="session")
async def mock_client(mock_db_session: AsyncMock) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Cliente HTTP cuja dependência de banco é a sessão mockada (sem banco real)."""

    async def override_get_db() -> AsyncGenerator[AsyncMock, None]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def settings_override() -> object:
    """Retorna settings com valores de teste."""
    return get_settings()
