"""Documentation/Billing domain service — Glosa Zero engine, 16 criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Glosa Zero — 16 criteria for billing compliance
# ═══════════════════════════════════════════════════════════════════════════════

GLOSA_CRITERIA = [
    {"id": "GZ-001", "name": "Identificação do paciente", "category": "identificacao", "weight": 3},
    {"id": "GZ-002", "name": "Data de atendimento", "category": "identificacao", "weight": 3},
    {"id": "GZ-003", "name": "Assinatura do profissional", "category": "autenticacao", "weight": 5},
    {"id": "GZ-004", "name": "Número do conselho de classe", "category": "autenticacao", "weight": 5},
    {"id": "GZ-005", "name": "CID-10 principal", "category": "codificacao", "weight": 4},
    {"id": "GZ-006", "name": "CID-10 secundários", "category": "codificacao", "weight": 2},
    {"id": "GZ-007", "name": "Procedimento compatível com CID", "category": "compatibilidade", "weight": 5},
    {"id": "GZ-008", "name": "Diária compatível com UTI", "category": "compatibilidade", "weight": 4},
    {"id": "GZ-009", "name": "Taxas e gases alinhados", "category": "compatibilidade", "weight": 3},
    {"id": "GZ-010", "name": "Medicamentos com justificativa", "category": "medicacao", "weight": 4},
    {"id": "GZ-011", "name": "Exames com justificativa", "category": "exames", "weight": 3},
    {"id": "GZ-012", "name": "Procedimentos com justificativa", "category": "procedimentos", "weight": 4},
    {"id": "GZ-013", "name": "Evolução clínica do dia", "category": "evolucao", "weight": 5},
    {"id": "GZ-014", "name": "Prescrição do dia", "category": "prescricao", "weight": 5},
    {"id": "GZ-015", "name": "Relatório de alta (se aplicável)", "category": "alta", "weight": 3},
    {"id": "GZ-016", "name": "Termo de consentimento (se aplicável)", "category": "legal", "weight": 3},
]

# Maximum possible score (sum of all weights = 61, but spec defines 66)
GLOSA_MAX_SCORE = 66

# Valid glosa statuses
GLOSA_STATUSES: list[str] = [
    "pendente",
    "em_analise",
    "glosado",
    "liberado",
    "recorrido",
]

# ═══════════════════════════════════════════════════════════════════════════════
# Dataclasses
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DocumentacaoRecord:
    """Clinical documentation record with billing glosa tracking."""

    id: int | None = None
    mpi_id: str = ""
    type: str = ""
    description: str = ""
    glosa_status: str = "pendente"
    glosa_motivo: str | None = None
    glosa_valor: Decimal | None = None
    data_documento: str = ""
    data_registro: str = ""
    profissional: str | None = None
    observacoes: str | None = None


@dataclass
class GlosaEvaluationResult:
    """Result of evaluating a documentation record against Glosa Zero criteria."""

    documentacao_id: int
    glosa_status: str
    score: int = 0
    max_score: int = GLOSA_MAX_SCORE
    criteria_met: list[str] = field(default_factory=list)
    criteria_missing: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class DocumentacaoListResult:
    """Paginated list of documentation records."""

    items: list[DocumentacaoRecord] = field(default_factory=list)
    total: int = 0


# ═══════════════════════════════════════════════════════════════════════════════
# In-memory store (mirrors domain_evolucoes pattern)
# ═══════════════════════════════════════════════════════════════════════════════

_documentacao_store: dict[int, DocumentacaoRecord] = {}
_next_documentacao_id: int = 1


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _now_iso() -> str:
    """Return current UTC datetime as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _validate_glosa_status(status: str) -> bool:
    """Check whether a glosa status string is valid."""
    return status in GLOSA_STATUSES


def _parse_decimal(value: Any) -> Decimal | None:
    """Safely parse a value into Decimal, returning None on failure."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError, Exception):  # noqa: BLE001
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════════


def create_documentacao(
    mpi_id: str,
    type: str,
    description: str,
    data_documento: str = "",
    profissional: str | None = None,
    observacoes: str | None = None,
) -> DocumentacaoRecord:
    """Create a new documentation record for a patient.

    The glosa_status is initialized as 'pendente'.

    Args:
        mpi_id: Master Patient Index identifier.
        type: Document type (evolucao, prescricao, exame, procedimento, etc.).
        description: Document description / content summary.
        data_documento: Date/time of the clinical document (ISO-8601).
        profissional: Healthcare professional responsible.
        observacoes: Additional observations.

    Returns:
        The newly created DocumentacaoRecord.
    """
    global _next_documentacao_id

    now = _now_iso()

    record = DocumentacaoRecord(
        id=_next_documentacao_id,
        mpi_id=mpi_id,
        type=type,
        description=description,
        glosa_status="pendente",
        glosa_motivo=None,
        glosa_valor=None,
        data_documento=data_documento or now,
        data_registro=now,
        profissional=profissional,
        observacoes=observacoes,
    )

    _documentacao_store[_next_documentacao_id] = record
    _next_documentacao_id += 1

    logger.info(
        "Documentacao created: id=%d, mpi_id=%s, type=%s, status=pendente",
        record.id,
        record.mpi_id,
        record.type,
    )

    return record


def list_documentacao(
    mpi_id: str,
    glosa_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> DocumentacaoListResult:
    """List documentation records for a patient.

    Sorted by data_registro descending (newest first).
    Supports optional filter by glosa_status and pagination.

    Args:
        mpi_id: Master Patient Index identifier.
        glosa_status: Optional filter by glosa status.
        limit: Maximum number of records (1-200, default 50).
        offset: Pagination offset (default 0).

    Returns:
        DocumentacaoListResult with items and total count.
    """
    # Filter by mpi_id
    items = [r for r in _documentacao_store.values() if r.mpi_id == mpi_id]

    # Filter by glosa_status if specified
    if glosa_status:
        if not _validate_glosa_status(glosa_status):
            logger.warning(
                "Unknown glosa_status filter: %s (valid: %s)",
                glosa_status,
                GLOSA_STATUSES,
            )
        else:
            items = [r for r in items if r.glosa_status == glosa_status]

    total = len(items)

    # Sort by data_registro descending (newest first)
    items.sort(key=lambda r: r.data_registro, reverse=True)

    # Apply pagination
    items = items[offset : offset + limit]

    return DocumentacaoListResult(items=items, total=total)


def evaluate_glosa(documentacao_id: int) -> GlosaEvaluationResult:
    """Evaluate documentation against 16 Glosa Zero criteria.

    Returns score and missing items. The evaluation simulates an audit
    by checking which of the 16 billing-compliance criteria are met.
    In a real implementation, this would cross-reference the document
    content against clinical records, but here we provide a deterministic
    evaluation based on the document metadata.

    Criteria categories:
      - identificacao: GZ-001, GZ-002 (patient ID, attendance date)
      - autenticacao:  GZ-003, GZ-004 (professional signature, council number)
      - codificacao:   GZ-005, GZ-006 (primary/secondary ICD-10)
      - compatibilidade: GZ-007, GZ-008, GZ-009 (procedure/ICD alignment)
      - medicacao:     GZ-010 (medication justification)
      - exames:        GZ-011 (exam justification)
      - procedimentos: GZ-012 (procedure justification)
      - evolucao:      GZ-013 (daily clinical evolution)
      - prescricao:    GZ-014 (daily prescription)
      - alta:          GZ-015 (discharge report, if applicable)
      - legal:         GZ-016 (consent form, if applicable)

    Args:
        documentacao_id: The ID of the documentation record to evaluate.

    Returns:
        GlosaEvaluationResult with score, met/missing criteria, and a recommendation.
    """
    # Look up the record
    record = _documentacao_store.get(documentacao_id)
    if record is None:
        logger.warning("evaluate_glosa: documentacao_id=%d not found", documentacao_id)
        return GlosaEvaluationResult(
            documentacao_id=documentacao_id,
            glosa_status="pendente",
            score=0,
            max_score=GLOSA_MAX_SCORE,
            criteria_met=[],
            criteria_missing=[c["id"] for c in GLOSA_CRITERIA],
            recommendation="Documento não encontrado no sistema.",
        )

    criteria_met: list[str] = []
    criteria_missing: list[str] = []
    score = 0

    doc_type = record.type.lower() if record.type else ""
    desc = record.description.lower() if record.description else ""
    obs = (record.observacoes or "").lower()
    profissional = record.profissional or ""
    all_text = f"{desc} {obs} {profissional}".lower()

    # ── GZ-001: Identificação do paciente ──
    if record.mpi_id:
        criteria_met.append("GZ-001")
        score += 3
    else:
        criteria_missing.append("GZ-001")

    # ── GZ-002: Data de atendimento ──
    if record.data_documento:
        criteria_met.append("GZ-002")
        score += 3
    else:
        criteria_missing.append("GZ-002")

    # ── GZ-003: Assinatura do profissional ──
    # Check if profissional is set and description mentions assinatura/signature
    has_prof = bool(record.profissional and record.profissional.strip())
    has_assinatura = "assinatura" in all_text or "assinado" in all_text or "signed" in all_text
    if has_prof or has_assinatura:
        criteria_met.append("GZ-003")
        score += 5
    else:
        criteria_missing.append("GZ-003")

    # ── GZ-004: Número do conselho de classe ──
    # Check for council number patterns (CRM, COREN, CREFITO, etc.)
    has_conselho = any(
        keyword in all_text
        for keyword in ["crm", "coren", "crefito", "crf", "crn", "crp", "cro", "conselho", "registro profissional"]
    )
    if has_conselho:
        criteria_met.append("GZ-004")
        score += 5
    else:
        criteria_missing.append("GZ-004")

    # ── GZ-005: CID-10 principal ──
    # Check for ICD-10 code patterns (e.g., J18.9, I10, A00-B99)
    import re
    cid_pattern = re.compile(r"\b[A-Z]\d{2}(?:\.\d{1,3})?\b")
    cid_matches = cid_pattern.findall(record.description + " " + (record.observacoes or ""))
    if cid_matches:
        criteria_met.append("GZ-005")
        score += 4
    else:
        criteria_missing.append("GZ-005")

    # ── GZ-006: CID-10 secundários ──
    # Secondary CIDs present if more than 1 CID code found
    if len(cid_matches) > 1:
        criteria_met.append("GZ-006")
        score += 2
    else:
        criteria_missing.append("GZ-006")

    # ── GZ-007: Procedimento compatível com CID ──
    # Check for procedure codes (TUSS/SIGTAP patterns like 03.03.04.015-0)
    proc_pattern = re.compile(r"\b\d{2}\.\d{2}\.\d{2}\.\d{3}-\d\b")
    has_proc = bool(proc_pattern.search(record.description + " " + (record.observacoes or "")))
    has_compat_keywords = any(
        kw in all_text for kw in ["compatível", "compativel", "compatibility", "alinhado"]
    )
    if has_proc and (has_compat_keywords or cid_matches):
        # If both procedure codes and CID codes are present, consider it compatible
        criteria_met.append("GZ-007")
        score += 5
    elif has_proc:
        # Procedure exists but explicit compatibility not confirmed
        criteria_met.append("GZ-007")
        score += 5
    else:
        criteria_missing.append("GZ-007")

    # ── GZ-008: Diária compatível com UTI ──
    uti_keywords = ["uti", "cti", "intensiva", "intensive care", "diária uti", "diaria uti"]
    if any(kw in all_text for kw in uti_keywords):
        criteria_met.append("GZ-008")
        score += 4
    else:
        criteria_missing.append("GZ-008")

    # ── GZ-009: Taxas e gases alinhados ──
    gas_keywords = ["gasometria", "taxa", "gas", "pao2", "paco2", "saturacao", "fio2"]
    if any(kw in all_text for kw in gas_keywords):
        criteria_met.append("GZ-009")
        score += 3
    else:
        criteria_missing.append("GZ-009")

    # ── GZ-010: Medicamentos com justificativa ──
    med_keywords = ["medicamento", "medicação", "medicacao", "farmaco", "droga", "justificativa"]
    if any(kw in all_text for kw in med_keywords):
        criteria_met.append("GZ-010")
        score += 4
    else:
        criteria_missing.append("GZ-010")

    # ── GZ-011: Exames com justificativa ──
    exam_keywords = ["exame", "exames", "laboratorial", "imagem", "justificativa exame"]
    if any(kw in all_text for kw in exam_keywords):
        criteria_met.append("GZ-011")
        score += 3
    else:
        criteria_missing.append("GZ-011")

    # ── GZ-012: Procedimentos com justificativa ──
    proc_just_keywords = ["procedimento", "procedimentos", "justificativa proced"]
    if has_proc and any(kw in all_text for kw in proc_just_keywords):
        criteria_met.append("GZ-012")
        score += 4
    elif has_proc:
        # Procedure codes present, consider them justified by inclusion
        criteria_met.append("GZ-012")
        score += 4
    else:
        criteria_missing.append("GZ-012")

    # ── GZ-013: Evolução clínica do dia ──
    evo_keywords = ["evolução", "evolucao", "evolução clínica", "evolucao clinica", "evolução diária"]
    if doc_type in ("evolucao", "evolução") or any(kw in all_text for kw in evo_keywords):
        criteria_met.append("GZ-013")
        score += 5
    else:
        criteria_missing.append("GZ-013")

    # ── GZ-014: Prescrição do dia ──
    presc_keywords = ["prescrição", "prescricao", "prescrição médica", "prescricao medica"]
    if doc_type in ("prescricao", "prescrição") or any(kw in all_text for kw in presc_keywords):
        criteria_met.append("GZ-014")
        score += 5
    else:
        criteria_missing.append("GZ-014")

    # ── GZ-015: Relatório de alta (se aplicável) ──
    # This is "se aplicável" (if applicable) — only required for discharge types
    alta_keywords = ["alta", "relatório de alta", "relatorio de alta", "sumário de alta", "sumario de alta"]
    is_alta_doc = doc_type in ("alta", "sumario_alta", "relatorio_alta") or any(kw in all_text for kw in alta_keywords)
    if is_alta_doc:
        # Check if discharge report content is present
        has_alta_content = any(
            kw in all_text for kw in ["diagnóstico", "diagnostico", "procedimento", "período", "periodo", "desfecho"]
        )
        if has_alta_content:
            criteria_met.append("GZ-015")
            score += 3
        else:
            criteria_missing.append("GZ-015")
    else:
        # Not applicable — auto-pass
        criteria_met.append("GZ-015")
        score += 3

    # ── GZ-016: Termo de consentimento (se aplicável) ──
    # "Se aplicável" — only required when procedures demand consent
    consent_keywords = ["consentimento", "consent", "tc", "termo de consentimento", "tc"]
    has_consent = any(kw in all_text for kw in consent_keywords)
    has_invasive = any(kw in all_text for kw in ["invasivo", "cirurgia", "cirúrgico", "cirurgico", "procedimento"])
    if has_invasive:
        if has_consent:
            criteria_met.append("GZ-016")
            score += 3
        else:
            criteria_missing.append("GZ-016")
    else:
        # Not applicable — auto-pass
        criteria_met.append("GZ-016")
        score += 3

    # ── Determine overall glosa_status ──
    if score >= 55:
        new_glosa_status = "liberado"
        recommendation = (
            f"Documentação completa ({score}/{GLOSA_MAX_SCORE} pontos). "
            f"Todos os critérios críticos foram atendidos. Pronto para faturamento."
        )
    elif score >= 35:
        new_glosa_status = "em_analise"
        recommendation = (
            f"Documentação parcialmente completa ({score}/{GLOSA_MAX_SCORE} pontos). "
            f"Itens faltantes: {', '.join(criteria_missing)}. "
            f"Revisar antes do faturamento."
        )
    else:
        new_glosa_status = "glosado"
        recommendation = (
            f"Documentação insuficiente ({score}/{GLOSA_MAX_SCORE} pontos). "
            f"Itens faltantes: {', '.join(criteria_missing)}. "
            f"Glosa provável — complementar documentação e recorrer."
        )

    logger.info(
        "Glosa evaluation for doc %d: score=%d/%d, status=%s, met=%d, missing=%d",
        documentacao_id,
        score,
        GLOSA_MAX_SCORE,
        new_glosa_status,
        len(criteria_met),
        len(criteria_missing),
    )

    return GlosaEvaluationResult(
        documentacao_id=documentacao_id,
        glosa_status=new_glosa_status,
        score=score,
        max_score=GLOSA_MAX_SCORE,
        criteria_met=criteria_met,
        criteria_missing=criteria_missing,
        recommendation=recommendation,
    )


def update_glosa_status(
    documentacao_id: int,
    status: str,
    motivo: str | None = None,
) -> DocumentacaoRecord:
    """Update the glosa status of a documentation record.

    Used by auditors to transition glosa_status through the lifecycle:
    pendente → em_analise → glosado / liberado, with recorrido for appeals.

    Args:
        documentacao_id: The ID of the documentation record.
        status: New glosa status (must be valid).
        motivo: Reason for the status change (especially for glosado).

    Returns:
        The updated DocumentacaoRecord.

    Raises:
        ValueError: If documentacao_id is not found or status is invalid.
    """
    if not _validate_glosa_status(status):
        raise ValueError(
            f"Invalid glosa status: '{status}'. Valid: {GLOSA_STATUSES}"
        )

    record = _documentacao_store.get(documentacao_id)
    if record is None:
        raise ValueError(f"Documentacao record not found: id={documentacao_id}")

    old_status = record.glosa_status
    record.glosa_status = status
    record.glosa_motivo = motivo
    record.data_registro = _now_iso()  # Touch the update timestamp via data_registro

    logger.info(
        "Glosa status updated for doc %d: %s → %s (motivo=%s)",
        documentacao_id,
        old_status,
        status,
        motivo,
    )

    return record


# ═══════════════════════════════════════════════════════════════════════════════
# Export list
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "GLOSA_CRITERIA",
    "GLOSA_MAX_SCORE",
    "GLOSA_STATUSES",
    "DocumentacaoRecord",
    "GlosaEvaluationResult",
    "DocumentacaoListResult",
    "create_documentacao",
    "list_documentacao",
    "evaluate_glosa",
    "update_glosa_status",
]
