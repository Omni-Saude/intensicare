"""add PASSO 2.1 + 2.2 tables: movimentação, prescrição, evoluções,
documentação, formulários, sedação

Revision ID: 0033
Revises: 0032
Create Date: 2026-07-08

Tables created:
  PASSO 2.1: patient_movements, beds, admission_episodes,
             prescricoes, interacao_alertas, auditoria_prescricao,
             agenda_prescricao, evolucao_templates, evolucoes, evolucao_sections
  PASSO 2.2: documentacao, form_definitions, clinical_form_submissions,
             sedation_assessments
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "0033"
down_revision: Union[str, None] = "0032"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.1 — Movimentação (3 tabelas)
    # ══════════════════════════════════════════════════════════════════════

    # ── patient_movements ──────────────────────────────────────────────────
    op.create_table(
        "patient_movements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False,
                  comment="Patient MPI identifier"),
        sa.Column("type", sa.String(length=16), nullable=False,
                  comment="Movement type: admission, transfer, discharge"),
        sa.Column("from_unit", sa.String(length=128), nullable=True,
                  comment="Origin unit (null on admission)"),
        sa.Column("to_unit", sa.String(length=128), nullable=True,
                  comment="Destination unit (null on discharge)"),
        sa.Column("from_bed", sa.String(length=32), nullable=True,
                  comment="Origin bed (null on admission)"),
        sa.Column("to_bed", sa.String(length=32), nullable=True,
                  comment="Destination bed (null on discharge)"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False,
                  comment="Date/time the movement occurred"),
        sa.Column("notes", sa.String(length=1024), nullable=True,
                  comment="Clinical notes"),
        sa.Column("registered_by", sa.String(length=255), nullable=True,
                  comment="Professional who registered the movement"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Record creation timestamp"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_patient_movements_mpi_id"),
        "patient_movements",
        ["mpi_id"],
        unique=False,
    )

    # ── beds ───────────────────────────────────────────────────────────────
    op.create_table(
        "beds",
        sa.Column("id", sa.String(length=32), nullable=False,
                  comment="Bed identifier (ex: 'UTI-A-01')"),
        sa.Column("unit", sa.String(length=128), nullable=False,
                  comment="Unit this bed belongs to"),
        sa.Column("status", sa.String(length=16), nullable=False,
                  server_default="free",
                  comment="Bed status: free, occupied, blocked, cleaning"),
        sa.Column("current_patient_mpi_id", sa.String(length=64), nullable=True,
                  comment="MPI ID of occupying patient (null if free)"),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True,
                  comment="Last status update timestamp"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── admission_episodes ─────────────────────────────────────────────────
    op.create_table(
        "admission_episodes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False,
                  comment="Patient MPI identifier"),
        sa.Column("admission_date", sa.DateTime(timezone=True), nullable=False,
                  comment="Admission date/time"),
        sa.Column("discharge_date", sa.DateTime(timezone=True), nullable=True,
                  comment="Discharge date/time (null if active)"),
        sa.Column("admission_type", sa.String(length=32), nullable=False,
                  comment="Admission type: eletiva, urgencia, emergencia, transferencia"),
        sa.Column("status", sa.String(length=16), nullable=True,
                  server_default="active",
                  comment="Episode status: active, discharged"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_admission_episodes_mpi_id"),
        "admission_episodes",
        ["mpi_id"],
        unique=False,
    )

    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.1 — Prescrição (4 tabelas)
    # ══════════════════════════════════════════════════════════════════════

    # ── prescricoes ────────────────────────────────────────────────────────
    op.create_table(
        "prescricoes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("medication", sa.String(length=255), nullable=False),
        sa.Column("dosage", sa.String(length=64), nullable=False,
                  comment="ex: '500mg', '1g', '20mg/mL'"),
        sa.Column("route", sa.String(length=32), nullable=False,
                  comment="Administration route: IV, PO, SC, IM, SN, IT, TOP, INAL"),
        sa.Column("frequency", sa.String(length=32), nullable=False,
                  comment="QID, TID, BID, QD, QOD, PRN, continuous, ou personalizada ex: 8/8h"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=True,
                  server_default="active",
                  comment="State: draft, active, completed, discontinued, suspended (ADR-027)"),
        sa.Column("version", sa.Integer(), nullable=True,
                  server_default="1",
                  comment="Optimistic locking version"),
        sa.Column("prescribed_by", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prescricoes_mpi_id"),
        "prescricoes",
        ["mpi_id"],
        unique=False,
    )

    # ── interacao_alertas ──────────────────────────────────────────────────
    op.create_table(
        "interacao_alertas",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("prescricao_id", sa.BigInteger(),
                  sa.ForeignKey("prescricoes.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False,
                  comment="contraindicated, severe, moderate, minor"),
        sa.Column("interaction_type", sa.String(length=32), nullable=False,
                  comment="drug-drug, drug-allergy, drug-food, duplicate"),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("resolved", sa.Boolean(), nullable=True,
                  server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interacao_alertas_prescricao_id"),
        "interacao_alertas",
        ["prescricao_id"],
        unique=False,
    )

    # ── auditoria_prescricao ───────────────────────────────────────────────
    op.create_table(
        "auditoria_prescricao",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("prescricao_id", sa.BigInteger(),
                  sa.ForeignKey("prescricoes.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False,
                  comment="created, updated, state_change, discontinued"),
        sa.Column("changed_by", sa.String(length=255), nullable=False),
        sa.Column("changes", postgresql.JSONB(), nullable=False,
                  comment="Snapshot of changed fields with old/new values"),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auditoria_prescricao_prescricao_id"),
        "auditoria_prescricao",
        ["prescricao_id"],
        unique=False,
    )

    # ── agenda_prescricao ──────────────────────────────────────────────────
    op.create_table(
        "agenda_prescricao",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("prescricao_id", sa.BigInteger(),
                  sa.ForeignKey("prescricoes.id", ondelete="CASCADE"),
                  nullable=False),
        sa.Column("scheduled_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=True,
                  server_default="pending",
                  comment="pending, administered, missed, refused"),
        sa.Column("administered_by", sa.String(length=255), nullable=True),
        sa.Column("administered_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_agenda_prescricao_prescricao_id"),
        "agenda_prescricao",
        ["prescricao_id"],
        unique=False,
    )

    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.1 — Evoluções (3 tabelas)
    # ══════════════════════════════════════════════════════════════════════

    # ── evolucao_templates ─────────────────────────────────────────────────
    op.create_table(
        "evolucao_templates",
        sa.Column("id", sa.String(length=32), nullable=False,
                  comment="Template key (ex: 'medico_diaria')"),
        sa.Column("role", sa.String(length=32), nullable=False,
                  comment="Clinical role: medico, enfermeiro, fisioterapeuta, ..."),
        sa.Column("name", sa.String(length=128), nullable=False,
                  comment="Human-readable template name"),
        sa.Column("sections", postgresql.JSONB(), nullable=False,
                  comment="Array of SBAR section definitions with field definitions"),
        sa.Column("definition_version", sa.String(length=16), nullable=False,
                  comment="Template version (ex: '1.0.0')"),
        sa.Column("active", sa.Boolean(), nullable=True,
                  server_default=sa.text("true"),
                  comment="Whether this template is active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Template creation timestamp"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── evolucoes ──────────────────────────────────────────────────────────
    op.create_table(
        "evolucoes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False,
                  comment="Master Patient Index identifier"),
        sa.Column("template_id", sa.String(length=32),
                  sa.ForeignKey("evolucao_templates.id"),
                  nullable=False,
                  comment="FK to evolucao_templates.id"),
        sa.Column("type", sa.String(length=16), nullable=False,
                  comment="Evolution type: admissao, diaria, alta, obito, intercorrencia"),
        sa.Column("author", sa.String(length=255), nullable=False,
                  comment="Professional who authored the note"),
        sa.Column("author_role", sa.String(length=32), nullable=False,
                  comment="Clinical role of the author"),
        sa.Column("sections", postgresql.JSONB(), nullable=False,
                  comment="Filled SBAR sections (Situation, Background, Assessment, Recommendation)"),
        sa.Column("content_hash", sa.String(length=64), nullable=False,
                  comment="SHA-256 hash of sections content for non-repudiation"),
        sa.Column("previous_id", sa.BigInteger(),
                  sa.ForeignKey("evolucoes.id"),
                  nullable=True,
                  comment="FK to previous version (amendment chain)"),
        sa.Column("status", sa.String(length=16), nullable=True,
                  server_default="final",
                  comment="Status: draft, final, amended"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Creation timestamp"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Last update timestamp"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_evolucoes_mpi_id"),
        "evolucoes",
        ["mpi_id"],
        unique=False,
    )

    # ── evolucao_sections ──────────────────────────────────────────────────
    op.create_table(
        "evolucao_sections",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("evolucao_id", sa.BigInteger(),
                  sa.ForeignKey("evolucoes.id"),
                  nullable=False,
                  comment="FK to evolucoes.id"),
        sa.Column("section_key", sa.String(length=32), nullable=False,
                  comment="Section key: situation, background, assessment, recommendation"),
        sa.Column("section_label", sa.String(length=64), nullable=False,
                  comment="Human-readable section label"),
        sa.Column("content", sa.String(length=4096), nullable=False,
                  comment="Section text content"),
        sa.Column("order", sa.Integer(), nullable=False,
                  comment="Display order within the evolution"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.2 — Documentação (1 tabela)
    # ══════════════════════════════════════════════════════════════════════

    # ── documentacao ───────────────────────────────────────────────────────
    op.create_table(
        "documentacao",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False,
                  comment="Patient MPI identifier"),
        sa.Column("type", sa.String(length=32), nullable=False,
                  comment="Document type: evolucao, prescricao, exame, procedimento"),
        sa.Column("description", sa.String(length=512), nullable=False,
                  comment="Document description / content summary"),
        sa.Column("glosa_status", sa.String(length=16), nullable=False,
                  server_default="pendente",
                  comment="Glosa status: pendente, em_analise, glosado, liberado, recorrido"),
        sa.Column("glosa_motivo", sa.String(length=512), nullable=True,
                  comment="Reason for glosa (when glosado)"),
        sa.Column("glosa_valor", sa.Numeric(precision=12, scale=2), nullable=True,
                  comment="Glosa amount in BRL (R$)"),
        sa.Column("data_documento", sa.DateTime(timezone=True), nullable=False,
                  comment="Date/time of the clinical document"),
        sa.Column("data_registro", sa.DateTime(timezone=True), nullable=True,
                  comment="Date/time the record was registered in the system"),
        sa.Column("profissional", sa.String(length=255), nullable=True,
                  comment="Healthcare professional responsible"),
        sa.Column("observacoes", sa.String(length=1024), nullable=True,
                  comment="Additional observations"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True,
                  comment="Record creation timestamp"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_documentacao_mpi_id"),
        "documentacao",
        ["mpi_id"],
        unique=False,
    )

    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.2 — Formulários (2 tabelas)
    # ══════════════════════════════════════════════════════════════════════

    # ── form_definitions ───────────────────────────────────────────────────
    op.create_table(
        "form_definitions",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("version", sa.String(length=16), nullable=True,
                  server_default="1.0.0"),
        sa.Column("fields", postgresql.JSONB(), nullable=False),
        sa.Column("scoring", postgresql.JSONB(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True,
                  server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── clinical_form_submissions ──────────────────────────────────────────
    op.create_table(
        "clinical_form_submissions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("form_id", sa.String(length=32),
                  sa.ForeignKey("form_definitions.id"),
                  nullable=False),
        sa.Column("form_type", sa.String(length=32), nullable=False,
                  comment="Cópia desnormalizada de form_definitions.id para compatibilidade com schema legado"),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("score", sa.Numeric(precision=8, scale=2), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=True),
        sa.Column("submitted_by", sa.String(length=255), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.String(length=16), nullable=False,
                  comment="Versão da definição de formulário usada"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_clinical_form_submissions_mpi_id"),
        "clinical_form_submissions",
        ["mpi_id"],
        unique=False,
    )

    # ══════════════════════════════════════════════════════════════════════
    # PASSO 2.2 — Sedação (1 tabela)
    # ══════════════════════════════════════════════════════════════════════

    # ── sedation_assessments ───────────────────────────────────────────────
    op.create_table(
        "sedation_assessments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("mpi_id", sa.String(length=64), nullable=False),
        sa.Column("rass_score", sa.Integer(), nullable=True,
                  comment="Richmond Agitation-Sedation Scale: -5 (unarousable) to +4 (combative)"),
        sa.Column("rass_label", sa.String(length=32), nullable=True,
                  comment="e.g. Sonolento, Agitado, Calmo"),
        sa.Column("bps_score", sa.Integer(), nullable=True,
                  comment="Behavioral Pain Scale: 3–12 (non-communicative patients)"),
        sa.Column("nrs_score", sa.Integer(), nullable=True,
                  comment="Numeric Rating Scale: 0–10 (communicative patients)"),
        sa.Column("cam_icu_positive", sa.Boolean(), nullable=True,
                  comment="CAM-ICU delirium screening result (True=positive for delirium)"),
        sa.Column("cam_icu_features", postgresql.JSONB(), nullable=True,
                  comment="CAM-ICU feature details (Feature 1-4, RASS reference)"),
        sa.Column("current_sedation", sa.String(length=128), nullable=True,
                  comment="Current sedation infusion, e.g. Propofol 20mL/h"),
        sa.Column("assessed_by", sa.String(length=255), nullable=False),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sedation_assessments_mpi_id"),
        "sedation_assessments",
        ["mpi_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop in reverse order to respect FK constraints
    op.drop_index(op.f("ix_sedation_assessments_mpi_id"), table_name="sedation_assessments")
    op.drop_table("sedation_assessments")

    op.drop_index(op.f("ix_clinical_form_submissions_mpi_id"), table_name="clinical_form_submissions")
    op.drop_table("clinical_form_submissions")
    op.drop_table("form_definitions")

    op.drop_index(op.f("ix_documentacao_mpi_id"), table_name="documentacao")
    op.drop_table("documentacao")

    op.drop_table("evolucao_sections")
    op.drop_index(op.f("ix_evolucoes_mpi_id"), table_name="evolucoes")
    op.drop_table("evolucoes")
    op.drop_table("evolucao_templates")

    op.drop_index(op.f("ix_agenda_prescricao_prescricao_id"), table_name="agenda_prescricao")
    op.drop_table("agenda_prescricao")
    op.drop_index(op.f("ix_auditoria_prescricao_prescricao_id"), table_name="auditoria_prescricao")
    op.drop_table("auditoria_prescricao")
    op.drop_index(op.f("ix_interacao_alertas_prescricao_id"), table_name="interacao_alertas")
    op.drop_table("interacao_alertas")
    op.drop_index(op.f("ix_prescricoes_mpi_id"), table_name="prescricoes")
    op.drop_table("prescricoes")

    op.drop_index(op.f("ix_admission_episodes_mpi_id"), table_name="admission_episodes")
    op.drop_table("admission_episodes")
    op.drop_table("beds")
    op.drop_index(op.f("ix_patient_movements_mpi_id"), table_name="patient_movements")
    op.drop_table("patient_movements")
