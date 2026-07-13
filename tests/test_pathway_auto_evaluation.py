"""Tests for :mod:`intensicare.services.pathway_auto_evaluation`.

Covers the missing link the Dim A re-audit flagged: before this module
existed, ``sepsis_input_provider.build_sepsis_inputs`` had zero callers and
pathway criteria were only ever updated through a manual PUT against
``pathway_enrollment.evaluate_criteria``. These tests exercise the real
wiring — ``vitals.ingest_vitals`` calling ``evaluate_enrolled_pathways``
best-effort after every ingestion — against the ``demo_patients`` fixture
(MPI-DEMO-001..005, seeded via ``scripts/dev/seed_demo.py`` through the same
production ``ingest_vitals``/``enroll_patient``/``evaluate_criteria`` paths).

Scenarios:
  1. Ingesting a critical vital (PAM < 65) for MPI-DEMO-001 — which already
     holds an ACTIVE sepse enrollment per the seed — auto-evaluates
     ``crit-sep-pam`` with the fresh value/met, and the enrollment's overall
     severity reflects it.
  2. A patient with no active enrollments (MPI-DEMO-003, per the seed's own
     "no enrollment" design) is a clean no-op: zero outcomes, no exception.
  3. A provider exception (monkeypatched) during auto-evaluation is caught
     and logged — vitals ingestion still succeeds normally.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.schemas.vitals import VitalSignCreate
from intensicare.services.pathway_auto_evaluation import (
    AutoEvalReport,
    evaluate_enrolled_pathways,
)
from intensicare.services.pathway_enrollment import get_patient_pathways
from intensicare.services.vitals import ingest_vitals

pytestmark = pytest.mark.asyncio

MPI_SEPSE = "MPI-DEMO-001"  # per seed_demo.py: active sepse enrollment, crit-sep-pam=58 (critical)
MPI_NO_ENROLLMENT = "MPI-DEMO-003"  # per seed_demo.py: isolated-fever, no enrollment


async def _sepse_criteria_by_id(db_session: AsyncSession, mpi_id: str) -> dict[str, dict]:
    pathways = await get_patient_pathways(db_session, mpi_id, status_filter="active")
    sepse = next(p for p in pathways if p["pathway_slug"] == "sepse")
    return {c["id"]: c for c in sepse["criteria_data"]}, sepse


@pytest_asyncio.fixture
async def seeded(db_session: AsyncSession, demo_patients):
    """Alias fixture — makes the ``demo_patients`` dependency explicit per test."""
    return demo_patients


class TestAutoEvalOnCriticalVitals:
    async def test_ingest_critical_pam_updates_sepse_criterion_and_severity(
        self, db_session: AsyncSession, seeded
    ) -> None:
        """(1) Ingesting a fresh critical PAM auto-evaluates crit-sep-pam with a
        real value/met and recomputes the enrollment's overall severity.
        """
        # Sanity check: the seed already gave MPI-DEMO-001 an active sepse
        # enrollment with crit-sep-pam=58 (critical band, met=False).
        before, _before_sepse = await _sepse_criteria_by_id(db_session, MPI_SEPSE)
        assert before["crit-sep-pam"]["value"] == 58
        assert before["crit-sep-pam"]["met"] is False

        # Fresh vitals ingestion: a NEW, distinct critical PAM (45 mmHg,
        # < 65 -> critical band), later than every seeded vitals point, via
        # the real production ingestion path.
        recorded_at = datetime.now(timezone.utc)
        response, _alerts, is_replay = await ingest_vitals(
            db_session,
            VitalSignCreate(
                mpi_id=MPI_SEPSE,
                recorded_at=recorded_at,
                heart_rate=110,
                systolic_bp=80,
                diastolic_bp=40,
                map_value=45.0,
                temperature=37.0,
                spo2=94,
                respiratory_rate=18,
                source_system="test-auto-eval",
            ),
        )

        assert is_replay is False
        assert response.message == "Vital signs ingested successfully"

        after, after_sepse = await _sepse_criteria_by_id(db_session, MPI_SEPSE)

        # crit-sep-pam was re-evaluated with the fresh value.
        assert after["crit-sep-pam"]["value"] == 45.0
        # PAM 45 < 65 -> critical band -> NOT met (graded "met" = severity
        # == "normal", the pathway-enrollment "goal achieved" convention —
        # see pathway_auto_evaluation._criterion_met docstring).
        assert after["crit-sep-pam"]["met"] is False
        assert after["crit-sep-pam"]["evaluated_at"] != before["crit-sep-pam"]["evaluated_at"]

        # crit-sep-qsofa is always present (sirs_count/qsofa_score are never
        # omitted by build_sepsis_inputs) — proves the sepsis provider ran.
        assert after["crit-sep-qsofa"]["value"] is not None

        # Overall severity recomputed: crit-sep-pam is critical, which
        # dominates the (unchanged) crit-sep-lactato=watch from the seed.
        assert after_sepse["severity"] == "critical"

    async def test_report_reflects_the_updated_enrollment(
        self, db_session: AsyncSession, seeded
    ) -> None:
        """Calling evaluate_enrolled_pathways directly returns a populated report."""
        now = datetime.now(timezone.utc)
        report = await evaluate_enrolled_pathways(db_session, MPI_SEPSE, now)

        assert isinstance(report, AutoEvalReport)
        assert report.mpi_id == MPI_SEPSE
        sepse_outcomes = [o for o in report.outcomes if o.pathway_slug == "sepse"]
        assert len(sepse_outcomes) == 1
        outcome = sepse_outcomes[0]
        assert outcome.error is None
        assert outcome.criteria_updated > 0
        assert outcome.severity is not None


class TestAutoEvalNoEnrollments:
    async def test_patient_without_enrollments_is_a_clean_noop(
        self, db_session: AsyncSession, seeded
    ) -> None:
        """(2) A patient with zero active enrollments produces an empty report,
        and ingestion for them still succeeds normally.
        """
        now = datetime.now(timezone.utc)
        report = await evaluate_enrolled_pathways(db_session, MPI_NO_ENROLLMENT, now)

        assert report.mpi_id == MPI_NO_ENROLLMENT
        assert report.outcomes == []

        # And the real ingestion hook must not choke on the no-op either.
        response, _alerts, is_replay = await ingest_vitals(
            db_session,
            VitalSignCreate(
                mpi_id=MPI_NO_ENROLLMENT,
                recorded_at=now,
                heart_rate=80,
                systolic_bp=120,
                diastolic_bp=75,
                temperature=37.0,
                spo2=98,
                respiratory_rate=14,
                source_system="test-auto-eval",
            ),
        )
        assert is_replay is False
        assert response.message == "Vital signs ingested successfully"

    async def test_unknown_patient_is_also_a_clean_noop(self, db_session: AsyncSession) -> None:
        """No demo seed at all — evaluate_enrolled_pathways must not raise."""
        now = datetime.now(timezone.utc)
        report = await evaluate_enrolled_pathways(db_session, "MPI-NOBODY-HOME", now)
        assert report.outcomes == []


class TestAutoEvalFailureIsolation:
    async def test_provider_exception_does_not_fail_ingestion(
        self, db_session: AsyncSession, seeded, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """(3) build_sepsis_inputs raising must not fail vitals ingestion —
        the hook in vitals.ingest_vitals wraps auto-evaluation best-effort.
        """

        async def _boom(*_args, **_kwargs):
            raise RuntimeError("synthetic sepsis_input_provider failure")

        monkeypatch.setattr(
            "intensicare.services.pathway_auto_evaluation.build_sepsis_inputs", _boom
        )

        response, _alerts, is_replay = await ingest_vitals(
            db_session,
            VitalSignCreate(
                mpi_id=MPI_SEPSE,
                recorded_at=datetime.now(timezone.utc) + timedelta(seconds=1),
                heart_rate=100,
                systolic_bp=90,
                diastolic_bp=50,
                map_value=60.0,
                temperature=38.0,
                spo2=95,
                respiratory_rate=20,
                source_system="test-auto-eval-boom",
            ),
        )

        assert is_replay is False
        assert response.message == "Vital signs ingested successfully"
        assert response.id is not None

    async def test_evaluate_enrolled_pathways_itself_reports_the_error(
        self, db_session: AsyncSession, seeded, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Calling evaluate_enrolled_pathways directly surfaces the failure on
        that enrollment's outcome (error set), without raising.
        """

        async def _boom(*_args, **_kwargs):
            raise RuntimeError("synthetic sepsis_input_provider failure")

        monkeypatch.setattr(
            "intensicare.services.pathway_auto_evaluation.build_sepsis_inputs", _boom
        )

        now = datetime.now(timezone.utc)
        report = await evaluate_enrolled_pathways(db_session, MPI_SEPSE, now)

        sepse_outcomes = [o for o in report.outcomes if o.pathway_slug == "sepse"]
        assert len(sepse_outcomes) == 1
        assert sepse_outcomes[0].error is not None
        assert "synthetic sepsis_input_provider failure" in sepse_outcomes[0].error
