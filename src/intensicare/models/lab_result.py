"""Resultados de exames laboratoriais — TimescaleDB hypertable em collected_at.

Tabela de hot-cache para resultados laboratoriais recebidos via FHIR/Gold.
UNIQUE (fhir_id, collected_at) garante idempotência na ingestão.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class LabResult(Base):
    """Resultado de exame laboratorial. Hypertable em collected_at."""

    __tablename__ = "lab_result"
    __table_args__ = (
        UniqueConstraint(
            "fhir_id",
            "collected_at",
            name="uq_lab_result_fhir_id_collected",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    fhir_id: Mapped[str] = mapped_column(String(128), nullable=False)
    loinc_code: Mapped[str | None] = mapped_column(String(32))
    analyte: Mapped[str | None] = mapped_column(String(255))
    value_num: Mapped[float | None] = mapped_column(Float)
    value_unit: Mapped[str | None] = mapped_column(String(32))
    reference_low: Mapped[float | None] = mapped_column(Float)
    reference_high: Mapped[float | None] = mapped_column(Float)
    abnormal_flag: Mapped[str | None] = mapped_column(String(16))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resulted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_system: Mapped[str | None] = mapped_column(String(32))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
