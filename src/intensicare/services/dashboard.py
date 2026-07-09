"""Dashboard service — aggregates patient data for the clinical dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from intensicare.models.alert import Alert
from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.patient_cache import PatientCache
from intensicare.models.vital_sign import VitalSign
from intensicare.schemas.dashboard import (
    DashboardResponse,
    LatestVitals,
    PatientBedSummary,
    PatientDetailResponse,
    ScoreHistoryPoint,
    TripleEncodingMeta,
    VitalsHistoryPoint,
)
from intensicare.schemas.severity import TripleEncoder, max_severity

# NEWS2 clinical risk-category thresholds (aggregate score)
NEWS2_HIGH_RISK_THRESHOLD = 7
NEWS2_MEDIUM_RISK_THRESHOLD = 5


async def get_dashboard(
    db: AsyncSession,
    unit: str | None = None,
) -> DashboardResponse:
    """Get all patients with their latest scores and alert status for the bed grid.

    Args:
        db: Async database session.
        unit: Optional unit filter.
    """
    # Get all active patients with eager-loaded relationships (F-CODE-001)
    patient_query = select(PatientCache).options(
        selectinload(PatientCache.scores),
        selectinload(PatientCache.alerts),
        selectinload(PatientCache.pathways),
    ).where(PatientCache.is_active.is_(True))
    if unit:
        patient_query = patient_query.where(PatientCache.unit == unit)
    patient_query = patient_query.order_by(PatientCache.bed_id)
    result = await db.execute(patient_query)
    patients = result.scalars().all()

    if not patients:
        return DashboardResponse(patients=[], total=0, active_alerts_total=0)

    mpi_ids = [p.mpi_id for p in patients]

    # Get latest MEWS for each patient — use a single query with DISTINCT ON
    # or iterate. For simplicity, do a subquery approach.
    # Get all alert counts grouped by mpi_id
    # P0-10: highest-severity-wins — collect ALL severities and take MAX
    alert_counts: dict[str, int] = {}
    alert_severities_list: dict[str, list[str]] = {}
    alert_query = (
        select(
            Alert.mpi_id,
            Alert.severity,
            func.count(Alert.id).over(partition_by=Alert.mpi_id),
        )
        .where(Alert.mpi_id.in_(mpi_ids), Alert.status == "active")
        .order_by(Alert.mpi_id, Alert.created_at.desc())
    )
    alert_result = await db.execute(alert_query)
    alert_rows = alert_result.fetchall()
    for row in alert_rows:
        mpi = row[0]
        sev = row[1]
        cnt = row[2]
        if mpi not in alert_counts:
            alert_counts[mpi] = cnt
            alert_severities_list[mpi] = []
        alert_severities_list[mpi].append(sev)

    # P0-10: compute MAX severity per patient (never last-writer-wins)
    alert_severities: dict[str, str | None] = {}
    for mpi, severities in alert_severities_list.items():
        alert_severities[mpi] = max_severity(*severities)

    total_alerts = sum(alert_counts.values())

    # Get latest MEWS and NEWS2 scores per patient
    # Use a raw approach: get all latest scores in subquery

    # Latest MEWS per patient
    mews_subq = (
        select(
            ClinicalScore.mpi_id,
            ClinicalScore.score_value,
            ClinicalScore.trend,
            func.row_number()
            .over(
                partition_by=ClinicalScore.mpi_id,
                order_by=desc(ClinicalScore.calculated_at),
            )
            .label("rn"),
        )
        .where(
            ClinicalScore.mpi_id.in_(mpi_ids),
            ClinicalScore.score_type == "MEWS",
        )
        .subquery()
    )
    mews_query = select(
        mews_subq.c.mpi_id,
        mews_subq.c.score_value,
        mews_subq.c.trend,
    ).where(mews_subq.c.rn == 1)
    mews_result = await db.execute(mews_query)
    mews_map = {row[0]: (row[1], row[2]) for row in mews_result.fetchall()}

    # Latest NEWS2 per patient
    news2_subq = (
        select(
            ClinicalScore.mpi_id,
            ClinicalScore.score_value,
            ClinicalScore.trend,
            ClinicalScore.components,
            func.row_number()
            .over(
                partition_by=ClinicalScore.mpi_id,
                order_by=desc(ClinicalScore.calculated_at),
            )
            .label("rn"),
        )
        .where(
            ClinicalScore.mpi_id.in_(mpi_ids),
            ClinicalScore.score_type == "NEWS2",
        )
        .subquery()
    )
    news2_query = select(
        news2_subq.c.mpi_id,
        news2_subq.c.score_value,
        news2_subq.c.trend,
        news2_subq.c.components,
    ).where(news2_subq.c.rn == 1)
    news2_result = await db.execute(news2_query)
    news2_map = {}
    for row in news2_result.fetchall():
        news2_map[row[0]] = (row[1], row[2])

    # Latest vital signs per patient (most recent VitalSign row)
    vitals_subq = (
        select(
            VitalSign.mpi_id,
            VitalSign.heart_rate,
            VitalSign.systolic_bp,
            VitalSign.diastolic_bp,
            VitalSign.spo2,
            VitalSign.respiratory_rate,
            VitalSign.temperature,
            VitalSign.recorded_at,
            func.row_number()
            .over(
                partition_by=VitalSign.mpi_id,
                order_by=desc(VitalSign.recorded_at),
            )
            .label("rn"),
        )
        .where(VitalSign.mpi_id.in_(mpi_ids))
        .subquery()
    )
    vitals_query = select(
        vitals_subq.c.mpi_id,
        vitals_subq.c.heart_rate,
        vitals_subq.c.systolic_bp,
        vitals_subq.c.diastolic_bp,
        vitals_subq.c.spo2,
        vitals_subq.c.respiratory_rate,
        vitals_subq.c.temperature,
        vitals_subq.c.recorded_at,
    ).where(vitals_subq.c.rn == 1)
    vitals_result = await db.execute(vitals_query)
    vitals_map = {
        row[0]: LatestVitals(
            heart_rate=row[1],
            systolic_bp=row[2],
            diastolic_bp=row[3],
            spo2=row[4],
            respiratory_rate=row[5],
            temperature=float(row[6]) if row[6] is not None else None,
            recorded_at=row[7].isoformat() if row[7] else None,
        )
        for row in vitals_result.fetchall()
    }

    # Build response
    bed_summaries = []
    for p in patients:
        mews_data = mews_map.get(p.mpi_id)
        news2_data = news2_map.get(p.mpi_id)

        # Determine NEWS2 risk category
        news2_risk = None
        news2_score = None
        if news2_data:
            news2_score = news2_data[0]
            if news2_score >= NEWS2_HIGH_RISK_THRESHOLD:
                news2_risk = "high"
            elif news2_score >= NEWS2_MEDIUM_RISK_THRESHOLD:
                news2_risk = "medium"
            else:
                news2_risk = "low"

        # Build triple-encoding for the highest severity
        highest_sev = alert_severities.get(p.mpi_id)
        highest_encoding = None
        if highest_sev:
            enc = TripleEncoder.encode(highest_sev)
            highest_encoding = TripleEncodingMeta(
                color=enc["color"],
                icon=enc["icon"],
                shape=enc["shape"],
                label=enc["label"],
                description=enc["description"],
            )

        bed_summaries.append(
            PatientBedSummary(
                mpi_id=p.mpi_id,
                bed_id=p.bed_id,
                display_name=p.display_name,
                unit=p.unit,
                latest_mews=mews_data[0] if mews_data else None,
                latest_news2=news2_score,
                news2_risk=news2_risk,
                mews_trend=mews_data[1] if mews_data else None,
                news2_trend=news2_data[1] if news2_data else None,
                active_alerts_count=alert_counts.get(p.mpi_id, 0),
                highest_alert_severity=alert_severities.get(p.mpi_id),
                highest_alert_encoding=highest_encoding,
                latest_vitals=vitals_map.get(p.mpi_id),
                last_updated=p.synced_at.isoformat() if p.synced_at else None,
            )
        )

    return DashboardResponse(
        patients=bed_summaries,
        total=len(bed_summaries),
        active_alerts_total=total_alerts,
    )


async def get_patient_detail(
    db: AsyncSession,
    mpi_id: str,
) -> PatientDetailResponse | None:
    """Get detailed patient information including vitals history and scores.

    Args:
        db: Async database session.
        mpi_id: Patient MPI ID.
    """
    # Get patient cache with eager-loaded relationships (F-CODE-001)
    patient_result = await db.execute(
        select(PatientCache)
        .options(
            selectinload(PatientCache.scores),
            selectinload(PatientCache.alerts),
            selectinload(PatientCache.pathways),
        )
        .where(PatientCache.mpi_id == mpi_id)
    )
    patient = patient_result.scalar_one_or_none()
    if not patient:
        return None

    # Get vitals history (last 24h)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    vitals_query = (
        select(VitalSign)
        .where(VitalSign.mpi_id == mpi_id, VitalSign.recorded_at >= cutoff)
        .order_by(VitalSign.recorded_at.asc())
        .limit(200)
    )
    vitals_result = await db.execute(vitals_query)
    vitals = vitals_result.scalars().all()

    vitals_history = [
        VitalsHistoryPoint(
            recorded_at=v.recorded_at.isoformat(),
            heart_rate=v.heart_rate,
            systolic_bp=v.systolic_bp,
            diastolic_bp=v.diastolic_bp,
            temperature=float(v.temperature) if v.temperature else None,
            spo2=v.spo2,
            respiratory_rate=v.respiratory_rate,
            avpu=v.avpu,
            supplemental_o2=v.supplemental_o2,
        )
        for v in vitals
    ]

    # Get MEWS history
    mews_query = (
        select(ClinicalScore)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == "MEWS",
            ClinicalScore.calculated_at >= cutoff,
        )
        .order_by(ClinicalScore.calculated_at.asc())
        .limit(200)
    )
    mews_result = await db.execute(mews_query)
    mews_history = [
        ScoreHistoryPoint(
            calculated_at=s.calculated_at.isoformat(),
            score_type=s.score_type,
            score_value=s.score_value,
            trend=s.trend,
        )
        for s in mews_result.scalars().all()
    ]

    # Get NEWS2 history
    news2_query = (
        select(ClinicalScore)
        .where(
            ClinicalScore.mpi_id == mpi_id,
            ClinicalScore.score_type == "NEWS2",
            ClinicalScore.calculated_at >= cutoff,
        )
        .order_by(ClinicalScore.calculated_at.asc())
        .limit(200)
    )
    news2_result = await db.execute(news2_query)
    news2_history = [
        ScoreHistoryPoint(
            calculated_at=s.calculated_at.isoformat(),
            score_type=s.score_type,
            score_value=s.score_value,
            trend=s.trend,
        )
        for s in news2_result.scalars().all()
    ]

    # Get active alerts
    alerts_query = (
        select(Alert)
        .where(Alert.mpi_id == mpi_id, Alert.status == "active")
        .order_by(Alert.created_at.desc())
        .limit(50)
    )
    alerts_result = await db.execute(alerts_query)
    alerts_list = []
    for a in alerts_result.scalars().all():
        alerts_list.append(
            {
                "id": a.id,
                "mpi_id": a.mpi_id,
                "score_id": a.score_id,
                "severity": a.severity,
                "status": a.status,
                "title": a.title,
                "body": a.body,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                "acknowledged_by": a.acknowledged_by,
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "resolution": a.resolution,
            }
        )

    return PatientDetailResponse(
        mpi_id=patient.mpi_id,
        bed_id=patient.bed_id,
        display_name=patient.display_name,
        unit=patient.unit,
        vitals_history=vitals_history,
        mews_history=mews_history,
        news2_history=news2_history,
        active_alerts=alerts_list,
    )
