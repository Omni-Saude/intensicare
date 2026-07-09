"""Schemas e templates SQL para as tabelas Gold da camada semântica.

Define:
- Estrutura de cada tabela Gold (vital_sign, lab_result, medication, etc.)
- Templates SQL para queries incrementais por domínio
- Mapeamento de domínio → coluna de watermark + cadência padrão
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Domínios suportados e suas cadências padrão
# ---------------------------------------------------------------------------

DOMAIN_CADENCE: dict[str, int] = {
    "sepsis": 300,          # 5 minutos — alta criticidade
    "electrolytes": 120,    # 2 minutos — expedited (visão §3.6)
    "aki": 3600,            # 1 hora — menor criticidade
    "ventilation": 600,     # 10 minutos
    "hemodynamics": 300,    # 5 minutos
    "neurology": 900,       # 15 minutos
    "medication": 1800,     # 30 minutos
}

# Coluna usada como watermark incremental por domínio
DOMAIN_WATERMARK_COLUMN: dict[str, str] = {
    "sepsis": "ingested_at",
    "electrolytes": "ingested_at",
    "aki": "ingested_at",
    "ventilation": "ingested_at",
    "hemodynamics": "ingested_at",
    "neurology": "ingested_at",
    "medication": "administered_at",
}

# ---------------------------------------------------------------------------
# Allowlists para defesa em profundidade (F-INT-001)
# ---------------------------------------------------------------------------

_ALLOWED_TABLES: frozenset[str] = frozenset({
    "gold_vital_sign",
    "gold_lab_result",
    "gold_medication",
})

_ALLOWED_WATERMARK_COLUMNS: frozenset[str] = frozenset({
    "ingested_at",
    "administered_at",
})


def _validate_table(table_name: str) -> str:
    """Valida que o nome da tabela está na allowlist (defesa em profundidade)."""
    if table_name not in _ALLOWED_TABLES:
        raise ValueError(
            f"Table name '{table_name}' not in allowlist. "
            f"Allowed: {sorted(_ALLOWED_TABLES)}"
        )
    return table_name


def _validate_watermark_column(column_name: str) -> str:
    """Valida que a coluna de watermark está na allowlist."""
    if column_name not in _ALLOWED_WATERMARK_COLUMNS:
        raise ValueError(
            f"Watermark column '{column_name}' not in allowlist. "
            f"Allowed: {sorted(_ALLOWED_WATERMARK_COLUMNS)}"
        )
    return column_name


# ---------------------------------------------------------------------------
# Definição de schemas das tabelas Gold
# ---------------------------------------------------------------------------


@dataclass
class GoldColumn:
    """Coluna de uma tabela Gold."""

    name: str
    data_type: str
    nullable: bool = True
    description: str = ""


@dataclass
class GoldTableSchema:
    """Schema de uma tabela Gold."""

    table_name: str
    columns: list[GoldColumn]
    description: str = ""


# ---------------------------------------------------------------------------
# Schemas das tabelas Gold
# ---------------------------------------------------------------------------

VITAL_SIGN_SCHEMA = GoldTableSchema(
    table_name="gold_vital_sign",
    description="Sinais vitais normalizados (edge canonical)",
    columns=[
        GoldColumn("id", "BIGINT", nullable=False, description="PK surrogate"),
        GoldColumn("patient_id", "VARCHAR", nullable=False, description="Patient FK"),
        GoldColumn("tenant_id", "VARCHAR", nullable=False, description="Tenant (workgroup)"),
        GoldColumn("unit", "VARCHAR", nullable=True, description="UTI unit"),
        GoldColumn("parameter", "VARCHAR", nullable=False, description="Canonical parameter name"),
        GoldColumn("value", "DOUBLE", nullable=False, description="Canonical numeric value"),
        GoldColumn("unit_canonical", "VARCHAR", nullable=False, description="Canonical unit string"),
        GoldColumn("recorded_at", "TIMESTAMP", nullable=False, description="Clinical timestamp"),
        GoldColumn("ingested_at", "TIMESTAMP", nullable=False, description="Ingestion watermark"),
        GoldColumn("source_system", "VARCHAR", nullable=True, description="Origem (HL7, FHIR, etc.)"),
    ],
)

LAB_RESULT_SCHEMA = GoldTableSchema(
    table_name="gold_lab_result",
    description="Resultados laboratoriais normalizados",
    columns=[
        GoldColumn("id", "BIGINT", nullable=False, description="PK surrogate"),
        GoldColumn("patient_id", "VARCHAR", nullable=False),
        GoldColumn("tenant_id", "VARCHAR", nullable=False),
        GoldColumn("unit", "VARCHAR", nullable=True),
        GoldColumn("parameter", "VARCHAR", nullable=False, description="Ex: creatinina, potassio"),
        GoldColumn("value", "DOUBLE", nullable=False),
        GoldColumn("unit_canonical", "VARCHAR", nullable=False),
        GoldColumn("collected_at", "TIMESTAMP", nullable=False, description="Coleta"),
        GoldColumn("resulted_at", "TIMESTAMP", nullable=True, description="Resultado disponível"),
        GoldColumn("ingested_at", "TIMESTAMP", nullable=False),
        GoldColumn("source_system", "VARCHAR", nullable=True),
    ],
)

MEDICATION_SCHEMA = GoldTableSchema(
    table_name="gold_medication",
    description="Administração de medicamentos normalizada",
    columns=[
        GoldColumn("id", "BIGINT", nullable=False, description="PK surrogate"),
        GoldColumn("patient_id", "VARCHAR", nullable=False),
        GoldColumn("tenant_id", "VARCHAR", nullable=False),
        GoldColumn("unit", "VARCHAR", nullable=True),
        GoldColumn("drug_name", "VARCHAR", nullable=False),
        GoldColumn("dose", "DOUBLE", nullable=True, description="Dose canonical (ex: mcg/kg/min)"),
        GoldColumn("dose_unit", "VARCHAR", nullable=True),
        GoldColumn("route", "VARCHAR", nullable=True, description="IV, PO, etc."),
        GoldColumn("administered_at", "TIMESTAMP", nullable=False),
        GoldColumn("ingested_at", "TIMESTAMP", nullable=False),
        GoldColumn("source_system", "VARCHAR", nullable=True),
    ],
)

# ---------------------------------------------------------------------------
# Templates SQL incrementais por domínio
# ---------------------------------------------------------------------------


def build_incremental_query(
    domain: str,
    tenant_id: str,
    last_watermark: str | None,
    *,
    table: str | None = None,
    watermark_column: str | None = None,
    limit: int = 10_000,
) -> tuple[str, list[str]]:
    """Constrói uma query SQL incremental parametrizada para um domínio.

    Args:
        domain: Domínio clínico (ex: ``"sepsis"``, ``"aki"``).
        tenant_id: Identificador do tenant para isolamento de workgroup.
        last_watermark: Último timestamp processado (ISO-8601).
            Se ``None``, carrega todos os registros (full load inicial).
        table: Nome da tabela Gold. Se ``None``, infere do domínio.
        watermark_column: Coluna de watermark. Se ``None``, usa padrão do domínio.
        limit: Número máximo de linhas por poll.

    Returns:
        Tuple ``(query, parameters)`` onde ``query`` é a string SQL com
        placeholders ``?`` e ``parameters`` é a lista de valores para
        ``ExecutionParameters`` do Athena.
    """
    tbl = _validate_table(table or _domain_to_table(domain))
    wm_col = _validate_watermark_column(
        watermark_column or DOMAIN_WATERMARK_COLUMN.get(domain, "ingested_at")
    )

    params: list[str] = [tenant_id]

    if last_watermark:
        where_clause = f"WHERE tenant_id = ? AND {wm_col} > TIMESTAMP ?"
        params.append(last_watermark)
    else:
        where_clause = "WHERE tenant_id = ?"

    params.append(str(limit))

    query = f"""
        SELECT *
        FROM {tbl}
        {where_clause}
        ORDER BY {wm_col} ASC
        LIMIT ?
    """
    return query.strip(), params


def build_domain_query(
    domain: str,
    tenant_id: str,
    last_watermark: str | None,
    *,
    limit: int = 10_000,
) -> tuple[str, list[str]]:
    """Constrói query parametrizada específica do domínio com os parâmetros relevantes.

    Cada domínio seleciona apenas as colunas e parâmetros relevantes para
    os algoritmos clínicos daquele domínio, reduzindo tráfego.
    """
    tbl = _validate_table(_domain_to_table(domain))
    columns = _domain_columns(domain)
    wm_col = _validate_watermark_column(
        DOMAIN_WATERMARK_COLUMN.get(domain, "ingested_at")
    )

    params: list[str] = [tenant_id]

    if last_watermark:
        where_clause = f"WHERE tenant_id = ? AND {wm_col} > TIMESTAMP ?"
        params.append(last_watermark)
    else:
        where_clause = "WHERE tenant_id = ?"

    params.append(str(limit))

    query = f"""
        SELECT {', '.join(columns)}
        FROM {tbl}
        {where_clause}
        ORDER BY {wm_col} ASC
        LIMIT ?
    """
    return query.strip(), params


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _domain_to_table(domain: str) -> str:
    """Mapeia domínio → tabela Gold."""
    mapping: dict[str, str] = {
        "sepsis": "gold_lab_result",
        "electrolytes": "gold_lab_result",
        "aki": "gold_lab_result",
        "ventilation": "gold_vital_sign",
        "hemodynamics": "gold_vital_sign",
        "neurology": "gold_vital_sign",
        "medication": "gold_medication",
    }
    return mapping.get(domain, "gold_vital_sign")


def _domain_columns(domain: str) -> list[str]:
    """Retorna colunas relevantes para um domínio clínico."""
    common = ["id", "patient_id", "tenant_id", "unit", "parameter",
              "value", "unit_canonical"]

    domain_extra: dict[str, list[str]] = {
        "sepsis": common + ["collected_at", "resulted_at", "ingested_at"],
        "electrolytes": common + ["collected_at", "resulted_at", "ingested_at"],
        "aki": common + ["collected_at", "resulted_at", "ingested_at"],
        "ventilation": common + ["recorded_at", "ingested_at"],
        "hemodynamics": common + ["recorded_at", "ingested_at"],
        "neurology": common + ["recorded_at", "ingested_at"],
        "medication": ["id", "patient_id", "tenant_id", "unit",
                        "drug_name", "dose", "dose_unit",
                        "administered_at", "ingested_at"],
    }
    return domain_extra.get(domain, common + ["ingested_at"])


# ---------------------------------------------------------------------------
# ORM models for fact_patient_score and fact_alert (Gold Writer — WO-020)
# ---------------------------------------------------------------------------

from datetime import datetime  # noqa: E402

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint  # noqa: E402
from sqlalchemy.orm import Mapped, mapped_column  # noqa: E402

from intensicare.core.database import Base  # noqa: E402


class FactPatientScore(Base):
    """Gold fact table para scores clínicos — PHI-free, versionado.

    Cada linha é uma cópia imutável de um clinical_score com:
    - algorithm_version (rastreabilidade da versão do algoritmo)
    - source_score_id (para idempotência ON CONFLICT)
    - Sem PHI (apenas mpi_id pseudonimizado, sem nomes/datas de nascimento)
    """

    __tablename__ = "fact_patient_score"
    __table_args__ = (
        UniqueConstraint("source_score_id", name="uq_fact_score_source"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    score_type: Mapped[str] = mapped_column(String(16), nullable=False)
    score_value: Mapped[int] = mapped_column(Integer, nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(32), nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    source_score_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="FK para clinical_score.id — idempotência"
    )


class FactAlert(Base):
    """Gold fact table para alertas clínicos — PHI-free, versionado.

    Cada linha é uma cópia imutável de um alert com:
    - definition_version (rastreabilidade da versão do catálogo de alertas)
    - source_alert_id (para idempotência ON CONFLICT)
    - Sem PHI (apenas mpi_id pseudonimizado)
    """

    __tablename__ = "fact_alert"
    __table_args__ = (
        UniqueConstraint("source_alert_id", name="uq_fact_alert_source"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="Canonical: normal, watch, urgent, critical"
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    definition_version: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="Versão do catálogo de definição de alerta (ex: ALERT-AKI-KDIGO-STAGE-01-abc123)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    source_alert_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="FK para alert.id — idempotência"
    )
