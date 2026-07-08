"""Documentation/Billing — model for clinical documentation and glosa tracking."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from intensicare.core.database import Base


class Documentacao(Base):
    """Clinical documentation record with billing glosa tracking.

    Stores clinical documents and billing records, tracking the glosa
    (audit/claim denial) lifecycle: pendente → em_analise → glosado /
    liberado, with recurso (appeal) support.

    Exposed via REST API at /patients/{mpi_id}/documentacao.
    """

    __tablename__ = "documentacao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="Patient MPI identifier"
    )
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Document type: evolucao, prescricao, exame, procedimento",
    )
    description: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="Document description / content summary"
    )
    glosa_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pendente",
        comment="Glosa status: pendente, em_analise, glosado, liberado, recorrido",
    )
    glosa_motivo: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="Reason for glosa (when glosado)"
    )
    glosa_valor: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True, comment="Glosa amount in BRL (R$)"
    )
    data_documento: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Date/time of the clinical document",
    )
    data_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Date/time the record was registered in the system",
    )
    profissional: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Healthcare professional responsible"
    )
    observacoes: Mapped[str | None] = mapped_column(
        String(1024), nullable=True, comment="Additional observations"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        comment="Record creation timestamp",
    )
