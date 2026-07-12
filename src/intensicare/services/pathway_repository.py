"""Pathway persistence layer — pure DAO over the pathway ORM models.

Part of the Sprint 1 patient-safety work to replace the deprecated
in-memory :class:`intensicare.services.trilhas_state.PathwayStore` with a
real Postgres-backed store (see ADR-0020/ADR-0021).

This module contains **no clinical business logic** — only data access.
Clinical rules (enrollment eligibility, state-machine transitions,
severity/trend/recommendation derivation) live in
:mod:`intensicare.services.pathway_enrollment`.

All relationships on the ORM models in :mod:`intensicare.models.pathway`
are declared ``lazy="raise"`` (F-CODE-001) — every access MUST go through
an explicit ``selectinload`` here. Do not touch a relationship attribute
on an object returned by this module unless the fetching method already
eager-loaded it.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from intensicare.models.pathway import (
    Pathway,
    PathwayCriteria,
    PathwayStateTransition,
    PatientPathway,
)


class PathwayRepository:
    """Async DAO for pathway definitions and patient enrollments.

    Wraps a single :class:`AsyncSession`. Callers (services) own the
    transaction boundary — this repository only ``flush``es so that
    generated PKs/defaults are available to the caller; it never
    ``commit``s or ``rollback``s. That is the job of the FastAPI
    ``get_db`` dependency (commit-on-success / rollback-on-exception) or
    of the calling service when it needs to recover from an
    ``IntegrityError`` mid-request.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Pathway definitions
    # ------------------------------------------------------------------

    async def get_pathway(self, pathway_id: int) -> Pathway | None:
        """Fetch a pathway by ID with its criteria eager-loaded."""
        stmt = (
            select(Pathway).options(selectinload(Pathway.criteria)).where(Pathway.id == pathway_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pathway_by_slug(self, slug: str) -> Pathway | None:
        """Fetch a pathway by its unique slug with criteria eager-loaded."""
        stmt = select(Pathway).options(selectinload(Pathway.criteria)).where(Pathway.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ------------------------------------------------------------------
    # Patient enrollments
    # ------------------------------------------------------------------

    async def get_active_enrollment(self, mpi_id: str, pathway_id: int) -> PatientPathway | None:
        """Fetch the patient's active enrollment in a given pathway, if any.

        Used to enforce the "no duplicate active enrollment" rule ahead
        of the actual INSERT (fast path — the authoritative guard is the
        partial unique index ``uq_active_enrollment``).
        """
        stmt = (
            select(PatientPathway)
            .options(selectinload(PatientPathway.pathway))
            .where(
                PatientPathway.mpi_id == mpi_id,
                PatientPathway.pathway_id == pathway_id,
                PatientPathway.status == "active",
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_enrollment(self, patient_pathway_id: int, mpi_id: str) -> PatientPathway | None:
        """Fetch a single enrollment scoped to the owning patient."""
        stmt = (
            select(PatientPathway)
            .options(selectinload(PatientPathway.pathway))
            .where(
                PatientPathway.id == patient_pathway_id,
                PatientPathway.mpi_id == mpi_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_enrollments(self, mpi_id: str, status: str | None) -> list[PatientPathway]:
        """List a patient's enrollments, optionally filtered by status.

        ``status=None`` returns enrollments in every status (the
        "all" filter at the service layer).
        """
        stmt = (
            select(PatientPathway)
            .options(selectinload(PatientPathway.pathway))
            .where(PatientPathway.mpi_id == mpi_id)
        )
        if status is not None:
            stmt = stmt.where(PatientPathway.status == status)
        stmt = stmt.order_by(PatientPathway.enrolled_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_enrollment(self, **fields: Any) -> PatientPathway:
        """Insert a new enrollment and return it with generated fields populated.

        Does not catch ``IntegrityError`` — the partial unique index
        ``uq_active_enrollment`` (migration 0037) may reject a racing
        duplicate active enrollment; the caller (service layer) is
        responsible for catching that and translating it into the
        clinical "already enrolled" error.
        """
        enrollment = PatientPathway(**fields)
        self.db.add(enrollment)
        await self.db.flush()
        await self.db.refresh(enrollment)
        return enrollment

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    async def add_transition(
        self, pp_id: int, from_state: str, to_state: str, reason: str
    ) -> PathwayStateTransition:
        """Record a state transition for an enrollment."""
        transition = PathwayStateTransition(
            patient_pathway_id=pp_id,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )
        self.db.add(transition)
        await self.db.flush()
        await self.db.refresh(transition)
        return transition

    async def list_transitions(self, pp_id: int) -> list[PathwayStateTransition]:
        """List all transitions for an enrollment, oldest first."""
        stmt = (
            select(PathwayStateTransition)
            .where(PathwayStateTransition.patient_pathway_id == pp_id)
            .order_by(PathwayStateTransition.changed_at.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # Boot-time definition sync (generic — consumed by the pathway sync job)
    # ------------------------------------------------------------------

    async def upsert_pathway_definition(
        self,
        meta: dict[str, Any],
        definition_hash: str,
        states: list[dict[str, Any]],
        criteria: list[dict[str, Any]],
    ) -> Pathway:
        """Upsert a compiled pathway definition (content-addressed by hash).

        Intended for the boot-time pathway sync job (compiled YAML →
        Postgres). Deliberately generic about the shape of ``meta`` /
        ``criteria`` so it isn't coupled to any single YAML schema.

        Args:
            meta: Pathway metadata. Must contain ``id``, ``name``, ``slug``.
                May contain ``description`` and ``active``.
            definition_hash: SHA-256 content hash of the compiled definition.
            states: Array of state objects, stored verbatim in the
                ``pathways.states`` JSONB column.
            criteria: Array of criteria dicts, each expected to contain at
                least ``id``, ``name``, ``category``. Optional keys:
                ``description``, ``unit``, ``normal_range``,
                ``alert_threshold``.

        Behavior:
            - INSERT if the pathway id does not exist yet.
            - UPDATE (name/slug/description/active/states/definition_hash)
              only if the stored ``definition_hash`` differs from the one
              supplied (or is NULL) — a no-op otherwise, so re-running the
              sync with an unchanged definition does not churn the table.
            - Criteria are synced (delete-and-insert for this pathway_id)
              only when the definition actually changed, since criteria
              are considered part of the versioned definition.
        """
        pathway_id = meta["id"]

        insert_stmt = pg_insert(Pathway).values(
            id=pathway_id,
            name=meta["name"],
            slug=meta["slug"],
            description=meta.get("description"),
            active=meta.get("active", True),
            states=states,
            definition_hash=definition_hash,
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[Pathway.id],
            set_={
                "name": insert_stmt.excluded.name,
                "slug": insert_stmt.excluded.slug,
                "description": insert_stmt.excluded.description,
                "active": insert_stmt.excluded.active,
                "states": insert_stmt.excluded.states,
                "definition_hash": insert_stmt.excluded.definition_hash,
            },
            where=Pathway.definition_hash.is_distinct_from(definition_hash),
        ).returning(Pathway.id)

        result = await self.db.execute(upsert_stmt)
        definition_changed = result.first() is not None

        if definition_changed:
            await self.db.execute(
                delete(PathwayCriteria).where(PathwayCriteria.pathway_id == pathway_id)
            )
            for crit in criteria:
                self.db.add(
                    PathwayCriteria(
                        id=crit["id"],
                        name=crit["name"],
                        category=crit.get("category", ""),
                        description=crit.get("description"),
                        unit=crit.get("unit"),
                        normal_range=crit.get("normal_range"),
                        alert_threshold=crit.get("alert_threshold"),
                        pathway_id=pathway_id,
                    )
                )

        await self.db.flush()

        pathway = await self.get_pathway(pathway_id)
        if pathway is None:  # pragma: no cover - defensive, should be unreachable
            raise RuntimeError(
                f"upsert_pathway_definition: pathway {pathway_id} missing after upsert"
            )
        return pathway
