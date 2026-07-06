"""
Configuração centralizada da aplicação usando pydantic-settings.
"""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação Intensicare."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Ambiente
    environment: Literal["development", "testing", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    debug: bool = False
    secret_key: SecretStr = SecretStr("change-me-in-production")

    # API
    api_host: str = "0.0.0.0"  # noqa: S104  # intentional bind-all default for container deploys; override via API_HOST
    api_port: int = 8000
    api_reload: bool = False
    api_workers: int = 1
    # CORS — por segurança, o default é restrito ao frontend local de
    # desenvolvimento. Em produção, defina CORS_ORIGINS explicitamente com
    # a lista de origens permitidas (ex: ["https://intensicare.exemplo.com"]).
    # O valor ["*"] NÃO é suportado em produção com allow_credentials=True.
    cors_origins: list[str] = ["http://localhost:3000"]

    # JWT / Auth (MVP — mantido como fallback para dev/test; Fase 3 usa IAM IC)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # ------------------------------------------------------------------
    # AWS IAM Identity Center — SSO (Fase 3 / WO-037)
    # ------------------------------------------------------------------
    # Quando ``iam_enabled`` é True, a validação de tokens IAM IC substitui
    # o JWT local nos ambientes staging/production.
    iam_enabled: bool = False

    # ARN do Identity Center instance (ex: arn:aws:sso:::instance/ssoins-xxxx)
    iam_identity_store_arn: str = ""
    # ARN da aplicação IAM Identity Center vinculada ao Intensicare
    iam_application_arn: str = ""
    # OIDC issuer do IAM Identity Center (ex: https://identitycenter.amazonaws.com/...)
    iam_oidc_issuer: str = ""
    # Público esperado no claim ``aud`` (client_id do OIDC)
    iam_client_id: str = ""
    # ARN do role IAM que o Identity Center assume ao autenticar
    iam_role_arn: str = ""
    # Região AWS onde o Identity Center está provisionado
    iam_region: str = "us-east-1"

    # ------------------------------------------------------------------
    # Lake Formation / ABAC (Fase 3 / WO-037)
    # ------------------------------------------------------------------
    # Catálogo de dados onde residem as tabelas clínicas
    lake_formation_data_catalog_id: str = ""
    # Prefixo dos recursos catalogados (ex: ``intensicare_prod``)
    lake_formation_database_prefix: str = "intensicare"

    # ------------------------------------------------------------------
    # KMS — hierarquia de chaves por tenant (Fase 3 / WO-037)
    # ------------------------------------------------------------------
    # ARN do KMS Key primário (CMK raiz) para envelope encryption.
    # Cada tenant deriva uma DEK a partir desta chave.
    kms_cmk_arn: str = ""
    kms_region: str = "us-east-1"
    # Tamanho das DEKs geradas por tenant (bytes) — padrão AES-256.
    kms_dek_size_bytes: int = 32

    # FHIR (HAPI FHIR / AMH Data Platform) — empty base URL disables enrichment
    fhir_base_url: str = ""
    fhir_auth_token: SecretStr | None = None

    # MPI (Master Patient Index) — empty base URL disables external sync
    mpi_base_url: str = ""
    mpi_auth_token: SecretStr | None = None

    # PostgreSQL / TimescaleDB
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "intensicare"
    postgres_password: SecretStr = SecretStr("intensicare_dev")
    postgres_db: str = "intensicare"
    postgres_min_connections: int = 2
    postgres_max_connections: int = 10

    @computed_field  # type: ignore[prop-decorator]  # pydantic computed property; mypy lacks decorated-property support
    @property
    def database_url(self) -> str:
        """Connection string assíncrona para SQLAlchemy."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    @computed_field  # type: ignore[prop-decorator]  # pydantic computed property; mypy lacks decorated-property support
    @property
    def database_sync_url(self) -> str:
        """Connection string síncrona (usada pelo Alembic)."""
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",
                username=self.postgres_user,
                password=self.postgres_password.get_secret_value(),
                host=self.postgres_host,
                port=self.postgres_port,
                path=self.postgres_db,
            )
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: SecretStr = SecretStr("")

    # Watchdog / Dead-man's switch (INV-5)
    # Window within which an external CloudWatch/Lambda must ping /health.
    # If no ping arrives within this window, the watchdog pages.
    watchdog_timeout_seconds: int = 30
    # Staleness threshold: if no clinical scores have been computed for any
    # (unit, domain) pair within this many minutes, the staleness monitor
    # fires an "alert-on-no-alerts" notification.
    staleness_alert_minutes: int = 15

    # Athena (optional — skipped in health check when disabled)
    athena_enabled: bool = False
    athena_database: str = "intensicare"
    athena_output_location: str = ""  # s3://bucket/prefix/
    athena_workgroup: str = "intensicare"
    athena_region: str = "us-east-1"

    @computed_field  # type: ignore[prop-decorator]  # pydantic computed property; mypy lacks decorated-property support
    @property
    def redis_url(self) -> str:
        """Connection string para Redis."""
        pwd = self.redis_password.get_secret_value()
        if pwd:
            url = (
                "redis://"
                + pwd
                + "@"
                + self.redis_host
                + ":"
                + str(self.redis_port)
                + "/"
                + str(self.redis_db)
            )
        else:
            url = (
                "redis://" + self.redis_host + ":" + str(self.redis_port) + "/" + str(self.redis_db)
            )
        return url


@lru_cache
def get_settings() -> Settings:
    """Retorna instância cacheada das configurações."""
    return Settings()


# Instância global
settings = get_settings()
