"""Prescrições e administrações de medicamentos.

Tabelas de hot-cache para ordens de medicação e administrações.
FK para patient_cache.mpi_id garante integridade referencial.
"""

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class MedicationOrder(Base):
    """Ordem de medicação (prescrição)."""

    __tablename__ = "medication_order"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("patient_cache.mpi_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fhir_id: Mapped[str] = mapped_column(String(128), nullable=False)
    medication_name: Mapped[str | None] = mapped_column(String(255))
    dose: Mapped[str | None] = mapped_column(String(64))
    route: Mapped[str | None] = mapped_column(String(64))
    frequency: Mapped[str | None] = mapped_column(String(64))
    ordered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MedicationAdministration(Base):
    """Administração (dispensação) de medicamento."""

    __tablename__ = "medication_administration"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("patient_cache.mpi_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    fhir_id: Mapped[str] = mapped_column(String(128), nullable=False)
    order_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("medication_order.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    administered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    dose_given: Mapped[str | None] = mapped_column(String(64))
    route: Mapped[str | None] = mapped_column(String(64))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
