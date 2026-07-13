"""Sedation domain service — RASS, BPS/NRS, CAM-ICU assessments.

Provides:
  - get_current_sedation: most recent sedation assessment for a patient
  - list_sedation_history: paginated history of sedation assessments
  - assess_sedation: create a new sedation assessment with RASS, pain scores, CAM-ICU
  - CAM-ICU full algorithm (Feature 1–4 → positive/negative determination)
  - Validators for RASS, BPS, NRS score ranges

CAM-ICU Algorithm (per Ely et al., 2001; PADIS 2018):
  Step 1 — RASS: if RASS <= -4 (deeply sedated/unconscious), STOP — cannot assess.
  Step 2 — Feature 1: Acute onset or fluctuating course (inicio_agudo)
  Step 3 — Feature 2: Inattention (desatencao)
  Step 4 — Feature 3: Altered level of consciousness (nivel_consciencia_alterado: current RASS != 0)
  Step 5 — Feature 4: Disorganized thinking (pensamento_desorganizado)
  RESULT: CAM-ICU positive = (Feature 1 OR Feature 2) AND Feature 3 AND Feature 4
           BUT per the classic algorithm: Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4)

  Standardized approach (PADIS 2018 / SCCM):
  Positive if: (Feature 1 OR Feature 2) AND Feature 3 AND Feature 4
  Implemented according to contract specification:
  (inicio_agudo OR curso_flutuante) AND desatencao AND
  (pensamento_desorganizado OR nivel_consciencia_alterado)
"""

from __future__ import annotations

__version__ = "3.0.0"

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.sedacao import SedationAssessment

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain data types
# ---------------------------------------------------------------------------


@dataclass
class CAMICUFeatures:
    """CAM-ICU features breakdown for delirium screening.

    Feature 1: Acute onset or fluctuating course (inicio_agudo)
    Feature 2: Inattention (desatencao)
    Feature 3: Altered level of consciousness (nivel_consciencia_alterado)
    Feature 4: Disorganized thinking (pensamento_desorganizado)
    """

    inicio_agudo: bool = False
    desatencao: bool = False
    pensamento_desorganizado: bool = False
    nivel_consciencia_alterado: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature_1_acute_onset": self.inicio_agudo,
            "feature_2_inattention": self.desatencao,
            "feature_3_altered_loc": self.nivel_consciencia_alterado,
            "feature_4_disorganized": self.pensamento_desorganizado,
        }


@dataclass
class SedationRecord:
    """Domain representation of a sedation assessment."""

    id: int | None = None
    mpi_id: str = ""
    rass_score: int | None = None
    rass_label: str | None = None
    bps_score: int | None = None
    nrs_score: int | None = None
    cam_icu_positive: bool | None = None
    cam_icu_features: CAMICUFeatures | None = None
    current_sedation: str | None = None
    assessed_by: str = ""
    assessed_at: str = ""
    notes: str | None = None


@dataclass
class SedationListResult:
    """Paginated result of sedation assessment history."""

    items: list[SedationRecord] = field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# RASS label mapping
# ---------------------------------------------------------------------------

_RASS_LABELS: dict[int, str] = {
    -5: "Não despertável",
    -4: "Sedação profunda",
    -3: "Sedação moderada",
    -2: "Sedação leve",
    -1: "Sonolento",
    0: "Alerta e calmo",
    1: "Inquieto",
    2: "Agitado",
    3: "Muito agitado",
    4: "Combativo",
}


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


def _validate_rass(score: int) -> bool:
    """Validate RASS score range: -5 to +4 inclusive."""
    return -5 <= score <= 4


def _validate_bps(score: int) -> bool:
    """Validate BPS (Behavioral Pain Scale) range: 3 to 12 inclusive."""
    return 3 <= score <= 12


def _validate_nrs(score: int) -> bool:
    """Validate NRS (Numeric Rating Scale) range: 0 to 10 inclusive."""
    return 0 <= score <= 10


# ---------------------------------------------------------------------------
# RASS label computation
# ---------------------------------------------------------------------------


def _calculate_rass_label(score: int) -> str:
    """Map RASS score to human-readable label.

    Args:
        score: RASS score (-5 to +4)

    Returns:
        Label string (e.g. "Sedação leve", "Agitado"), or "Desconhecido" if out of range.

    >>> _calculate_rass_label(-2)
    'Sedação leve'
    >>> _calculate_rass_label(4)
    'Combativo'
    """
    return _RASS_LABELS.get(score, "Desconhecido")


# ---------------------------------------------------------------------------
# CAM-ICU evaluation
# ---------------------------------------------------------------------------


def _evaluate_cam_icu(features: dict | CAMICUFeatures) -> tuple[bool, CAMICUFeatures]:
    """Evaluate CAM-ICU delirium screening.

    CAM-ICU is positive when:
        (Feature 1: acute onset/fluctuating course)
        AND Feature 2: inattention
        AND (Feature 3: altered LOC OR Feature 4: disorganized thinking)

    In the classic algorithm:
        Positive = Feature 1 AND Feature 2 AND (Feature 3 OR Feature 4)

    Args:
        features: Dict with keys 'inicio_agudo', 'desatencao',
                  'pensamento_desorganizado', 'nivel_consciencia_alterado',
                  or a CAMICUFeatures dataclass.

    Returns:
        Tuple of (is_positive: bool, CAMICUFeatures dataclass)

    >>> _evaluate_cam_icu(
    ...     {
    ...         "inicio_agudo": True,
    ...         "desatencao": True,
    ...         "pensamento_desorganizado": False,
    ...         "nivel_consciencia_alterado": True,
    ...     }
    ... )
    (True, CAMICUFeatures(inicio_agudo=True, desatencao=True, ...))
    """
    if isinstance(features, CAMICUFeatures):
        f = features
    else:
        f = CAMICUFeatures(
            inicio_agudo=bool(features.get("inicio_agudo", False)),
            desatencao=bool(features.get("desatencao", False)),
            pensamento_desorganizado=bool(features.get("pensamento_desorganizado", False)),
            nivel_consciencia_alterado=bool(features.get("nivel_consciencia_alterado", False)),
        )

    # CAM-ICU positive algorithm:
    # Feature 1 (acute onset/fluctuating) AND
    # Feature 2 (inattention) AND
    # (Feature 3 (altered LOC) OR Feature 4 (disorganized thinking))
    is_positive = (
        f.inicio_agudo
        and f.desatencao
        and (f.pensamento_desorganizado or f.nivel_consciencia_alterado)
    )

    return is_positive, f


# ---------------------------------------------------------------------------
# Public API — synchronous (pure domain logic, no DB)
# ---------------------------------------------------------------------------


def assess_sedation_pure(
    mpi_id: str,
    rass_score: int | None = None,
    bps_score: int | None = None,
    nrs_score: int | None = None,
    cam_icu_features: dict | None = None,
    current_sedation: str | None = None,
    assessed_by: str = "system",
    notes: str | None = None,
) -> SedationRecord:
    """Create a sedation assessment record (domain logic only, no DB write).

    Validates RASS, BPS, NRS score ranges. Evaluates CAM-ICU if features provided.
    Computes RASS label from score.

    Args:
        mpi_id: Patient MPI identifier.
        rass_score: Richmond Agitation-Sedation Scale (-5 to +4).
        bps_score: Behavioral Pain Scale (3–12) for non-communicative patients.
        nrs_score: Numeric Rating Scale (0–10) for communicative patients.
        cam_icu_features: Dict with CAM-ICU Feature 1–4 booleans.
        current_sedation: Current sedation infusion description.
        assessed_by: Healthcare professional identifier (default: "system").
        notes: Additional clinical notes.

    Returns:
        SedationRecord with validated and computed fields.

    Raises:
        ValueError: If any score is outside the valid range.
    """
    # Validate RASS
    if rass_score is not None and not _validate_rass(rass_score):
        raise ValueError(f"RASS score {rass_score} outside valid range [-5, +4]")

    # Validate BPS
    if bps_score is not None and not _validate_bps(bps_score):
        raise ValueError(f"BPS score {bps_score} outside valid range [3, 12]")

    # Validate NRS
    if nrs_score is not None and not _validate_nrs(nrs_score):
        raise ValueError(f"NRS score {nrs_score} outside valid range [0, 10]")

    # Compute RASS label
    rass_label = None
    if rass_score is not None:
        rass_label = _calculate_rass_label(rass_score)

    # Evaluate CAM-ICU
    cam_icu_positive: bool | None = None
    cam_features_obj: CAMICUFeatures | None = None

    if cam_icu_features:
        # Check if patient is too deeply sedated for CAM-ICU
        # RASS -4 or -5 = cannot assess reliably
        if rass_score is not None and rass_score <= -4:
            logger.info(
                "CAM-ICU not assessable: RASS=%d (deeply sedated/unconscious)",
                rass_score,
            )
            cam_icu_positive = None
            cam_features_obj = CAMICUFeatures(
                inicio_agudo=bool(cam_icu_features.get("inicio_agudo", False)),
                desatencao=bool(cam_icu_features.get("desatencao", False)),
                pensamento_desorganizado=bool(
                    cam_icu_features.get("pensamento_desorganizado", False)
                ),
                nivel_consciencia_alterado=bool(
                    cam_icu_features.get("nivel_consciencia_alterado", False)
                ),
            )
        else:
            cam_icu_positive, cam_features_obj = _evaluate_cam_icu(cam_icu_features)

    now_iso = datetime.now(timezone.utc).isoformat()

    return SedationRecord(
        mpi_id=mpi_id,
        rass_score=rass_score,
        rass_label=rass_label,
        bps_score=bps_score,
        nrs_score=nrs_score,
        cam_icu_positive=cam_icu_positive,
        cam_icu_features=cam_features_obj,
        current_sedation=current_sedation,
        assessed_by=assessed_by,
        assessed_at=now_iso,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# DB-backed API — async, requires AsyncSession
# ---------------------------------------------------------------------------


def _model_to_record(model: SedationAssessment) -> SedationRecord:
    """Convert a SQLAlchemy SedationAssessment model to a SedationRecord."""
    features = None
    if model.cam_icu_features:
        features = CAMICUFeatures(
            inicio_agudo=model.cam_icu_features.get("feature_1_acute_onset", False),
            desatencao=model.cam_icu_features.get("feature_2_inattention", False),
            pensamento_desorganizado=model.cam_icu_features.get("feature_4_disorganized", False),
            nivel_consciencia_alterado=model.cam_icu_features.get("feature_3_altered_loc", False),
        )

    assessed_at_str = ""
    if model.assessed_at:
        assessed_at_str = model.assessed_at.isoformat()

    return SedationRecord(
        id=model.id,
        mpi_id=model.mpi_id,
        rass_score=model.rass_score,
        rass_label=model.rass_label,
        bps_score=model.bps_score,
        nrs_score=model.nrs_score,
        cam_icu_positive=model.cam_icu_positive,
        cam_icu_features=features,
        current_sedation=model.current_sedation,
        assessed_by=model.assessed_by,
        assessed_at=assessed_at_str,
        notes=model.notes,
    )


async def get_current_sedation(
    db: AsyncSession,
    mpi_id: str,
) -> SedationRecord | None:
    """Get the most recent sedation assessment for a patient.

    Args:
        db: Async database session.
        mpi_id: Patient MPI identifier.

    Returns:
        SedationRecord if an assessment exists, None otherwise.
    """
    stmt = (
        select(SedationAssessment)
        .where(SedationAssessment.mpi_id == mpi_id)
        .order_by(desc(SedationAssessment.assessed_at))
        .limit(1)
    )
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()

    if model is None:
        return None

    return _model_to_record(model)


async def list_sedation_history(
    db: AsyncSession,
    mpi_id: str,
    limit: int = 50,
    offset: int = 0,
) -> SedationListResult:
    """List sedation assessment history for a patient, paginated.

    Returns assessments ordered by date descending (most recent first).

    Args:
        db: Async database session.
        mpi_id: Patient MPI identifier.
        limit: Maximum number of records to return (1–500, default 50).
        offset: Offset for pagination (default 0).

    Returns:
        SedationListResult with items and total count.
    """
    # Clamp limits
    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    # Get total count
    count_stmt = select(SedationAssessment).where(SedationAssessment.mpi_id == mpi_id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())

    # Get paginated results
    stmt = (
        select(SedationAssessment)
        .where(SedationAssessment.mpi_id == mpi_id)
        .order_by(desc(SedationAssessment.assessed_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    models = result.scalars().all()

    items = [_model_to_record(m) for m in models]

    return SedationListResult(
        items=items,
        total=total,
    )


async def assess_sedation(
    db: AsyncSession,
    mpi_id: str,
    rass_score: int | None = None,
    bps_score: int | None = None,
    nrs_score: int | None = None,
    cam_icu_features: dict | None = None,
    current_sedation: str | None = None,
    assessed_by: str = "system",
    notes: str | None = None,
) -> SedationRecord:
    """Create and persist a new sedation assessment.

    Combines pure domain logic (assess_sedation_pure) with database persistence.
    Validates RASS, BPS, NRS scores. Evaluates CAM-ICU delirium screening.
    Stores the record in the database and returns the domain object.

    Args:
        db: Async database session.
        mpi_id: Patient MPI identifier.
        rass_score: Richmond Agitation-Sedation Scale (-5 to +4).
        bps_score: Behavioral Pain Scale (3–12).
        nrs_score: Numeric Rating Scale (0–10).
        cam_icu_features: Dict with CAM-ICU Feature 1–4 booleans.
        current_sedation: Current sedation infusion description.
        assessed_by: Healthcare professional identifier.
        notes: Additional clinical notes.

    Returns:
        SedationRecord with id populated from database.

    Raises:
        ValueError: If any score is outside valid range.
    """
    # Step 1: Pure domain validation and computation
    record = assess_sedation_pure(
        mpi_id=mpi_id,
        rass_score=rass_score,
        bps_score=bps_score,
        nrs_score=nrs_score,
        cam_icu_features=cam_icu_features,
        current_sedation=current_sedation,
        assessed_by=assessed_by,
        notes=notes,
    )

    # Step 2: Build SQLAlchemy model
    cam_features_dict = None
    if record.cam_icu_features is not None:
        cam_features_dict = record.cam_icu_features.to_dict()

    model = SedationAssessment(
        mpi_id=record.mpi_id,
        rass_score=record.rass_score,
        rass_label=record.rass_label,
        bps_score=record.bps_score,
        nrs_score=record.nrs_score,
        cam_icu_positive=record.cam_icu_positive,
        cam_icu_features=cam_features_dict,
        current_sedation=record.current_sedation,
        assessed_by=record.assessed_by,
        assessed_at=datetime.fromisoformat(record.assessed_at)
        if record.assessed_at
        else datetime.now(timezone.utc),
        notes=record.notes,
    )

    # Step 3: Persist
    db.add(model)
    await db.flush()
    await db.refresh(model)

    # Step 4: Return domain object with database id
    record.id = model.id
    if model.assessed_at:
        record.assessed_at = model.assessed_at.isoformat()

    return record


# ---------------------------------------------------------------------------
# Synchronous re-exports for convenience (pure domain logic, no DB needed)
# These match the original spec signatures for the validation test.
# ---------------------------------------------------------------------------


def assess_sedation_sync(
    mpi_id: str,
    rass_score: int | None = None,
    bps_score: int | None = None,
    nrs_score: int | None = None,
    cam_icu_features: dict | None = None,
    current_sedation: str | None = None,
    assessed_by: str = "system",
    notes: str | None = None,
) -> SedationRecord:
    """Synchronous wrapper — pure domain logic, no DB persistence.

    Performs validation, RASS label computation, and CAM-ICU evaluation.
    Does NOT write to the database. Use the async assess_sedation(db, ...)
    for full persistence.

    >>> record = assess_sedation_sync(
    ...     "P001",
    ...     rass_score=-2,
    ...     bps_score=4,
    ...     cam_icu_features={
    ...         "inicio_agudo": False,
    ...         "desatencao": False,
    ...         "pensamento_desorganizado": False,
    ...         "nivel_consciencia_alterado": False,
    ...     },
    ... )
    >>> record.rass_label
    'Sedação leve'
    >>> record.cam_icu_positive
    False
    """
    return assess_sedation_pure(
        mpi_id=mpi_id,
        rass_score=rass_score,
        bps_score=bps_score,
        nrs_score=nrs_score,
        cam_icu_features=cam_icu_features,
        current_sedation=current_sedation,
        assessed_by=assessed_by,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Utility: bulk CAM-ICU evaluation for batch processing
# ---------------------------------------------------------------------------


def evaluate_cam_icu_batch(
    features: dict,
    rass_score: int | None = None,
) -> dict[str, Any]:
    """Evaluate CAM-ICU and return a structured result with metadata.

    This is a convenience wrapper for batch alert evaluation contexts.

    Args:
        features: Dict with CAM-ICU feature booleans.
        rass_score: Current RASS score for deep sedation gate.

    Returns:
        Dict with:
          - cam_icu_positive: bool | None
          - cam_icu_assessable: bool
          - features: CAMICUFeatures
          - recommendation: str (if positive)
    """
    # Deep sedation gate
    if rass_score is not None and rass_score <= -4:
        return {
            "cam_icu_positive": None,
            "cam_icu_assessable": False,
            "features": CAMICUFeatures(
                inicio_agudo=bool(features.get("inicio_agudo", False)),
                desatencao=bool(features.get("desatencao", False)),
                pensamento_desorganizado=bool(features.get("pensamento_desorganizado", False)),
                nivel_consciencia_alterado=bool(features.get("nivel_consciencia_alterado", False)),
            ),
            "recommendation": (
                "Paciente profundamente sedado (RASS <= -4). "
                "CAM-ICU não avaliável. Reavaliar após redução da sedação."
            ),
        }

    is_positive, cam_features = _evaluate_cam_icu(features)

    result: dict[str, Any] = {
        "cam_icu_positive": is_positive,
        "cam_icu_assessable": True,
        "features": cam_features,
        "recommendation": None,
    }

    if is_positive:
        if rass_score is not None and rass_score >= 0:
            result["recommendation"] = (
                "Delirium hiperativo (CAM-ICU + com RASS >= 0). "
                "Avaliar dexmedetomidina/haloperidol e medidas não farmacológicas."
            )
        else:
            result["recommendation"] = (
                "Delirium hipoativo (CAM-ICU + com RASS < 0). "
                "Avaliar suspensão de benzodiazepínicos, mobilização precoce."
            )

    return result
