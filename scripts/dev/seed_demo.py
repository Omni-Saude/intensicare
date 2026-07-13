"""Synthetic demo-data seeder for IntensiCare (Sprint 1 patient-safety demo).

Seeds a fixed, clearly-synthetic namespace of 5 patients
(``MPI-DEMO-001``..``MPI-DEMO-005``) into ``UTI-DEMO`` beds ``DEMO-01``..
``DEMO-05``, ingests a short vitals history for each through the *real*
production ingestion path (:func:`intensicare.services.vitals.ingest_vitals`
— so MEWS/NEWS2/SOFA/qSOFA scoring and the live alert engine run exactly as
they would for a real patient), and enrolls a subset of them into care
pathways via the *real* enrollment path
(:func:`intensicare.services.pathway_enrollment.enroll_patient` /
``evaluate_criteria``).

Design decisions
-----------------
- **Patient upsert reuses ``mpi_resolver.sync_patient_cache`` verbatim**
  (same PHI-encryption path used for real MPI-synced patients) rather than
  duplicating its upsert/encryption logic. Since ``MPIClient`` only talks to
  a real external MPI HTTP service (there is no fake/dev-mode client in this
  codebase), this module installs a tiny in-memory stand-in
  (:class:`_DemoMPIClient`) as the module-level singleton returned by
  ``intensicare.clients.mpi_client.get_mpi_client()`` for the duration of the
  upsert, then restores whatever was there before. ``mpi_resolver.py`` is not
  modified.
- **PHI encryption GUC**: ``patient_encryption.encrypt_phi`` requires the
  Postgres GUC ``app.encryption_key`` to already be set on the session (see
  ``kms_keys.set_session_encryption_key``). This module calls it once for
  ``DEMO_TENANT_ID`` before the patient upsert — mirroring what an
  authenticated request middleware would do.
- **Tenant choice**: demo patients use ``tenant_id="austa"`` (not the
  ``"default"`` house convention documented in migration 0038) because, at
  the time this seed was written, this dev database only has
  ``threshold_config`` rows seeded for tenant ``"austa"`` (migration 0038,
  which seeds the ``"default"`` tenant, had not been applied yet). Using
  ``"austa"`` lets the live alert engine actually fire MEWS/NEWS2 alerts for
  the critical demo patients instead of silently no-op'ing on a missing
  threshold config. If migration 0038 lands and ``"default"`` gets
  first-class thresholds too, this constant can move back to the house
  convention with no other code changes.
- **Pathway criteria band evaluation reuses
  ``intensicare.services.trilhas_compiler.PredicateCompiler`` verbatim** —
  the exact same graded-band compiler the runtime alert/pathway engine uses
  — rather than re-implementing band-range matching. Note the polarity
  flip: ``PredicateCompiler``'s own ``EvaluationResult.met`` means "this
  value is alert-worthy" (``severity != "normal"``), which is the opposite
  of what ``pathway_enrollment.evaluate_criteria`` expects for its
  ``met`` field (``True`` == "criterion goal achieved"). This module derives
  ``met = (severity == "normal")`` explicitly — see ``_evaluate_pathway_input``.
- **Boot-time pathway sync tolerance**: enrollment (Etapa C) requires the
  ``pathways``/``pathway_criteria`` tables to be populated. This module
  imports ``intensicare.services.pathway_definitions_sync`` lazily and, if
  the pathways table is empty AND that module can't be imported/run, skips
  enrollment with a clear warning recorded on :class:`SeedReport` instead of
  failing the whole seed. As of this writing the module already exists on
  this branch and the sync succeeds.
- **Lab/bundle inputs with no vitals-schema home** (``lactato``,
  ``fluid_volume``, ``rass_score``, ``bps_score`` — all declared
  ``source: amh_gold`` or otherwise absent from
  ``VitalSignCreate``/``VitalSign``) are passed directly as pathway
  evaluation inputs; ``pam`` *is* a vitals field (``map_value``) and the
  seeded vitals carry the same numeric value quoted in the spec, so the
  pathway evaluation is consistent with the persisted vitals history.
- **``patient_cache`` schema drift fallback**: the ORM model
  (``intensicare.models.patient_cache.PatientCache``) and
  ``mpi_resolver.sync_patient_cache`` both assume the *migrated* schema from
  alembic migration ``0004`` (``display_name``/``mrn``/``birth_date`` as
  encrypted ``BYTEA``). Some dev databases predate that migration being
  applied (this repo's alembic history currently has a duplicate revision id
  and isn't cleanly ``alembic upgrade head``-able — a pre-existing issue
  outside this task's 3-file scope) and still have the legacy plaintext
  schema (``varchar``/``varchar``/``date``). Blindly running the real,
  encrypted-BYTEA upsert against a legacy-schema table doesn't just fail
  loudly — Postgres *silently* coerces the ``BYTEA`` bind value into its
  hex-escaped text form for a ``varchar`` column (e.g. ``\\x1234ab...``),
  which would corrupt the ``display_name``/``mrn`` of every row in the
  *shared* ``patient_cache`` table it touches (not just the demo namespace)
  the moment such an ALTER-adjacent write happened. Rather than ALTERing the
  live (shared, multi-tenant) table to the new schema — which would also be
  visible to and could break the currently-running server's
  non-decrypting read paths for pre-existing patients — this module detects
  the column's actual runtime type (``_patient_cache_schema_supports_encrypted_phi``)
  and, only when the table is still on the legacy schema, upserts demo
  patients through a schema-compatible fallback
  (``_upsert_patient_legacy_schema``) that still computes the real blind
  index via ``patient_encryption.compute_mrn_bidx``. The primary path (via
  ``mpi_resolver.sync_patient_cache``, fully PHI-encrypted) activates
  automatically once the target database is migrated to ``0004``.
- **Idempotency**: patient upsert is a real upsert (keyed by ``mpi_id``).
  The clinical trail (vitals/scores/alerts/pathway enrollments+transitions)
  is wiped for the ``MPI-DEMO-%`` namespace and fully re-inserted on every
  call, so running ``seed()``/the CLI twice produces identical counts.
  ``patient_cache`` rows for the demo namespace are intentionally NOT wiped
  by a normal ``seed()`` call (only by ``--wipe``), matching the "namespace
  wipe" semantics: vitals/scores/alerts/pathways/pathway_state_transitions.
- **Fixture vs CLI transactions**: ``seed()`` itself never commits — every
  write goes through the same ``db.flush()``-only services the production
  code paths already use. The CLI (`main()`) commits explicitly at the end;
  the pytest fixture (see ``tests/conftest.py::demo_patients``) relies on the
  caller's transaction/SAVEPOINT instead.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Make the repo root importable (`scripts.dev.seed_demo` is not an installed
# package) so this file also works when invoked directly as
# `python scripts/dev/seed_demo.py` from the repo root, and so `src/` (where
# the `intensicare` package lives) is importable regardless of whether the
# project was `pip install -e`'d.
_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# ── Demo namespace constants ────────────────────────────────────────────
DEMO_MPI_PREFIX = "MPI-DEMO-"
DEMO_UNIT = "UTI-DEMO"
DEMO_TENANT_ID = "austa"  # see module docstring — chosen so alerts actually fire
SEPSE_PATHWAY_ID = 2
SEDACAO_PATHWAY_ID = 6
VITALS_POINTS_PER_PATIENT = 10  # within the 8-12 spec range


@dataclass
class SeedReport:
    """Summary of a single ``seed()`` run."""

    profile: str = "default"
    patients: list[str] = field(default_factory=list)
    vitals_ingested: int = 0
    alerts_created: int = 0
    pathways_synced: bool = False
    pathway_sync_message: str = ""
    enrollments: list[dict[str, Any]] = field(default_factory=list)
    enrollment_skipped_reason: str | None = None

    def as_text(self) -> str:
        lines = [
            f"SeedReport(profile={self.profile!r})",
            f"  patients:            {len(self.patients)} — {self.patients}",
            f"  vitals_ingested:     {self.vitals_ingested}",
            f"  alerts_created:      {self.alerts_created}",
            f"  pathways_synced:     {self.pathways_synced} ({self.pathway_sync_message})",
        ]
        if self.enrollment_skipped_reason:
            lines.append(f"  enrollments SKIPPED: {self.enrollment_skipped_reason}")
        else:
            lines.append(f"  enrollments:         {len(self.enrollments)}")
            for enr in self.enrollments:
                if enr.get("error"):
                    lines.append(f"    - {enr['mpi_id']} pathway={enr['pathway_id']}: ERROR {enr['error']}")
                else:
                    lines.append(
                        f"    - {enr['mpi_id']} pathway={enr['pathway_id']} "
                        f"pp_id={enr['patient_pathway_id']} severity={enr['severity']}"
                    )
        return "\n".join(lines)


# ── Per-patient clinical narrative ──────────────────────────────────────
# (num) -> (display_name, vitals profile (lo, hi) tuples interpolated across
# the timeline, avpu at the deteriorated end of the timeline)
_PATIENT_NAMES: dict[str, str] = {
    "001": "DEMO Sepse Crítica",
    "002": "DEMO Sedação Agitação",
    "003": "DEMO Febre Isolada",
    "004": "DEMO Controle Normal",
    "005": "DEMO Choque Séptico Grave",
}

# Each profile interpolates linearly from the first vitals point (now-6h) to
# the last (now-5min), so the *most recent* reading matches the target
# clinical picture described in the approved design.
_VITALS_PROFILES: dict[str, dict[str, Any]] = {
    "001": {  # Sepse Crítica — worsening trend, ends at PAS~75/FC118/FR24/T38.9/SpO2 92
        "heart_rate": (98, 118),
        "systolic_bp": (92, 75),
        "diastolic_bp": (58, 42),
        "respiratory_rate": (20, 24),
        "temperature": (37.8, 38.9),
        "spo2": (95, 92),
        "map_value": (68, 58),
        "avpu_final": "V",
    },
    "002": {  # Sedação Agitação — mild tachycardia/tachypnea consistent with RASS +3
        "heart_rate": (92, 112),
        "systolic_bp": (124, 132),
        "diastolic_bp": (78, 84),
        "respiratory_rate": (18, 22),
        "temperature": (36.9, 37.2),
        "spo2": (97, 96),
        "map_value": (92, 96),
        "avpu_final": "A",
    },
    "003": {  # Febre Isolada — flat/normal except temperature
        "heart_rate": (86, 90),
        "systolic_bp": (118, 116),
        "diastolic_bp": (74, 72),
        "respiratory_rate": (18, 18),
        "temperature": (38.5, 38.5),
        "spo2": (97, 97),
        "map_value": (86, 86),
        "avpu_final": "A",
    },
    "004": {  # Controle Normal — negative control, flat/normal throughout
        "heart_rate": (78, 78),
        "systolic_bp": (118, 118),
        "diastolic_bp": (76, 76),
        "respiratory_rate": (16, 16),
        "temperature": (36.8, 36.8),
        "spo2": (98, 98),
        "map_value": (90, 90),
        "avpu_final": "A",
    },
    "005": {  # Choque Séptico Grave — most severe, ends at PAM 58 (per spec)
        "heart_rate": (112, 134),
        "systolic_bp": (80, 65),
        "diastolic_bp": (50, 38),
        "respiratory_rate": (24, 28),
        "temperature": (38.6, 39.4),
        "spo2": (91, 87),
        "map_value": (66, 58),
        "avpu_final": "V",
    },
}


def _lerp(lo: float, hi: float, fraction: float) -> float:
    return lo + (hi - lo) * fraction


# ── Etapa A — patients ───────────────────────────────────────────────────


async def _build_demo_mpi_patients(now: datetime) -> dict[str, Any]:
    """Build synthetic MPIPatient records for the fake MPI client."""
    from intensicare.clients.mpi_client import MPIPatient

    admission_dt = (now - timedelta(hours=6)).isoformat()
    patients: dict[str, Any] = {}
    for num, name in _PATIENT_NAMES.items():
        mpi_id = f"{DEMO_MPI_PREFIX}{num}"
        patients[mpi_id] = MPIPatient(
            mpi_id=mpi_id,
            tenant_id=DEMO_TENANT_ID,
            display_name=name,
            mrn=f"DEMO-MRN-{num}",
            birth_date="1960-01-01",
            cpf=None,
            cns=None,
            gender="O",
            admission_dt=admission_dt,
            discharge_dt=None,
            bed_id=f"DEMO-{num[-2:]}",
            unit=DEMO_UNIT,
        )
    return patients


async def _set_demo_encryption_key(db: AsyncSession, tenant_id: str) -> None:
    """Set the ``app.encryption_key`` GUC via local (dev/test) DEK derivation.

    Deliberately bypasses ``kms_keys.set_session_encryption_key`` /
    ``KMSEngine.get_or_create_dek``: this repo's dev ``.env`` currently sets
    ``KMS_CMK_ARN=<blank>   # AWS KMS Customer Master Key ARN`` on one line,
    and pydantic-settings does not strip the inline ``#`` comment, so
    ``settings.kms_cmk_arn`` ends up truthy (the comment text) even though
    no real KMS is configured — routing ``get_or_create_dek`` into the
    ``boto3``/AWS-KMS branch, which fails with ``NoCredentialsError`` in any
    local dev environment. That's a pre-existing ``.env`` parsing issue,
    outside this task's 3-file scope (``seed_demo.py`` /
    ``tests/conftest.py`` / ``Makefile``).

    ``KMSEngine._derive_dek_local`` is the exact deterministic HKDF-SHA256
    derivation ``get_or_create_dek`` itself would use once
    ``settings.kms_cmk_arn`` is falsy — calling it directly produces the
    same DEK an unaffected dev/test environment would get, so seeded PHI
    stays round-trippable with ``decrypt_phi`` once the ``.env`` issue is
    fixed.
    """
    from sqlalchemy import text

    from intensicare.services.kms_keys import KMSEngine

    dek = KMSEngine._derive_dek_local(tenant_id)
    await db.execute(
        text("SELECT set_config('app.encryption_key', :key, false)"),
        {"key": dek.plaintext.hex()},
    )


class _DemoMPIClient:
    """Minimal stand-in for :class:`MPIClient` — no HTTP calls.

    Only used transiently while upserting the synthetic demo patients via
    the real ``mpi_resolver.sync_patient_cache`` path.
    """

    def __init__(self, patients: dict[str, Any]) -> None:
        self._patients = patients

    @property
    def is_configured(self) -> bool:
        return True

    async def get_patient(self, mpi_id: str) -> Any | None:
        return self._patients.get(mpi_id)


async def _patient_cache_schema_supports_encrypted_phi(db: AsyncSession) -> bool:
    """True if ``patient_cache.display_name`` is BYTEA (post-migration-0004 schema).

    See the module docstring's "``patient_cache`` schema drift fallback"
    section for why this check exists.
    """
    result = await db.execute(
        text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_name = 'patient_cache' AND column_name = 'display_name'"
        )
    )
    return result.scalar_one_or_none() == "bytea"


async def _upsert_patient_legacy_schema(db: AsyncSession, mpi_patient: Any) -> None:
    """Upsert one demo patient against the legacy (pre-migration-0004) schema.

    ``display_name``/``mrn`` are stored as the plaintext the live column
    actually supports; ``mrn_bidx`` still goes through the real blind-index
    helper (``patient_encryption.compute_mrn_bidx``) since ``mrn_bidx`` is
    already ``BYTEA`` in both schema states. ``birth_date``/``cpf``/``cns``
    are left NULL (none of the demo profiles populate them).
    """
    from intensicare.services.patient_encryption import compute_mrn_bidx

    # compute_mrn_bidx (hmac via pgcrypto) also requires app.encryption_key.
    await _set_demo_encryption_key(db, mpi_patient.tenant_id or DEMO_TENANT_ID)
    mrn_bidx = await compute_mrn_bidx(db, mpi_patient.mrn) if mpi_patient.mrn else None
    admission_dt = _parse_iso(mpi_patient.admission_dt)
    is_active = mpi_patient.discharge_dt is None
    synced_at = datetime.now(timezone.utc)

    await db.execute(
        text(
            """
            INSERT INTO patient_cache (
                mpi_id, tenant_id, display_name, mrn, birth_date,
                cpf, cns, mrn_bidx, gender, admission_dt, bed_id, unit,
                synced_at, is_active
            ) VALUES (
                :mpi_id, :tenant_id, :display_name, :mrn, NULL,
                NULL, NULL, :mrn_bidx, :gender, :admission_dt, :bed_id, :unit,
                :synced_at, :is_active
            )
            ON CONFLICT (mpi_id) DO UPDATE SET
                tenant_id = EXCLUDED.tenant_id,
                display_name = EXCLUDED.display_name,
                mrn = EXCLUDED.mrn,
                mrn_bidx = EXCLUDED.mrn_bidx,
                gender = EXCLUDED.gender,
                admission_dt = EXCLUDED.admission_dt,
                bed_id = EXCLUDED.bed_id,
                unit = EXCLUDED.unit,
                synced_at = EXCLUDED.synced_at,
                is_active = EXCLUDED.is_active
            """
        ),
        {
            "mpi_id": mpi_patient.mpi_id,
            "tenant_id": mpi_patient.tenant_id,
            "display_name": mpi_patient.display_name,
            "mrn": mpi_patient.mrn,
            "mrn_bidx": mrn_bidx,
            "gender": mpi_patient.gender,
            "admission_dt": admission_dt,
            "bed_id": mpi_patient.bed_id,
            "unit": mpi_patient.unit,
            "synced_at": synced_at,
            "is_active": is_active,
        },
    )


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


async def _upsert_demo_patients(db: AsyncSession, now: datetime) -> list[str]:
    """Upsert the 5 synthetic demo patients.

    Primary path: ``mpi_resolver.sync_patient_cache`` (real PHI-encryption
    upsert), with the module-level MPI client singleton temporarily swapped
    for a fake one so it runs unmodified against synthetic data instead of a
    real external MPI. Falls back to a schema-compatible plaintext upsert
    when this database's ``patient_cache`` predates migration 0004 — see the
    module docstring.
    """
    patients = await _build_demo_mpi_patients(now)

    if not await _patient_cache_schema_supports_encrypted_phi(db):
        logger.warning(
            "patient_cache.display_name is not BYTEA on this database "
            "(legacy/unmigrated schema) — falling back to a schema-compatible "
            "plaintext upsert for the MPI-DEMO-* namespace. See seed_demo.py "
            "module docstring for details."
        )
        upserted: list[str] = []
        for mpi_id, mpi_patient in patients.items():
            await _upsert_patient_legacy_schema(db, mpi_patient)
            upserted.append(mpi_id)
        await db.flush()
        return upserted

    import intensicare.clients.mpi_client as mpi_client_module
    from intensicare.services.mpi_resolver import sync_patient_cache

    # PHI encryption (encrypt_phi/compute_mrn_bidx) requires the Postgres
    # GUC app.encryption_key to already be set on this session.
    await _set_demo_encryption_key(db, DEMO_TENANT_ID)

    original_client = mpi_client_module._mpi_client
    mpi_client_module._mpi_client = _DemoMPIClient(patients)
    try:
        upserted = []
        for mpi_id in patients:
            cached = await sync_patient_cache(db, mpi_id)
            if cached is not None:
                upserted.append(mpi_id)
            else:
                logger.warning("Demo patient upsert returned None for %s", mpi_id)
        return upserted
    finally:
        mpi_client_module._mpi_client = original_client


# ── Etapa B — wipe + vitals ──────────────────────────────────────────────


async def _wipe_demo_namespace(db: AsyncSession) -> None:
    """Delete vitals/scores/alerts/pathway enrollments for the DEMO namespace.

    Never touches ``mpi_id`` outside the ``MPI-DEMO-%`` prefix, and never
    deletes ``patient_cache`` rows here (only ``--wipe`` does that).
    """
    from intensicare.models.alert import Alert
    from intensicare.models.clinical_score import ClinicalScore
    from intensicare.models.pathway import PatientPathway, PathwayStateTransition
    from intensicare.models.vital_sign import VitalSign

    like_pattern = f"{DEMO_MPI_PREFIX}%"

    pp_ids_subq = select(PatientPathway.id).where(PatientPathway.mpi_id.like(like_pattern))
    await db.execute(
        delete(PathwayStateTransition).where(
            PathwayStateTransition.patient_pathway_id.in_(pp_ids_subq)
        )
    )
    await db.execute(delete(PatientPathway).where(PatientPathway.mpi_id.like(like_pattern)))
    await db.execute(delete(Alert).where(Alert.mpi_id.like(like_pattern)))
    await db.execute(delete(ClinicalScore).where(ClinicalScore.mpi_id.like(like_pattern)))
    await db.execute(delete(VitalSign).where(VitalSign.mpi_id.like(like_pattern)))
    await db.flush()


def _generate_vitals_points(
    num: str, profile: dict[str, Any], now: datetime, n: int = VITALS_POINTS_PER_PATIENT
) -> list[Any]:
    """Build ``n`` VitalSignCreate points spread from now-6h to now-5min."""
    from intensicare.schemas.vitals import VitalSignCreate

    mpi_id = f"{DEMO_MPI_PREFIX}{num}"
    start = now - timedelta(hours=6)
    end = now - timedelta(minutes=5)

    points: list[Any] = []
    for i in range(n):
        fraction = i / (n - 1) if n > 1 else 1.0
        recorded_at = start + (end - start) * fraction

        avpu_final = profile["avpu_final"]
        avpu = avpu_final if (fraction >= 0.7 and avpu_final != "A") else "A"

        points.append(
            VitalSignCreate(
                mpi_id=mpi_id,
                recorded_at=recorded_at,
                heart_rate=round(_lerp(*profile["heart_rate"], fraction)),
                systolic_bp=round(_lerp(*profile["systolic_bp"], fraction)),
                diastolic_bp=round(_lerp(*profile["diastolic_bp"], fraction)),
                respiratory_rate=round(_lerp(*profile["respiratory_rate"], fraction)),
                temperature=round(_lerp(*profile["temperature"], fraction), 1),
                spo2=round(_lerp(*profile["spo2"], fraction)),
                avpu=avpu,
                map_value=round(_lerp(*profile["map_value"], fraction), 1),
                source_system="seed_demo",
            )
        )
    return points


async def _ingest_all_demo_vitals(db: AsyncSession, now: datetime) -> tuple[int, int]:
    """Ingest the vitals timeline for every demo patient via the real ingest path."""
    from intensicare.services.vitals import ingest_vitals

    total_vitals = 0
    total_alerts = 0
    for num, profile in _VITALS_PROFILES.items():
        for point in _generate_vitals_points(num, profile, now):
            _response, alerts, is_replay = await ingest_vitals(db, point)
            if not is_replay:
                total_vitals += 1
            total_alerts += len(alerts)
    return total_vitals, total_alerts


# ── Etapa C — pathway enrollments ────────────────────────────────────────


async def _ensure_pathways_synced(db: AsyncSession, engine: Any) -> tuple[bool, str]:
    """Ensure the ``pathways``/``pathway_criteria`` tables are populated.

    Runs the boot-time YAML->DB sync inline if the table is empty. Tolerates
    the sync module not being importable/runnable yet (per spec) by
    returning ``(False, reason)`` instead of raising.
    """
    from intensicare.models.pathway import Pathway

    count = (await db.execute(select(func.count()).select_from(Pathway))).scalar_one()
    if count > 0:
        return True, f"pathways table already populated ({count} rows)"

    try:
        from intensicare.services.pathway_definitions_sync import sync_pathway_definitions
    except ImportError as exc:
        return False, f"pathway_definitions_sync not importable yet: {exc}"

    try:
        report = await sync_pathway_definitions(db, engine)
        await db.flush()
    except Exception as exc:  # noqa: BLE001 - must not abort the whole seed
        logger.exception("Inline pathway definitions sync failed")
        return False, f"pathway_definitions_sync raised: {exc}"

    return True, f"synced inline (synced={report.synced}, failed={report.failed})"


def _evaluate_pathway_input(
    engine: Any, pathway_id: int, criterion_id: str, input_name: str, value: float
) -> dict[str, Any]:
    """Evaluate ``value`` against ``criterion_id``'s YAML graded band.

    Reuses ``trilhas_compiler.PredicateCompiler`` (the same compiler the
    runtime engine uses) to classify the value into a severity band, then
    derives the *pathway-enrollment* notion of "met" (goal achieved) as
    ``severity == "normal"`` — the inverse of
    ``EvaluationResult.met`` (which means "alert-worthy").
    """
    from intensicare.services.trilhas_compiler import PredicateCompiler

    pdef = engine.get_pathway(pathway_id)
    if pdef is None:
        raise ValueError(f"TrilhasEngine has no pathway id={pathway_id}")

    crit = next((c for c in pdef.criteria if c.get("id") == criterion_id), None)
    if crit is None:
        raise ValueError(f"Pathway {pathway_id} has no criterion {criterion_id!r}")

    predicate = crit.get("predicate")
    if not predicate:
        raise ValueError(f"Criterion {criterion_id!r} has no predicate")

    compiler = PredicateCompiler()
    compiled = compiler.compile(predicate)
    result = compiler.evaluate(compiled, {input_name: value})

    met = result.severity == "normal"
    return {"id": criterion_id, "met": met, "value": value}


async def _enroll_and_evaluate(
    db: AsyncSession,
    engine: Any,
    *,
    mpi_id: str,
    pathway_id: int,
    bed_id: str,
    inputs: dict[str, tuple[str, float]],
) -> dict[str, Any]:
    from intensicare.services.pathway_enrollment import enroll_patient, evaluate_criteria

    result = await enroll_patient(
        db,
        mpi_id=mpi_id,
        pathway_id=pathway_id,
        encounter_id=f"ENC-{mpi_id}",
        bed_id=bed_id,
        unit=DEMO_UNIT,
        enrolled_by="seed_demo",
    )
    if result.error:
        return {"mpi_id": mpi_id, "pathway_id": pathway_id, "error": result.error}

    criteria_updates = [
        _evaluate_pathway_input(engine, pathway_id, criterion_id, input_name, value)
        for criterion_id, (input_name, value) in inputs.items()
    ]
    eval_result = await evaluate_criteria(
        db,
        mpi_id=mpi_id,
        patient_pathway_id=result.patient_pathway_id,
        criteria_updates=criteria_updates,
    )
    return {
        "mpi_id": mpi_id,
        "pathway_id": pathway_id,
        "patient_pathway_id": result.patient_pathway_id,
        "severity": eval_result.severity,
        "criteria": criteria_updates,
    }


async def _enroll_demo_patients(db: AsyncSession, engine: Any) -> list[dict[str, Any]]:
    """Etapa C enrollments, exactly as specified in the approved design.

    - DEMO-001 -> sepse: pam=58 (critical band), lactato=3.2 (watch band)
    - DEMO-002 -> sedação: rass_score=+3 (urgent band)
    - DEMO-005 -> sepse: lactato=4.2, pam=58 (both critical), fluid_volume=15 (critical)
    - DEMO-003 / DEMO-004: no enrollment (isolated-fever / negative-control cases)
    """
    enrollments = [
        await _enroll_and_evaluate(
            db,
            engine,
            mpi_id=f"{DEMO_MPI_PREFIX}001",
            pathway_id=SEPSE_PATHWAY_ID,
            bed_id="DEMO-01",
            inputs={
                "crit-sep-pam": ("pam", 58),
                "crit-sep-lactato": ("lactato", 3.2),
            },
        ),
        await _enroll_and_evaluate(
            db,
            engine,
            mpi_id=f"{DEMO_MPI_PREFIX}002",
            pathway_id=SEDACAO_PATHWAY_ID,
            bed_id="DEMO-02",
            inputs={
                "crit-sed-rass": ("rass_score", 3),
            },
        ),
        await _enroll_and_evaluate(
            db,
            engine,
            mpi_id=f"{DEMO_MPI_PREFIX}005",
            pathway_id=SEPSE_PATHWAY_ID,
            bed_id="DEMO-05",
            inputs={
                "crit-sep-lactato": ("lactato", 4.2),
                "crit-sep-pam": ("pam", 58),
                "crit-sep-fluid": ("fluid_volume", 15),
            },
        ),
    ]
    return enrollments


# ── Public entry point ────────────────────────────────────────────────────


async def seed(db: AsyncSession, *, profile: str = "default", now: datetime | None = None) -> SeedReport:
    """Seed the synthetic demo namespace (5 patients, vitals, pathway enrollments).

    Never commits — the caller owns the transaction (CLI commits explicitly;
    the pytest fixture relies on the test's SAVEPOINT/rollback).

    Args:
        db: Active async session.
        profile: Reserved for future variation of the demo dataset; only
            ``"default"`` is implemented today.
        now: Reference "now" for the vitals timeline (defaults to
            ``datetime.now(timezone.utc)``). Passing a fixed value makes
            output reproducible for tests.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    report = SeedReport(profile=profile)

    # Etapa A — patients (idempotent upsert by mpi_id).
    report.patients = await _upsert_demo_patients(db, now)

    # Etapa B — wipe + re-ingest the clinical trail for the DEMO namespace.
    await _wipe_demo_namespace(db)
    report.vitals_ingested, report.alerts_created = await _ingest_all_demo_vitals(db, now)

    # Etapa C — pathway enrollments (requires pathways/pathway_criteria populated).
    from intensicare.services.trilhas_engine import TrilhasEngine

    try:
        engine = TrilhasEngine()
    except Exception as exc:  # noqa: BLE001 - engine load failure must not sink A/B
        logger.exception("TrilhasEngine failed to load — skipping enrollments")
        report.pathways_synced = False
        report.pathway_sync_message = f"TrilhasEngine() raised: {exc}"
        report.enrollment_skipped_reason = report.pathway_sync_message
        return report

    synced_ok, sync_msg = await _ensure_pathways_synced(db, engine)
    report.pathways_synced = synced_ok
    report.pathway_sync_message = sync_msg

    if synced_ok:
        report.enrollments = await _enroll_demo_patients(db, engine)
    else:
        report.enrollment_skipped_reason = sync_msg

    return report


# ── CLI ────────────────────────────────────────────────────────────────────


async def _wipe_only(db: AsyncSession) -> None:
    """``--wipe``: remove the clinical trail AND the demo patients themselves."""
    from intensicare.models.patient_cache import PatientCache

    await _wipe_demo_namespace(db)
    await db.execute(delete(PatientCache).where(PatientCache.mpi_id.like(f"{DEMO_MPI_PREFIX}%")))
    await db.flush()


async def _run_cli(database_url: str | None, wipe: bool, profile: str) -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from intensicare.config import settings

    url = database_url or settings.database_url
    engine = create_async_engine(url, echo=False)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with session_factory() as db:
            if wipe:
                await _wipe_only(db)
                await db.commit()
                logger.info("Wiped MPI-DEMO-* namespace (patients + clinical data).")
                return

            report = await seed(db, profile=profile)
            await db.commit()
            print(report.as_text())
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Seed synthetic demo patients (MPI-DEMO-001..005) with vitals and "
            "pathway enrollments for local dev/demo use."
        )
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override the target database URL (defaults to settings.database_url).",
    )
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Only remove the MPI-DEMO-* namespace (patients + clinical trail) and exit.",
    )
    parser.add_argument(
        "--profile",
        default="default",
        help="Demo dataset profile (reserved for future use; only 'default' exists today).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    asyncio.run(_run_cli(args.database_url, args.wipe, args.profile))


if __name__ == "__main__":
    main()
