"""Testes para o stub de autenticação e o módulo real de auth.

Verifica:
- Stub funciona em ambiente de desenvolvimento (aceita qualquer token Bearer)
- Stub retorna 403 em produção (bloqueado)
- Módulo real de auth (JWT) funciona com tokens válidos
"""

import importlib.util
import sys
from unittest.mock import patch

from fastapi import HTTPException
import pytest

# ═══════════════════════════════════════════════════════════════════════════
# Helpers — importa o stub diretamente (não o pacote auth/)
# ═══════════════════════════════════════════════════════════════════════════

# Nome único para não colidir com o pacote ``intensicare.auth``.
_AUTH_STUB_MODULE_NAME = "intensicare._auth_stub_file"


def _import_auth_stub():
    """Importa o arquivo stub ``intensicare/auth.py`` diretamente,
    ignorando o pacote ``intensicare/auth/`` que o sombreia."""
    import os

    # Se já foi carregado, retorna do cache
    if _AUTH_STUB_MODULE_NAME in sys.modules:
        return sys.modules[_AUTH_STUB_MODULE_NAME]

    # Caminho absoluto para o stub (relativo à raiz do projeto)
    stub_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "src", "intensicare", "auth.py",
    )

    spec = importlib.util.spec_from_file_location(
        _AUTH_STUB_MODULE_NAME,
        stub_path,
    )
    assert spec is not None, f"Não foi possível encontrar o stub em {stub_path}"
    assert spec.loader is not None

    mod = importlib.util.module_from_spec(spec)
    sys.modules[_AUTH_STUB_MODULE_NAME] = mod
    spec.loader.exec_module(mod)
    return mod


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


class FakeRequest:
    """Simula um request do FastAPI para os testes do stub."""

    def __init__(self, auth_header: str = ""):
        self.headers = {"Authorization": auth_header}


@pytest.fixture
def auth_stub():
    """Retorna o módulo stub carregado isoladamente."""
    return _import_auth_stub()


# ═══════════════════════════════════════════════════════════════════════════
# Testes do Stub de Auth
# ═══════════════════════════════════════════════════════════════════════════


class TestAuthStubDevEnvironment:
    """Stub em ambiente 'development' (padrão)."""

    @pytest.mark.asyncio
    async def test_stub_accepts_valid_bearer_token(self, auth_stub):
        """Token Bearer válido deve ser aceito em dev."""
        request = FakeRequest("Bearer user123:admin")
        user = await auth_stub.get_current_user(request)
        assert user["sub"] == "user123"
        assert user["role"] == "admin"

    @pytest.mark.asyncio
    async def test_stub_accepts_simple_token(self, auth_stub):
        """Token Bearer simples (sem role) deve ser aceito em dev."""
        request = FakeRequest("Bearer just-a-token")
        user = await auth_stub.get_current_user(request)
        assert user["sub"] == "just-a-token"
        assert user["role"] == "user"

    @pytest.mark.asyncio
    async def test_stub_rejects_missing_header(self, auth_stub):
        """Requisição sem header Authorization deve retornar 401."""
        request = FakeRequest("")
        with pytest.raises(HTTPException) as exc_info:
            await auth_stub.get_current_user(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_stub_rejects_non_bearer_header(self, auth_stub):
        """Header sem prefixo 'Bearer ' deve retornar 401."""
        request = FakeRequest("Basic dXNlcjpwYXNz")
        with pytest.raises(HTTPException) as exc_info:
            await auth_stub.get_current_user(request)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_stub_rejects_empty_token(self, auth_stub):
        """Token vazio (apenas 'Bearer ') deve retornar 401."""
        request = FakeRequest("Bearer ")
        with pytest.raises(HTTPException) as exc_info:
            await auth_stub.get_current_user(request)
        assert exc_info.value.status_code == 401


class TestAuthStubProduction:
    """Stub em ambiente 'production' — deve ser bloqueado."""

    @pytest.mark.asyncio
    async def test_stub_blocked_in_production(self, auth_stub):
        """Em produção, get_current_user deve levantar 403."""
        with patch.object(
            auth_stub.settings, "environment", "production"
        ):
            request = FakeRequest("Bearer any-token")
            with pytest.raises(HTTPException) as exc_info:
                await auth_stub.get_current_user(request)
            assert exc_info.value.status_code == 403
            assert "disabled in production" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_stub_blocked_in_staging(self, auth_stub):
        """Em staging, get_current_user também deve levantar 403."""
        with patch.object(
            auth_stub.settings, "environment", "staging"
        ):
            request = FakeRequest("Bearer any-token")
            with pytest.raises(HTTPException) as exc_info:
                await auth_stub.get_current_user(request)
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_require_admin_blocked_in_production(self, auth_stub):
        """Em produção, require_admin também deve levantar 403."""
        with patch.object(
            auth_stub.settings, "environment", "production"
        ):
            # require_admin é uma dependência FastAPI que chama get_current_user
            # antes — mas o bloqueio acontece em require_admin também.
            with pytest.raises(HTTPException) as exc_info:
                await auth_stub.require_admin({"sub": "user", "role": "admin"})
            assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_stub_allowed_in_testing(self, auth_stub):
        """Em ambiente 'testing', o stub funciona normalmente."""
        with patch.object(
            auth_stub.settings, "environment", "testing"
        ):
            request = FakeRequest("Bearer test-token:admin")
            user = await auth_stub.get_current_user(request)
            assert user["sub"] == "test-token"
            assert user["role"] == "admin"


# ═══════════════════════════════════════════════════════════════════════════
# Testes do Módulo Real de Auth (JWT)
# ═══════════════════════════════════════════════════════════════════════════


class TestRealAuthJWT:
    """Validação JWT real — usa o pacote ``intensicare.auth``."""

    def test_jwt_create_and_verify(self):
        """Token JWT criado deve ser verificável."""
        from intensicare.auth.jwt import create_access_token, verify_token

        token = create_access_token({"sub": "testuser", "role": "admin"})
        assert token is not None
        assert isinstance(token, str)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    def test_jwt_rejects_invalid_token(self):
        """Token JWT inválido deve ser rejeitado."""
        from intensicare.auth.jwt import verify_token

        payload = verify_token("not.a.valid.jwt.token")
        assert payload is None

    def test_jwt_expired_token(self):
        """Token expirado deve ser rejeitado."""
        from datetime import datetime, timedelta, timezone
        from jose import jwt
        from intensicare.config import settings

        # Cria token já expirado
        expire = datetime.now(timezone.utc) - timedelta(hours=1)
        secret = settings.secret_key.get_secret_value()
        token = jwt.encode(
            {"sub": "expired_user", "exp": expire},
            secret,
            algorithm=settings.jwt_algorithm,
        )

        from intensicare.auth.jwt import verify_token
        payload = verify_token(token)
        assert payload is None  # Expirado → None

    def test_decode_token_valid(self):
        """decode_token deve retornar payload para token válido."""
        from intensicare.auth.jwt import create_access_token, decode_token

        token = create_access_token({"sub": "decode_test"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "decode_test"
