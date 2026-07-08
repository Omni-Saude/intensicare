"""Evoluções Clínicas (Clinical Notes) — SQLAlchemy models.

ADR-028: SBAR-structured clinical notes with template-driven sections,
non-repudiation via SHA-256 content hashing, and amendment chains.
"""

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from intensicare.core.database import Base


# ---------------------------------------------------------------------------
# EvolucaoTemplate — templates for clinical note sections
# ---------------------------------------------------------------------------


class EvolucaoTemplate(Base):
    """Pre-defined SBAR templates keyed by clinical role.

    Each template defines a set of sections (SBAR: Situation, Background,
    Assessment, Recommendation) with field definitions for each role
    (medico, enfermeiro, fisioterapeuta, etc.).
    """

    __tablename__ = "evolucao_templates"

    id: Mapped[str] = mapped_column(
        String(32), primary_key=True, comment="Template key (ex: 'medico_diaria')"
    )
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Clinical role: medico, enfermeiro, fisioterapeuta, "
        "farmaceutico, nutricionista, psicologo, fonoaudiologo, "
        "musicoterapeuta, tecnico_enfermagem",
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Human-readable template name"
    )
    sections: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Array of SBAR section definitions with field definitions",
    )
    definition_version: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="Template version (ex: '1.0.0')"
    )
    active: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="Whether this template is active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Template creation timestamp",
    )

    # Relationships
    evolucoes: Mapped[list["Evolucao"]] = relationship(
        "Evolucao", back_populates="template"
    )

    def __repr__(self) -> str:
        return f"<EvolucaoTemplate(id={self.id!r}, role={self.role!r})>"


# ---------------------------------------------------------------------------
# Evolucao — clinical notes / evolution records
# ---------------------------------------------------------------------------


class Evolucao(Base):
    """Clinical evolution note for a patient.

    Supports SBAR-structured notes, amendment chains (previous_id),
    and non-repudiation via SHA-256 content hash.
    """

    __tablename__ = "evolucoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    mpi_id: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="Master Patient Index identifier"
    )
    template_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("evolucao_templates.id"),
        nullable=False,
        comment="FK to evolucao_templates.id",
    )
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="Evolution type: admissao, diaria, alta, obito, intercorrencia",
    )
    author: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Professional who authored the note"
    )
    author_role: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="Clinical role of the author"
    )
    sections: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Filled SBAR sections (Situation, Background, Assessment, Recommendation)",
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of sections content for non-repudiation",
    )
    previous_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("evolucoes.id"),
        nullable=True,
        comment="FK to previous version (amendment chain)",
    )
    status: Mapped[str] = mapped_column(
        String(16),
        default="final",
        comment="Status: draft, final, amended",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        comment="Last update timestamp",
    )

    # Relationships
    template: Mapped["EvolucaoTemplate"] = relationship(
        "EvolucaoTemplate", back_populates="evolucoes"
    )
    sections_rel: Mapped[list["EvolucaoSection"]] = relationship(
        "EvolucaoSection", back_populates="evolucao", cascade="all, delete-orphan"
    )
    previous: Mapped["Evolucao | None"] = relationship(
        "Evolucao", remote_side=[id], backref="amendments"
    )

    def __repr__(self) -> str:
        return (
            f"<Evolucao(id={self.id!r}, mpi_id={self.mpi_id!r}, "
            f"type={self.type!r}, status={self.status!r})>"
        )


# ---------------------------------------------------------------------------
# EvolucaoSection — individual SBAR sections
# ---------------------------------------------------------------------------


class EvolucaoSection(Base):
    """Individual SBAR section content for an evolution note.

    Normalized storage for each section (situation, background,
    assessment, recommendation) with ordering.
    """

    __tablename__ = "evolucao_sections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    evolucao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("evolucoes.id"),
        nullable=False,
        comment="FK to evolucoes.id",
    )
    section_key: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Section key: situation, background, assessment, recommendation",
    )
    section_label: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="Human-readable section label"
    )
    content: Mapped[str] = mapped_column(
        String(4096), nullable=False, comment="Section text content"
    )
    order: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Display order within the evolution"
    )

    # Relationships
    evolucao: Mapped["Evolucao"] = relationship(
        "Evolucao", back_populates="sections_rel"
    )

    def __repr__(self) -> str:
        return (
            f"<EvolucaoSection(id={self.id!r}, evolucao_id={self.evolucao_id!r}, "
            f"section_key={self.section_key!r}, order={self.order!r})>"
        )
