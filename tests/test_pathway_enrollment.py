"""Tests for the pathway enrollment/evaluation service
(:mod:`intensicare.services.pathway_enrollment`).

Ports the clinical-rule test cases from the legacy in-memory suite
(``tests/test_domain_trilhas_engine.py`` — see its ``TestPathwayEnrollment``,
``TestCriteriaEvaluation``, ``TestPatientPathways`` and ``TestPathwayProgress``
classes) onto the Postgres-backed implementation, using real pathway
definitions synced from the production YAML source
(``_work/alerts/pathways/*.yaml``) via the same boot-time path the app uses
(``TrilhasEngine`` + ``pathway_definitions_sync.sync_pathway_definitions``).

Two synced pathways are used, chosen for their different shapes:
  - id=1 "Ventilação Mecânica" (slug "ventilacao"): 2 states
    (initial -> alta[terminal]), 2 criteria (crit-vent-pf, crit-vent-peep).
    A single "all criteria met" evaluation both transitions AND completes
    the pathway in one step — exercises the terminal-state/completion path.
  - id=2 "Sepse" (slug "sepse"): 5 states
    (initial -> confirmacao -> tratamento -> estabilizacao -> alta[terminal]),
    15 criteria (7 preserved from v3 + 8 added by sepse.yaml v4.0.0's port of
    domain_sepsis.py's rich alert logic — see tests/test_sepse_yaml_parity.py).
    Used where a transition to a non-terminal intermediate state is needed
    (enrollment stays "active").
"""

from __future__ import annotations

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.pathway_definitions_sync import sync_pathway_definitions
from intensicare.services.pathway_enrollment import (
    enroll_patient,
    evaluate_criteria,
    get_pathway_progress,
    get_patient_pathways,
)
from intensicare.services.pathway_repository import PathwayRepository
from intensicare.services.trilhas_engine import TrilhasEngine

VENTILACAO_ID = 1
SEPSE_ID = 2

VENTILACAO_CRITERIA = ["crit-vent-pf", "crit-vent-peep"]

# sepse.yaml v4.0.0 (Sprint 3 sepsis governance — fix/sprint-3-sepsis-governance)
# ported the rich domain_sepsis.py alert logic (SIRS, PCT stewardship, SSC-2021
# bundle timers) to 8 new declarative criteria alongside the 7 preserved from
# v3. `evaluate_criteria`'s "all criteria met -> advance state" rule (Rule 8,
# pathway_enrollment.py) checks ALL of a pathway's criteria_data entries, not
# just a caller-chosen subset — so SEPSE_CRITERIA must list every criterion in
# the YAML for `_met(*SEPSE_CRITERIA)` to actually satisfy `all_met` and drive
# the transition tested below. Adjusted here (not a 2-file-scope violation of
# the sepsis port itself — this is the pre-existing enrollment suite reacting
# to the pathway's criteria count changing, exactly as anticipated by the port
# task's verification step 3).
SEPSE_CRITERIA = [
    "crit-sep-qsofa",
    "crit-sep-lactato",
    "crit-sep-pct",
    "crit-sep-pam",
    "crit-sep-culturas",
    "crit-sep-atb",
    "crit-sep-fluid",
    "crit-sep-screen",
    "crit-sep-organ",
    "crit-sep-shock",
    "crit-sep-bundle-atb-1h",
    "crit-sep-bundle-reaval-3h",
    "crit-sep-culturas-antes-atb",
    "crit-sep-pct-rising",
    "crit-sep-pct-deesc",
]


@pytest_asyncio.fixture
async def synced_pathways(db_session: AsyncSession) -> TrilhasEngine:
    """Sync the real YAML pathway catalog into the test DB.

    Uses the exact same production path as boot (``TrilhasEngine`` loads +
    compiles the YAML, ``sync_pathway_definitions`` upserts it into
    ``pathways``/``pathway_criteria``), so these tests exercise
    ``pathway_enrollment.py`` against real pathway shapes rather than
    hand-rolled fixtures. Runs inside the test's own db_session
    transaction/SAVEPOINT — reverted at teardown like any other write.
    """
    engine = TrilhasEngine()
    report = await sync_pathway_definitions(db_session, engine)
    assert not report.failed, f"pathway sync failures: {report.failed}"
    return engine


def _met(*ids: str) -> list[dict]:
    return [{"id": cid, "met": True, "value": 1} for cid in ids]


# ═══════════════════════════════════════════════════════════════════════════
# Enrollment — Rules 3, 4, 6
# ═══════════════════════════════════════════════════════════════════════════


class TestEnrollPatient:
    async def test_enroll_sets_initial_state_and_normal_severity(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 6: enrollment always starts at 'initial' / severity 'normal'."""
        result = await enroll_patient(db_session, mpi_id="MPI-ENR-001", pathway_id=VENTILACAO_ID)

        assert result.error == ""
        assert result.patient_pathway_id is not None
        assert result.mpi_id == "MPI-ENR-001"
        assert result.pathway_id == VENTILACAO_ID
        assert result.current_state == "initial"
        assert result.status == "active"
        assert result.severity == "normal"
        assert result.enrolled_at != ""

    async def test_enroll_populates_criteria_data_defaults(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 7 (setup): every pathway criterion appears with met=False by default."""
        await enroll_patient(db_session, mpi_id="MPI-ENR-002", pathway_id=VENTILACAO_ID)

        pathways = await get_patient_pathways(db_session, "MPI-ENR-002")
        assert len(pathways) == 1
        crit_ids = {c["id"] for c in pathways[0]["criteria_data"]}
        assert crit_ids == set(VENTILACAO_CRITERIA)
        assert all(c["met"] is False for c in pathways[0]["criteria_data"])

    async def test_enroll_with_initial_criteria(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        result = await enroll_patient(
            db_session,
            mpi_id="MPI-ENR-003",
            pathway_id=VENTILACAO_ID,
            initial_criteria=[{"id": "crit-vent-pf", "met": True, "value": 320}],
        )
        assert result.error == ""

        pathways = await get_patient_pathways(db_session, "MPI-ENR-003")
        criteria = pathways[0]["criteria_data"]
        pf = next(c for c in criteria if c["id"] == "crit-vent-pf")
        assert pf["met"] is True
        assert pf["value"] == 320
        # Criterion not specified in initial_criteria defaults to met=False.
        peep = next(c for c in criteria if c["id"] == "crit-vent-peep")
        assert peep["met"] is False

    async def test_enroll_duplicate_active_returns_semantic_pt_br_error(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 4: duplicate active enrollment is a clean PT-BR service error,
        not a raw IntegrityError bubbling out of the DB layer.
        """
        first = await enroll_patient(db_session, mpi_id="MPI-ENR-004", pathway_id=VENTILACAO_ID)
        assert first.error == ""

        second = await enroll_patient(db_session, mpi_id="MPI-ENR-004", pathway_id=VENTILACAO_ID)
        assert second.error != ""
        assert "já está inscrito" in second.error
        assert second.patient_pathway_id is None

    async def test_enroll_invalid_pathway_returns_error(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        result = await enroll_patient(db_session, mpi_id="MPI-ENR-005", pathway_id=999999)
        assert result.error != ""
        assert "não encontrado" in result.error
        assert result.patient_pathway_id is None

    async def test_enroll_inactive_pathway_returns_error(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        # Minimal manual upsert of an inactive pathway — deliberately not
        # going through the YAML/engine sync, since no shipped YAML pathway
        # is inactive.
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90100, "name": "Pathway Desativado", "slug": "desativado", "active": False},
            definition_hash="hash-v1",
            states=[
                {"id": "initial", "name": "Inicial", "order": 0, "is_terminal": False},
                {"id": "alta", "name": "Alta", "order": 1, "is_terminal": True},
            ],
            criteria=[],
        )

        result = await enroll_patient(db_session, mpi_id="MPI-ENR-006", pathway_id=90100)
        assert result.error != ""
        assert "não está ativo" in result.error


# ═══════════════════════════════════════════════════════════════════════════
# Criteria evaluation — Rules 7, 8, 9, 10, 3
# ═══════════════════════════════════════════════════════════════════════════


class TestEvaluateCriteria:
    async def test_all_criteria_met_transitions_to_terminal_and_completes(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 8 + Rule 3: ventilacao has only 2 states (initial -> alta
        [terminal]), so marking both criteria met in one shot both advances
        the state machine AND completes the pathway.
        """
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-100", pathway_id=VENTILACAO_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        result = await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-100",
            patient_pathway_id=pp_id,
            criteria_updates=_met(*VENTILACAO_CRITERIA),
        )

        assert result.state_changed is True
        assert result.new_state == "alta"
        assert "Avançando" in result.transition_reason
        # Severity is now band-based (gatekeeper G-S2 fix), not the old
        # met/total ratio — it no longer follows from "2/2 met". Both
        # criteria were evaluated here with the placeholder value=1 (see
        # _met()): crit-vent-pf=1 falls in the YAML graded band [0, 100)
        # -> "critical"; crit-vent-peep=1 fails its ">= 5" threshold ->
        # "normal". Pathway severity is the max of evaluated criteria ->
        # "critical". This is independent of the "met" flags driving the
        # state transition above (Rule 8 only reads "met", never severity).
        assert result.severity == "critical"

        pathways = await get_patient_pathways(db_session, "MPI-ENR-100", status_filter="completed")
        assert len(pathways) == 1
        assert pathways[0]["status"] == "completed"
        assert pathways[0]["completed_at"] is not None
        assert pathways[0]["current_state"] == "alta"

    async def test_partial_criteria_met_does_not_transition(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 8: state only advances when ALL criteria are met."""
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-101", pathway_id=SEPSE_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        result = await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-101",
            patient_pathway_id=pp_id,
            criteria_updates=_met("crit-sep-qsofa"),
        )

        assert result.state_changed is False
        # new_state stays at the current (unchanged) state when there's no
        # transition — evaluate_criteria only overwrites it on an advance.
        assert result.new_state == "initial"
        # Gatekeeper G-S2 fix: severity is no longer "1 of 7 met (~14%) ->
        # critical" (the old ratio rule wrongly treated the other 6
        # never-evaluated criteria as "failed"). Only crit-sep-qsofa was
        # evaluated (value=1), which falls in the YAML graded band [0, 2)
        # -> "normal"; the other 6 are PENDING and excluded from the
        # computation entirely. Pathway severity is "normal" — this is the
        # exact scenario the bug fix targets (partial evaluation must not
        # inflate severity).
        assert result.severity == "normal"

    async def test_all_criteria_met_transitions_to_intermediate_state(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Sepse has 5 states — reaching 'confirmacao' (not terminal) must
        leave the enrollment active (Rule 3 only fires on terminal states).
        """
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-102", pathway_id=SEPSE_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        result = await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-102",
            patient_pathway_id=pp_id,
            criteria_updates=_met(*SEPSE_CRITERIA),
        )

        assert result.state_changed is True
        assert result.new_state == "confirmacao"
        # Severity is band-based (gatekeeper G-S2 fix), not "7/7 met = 100%".
        # All 7 criteria were evaluated with the placeholder value=1 (see
        # _met()); classified against their real YAML bands: qsofa=1 ->
        # normal, lactato=1 -> normal, pct=1 -> watch, pam=1 -> critical
        # (PAM 1 mmHg is well under the 65 mmHg band boundary), the two
        # boolean bundle criteria (culturas/atb) -> urgent (truthy value=1
        # "fires"), fluid=1 -> critical. Max across evaluated = "critical".
        # This is independent of the "met" flags driving the transition
        # above (Rule 8 only reads "met", never severity).
        assert result.severity == "critical"

        pathways = await get_patient_pathways(db_session, "MPI-ENR-102")
        assert len(pathways) == 1
        assert pathways[0]["status"] == "active"
        assert pathways[0]["current_state"] == "confirmacao"

    async def test_criteria_updates_recorded_with_evaluated_at(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 7: individual criterion met/value/evaluated_at are updated."""
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-103", pathway_id=VENTILACAO_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        result = await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-103",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-pf", "met": True, "value": 310}],
        )

        pf = next(c for c in result.criteria if c["id"] == "crit-vent-pf")
        assert pf["met"] is True
        assert pf["value"] == 310
        assert pf["evaluated_at"] is not None

        peep = next(c for c in result.criteria if c["id"] == "crit-vent-peep")
        assert peep["met"] is False


# ═══════════════════════════════════════════════════════════════════════════
# get_patient_pathways — Rule 13 + legacy dict shape
# ═══════════════════════════════════════════════════════════════════════════


class TestGetPatientPathways:
    async def test_shape_matches_legacy_patient_pathway_dict(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        await enroll_patient(db_session, mpi_id="MPI-ENR-200", pathway_id=VENTILACAO_ID)

        pathways = await get_patient_pathways(db_session, "MPI-ENR-200")
        assert len(pathways) == 1
        pw = pathways[0]

        expected_keys = {
            "id",
            "mpi_id",
            "encounter_id",
            "bed_id",
            "unit",
            "pathway_id",
            "pathway_name",
            "pathway_slug",
            "current_state",
            "criteria_data",
            "status",
            "severity",
            "enrolled_at",
            "enrolled_by",
            "completed_at",
            "updated_at",
        }
        assert expected_keys <= set(pw.keys())

        assert pw["mpi_id"] == "MPI-ENR-200"
        assert pw["pathway_id"] == VENTILACAO_ID
        assert pw["pathway_name"] == "Ventilação Mecânica"
        assert pw["pathway_slug"] == "ventilacao"
        assert pw["status"] == "active"
        assert pw["completed_at"] is None

        # Timestamps are ISO strings, not datetime objects.
        assert isinstance(pw["enrolled_at"], str)
        from datetime import datetime as _dt

        _dt.fromisoformat(pw["enrolled_at"])
        assert isinstance(pw["updated_at"], str)
        _dt.fromisoformat(pw["updated_at"])

    async def test_status_filter_active_vs_completed_vs_all(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 13: status_filter scopes the returned enrollments."""
        completed_enrolled = await enroll_patient(
            db_session, mpi_id="MPI-ENR-201", pathway_id=VENTILACAO_ID
        )
        pp_id = completed_enrolled.patient_pathway_id
        assert pp_id is not None
        await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-201",
            patient_pathway_id=pp_id,
            criteria_updates=_met(*VENTILACAO_CRITERIA),
        )

        # Enroll in a second (still-active) pathway for the same patient.
        await enroll_patient(db_session, mpi_id="MPI-ENR-201", pathway_id=SEPSE_ID)

        active = await get_patient_pathways(db_session, "MPI-ENR-201", status_filter="active")
        assert len(active) == 1
        assert active[0]["pathway_id"] == SEPSE_ID

        completed = await get_patient_pathways(db_session, "MPI-ENR-201", status_filter="completed")
        assert len(completed) == 1
        assert completed[0]["pathway_id"] == VENTILACAO_ID

        every_status = await get_patient_pathways(db_session, "MPI-ENR-201", status_filter="all")
        assert len(every_status) == 2

    async def test_unknown_mpi_returns_empty_list(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        assert await get_patient_pathways(db_session, "MPI-DOES-NOT-EXIST") == []


# ═══════════════════════════════════════════════════════════════════════════
# get_pathway_progress — Rules 11, 12, 14
# ═══════════════════════════════════════════════════════════════════════════


class TestGetPathwayProgress:
    async def test_progress_criteria_summary(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 14: criteria_summary total/met/not_met/pending."""
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-300", pathway_id=VENTILACAO_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-300",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-pf", "met": True, "value": 300}],
        )

        progress = await get_pathway_progress(db_session, "MPI-ENR-300", pp_id)
        assert progress.criteria_summary == {"total": 2, "met": 1, "not_met": 1, "pending": 0}

    async def test_progress_trend_and_recommendation_across_transition(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        """Rule 11: trend 'none' before any transition, 'improving' after.
        Rule 12: PT-BR recommendation reflects severity for the pathway.
        """
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-301", pathway_id=VENTILACAO_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        # Before any evaluation: no transitions yet.
        progress0 = await get_pathway_progress(db_session, "MPI-ENR-301", pp_id)
        assert progress0.trend == "none"
        assert progress0.state_history == []

        # Only crit-vent-pf evaluated so far (value=300), no transition yet.
        # Gatekeeper G-S2 fix: severity is band-based, not "1 of 2 met (50%)
        # -> urgent". pf_ratio=300 falls in the YAML graded band [300, +inf)
        # -> "normal" (the only evaluated criterion; crit-vent-peep is
        # PENDING and excluded) -> pathway severity "normal" ->
        # "Dentro das metas" recommendation branch.
        await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-301",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-pf", "met": True, "value": 300}],
        )
        progress1 = await get_pathway_progress(db_session, "MPI-ENR-301", pp_id)
        assert progress1.trend == "none"
        assert "Dentro das metas" in progress1.recommendation
        assert "Ventilação Mecânica" in progress1.recommendation

        # All met -> transitions to terminal 'alta', completing the pathway.
        # crit-vent-peep=8 satisfies its ">= 5" YAML threshold predicate;
        # the compiler classifies a met threshold predicate as "urgent"
        # (same alerting-engine semantics used everywhere else in Trilhas —
        # reused as-is here, not reinterpreted). Max(normal, urgent) ->
        # "urgent" -> "ATENÇÃO" recommendation branch, even though the
        # pathway has just completed (severity reflects the criteria
        # values, not completion status).
        await evaluate_criteria(
            db_session,
            mpi_id="MPI-ENR-301",
            patient_pathway_id=pp_id,
            criteria_updates=[{"id": "crit-vent-peep", "met": True, "value": 8}],
        )
        progress2 = await get_pathway_progress(db_session, "MPI-ENR-301", pp_id)
        assert progress2.trend == "improving"
        assert len(progress2.state_history) == 1
        transition = progress2.state_history[0]
        assert transition["from_state"] == "initial"
        assert transition["to_state"] == "alta"
        assert transition["changed_at"] is not None
        assert "ATENÇÃO" in progress2.recommendation

    async def test_progress_unknown_patient_pathway_returns_fallback(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        progress = await get_pathway_progress(db_session, "MPI-ENR-999", 9999999)
        assert progress.patient_pathway_id == 9999999
        assert progress.pathway_name == "Desconhecido"
        assert progress.current_state == ""
        assert progress.criteria_summary == {"total": 0, "met": 0, "not_met": 0, "pending": 0}
        assert progress.criteria == []
        assert progress.state_history == []
        assert progress.trend == "none"
        assert "não localizada" in progress.recommendation

    async def test_progress_respects_mpi_id_scoping(
        self, db_session: AsyncSession, synced_pathways: TrilhasEngine
    ) -> None:
        enrolled = await enroll_patient(db_session, mpi_id="MPI-ENR-302", pathway_id=VENTILACAO_ID)
        pp_id = enrolled.patient_pathway_id
        assert pp_id is not None

        progress = await get_pathway_progress(db_session, "MPI-WRONG-PATIENT", pp_id)
        assert progress.pathway_name == "Desconhecido"
        assert "não localizada" in progress.recommendation
