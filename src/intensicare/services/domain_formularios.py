"""Clinical Forms domain service — scoring engine (SOFA, RASS, CAM-ICU, Glasgow, BPS/NRS).

Implements the full clinical forms API:
- 5 form types with complete scoring engines
- Submission tracking with in-memory storage
- Score calculation with severity classification

SOFA: 0-24 (6 organ systems), RASS: -5 to +4, CAM-ICU: binary,
Glasgow: 3-15, BPS: 3-12, NRS: 0-10.
"""

from __future__ import annotations

__version__ = "3.0.0"

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Form definitions
# ---------------------------------------------------------------------------

FORM_DEFINITIONS: dict[str, dict[str, Any]] = {
    "rass": {
        "name": "RASS — Richmond Agitation-Sedation Scale",
        "description": (
            "Escala de agitação e sedação de Richmond. Avalia o nível "
            "de sedação e agitação do paciente em UTI. Varia de -5 "
            "(incapaz de despertar) a +4 (combativo)."
        ),
        "range": [-5, 4],
        "scoring": {
            "-5": "Não despertável",
            "-4": "Sedação profunda",
            "-3": "Sedação moderada",
            "-2": "Sedação leve",
            "-1": "Sonolento",
            "0": "Alerta e calmo",
            "1": "Inquieto",
            "2": "Agitado",
            "3": "Muito agitado",
            "4": "Combativo",
        },
    },
    "cam-icu": {
        "name": "CAM-ICU — Confusion Assessment Method for ICU",
        "description": (
            "Método de avaliação de confusão mental para UTI. "
            "Avalia delirium através de 4 características: início agudo/curso "
            "flutuante, desatenção, pensamento desorganizado e nível de "
            "consciência alterado. Positivo quando início agudo + desatenção "
            "estão presentes, juntamente com pensamento desorganizado OU "
            "nível de consciência alterado."
        ),
        "features": [
            "inicio_agudo",
            "desatencao",
            "pensamento_desorganizado",
            "nivel_consciencia_alterado",
        ],
        "positive_criteria": ["inicio_agudo", "desatencao"],
    },
    "bps-nrs": {
        "name": "BPS/NRS — Behavioral Pain Scale / Numeric Rating Scale",
        "description": (
            "Avaliação de dor em UTI. BPS (Behavioral Pain Scale): "
            "3 indicadores comportamentais (expressão facial, membros superiores, "
            "adaptação à ventilação), pontuação 3-12. NRS (Numeric Rating Scale): "
            "auto-relato do paciente, pontuação 0-10."
        ),
        "bps_range": [3, 12],
        "nrs_range": [0, 10],
    },
    "glasgow": {
        "name": "Glasgow Coma Scale",
        "description": (
            "Escala de Coma de Glasgow. Avalia o nível de consciência "
            "através de 3 componentes: abertura ocular (1-4), resposta "
            "verbal (1-5) e resposta motora (1-6). Pontuação total 3-15."
        ),
        "range": [3, 15],
        "components": ["ocular", "verbal", "motora"],
    },
    "sofa": {
        "name": "SOFA — Sequential Organ Failure Assessment",
        "description": (
            "Avaliação sequencial de falência de órgãos. Avalia 6 sistemas: "
            "respiratório (PaO2/FiO2), coagulação (plaquetas), hepático "
            "(bilirrubina), cardiovascular (PAM + vasopressores), neurológico "
            "(Glasgow) e renal (creatinina + débito urinário). "
            "Pontuação total 0-24."
        ),
        "range": [0, 24],
        "components": [
            "respiratorio",
            "coagulacao",
            "hepatico",
            "cardiovascular",
            "neurologico",
            "renal",
        ],
    },
}

# ---------------------------------------------------------------------------
# Cross-field clinical validation rules (invariants)
# ---------------------------------------------------------------------------

CROSS_FIELD_RULES: dict[str, dict[str, Any]] = {
    "cam-icu_rass_block": {
        "description": (
            "CAM-ICU não pode ser aplicado quando RASS = -5 (paciente incapaz "
            "de despertar / unarousable). A avaliação de delirium requer que o "
            "paciente responda a estímulos."
        ),
        "blocked_form": "cam-icu",
        "depends_on_form": "rass",
        "blocking_value": -5.0,
        "blocking_condition": "eq",
        "error_message": (
            "CAM-ICU não aplicável — RASS = -5 (paciente incapaz de despertar)"
        ),
        "http_status": 422,
        "severity": "critical",
        "clinical_rationale": (
            "RASS -5 indica paciente não despertável (unarousable), o que "
            "torna impossível avaliar as características do CAM-ICU (início "
            "agudo, desatenção, pensamento desorganizado, nível de consciência "
            "alterado). O escore CAM-ICU é inválido neste contexto."
        ),
    },
    # Future invariants can be added here:
    # "glasgow_intubated_block": { ... },
    # "bps_nrs_unarousable_block": { ... },
}


def check_cross_field_rules(
    mpi_id: str,
    form_type: str,
    data: dict,
) -> None:
    """Validate cross-field clinical invariants before form submission.

    Checks the in-memory submission store for conditions that block
    the current form. For example, CAM-ICU is blocked when the latest
    RASS score for the patient is -5 (unarousable).

    Args:
        mpi_id: Patient MPI identifier.
        form_type: Form type being submitted (e.g., 'cam-icu').
        data: Form data dict (unused currently, available for future rules).

    Raises:
        CrossFieldValidationError: When a clinical invariant is violated.
    """
    if form_type == "cam-icu":
        # Check latest RASS score for this patient
        latest_rass = _get_latest_rass_score(mpi_id)
        if latest_rass is not None and latest_rass == -5.0:
            rule = CROSS_FIELD_RULES["cam-icu_rass_block"]
            raise CrossFieldValidationError(
                message=rule["error_message"],
                rule_id="cam-icu_rass_block",
                http_status=rule["http_status"],
            )


def _get_latest_rass_score(mpi_id: str) -> float | None:
    """Get the most recent RASS score for a patient from submissions.

    Args:
        mpi_id: Patient MPI identifier.

    Returns:
        Latest RASS score (float), or None if no RASS submitted.
    """
    rass_subs = [
        s for s in _submissions
        if s["mpi_id"] == mpi_id and s["form_type"] == "rass" and s["score"] is not None
    ]
    if not rass_subs:
        return None
    # Return the most recent (sorted by submitted_at descending)
    rass_subs.sort(key=lambda s: s["submitted_at"], reverse=True)
    return float(rass_subs[0]["score"])


class CrossFieldValidationError(ValueError):
    """Raised when a cross-field clinical invariant is violated.

    Carries additional metadata for API layer to produce proper HTTP responses.
    """

    def __init__(
        self,
        message: str,
        rule_id: str = "",
        http_status: int = 422,
    ) -> None:
        super().__init__(message)
        self.rule_id = rule_id
        self.http_status = http_status


# Known definition versions per form type
VALID_DEFINITION_VERSIONS: dict[str, frozenset[str]] = {
    "rass": frozenset({"rass-v1.0", "1.0.0"}),
    "cam-icu": frozenset({"cam-icu-v1.0", "1.0.0"}),
    "bps-nrs": frozenset({"bps-nrs-v1.0", "1.0.0"}),
    "glasgow": frozenset({"glasgow-v1.0", "1.0.0"}),
    "sofa": frozenset({"sofa-v1.0", "1.0.0"}),
}


def _validate_definition_version(
    form_type: str,
    definition_version: str | None,
) -> None:
    """Validate that the definition_version is known for the form_type.

    Args:
        form_type: Form type (rass, cam-icu, etc.).
        definition_version: Schema version string.

    Raises:
        ValueError: If definition_version is unknown for the form_type.
    """
    if definition_version is None:
        return  # None is acceptable (no version specified)

    known_versions = VALID_DEFINITION_VERSIONS.get(form_type)
    if known_versions is None:
        # Unknown form_type — handled elsewhere
        return

    if definition_version not in known_versions:
        raise ValueError(
            f"definition_version '{definition_version}' não reconhecido para "
            f"form_type '{form_type}'. Versões conhecidas: {sorted(known_versions)}"
        )


# ---------------------------------------------------------------------------
# In-memory submission store
# ---------------------------------------------------------------------------

_submissions: list[dict[str, Any]] = []
_next_id: int = 1


def _now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class FormTypeInfo:
    """Metadata for a clinical form type."""

    id: str
    name: str
    description: str
    version: str = "1.0.0"
    active: bool = True


@dataclass
class FormSubmissionResult:
    """Result of a clinical form submission."""

    id: int | None = None
    mpi_id: str = ""
    form_id: str = ""
    form_type: str = ""
    data: dict = field(default_factory=dict)
    score: float | None = None
    severity: str | None = None
    submitted_by: str = ""
    submitted_at: str = ""
    version: str = "1.0.0"
    definition_version: str | None = None


@dataclass
class FormListResult:
    """List of form types."""

    items: list[FormTypeInfo] = field(default_factory=list)
    total: int = 0


@dataclass
class SubmissionListResult:
    """List of form submissions."""

    items: list[FormSubmissionResult] = field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_form_types() -> FormListResult:
    """Return all available clinical form types.

    Returns:
        FormListResult with items list and total count.
    """
    items = [
        FormTypeInfo(
            id=form_id,
            name=defn["name"],
            description=defn["description"],
        )
        for form_id, defn in FORM_DEFINITIONS.items()
    ]
    return FormListResult(items=items, total=len(items))


def submit_form(
    mpi_id: str,
    form_id: str,
    form_type: str,
    data: dict,
    submitted_by: str = "system",
    definition_version: str | None = None,
) -> FormSubmissionResult:
    """Submit a clinical form for a patient.

    Args:
        mpi_id: Patient MPI identifier.
        form_id: Unique form instance ID (or generated).
        form_type: One of rass, cam-icu, bps-nrs, glasgow, sofa.
        data: Form-specific data dict.
        submitted_by: Clinician or system identifier.
        definition_version: Form schema version (e.g., 'rass-v1.0').

    Returns:
        FormSubmissionResult with score and severity populated.

    Raises:
        ValueError: If form_type is unknown.
    """
    if form_type not in FORM_DEFINITIONS:
        raise ValueError(
            f"Unknown form_type: {form_type!r}. "
            f"Must be one of: {', '.join(FORM_DEFINITIONS)}"
        )

    # ── Validate definition_version ────────────────────────────────────
    _validate_definition_version(form_type, definition_version)

    # ── Cross-field clinical invariant validation ──────────────────────
    check_cross_field_rules(mpi_id, form_type, data)

    score, severity = calculate_score(form_type, data)

    submission = {
        "id": _next_id_increment(),
        "mpi_id": mpi_id,
        "form_id": form_id,
        "form_type": form_type,
        "data": data,
        "score": score,
        "severity": severity,
        "submitted_by": submitted_by,
        "submitted_at": _now_iso(),
        "version": "1.0.0",
        "definition_version": definition_version,
    }
    _submissions.append(submission)

    return FormSubmissionResult(
        id=submission["id"],
        mpi_id=submission["mpi_id"],
        form_id=submission["form_id"],
        form_type=submission["form_type"],
        data=submission["data"],
        score=submission["score"],
        severity=submission["severity"],
        submitted_by=submission["submitted_by"],
        submitted_at=submission["submitted_at"],
        version=submission["version"],
        definition_version=submission.get("definition_version"),
    )


def list_submissions(
    mpi_id: str,
    form_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> SubmissionListResult:
    """List clinical form submissions for a patient.

    Args:
        mpi_id: Patient MPI identifier.
        form_id: Optional filter by form type (e.g. 'rass', 'sofa').
        limit: Maximum records to return (1-200).
        offset: Pagination offset.

    Returns:
        SubmissionListResult with items and total count.
    """
    # Filter by patient
    patient_subs = [s for s in _submissions if s["mpi_id"] == mpi_id]

    # Optional form type filter
    if form_id:
        patient_subs = [s for s in patient_subs if s["form_id"] == form_id]

    # Sort by submission time descending
    patient_subs.sort(key=lambda s: s["submitted_at"], reverse=True)

    total = len(patient_subs)

    # Paginate
    page = patient_subs[offset : offset + limit]

    items = [
        FormSubmissionResult(
            id=s["id"],
            mpi_id=s["mpi_id"],
            form_id=s["form_id"],
            form_type=s["form_type"],
            data=s["data"],
            score=s["score"],
            severity=s["severity"],
            submitted_by=s["submitted_by"],
            submitted_at=s["submitted_at"],
            version=s["version"],
            definition_version=s.get("definition_version"),
        )
        for s in page
    ]

    return SubmissionListResult(items=items, total=total)


# ---------------------------------------------------------------------------
# Score calculation — dispatcher
# ---------------------------------------------------------------------------


def calculate_score(
    form_type: str, data: dict
) -> tuple[float | None, str | None]:
    """Calculate clinical score for a form type.

    Args:
        form_type: One of rass, cam-icu, bps-nrs, glasgow, sofa.
        data: Form-specific data dict.

    Returns:
        Tuple of (score, severity_label).

        Score ranges:
        - SOFA: 0-24
        - RASS: -5 to +4
        - CAM-ICU: 0 (negative) or 1 (positive)
        - Glasgow: 3-15
        - BPS: 3-12, NRS: 0-10

    Raises:
        ValueError: If form_type is unknown.
    """
    if form_type not in FORM_DEFINITIONS:
        raise ValueError(
            f"Unknown form_type: {form_type!r}. "
            f"Must be one of: {', '.join(FORM_DEFINITIONS)}"
        )

    if form_type == "sofa":
        score = _calculate_sofa(data)
        severity = _sofa_severity(score)
        return score, severity

    elif form_type == "rass":
        score = _calculate_rass(data)
        severity = _rass_severity(score)
        return score, severity

    elif form_type == "cam-icu":
        score = _calculate_cam_icu(data)
        severity = "delirium_positivo" if score == 1 else "delirium_negativo"
        return score, severity

    elif form_type == "glasgow":
        score = _calculate_glasgow(data)
        severity = _glasgow_severity(score)
        return score, severity

    elif form_type == "bps-nrs":
        score, severity = _calculate_bps_nrs(data)
        return score, severity

    return None, None


# ---------------------------------------------------------------------------
# Per-form scoring engines
# ---------------------------------------------------------------------------


# ── SOFA ────────────────────────────────────────────────────────────────────


def _calculate_sofa(data: dict) -> float:
    """Calculate SOFA score (0-24) from 6 organ system components.

    Each component scores 0-4.

    Component keys in data:
        respiratorio: {pao2_fio2, ventilacao_mecanica}
        coagulacao: {plaquetas}
        hepatico: {bilirrubina}
        cardiovascular: {pam, vasopressor, dose_vasopressor}
        neurologico: {glasgow}
        renal: {creatinina, debito_urinario_24h}

    Returns:
        Total SOFA score 0-24.
    """
    total = 0

    # --- Respiratory (PaO2/FiO2) ---
    resp = data.get("respiratorio", {}) if isinstance(data.get("respiratorio"), dict) else {}
    pao2_fio2 = _num(resp.get("pao2_fio2"))
    vent = bool(resp.get("ventilacao_mecanica", False))

    if pao2_fio2 is not None:
        if pao2_fio2 >= 400:
            pass  # 0
        elif pao2_fio2 >= 300:
            total += 1
        elif pao2_fio2 >= 200:
            total += 2
        elif vent:
            total += 3 if pao2_fio2 >= 100 else 4
        else:
            total += 2  # Cap at 2 without ventilation

    # --- Coagulation (Platelets x10³/µL) ---
    coag = data.get("coagulacao", {}) if isinstance(data.get("coagulacao"), dict) else {}
    plaquetas = _num(coag.get("plaquetas"))

    if plaquetas is not None:
        if plaquetas >= 150:
            pass  # 0
        elif plaquetas >= 100:
            total += 1
        elif plaquetas >= 50:
            total += 2
        elif plaquetas >= 20:
            total += 3
        else:
            total += 4

    # --- Hepatic (Bilirubin mg/dL) ---
    hep = data.get("hepatico", {}) if isinstance(data.get("hepatico"), dict) else {}
    bili = _num(hep.get("bilirrubina"))

    if bili is not None:
        if bili < 1.2:
            pass  # 0
        elif bili < 2.0:
            total += 1
        elif bili < 6.0:
            total += 2
        elif bili < 12.0:
            total += 3
        else:
            total += 4

    # --- Cardiovascular (MAP + vasopressors) ---
    cv = data.get("cardiovascular", {}) if isinstance(data.get("cardiovascular"), dict) else {}
    pam = _num(cv.get("pam"))
    vasopressor = cv.get("vasopressor", "")
    dose_vaso = _num(cv.get("dose_vasopressor"))

    if pam is not None:
        if not vasopressor or str(vasopressor).lower() in ("", "none"):
            if pam < 70:
                total += 1
            # else 0
        else:
            vtype = str(vasopressor).lower().strip()
            dose = dose_vaso if dose_vaso is not None else 0

            if vtype == "dopamina":
                if dose <= 5:
                    total += 2
                elif dose <= 15:
                    total += 3
                else:
                    total += 4
            elif vtype in ("epinefrina", "norepinefrina", "noradrenalina"):
                if dose <= 0.1:
                    total += 3
                else:
                    total += 4
            elif vtype in ("dobutamina",):
                total += 2
            else:
                total += 2  # Unknown vasopressor

    # --- Neurological (Glasgow) ---
    neuro = data.get("neurologico", {}) if isinstance(data.get("neurologico"), dict) else {}
    gcs = _num(neuro.get("glasgow"))

    if gcs is not None:
        gcs_i = int(gcs)
        if gcs_i == 15:
            pass  # 0
        elif gcs_i >= 13:
            total += 1
        elif gcs_i >= 10:
            total += 2
        elif gcs_i >= 6:
            total += 3
        else:
            total += 4

    # --- Renal (Creatinine + urine output) ---
    renal = data.get("renal", {}) if isinstance(data.get("renal"), dict) else {}
    creatinina = _num(renal.get("creatinina"))
    debito_ur = _num(renal.get("debito_urinario_24h"))

    cr_score = 0
    uo_score = 0

    if creatinina is not None:
        if creatinina < 1.2:
            cr_score = 0
        elif creatinina < 2.0:
            cr_score = 1
        elif creatinina < 3.5:
            cr_score = 2
        elif creatinina < 5.0:
            cr_score = 3
        else:
            cr_score = 4

    if debito_ur is not None:
        if debito_ur < 200:
            uo_score = 4
        elif debito_ur < 500:
            uo_score = 3
        else:
            uo_score = 0

    total += max(cr_score, uo_score)

    return float(total)


def _sofa_severity(score: float) -> str | None:
    """Classify SOFA score into severity band."""
    s = int(score)
    if s <= 6:
        return "baixo_risco"
    elif s <= 9:
        return "risco_moderado"
    elif s <= 12:
        return "risco_alto"
    else:
        return "risco_muito_alto"


# ── RASS ────────────────────────────────────────────────────────────────────


def _calculate_rass(data: dict) -> float:
    """Calculate RASS score (-5 to +4).

    Expects data["nivel"] as the numeric RASS score.

    Returns:
        RASS score -5 to +4.
    """
    nivel = _num(data.get("nivel"))
    if nivel is None:
        return 0.0
    return max(-5.0, min(4.0, nivel))


def _rass_severity(score: float) -> str | None:
    """Classify RASS score severity."""
    s = int(score)
    scoring = FORM_DEFINITIONS["rass"]["scoring"]
    return scoring.get(str(s))


# ── CAM-ICU ─────────────────────────────────────────────────────────────────


def _calculate_cam_icu(data: dict) -> float:
    """Calculate CAM-ICU result (binary: 1=positive, 0=negative).

    CAM-ICU is positive when:
    - Feature 1 (inicio_agudo/curso_flutuante) AND
    - Feature 2 (desatencao) are present, AND
    - Feature 3 (pensamento_desorganizado) OR
    - Feature 4 (nivel_consciencia_alterado) is present.

    Returns:
        1.0 for delirium positive, 0.0 for negative.
    """
    inicio_agudo = bool(data.get("inicio_agudo", False))
    desatencao = bool(data.get("desatencao", False))
    pensamento = bool(data.get("pensamento_desorganizado", False))
    consciencia = bool(data.get("nivel_consciencia_alterado", False))

    # Features 1+2 are required
    if not (inicio_agudo and desatencao):
        return 0.0

    # Feature 3 OR 4 must also be present
    if pensamento or consciencia:
        return 1.0

    return 0.0


# ── Glasgow ─────────────────────────────────────────────────────────────────


def _calculate_glasgow(data: dict) -> float:
    """Calculate Glasgow Coma Scale (3-15).

    Components:
        ocular: 1-4 (abertura ocular)
        verbal: 1-5 (resposta verbal)
        motora: 1-6 (resposta motora)

    If any component is missing, scores minimum for that component.

    Returns:
        Glasgow score 3-15.
    """
    ocular = _num(data.get("ocular"))
    verbal = _num(data.get("verbal"))
    motora = _num(data.get("motora"))

    # Validate ranges
    o = max(1, min(4, int(ocular))) if ocular is not None else 1
    v = max(1, min(5, int(verbal))) if verbal is not None else 1
    m = max(1, min(6, int(motora))) if motora is not None else 1

    return float(o + v + m)


def _glasgow_severity(score: float) -> str | None:
    """Classify Glasgow score severity."""
    s = int(score)
    if s >= 13:
        return "leve"
    elif s >= 9:
        return "moderado"
    elif s >= 6:
        return "grave"
    else:
        return "muito_grave"


# ── BPS/NRS ─────────────────────────────────────────────────────────────────


def _calculate_bps_nrs(data: dict) -> tuple[float | None, str | None]:
    """Calculate BPS or NRS pain score.

    BPS (Behavioral Pain Scale): 3-12
        - expressao_facial: 1-4
        - membros_superiores: 1-4
        - ventilacao_mecanica_indicador: 1-4

    NRS (Numeric Rating Scale): 0-10
        - nrs: direct self-report value

    The type is determined from data["tipo"] (default: "bps").

    Returns:
        Tuple of (score, severity_label).
    """
    tipo = str(data.get("tipo", "bps")).lower().strip()

    if tipo == "nrs":
        nrs_val = _num(data.get("nrs"))
        if nrs_val is None:
            return None, None
        score = max(0.0, min(10.0, nrs_val))
        severity = _nrs_severity(score)
        return score, severity
    else:
        # BPS
        facial = _num(data.get("expressao_facial"))
        membros = _num(data.get("membros_superiores"))
        ventilacao = _num(data.get("ventilacao_mecanica_indicador"))

        if facial is None and membros is None and ventilacao is None:
            return None, None

        f = max(1, min(4, int(facial))) if facial is not None else 1
        m = max(1, min(4, int(membros))) if membros is not None else 1
        v = max(1, min(4, int(ventilacao))) if ventilacao is not None else 1

        score = float(f + m + v)
        severity = _bps_severity(score)
        return score, severity


def _bps_severity(score: float) -> str | None:
    """Classify BPS score severity."""
    s = int(score)
    if s <= 3:
        return "sem_dor"
    elif s <= 6:
        return "dor_leve"
    elif s <= 9:
        return "dor_moderada"
    else:
        return "dor_intensa"


def _nrs_severity(score: float) -> str | None:
    """Classify NRS score severity."""
    s = int(score)
    if s == 0:
        return "sem_dor"
    elif s <= 3:
        return "dor_leve"
    elif s <= 6:
        return "dor_moderada"
    else:
        return "dor_intensa"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _num(v: Any) -> float | None:
    """Safely convert a value to float."""
    if v is None:
        return None
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _next_id_increment() -> int:
    """Generate next unique submission ID."""
    global _next_id
    current = _next_id
    _next_id += 1
    return current
