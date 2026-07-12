"""Tests for the synthetic demo seeder (scripts/dev/seed_demo.py).

Sprint 1 patient-safety demo data. Proves:
  - the seed is idempotent — running it twice in the same session/
    transaction produces stable counts, not accumulating duplicates
    (the wipe-then-reinsert design of ``seed()``);
  - DEMO-001 ("Sepse Crítica") carries a high MEWS score, a real sepse
    enrollment, and a correctly graded-band-classified pam=58 criterion
    (critical band, per SSC-2021 thresholds in
    ``_work/alerts/pathways/sepse.yaml``);
  - every seeded vital is fresh (``recorded_at`` within the last 24h) —
    this is the exact "stale cutoff" bug the audit flagged: demo vitals
    must never look like old/expired readings.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.models.clinical_score import ClinicalScore
from intensicare.models.pathway import PatientPathway
from intensicare.models.vital_sign import VitalSign
from scripts.dev.seed_demo import DEMO_MPI_PREFIX, SEPSE_PATHWAY_ID, seed

EXPECTED_MPI_IDS = [f"{DEMO_MPI_PREFIX}00{i}" for i in range(1, 6)]


# ═══════════════════════════════════════════════════════════════════════════
# Idempotency
# ═══════════════════════════════════════════════════════════════════════════


class TestSeedDemoIdempotency:
    async def test_seed_produces_five_patients(self, demo_patients) -> None:
        report = demo_patients
        assert len(report.patients) == 5
        assert sorted(report.patients) == EXPECTED_MPI_IDS
        assert report.vitals_ingested > 0
        assert report.pathways_synced is True, report.pathway_sync_message
        assert not report.enrollment_skipped_reason, report.enrollment_skipped_reason
        assert all(not e.get("error") for e in report.enrollments), report.enrollments

    async def test_seed_is_idempotent_within_same_session(
        self, demo_patients, db_session: AsyncSession
    ) -> None:
        """Calling seed() twice in the same session/transaction must yield
        stable counts — the namespace is wiped and fully re-inserted each
        call, so it must never accumulate duplicate vitals/scores/
        enrollments."""
        first = demo_patients
        second = await seed(db_session, now=datetime.now(timezone.utc))

        assert sorted(second.patients) == sorted(first.patients) == EXPECTED_MPI_IDS
        assert second.vitals_ingested == first.vitals_ingested
        assert second.pathways_synced == first.pathways_synced
        assert len(second.enrollments) == len(first.enrollments)
        assert all(not e.get("error") for e in second.enrollments), second.enrollments

        # Row-count assertions directly against the DB: no duplicates left
        # behind by the first call once the second call's wipe+reinsert ran.
        vitals = (
            await db_session.execute(
                select(VitalSign).where(VitalSign.mpi_id.like(f"{DEMO_MPI_PREFIX}%"))
            )
        ).scalars().all()
        assert len(vitals) == second.vitals_ingested

        enrollments = (
            await db_session.execute(
                select(PatientPathway).where(
                    PatientPathway.mpi_id.like(f"{DEMO_MPI_PREFIX}%")
                )
            )
        ).scalars().all()
        assert len(enrollments) == len(second.enrollments)


# ═══════════════════════════════════════════════════════════════════════════
# DEMO-001 clinical content (Sepse Crítica)
# ═══════════════════════════════════════════════════════════════════════════


class TestSeedDemoClinicalContent:
    async def test_demo_001_has_high_mews_score(
        self, demo_patients, db_session: AsyncSession
    ) -> None:
        mpi_id = f"{DEMO_MPI_PREFIX}001"
        scores = (
            await db_session.execute(
                select(ClinicalScore).where(
                    ClinicalScore.mpi_id == mpi_id,
                    ClinicalScore.score_type == "MEWS",
                )
            )
        ).scalars().all()
        assert scores, "DEMO-001 deve ter pelo menos um score MEWS calculado"
        max_score = max(s.score_value for s in scores)
        # DEMO-001's worst reading (HR118/SBP75/RR24/T38.9/AVPU=V) scores 9/15
        # under MEWS-v3.0.0 (Subbe 2001) — well above the clinically
        # recognized "high risk / escalate" threshold of >=5.
        assert max_score >= 5, (
            f"DEMO-001 (Sepse Crítica) deveria ter um MEWS alto; "
            f"max observado={max_score} scores={[s.score_value for s in scores]}"
        )

    async def test_demo_001_enrolled_in_sepse_with_pam_critical_band(
        self, demo_patients
    ) -> None:
        report = demo_patients
        mpi_id = f"{DEMO_MPI_PREFIX}001"
        enrollment = next(
            (e for e in report.enrollments if e["mpi_id"] == mpi_id), None
        )
        assert enrollment is not None, f"{mpi_id} deveria estar inscrito em um pathway"
        assert not enrollment.get("error"), enrollment
        assert enrollment["pathway_id"] == SEPSE_PATHWAY_ID

        criteria_by_id = {c["id"]: c for c in enrollment["criteria"]}
        assert "crit-sep-pam" in criteria_by_id
        pam = criteria_by_id["crit-sep-pam"]
        assert pam["value"] == 58
        # pam=58 falls in the sepse.yaml crit-sep-pam critical band
        # (range [0, 65] -> severity critical), which is NOT the "normal"
        # band -> pathway-enrollment's `met` (goal achieved) must be False.
        assert pam["met"] is False

        # Both evaluated criteria (pam critical, lactato watch) are unmet,
        # and none of the pathway's other 5 criteria were evaluated either
        # -> 0/7 met -> _determine_severity buckets this as "critical".
        assert enrollment["severity"] == "critical"

    async def test_demo_001_pathway_persisted_with_critical_pam(
        self, demo_patients, db_session: AsyncSession
    ) -> None:
        mpi_id = f"{DEMO_MPI_PREFIX}001"
        pp = (
            await db_session.execute(
                select(PatientPathway).where(
                    PatientPathway.mpi_id == mpi_id,
                    PatientPathway.pathway_id == SEPSE_PATHWAY_ID,
                )
            )
        ).scalar_one_or_none()
        assert pp is not None
        assert pp.status == "active"
        assert pp.severity == "critical"

        criteria_by_id = {c["id"]: c for c in (pp.criteria_data or [])}
        assert "crit-sep-pam" in criteria_by_id
        assert criteria_by_id["crit-sep-pam"]["met"] is False
        assert criteria_by_id["crit-sep-pam"]["value"] == 58


# ═══════════════════════════════════════════════════════════════════════════
# Freshness — the audit's "stale cutoff" bug
# ═══════════════════════════════════════════════════════════════════════════


class TestSeedDemoVitalsFreshness:
    async def test_all_demo_patients_have_fresh_vitals(
        self, demo_patients, db_session: AsyncSession
    ) -> None:
        """No DEMO patient's most recent vital may be older than 24h — a
        stale reading would silently fail any "active patient" cutoff
        filter (the exact bug flagged by the audit)."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        rows = (
            await db_session.execute(
                select(VitalSign.mpi_id, VitalSign.recorded_at).where(
                    VitalSign.mpi_id.like(f"{DEMO_MPI_PREFIX}%")
                )
            )
        ).all()
        assert rows, "esperava vitals seedados para o namespace MPI-DEMO-*"

        latest_by_patient: dict[str, datetime] = {}
        for mpi_id, recorded_at in rows:
            current = latest_by_patient.get(mpi_id)
            if current is None or recorded_at > current:
                latest_by_patient[mpi_id] = recorded_at

        assert sorted(latest_by_patient) == EXPECTED_MPI_IDS
        for mpi_id, latest in latest_by_patient.items():
            assert latest > cutoff, (
                f"{mpi_id}: última vital em {latest.isoformat()} está mais "
                f"velha que o cutoff de 24h ({cutoff.isoformat()}) — bug do "
                "cutoff de staleness da auditoria."
            )
