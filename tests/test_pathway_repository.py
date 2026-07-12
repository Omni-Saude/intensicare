"""Tests for the pathway persistence DAO (:mod:`intensicare.services.pathway_repository`).

Exercises ``PathwayRepository`` directly against a real Postgres test
database (the ``db_session`` fixture — external transaction + per-test
SAVEPOINT rollback, see ``tests/conftest.py``). Covers:

- CRUD of ``PatientPathway`` enrollments.
- That relationships eager-loaded via ``selectinload`` (``Pathway.criteria``
  through :meth:`PathwayRepository.get_pathway`, ``PatientPathway.pathway``
  through the enrollment getters) can be accessed without tripping the
  ``lazy="raise"`` guard (F-CODE-001) — and conversely that relationships
  the repository did *not* eager-load (``PatientPathway.transitions``,
  ``Pathway.criteria`` reached transitively through an enrollment) DO raise,
  proving the guard is actually active rather than silently N+1-loading.
- The partial unique index ``uq_active_enrollment`` (migration 0037): since
  the test schema is built from ``Base.metadata.create_all`` (SQLAlchemy
  ORM metadata), not ``alembic upgrade`` (raw-SQL migrations aren't
  replayed), ``conftest.py::create_tables`` creates this index explicitly
  once per test session, right after ``create_all`` — so it's present for
  every test without any per-test DDL (see ``TestActiveEnrollmentUniqueness``
  for why those tests still call ``db_session.commit()``).
- ``upsert_pathway_definition``: insert, no-op re-upsert on unchanged hash,
  and update + criteria resync on a changed hash.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.services.pathway_repository import PathwayRepository

# pytest-asyncio runs in "auto" mode (see pyproject.toml) with the default
# fixture/test loop scope pinned to "session" — no per-test marker needed;
# every `async def test_*` here shares the one event loop with db_session.


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _states() -> list[dict[str, Any]]:
    return [
        {"id": "initial", "name": "Avaliação Inicial", "order": 0, "is_terminal": False},
        {"id": "alta", "name": "Alta", "order": 1, "is_terminal": True},
    ]


def _criteria(*ids: str) -> list[dict[str, Any]]:
    return [
        {
            "id": cid,
            "name": f"Critério {cid}",
            "category": "teste",
            "description": f"Descrição {cid}",
            "unit": None,
            "normal_range": None,
            "alert_threshold": None,
        }
        for cid in ids
    ]


async def _enroll(
    repo: PathwayRepository,
    *,
    mpi_id: str,
    pathway_id: int,
    status: str = "active",
    current_state: str = "initial",
    encounter_id: str = "ENC-1",
):
    now = datetime.now(timezone.utc)
    return await repo.create_enrollment(
        mpi_id=mpi_id,
        encounter_id=encounter_id,
        bed_id="B1",
        unit="UTI-1",
        pathway_id=pathway_id,
        current_state=current_state,
        criteria_data=[],
        status=status,
        severity="normal",
        enrolled_at=now,
        enrolled_by="test",
        completed_at=None,
        updated_at=now,
    )


# ═══════════════════════════════════════════════════════════════════════════
# upsert_pathway_definition
# ═══════════════════════════════════════════════════════════════════════════


class TestUpsertPathwayDefinition:
    async def test_insert_new_pathway(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        pathway = await repo.upsert_pathway_definition(
            meta={"id": 90001, "name": "Teste A", "slug": "teste-a", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-a", "crit-b"),
        )

        assert pathway.id == 90001
        assert pathway.name == "Teste A"
        assert pathway.slug == "teste-a"
        assert pathway.definition_hash == "hash-v1"
        assert pathway.active is True
        assert pathway.states == _states()

        # Pathway.criteria was eager-loaded by get_pathway() (called
        # internally by upsert_pathway_definition to build the return
        # value) — accessing it must not trip lazy="raise".
        crit_ids = {c.id for c in pathway.criteria}
        assert crit_ids == {"crit-a", "crit-b"}

    async def test_reupsert_same_hash_is_noop(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90002, "name": "Original", "slug": "teste-b", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-a"),
        )

        # Re-run with the SAME hash but different content — the WHERE
        # definition_hash IS DISTINCT FROM clause must block the update
        # entirely (content-addressed no-op), regardless of what's passed.
        pathway = await repo.upsert_pathway_definition(
            meta={"id": 90002, "name": "Changed Name", "slug": "teste-b-changed", "active": False},
            definition_hash="hash-v1",
            states=[{"id": "should-not-apply", "name": "x", "order": 0, "is_terminal": True}],
            criteria=_criteria("crit-should-not-apply"),
        )

        assert pathway.name == "Original"
        assert pathway.slug == "teste-b"
        assert pathway.active is True
        assert pathway.states == _states()
        crit_ids = {c.id for c in pathway.criteria}
        assert crit_ids == {"crit-a"}

    async def test_hash_change_updates_and_resyncs_criteria(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90003, "name": "V1", "slug": "teste-c", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-old-1", "crit-old-2"),
        )

        new_states = [
            {"id": "initial", "name": "Avaliação Inicial", "order": 0, "is_terminal": False},
            {"id": "meio", "name": "Estado Intermediário", "order": 1, "is_terminal": False},
            {"id": "alta", "name": "Alta", "order": 2, "is_terminal": True},
        ]
        pathway = await repo.upsert_pathway_definition(
            meta={"id": 90003, "name": "V2", "slug": "teste-c-v2", "active": True},
            definition_hash="hash-v2",
            states=new_states,
            criteria=_criteria("crit-new-1"),
        )

        assert pathway.name == "V2"
        assert pathway.slug == "teste-c-v2"
        assert pathway.definition_hash == "hash-v2"
        assert pathway.states == new_states

        # Criteria resynced: old ones deleted, only the new set remains.
        crit_ids = {c.id for c in pathway.criteria}
        assert crit_ids == {"crit-new-1"}


# ═══════════════════════════════════════════════════════════════════════════
# Pathway getters + eager-load / lazy="raise" boundary
# ═══════════════════════════════════════════════════════════════════════════


class TestPathwayGetters:
    async def test_get_pathway_by_slug_criteria_accessible(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90010, "name": "Slug Test", "slug": "slug-test", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-x", "crit-y"),
        )

        pathway = await repo.get_pathway_by_slug("slug-test")
        assert pathway is not None
        # selectinload(Pathway.criteria) means this does NOT raise.
        assert {c.id for c in pathway.criteria} == {"crit-x", "crit-y"}

    async def test_get_pathway_unknown_returns_none(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        assert await repo.get_pathway(999999) is None
        assert await repo.get_pathway_by_slug("does-not-exist") is None


# ═══════════════════════════════════════════════════════════════════════════
# Enrollment CRUD
# ═══════════════════════════════════════════════════════════════════════════


class TestEnrollmentCrud:
    async def test_create_and_get_active_enrollment(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90020, "name": "CRUD Pathway", "slug": "crud-pathway", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-1"),
        )

        enrollment = await _enroll(repo, mpi_id="MPI-REPO-001", pathway_id=90020)
        assert enrollment.id is not None
        assert enrollment.mpi_id == "MPI-REPO-001"
        assert enrollment.pathway_id == 90020
        assert enrollment.current_state == "initial"
        assert enrollment.status == "active"

        fetched = await repo.get_active_enrollment("MPI-REPO-001", 90020)
        assert fetched is not None
        assert fetched.id == enrollment.id
        # PatientPathway.pathway was eager-loaded (selectinload) — safe to touch.
        assert fetched.pathway.slug == "crud-pathway"

    async def test_get_active_enrollment_none_when_not_active(
        self, db_session: AsyncSession
    ) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={
                "id": 90021,
                "name": "Inactive Enrollment",
                "slug": "inactive-enrollment",
                "active": True,
            },
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )
        await _enroll(repo, mpi_id="MPI-REPO-002", pathway_id=90021, status="completed")

        assert await repo.get_active_enrollment("MPI-REPO-002", 90021) is None

    async def test_get_enrollment_scoped_to_mpi_id(self, db_session: AsyncSession) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90022, "name": "Scoped", "slug": "scoped", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )
        enrollment = await _enroll(repo, mpi_id="MPI-REPO-003", pathway_id=90022)

        # Right mpi_id: found.
        found = await repo.get_enrollment(enrollment.id, "MPI-REPO-003")
        assert found is not None
        assert found.id == enrollment.id

        # Wrong mpi_id: not found (scoping to the owning patient).
        assert await repo.get_enrollment(enrollment.id, "MPI-WRONG") is None

    async def test_list_enrollments_filters_by_status_and_orders_desc(
        self, db_session: AsyncSession
    ) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90023, "name": "List A", "slug": "list-a", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )
        await repo.upsert_pathway_definition(
            meta={"id": 90024, "name": "List B", "slug": "list-b", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )

        active_one = await _enroll(repo, mpi_id="MPI-REPO-004", pathway_id=90023)
        completed_one = await _enroll(
            repo, mpi_id="MPI-REPO-004", pathway_id=90024, status="completed"
        )

        all_enrollments = await repo.list_enrollments("MPI-REPO-004", None)
        assert {e.id for e in all_enrollments} == {active_one.id, completed_one.id}

        active_only = await repo.list_enrollments("MPI-REPO-004", "active")
        assert [e.id for e in active_only] == [active_one.id]

        completed_only = await repo.list_enrollments("MPI-REPO-004", "completed")
        assert [e.id for e in completed_only] == [completed_one.id]

    async def test_enrollment_pathway_criteria_not_eager_loaded_raises(
        self, db_session: AsyncSession
    ) -> None:
        """Enrollment getters only selectinload PatientPathway.pathway — the
        transitive Pathway.criteria was NOT eager-loaded through that chain,
        so touching it must trip lazy="raise" (F-CODE-001). Callers needing
        criteria must fetch the pathway explicitly via repo.get_pathway().
        """
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90025, "name": "Raise Test", "slug": "raise-test", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=_criteria("crit-1"),
        )
        await _enroll(repo, mpi_id="MPI-REPO-005", pathway_id=90025)

        fetched = await repo.get_active_enrollment("MPI-REPO-005", 90025)
        assert fetched is not None
        with pytest.raises(InvalidRequestError):
            _ = fetched.pathway.criteria

    async def test_enrollment_transitions_not_eager_loaded_raises(
        self, db_session: AsyncSession
    ) -> None:
        """PatientPathway.transitions is lazy="raise" and none of the
        repository getters eager-load it — must use list_transitions().
        """
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={
                "id": 90026,
                "name": "Transitions Raise",
                "slug": "transitions-raise",
                "active": True,
            },
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )
        enrollment = await _enroll(repo, mpi_id="MPI-REPO-006", pathway_id=90026)

        fetched = await repo.get_enrollment(enrollment.id, "MPI-REPO-006")
        assert fetched is not None
        with pytest.raises(InvalidRequestError):
            _ = fetched.transitions


# ═══════════════════════════════════════════════════════════════════════════
# State transitions
# ═══════════════════════════════════════════════════════════════════════════


class TestStateTransitions:
    async def test_add_and_list_transitions_ordered_oldest_first(
        self, db_session: AsyncSession
    ) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90030, "name": "Transitions", "slug": "transitions", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )
        enrollment = await _enroll(repo, mpi_id="MPI-REPO-007", pathway_id=90030)

        t1 = await repo.add_transition(
            pp_id=enrollment.id, from_state="initial", to_state="meio", reason="primeiro"
        )
        t2 = await repo.add_transition(
            pp_id=enrollment.id, from_state="meio", to_state="alta", reason="segundo"
        )

        transitions = await repo.list_transitions(enrollment.id)
        assert [t.id for t in transitions] == [t1.id, t2.id]
        assert transitions[0].from_state == "initial"
        assert transitions[0].to_state == "meio"
        assert transitions[0].reason == "primeiro"
        assert transitions[1].to_state == "alta"


# ═══════════════════════════════════════════════════════════════════════════
# uq_active_enrollment partial unique index (migration 0037)
# ═══════════════════════════════════════════════════════════════════════════


class TestActiveEnrollmentUniqueness:
    """The partial unique index ``uq_active_enrollment`` (migration 0037) is
    created once per test session in ``conftest.py::create_tables`` (right
    after ``Base.metadata.create_all``, which doesn't replay alembic's
    raw-SQL migrations on its own) — no per-test DDL needed.

    Each test below still calls ``db_session.commit()`` after the first
    enrollment, on purpose: in production, ``PathwayRepository`` only
    ``flush()``es (see its docstring — the caller/``get_db`` dependency owns
    the transaction boundary), so ``enroll_patient`` for one HTTP request
    commits at the FastAPI ``get_db`` boundary before the next request's
    enrollment attempt begins. Committing here simulates that same request
    boundary: it releases the current SAVEPOINT and opens a fresh one (the
    fixture's OUTER transaction — and therefore full-suite isolation — is
    untouched; see ``db_session``'s docstring in conftest.py), so that when
    the *second* enrollment's flush fails and gets rolled back, only that
    second attempt's SAVEPOINT is undone — the already-"committed" first
    enrollment survives, exactly like two independent requests would.
    """

    async def test_second_active_enrollment_raises_integrity_error(
        self, db_session: AsyncSession
    ) -> None:
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90040, "name": "Uniqueness", "slug": "uniqueness", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )

        first = await _enroll(repo, mpi_id="MPI-REPO-008", pathway_id=90040)
        await db_session.commit()

        with pytest.raises(IntegrityError):
            await _enroll(repo, mpi_id="MPI-REPO-008", pathway_id=90040)

        # The failed flush aborted the current SAVEPOINT — roll back to
        # recover the session for further use, mirroring exactly what
        # pathway_enrollment.enroll_patient does on this race path.
        await db_session.rollback()

        still_active = await repo.get_active_enrollment("MPI-REPO-008", 90040)
        assert still_active is not None
        assert still_active.id == first.id

    async def test_reenroll_allowed_after_previous_completed(
        self, db_session: AsyncSession
    ) -> None:
        """The unique index is partial (WHERE status='active') — a patient
        may be re-enrolled in the same pathway once the prior enrollment is
        no longer active.
        """
        repo = PathwayRepository(db_session)
        await repo.upsert_pathway_definition(
            meta={"id": 90041, "name": "Reenroll", "slug": "reenroll", "active": True},
            definition_hash="hash-v1",
            states=_states(),
            criteria=[],
        )

        first = await _enroll(repo, mpi_id="MPI-REPO-009", pathway_id=90041, status="completed")
        await db_session.commit()
        second = await _enroll(repo, mpi_id="MPI-REPO-009", pathway_id=90041, status="active")

        assert second.id != first.id
        active = await repo.get_active_enrollment("MPI-REPO-009", 90041)
        assert active is not None
        assert active.id == second.id
