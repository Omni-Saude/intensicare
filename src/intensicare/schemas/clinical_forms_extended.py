"""Pydantic schemas for clinical forms — form definitions and submissions.

Corresponde ao contrato OpenAPI em docs/contracts/formularios-clinicos-openapi.yaml.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


# ── ClinicalFormType (form definition catalog) ────────────────────────────


class FieldDefinitionSchema(BaseModel):
    """Campo individual que compõe um formulário clínico."""

    name: str = Field(..., description="Nome interno do campo", examples=["nivel_consciencia"])
    label: str = Field(..., description="Rótulo de exibição do campo", examples=["Nível de Consciência"])
    type: str = Field(
        ...,
        description="Tipo do campo: text, number, select, boolean",
        examples=["select"],
        pattern=r"^(text|number|select|boolean)$",
    )
    required: bool = Field(default=True, description="Se o campo é obrigatório")


class ScoreRangeSchema(BaseModel):
    """Faixa de valores possíveis para o escore do formulário."""

    min: float | None = Field(None, description="Valor mínimo possível")
    max: float | None = Field(None, description="Valor máximo possível")


class ClinicalFormTypeSchema(BaseModel):
    """Tipo de formulário clínico disponível no sistema (response)."""

    id: str = Field(
        ...,
        description="Identificador do tipo de formulário",
        examples=["rass"],
    )
    name: str = Field(
        ...,
        description="Nome descritivo do formulário",
        examples=["Richmond Agitation-Sedation Scale (RASS)"],
    )
    description: str | None = Field(
        None,
        description="Descrição do formulário e sua finalidade clínica",
    )
    version: str = Field(
        default="1.0.0",
        description="Versão da definição do formulário",
    )
    score_range: ScoreRangeSchema | None = Field(
        None,
        description="Faixa de valores possíveis para o escore",
    )
    fields: list[FieldDefinitionSchema] = Field(
        default_factory=list,
        description="Campos que compõem o formulário",
    )
    active: bool = Field(default=True, description="Se o formulário está ativo")

    class Config:
        from_attributes = True


class ClinicalFormTypeListResponse(BaseModel):
    """Resposta da listagem de tipos de formulários clínicos."""

    items: list[ClinicalFormTypeSchema] = Field(
        default_factory=list,
        description="Lista de tipos de formulários disponíveis",
    )
    total: int = Field(..., description="Total de tipos disponíveis", examples=[5])


# ── ClinicalFormSubmission (submitted forms) ──────────────────────────────


class ClinicalFormSubmissionSchema(BaseModel):
    """Formulário clínico submetido (response)."""

    id: int = Field(..., description="Identificador único do formulário submetido")
    mpi_id: str = Field(
        ...,
        description="Identificador MPI do paciente",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
    form_id: str = Field(
        ...,
        description="ID da definição do formulário usado",
        examples=["rass"],
    )
    form_type: str = Field(
        ...,
        description="Tipo de formulário clínico",
        examples=["rass"],
    )
    data: dict[str, Any] = Field(
        ...,
        description="Dados específicos do formulário preenchido",
    )
    score: Decimal | None = Field(
        None,
        description="Escore calculado do formulário. Null se não aplicável.",
        examples=[-2],
    )
    severity: str | None = Field(
        None,
        description="Nível de severidade associado ao escore",
    )
    submitted_by: str = Field(
        ...,
        description="Profissional que preencheu o formulário",
        examples=["Enf. Maria Fernanda Souza"],
    )
    submitted_at: datetime = Field(
        ...,
        description="Data e hora de submissão do formulário (UTC)",
        examples=["2026-07-07T09:15:00Z"],
    )
    version: str = Field(
        ...,
        description="Versão da definição de formulário usada",
        examples=["1.0.0"],
    )
    definition_version: str | None = Field(
        None,
        description="Versão do schema do formulário (e.g., 'rass-v1.0')",
        examples=["rass-v1.0"],
    )

    class Config:
        from_attributes = True


class ClinicalFormSubmissionListResponse(BaseModel):
    """Resposta da listagem de formulários submetidos de um paciente."""

    items: list[ClinicalFormSubmissionSchema] = Field(
        default_factory=list,
        description="Lista de formulários submetidos",
    )
    total: int = Field(
        ...,
        description="Total de registros disponíveis",
        examples=[49],
    )


# ── ClinicalFormSubmitRequest ─────────────────────────────────────────────


class ClinicalFormSubmitRequest(BaseModel):
    """Request body para submeter um novo formulário clínico."""

    form_type: str = Field(
        ...,
        description="Tipo de formulário clínico a ser submetido",
        examples=["rass"],
    )
    data: dict[str, Any] = Field(
        ...,
        description="Dados específicos do formulário preenchido",
    )
    score: Decimal | None = Field(
        None,
        description="Escore calculado do formulário. Null se não aplicável.",
        examples=[-2],
    )
    severity: str | None = Field(
        None,
        description="Nível de severidade associado ao escore",
    )
    definition_version: str | None = Field(
        None,
        description="Versão do schema do formulário (e.g., 'rass-v1.0')",
        examples=["rass-v1.0"],
    )
    notes: str | None = Field(
        None,
        max_length=2000,
        description="Observações adicionais do avaliador",
        examples=["Paciente colaborativo. Avaliação realizada durante visita matinal."],
    )
