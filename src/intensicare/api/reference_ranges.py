"""Reference ranges API — vital thresholds and score bands for frontend useThreshold hook.

Provides a read-only endpoint that returns vital sign reference ranges and
severity-score bands. Tries the database first (ThresholdConfig table); falls
back to hardcoded medical-literature defaults when no configs are present.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.core.database import get_db
from intensicare.models.threshold_config import ThresholdConfig
from intensicare.models.user import User

router = APIRouter(prefix="/api", tags=["reference-ranges"])

# ---------------------------------------------------------------------------
# Hardcoded fallback defaults (medical literature)
# ---------------------------------------------------------------------------

DEFAULT_VITAL_THRESHOLDS: list[dict] = [
    {
        "vital_name": "heart_rate",
        "unit": "bpm",
        "low_critical": 40,
        "low_warn": 50,
        "high_warn": 100,
        "high_critical": 130,
    },
    {
        "vital_name": "systolic_bp",
        "unit": "mmHg",
        "low_critical": 80,
        "low_warn": 90,
        "high_warn": 160,
        "high_critical": 180,
    },
    {
        "vital_name": "diastolic_bp",
        "unit": "mmHg",
        "low_critical": 50,
        "low_warn": 60,
        "high_warn": 100,
        "high_critical": 110,
    },
    {
        "vital_name": "respiratory_rate",
        "unit": "rpm",
        "low_critical": 8,
        "low_warn": 12,
        "high_warn": 25,
        "high_critical": 35,
    },
    {
        "vital_name": "spo2",
        "unit": "%",
        "low_critical": 88,
        "low_warn": 92,
        "high_warn": 100,
        "high_critical": 100,
    },
    {
        "vital_name": "temperature",
        "unit": "°C",
        "low_critical": 35,
        "low_warn": 36,
        "high_warn": 38,
        "high_critical": 39,
    },
]

DEFAULT_SCORE_BANDS: list[dict] = [
    {
        "name": "sofa",
        "bands": [
            {"min": 0, "max": 6, "severity": "normal"},
            {"min": 7, "max": 9, "severity": "watch"},
            {"min": 10, "max": 12, "severity": "urgent"},
            {"min": 13, "max": 24, "severity": "critical"},
        ],
    }
]


@router.get("/reference-ranges")
async def get_reference_ranges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return vital thresholds and severity score bands.

    Consumed by the frontend ``useThreshold`` hook.

    Tries the database first (ThresholdConfig rows); falls back to
    hardcoded medical-literature defaults when no configs are present.
    """
    result = await db.execute(select(ThresholdConfig))
    configs = result.scalars().all()

    if configs:
        vitals: list[dict] = []
        for c in configs:
            vitals.append(
                {
                    "vital_name": c.score_type,
                    "unit": "",
                    "low_critical": 0,
                    "low_warn": 0,
                    "high_warn": c.watch_threshold,
                    "high_critical": c.critical_threshold,
                }
            )
        return {"vitals": vitals, "scores": DEFAULT_SCORE_BANDS}

    return {"vitals": DEFAULT_VITAL_THRESHOLDS, "scores": DEFAULT_SCORE_BANDS}
