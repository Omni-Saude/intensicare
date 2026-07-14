# =============================================================================
# Intensicare — Dockerfile multi-estágio
# Estágios: development (dev) e production (prod)
# =============================================================================

# ---------------------------------------------------------------------------
# Estágio base — dependências comuns
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Dependências de sistema para asyncpg + build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências Python via pyproject.toml
COPY pyproject.toml .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -e ".[dev]"

# ---------------------------------------------------------------------------
# Estágio de desenvolvimento — código montado via volume
# ---------------------------------------------------------------------------
FROM base AS development

ENV ENVIRONMENT=development \
    LOG_LEVEL=DEBUG

# Copia código mínimo (a maior parte vem por volume mount)
COPY src/ ./src/
COPY tests/ ./tests/
COPY alembic/ ./alembic/

EXPOSE 8000

CMD ["uvicorn", "intensicare.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src"]

# ---------------------------------------------------------------------------
# Estágio de produção — código copiado, sem dev dependencies
# ---------------------------------------------------------------------------
FROM python:3.12-slim-bookworm AS production

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive \
    ENVIRONMENT=production

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia metadados do projeto e o código-fonte. O código (e o README, referenciado
# como `readme` no pyproject.toml) precisa estar presente ANTES do pip install
# porque o pacote agora é instalado em modo não-editável (ver abaixo) — o
# hatchling precisa do conteúdo real de src/intensicare e do README.md para
# construir o wheel e validar os metadados do projeto.
COPY pyproject.toml README.md .
COPY src/ ./src/
COPY alembic/ ./alembic/

# Instala o pacote como wheel real (não-editável). `pip install -e` é
# anti-padrão para imagens de produção (o pacote instalado apontaria para o
# source tree do estágio de build, que não deveria ser a fonte de verdade da
# imagem final) e, neste ambiente, também aciona um AttributeError por
# incompatibilidade entre os hooks PEP 660 do hatchling e o pip usado no
# build isolation — atualizar pip/setuptools/wheel/hatchling antes do install
# evita ambos os problemas.
RUN pip install --upgrade pip setuptools wheel hatchling \
    && pip install ".[test]"  # test inclui httpx para healthcheck
RUN pip uninstall -y pytest pytest-cov pytest-asyncio factory-boy faker ruff mypy pre-commit || true

# Cria usuário não-root
RUN groupadd -r intensicare && useradd -r -g intensicare -d /app -s /sbin/nologin intensicare \
    && chown -R intensicare:intensicare /app
USER intensicare

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

CMD ["uvicorn", "intensicare.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
