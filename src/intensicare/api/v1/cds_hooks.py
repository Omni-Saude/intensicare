"""CDS Hooks 2.0 (HL7) — discovery + patient-view service.

Interoperability adapter (audit Dim E, dedução -4: "DSL não interoperável;
zero Arden/CQL/CDS Hooks"). The clinical decision logic stays as the
IntensiCare DSL (Trilhas Engine, YAML pathways — ADR-0020/ADR-0021,
deliberately kept as-is), but its *output* can and should speak a standard
so third-party EHRs can surface IntensiCare recommendations without
understanding the DSL. CDS Hooks 2.0 (https://cds-hooks.hl7.org) is that
standard: a discovery endpoint plus per-hook services that respond with
JSON "cards".

This router intentionally contains NO clinical/business logic of its own —
it is a thin translation layer over the existing pathway services
(``pathway_enrollment.get_patient_pathways`` / ``get_pathway_progress`` and
``pathway_repository.PathwayRepository``), reusing the same recommendation
text, criteria evaluation and severity model already used by the internal
``/api/v1/patients/{mpi_id}/pathways*`` endpoints.

Auth decisions
--------------
* ``GET /cds-services`` (discovery) is deliberately left **public** (no
  ``Depends(get_current_user)``). Per the CDS Hooks 2.0 spec, a CDS Client
  discovers available services *before* it has established any patient or
  auth context, and the discovery response carries only service metadata
  (hook name, title, description, id) — no PHI. This mirrors the existing
  public routes in this codebase (``GET /api/v1/health``,
  ``POST /api/v1/auth/login``), which are public by simply omitting the
  auth dependency — there is no separate "public route" decorator here.
* ``POST /cds-services/intensicare-pathway-alerts`` (the actual service
  call) carries a ``patientId`` in its body and DOES require
  authentication (``Depends(get_current_user)``), same as every other
  data-bearing route in this codebase. This is a deliberate deviation from
  the base CDS Hooks spec, which defers authorization to the CDS Client's
  own trust framework (typically SMART Backend Services / mutual TLS
  between the EHR and the CDS Service) and does not mandate a bearer
  token on the service call itself. Real-world CDS Hooks deployments
  commonly add their own authorization on top of the spec baseline (the
  spec explicitly allows this), so this is a supported deviation, not a
  spec violation — but it is documented here because a third-party EHR
  integrating with this service will need a valid IntensiCare bearer
  token to call it, unlike a "pure" spec-only implementation.
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.auth.dependencies import get_current_user
from intensicare.config import settings
from intensicare.core.database import get_db
from intensicare.models.pathway import Pathway
from intensicare.models.user import User
from intensicare.schemas.severity import SeverityLevel
from intensicare.services.domain_trilhas_engine import PathwayProgressResult
from intensicare.services.pathway_enrollment import (
    get_pathway_progress,
    get_patient_pathways,
)
from intensicare.services.pathway_repository import PathwayRepository

router = APIRouter(tags=["cds-hooks"])

SERVICE_ID = "intensicare-pathway-alerts"
SERVICE_PATH = f"/cds-services/{SERVICE_ID}"

# CDS Hooks "indicator" is one of info | warning | critical (NOT the same
# vocabulary as IntensiCare's four-level severity model) — map our
# normal/watch/urgent/critical onto the spec's three-level indicator.
_INDICATOR_BY_SEVERITY: dict[str, str] = {
    "normal": "info",
    "watch": "info",
    "urgent": "warning",
    "critical": "critical",
}

_SUMMARY_MAX_LEN = 140


# ===========================================================================
# CDS Hooks 2.0 request/response schemas (field names follow the spec's
# camelCase JSON exactly — this is the wire format, not an internal model).
# ===========================================================================


class CDSHookContext(BaseModel):
    """``context`` object of a CDS Hooks request. Only ``patientId`` is
    required by this service; other hook-specific context fields (e.g.
    ``encounterId``, ``userId``) are accepted but unused."""

    model_config = ConfigDict(extra="allow")

    patientId: str = Field(..., min_length=1, description="MPI id of the patient in view")


class CDSHookRequest(BaseModel):
    """CDS Hooks 2.0 service-call request body."""

    model_config = ConfigDict(extra="allow")

    hook: str = Field(..., description="CDS Hooks hook name, e.g. 'patient-view'")
    hookInstance: str = Field(..., description="Unique id for this hook invocation")
    context: CDSHookContext
    fhirServer: str | None = None
    fhirAuthorization: dict[str, Any] | None = None
    prefetch: dict[str, Any] | None = None


class CDSHooksSource(BaseModel):
    label: str
    url: str | None = None


class CDSHooksLink(BaseModel):
    label: str
    url: str
    type: Literal["absolute", "smart"] = "absolute"


class CDSHooksCard(BaseModel):
    """A single CDS Hooks 2.0 card — one per active, clinically-relevant
    (severity >= watch) pathway enrollment."""

    uuid: str
    summary: str = Field(..., max_length=_SUMMARY_MAX_LEN)
    detail: str | None = None
    indicator: Literal["info", "warning", "critical"]
    source: CDSHooksSource
    links: list[CDSHooksLink] = Field(default_factory=list)


class CDSHooksCardResponse(BaseModel):
    cards: list[CDSHooksCard]


class CDSService(BaseModel):
    hook: str
    title: str
    description: str
    id: str
    prefetch: dict[str, str] | None = None


class CDSServicesDiscovery(BaseModel):
    services: list[CDSService]


# ===========================================================================
# GET /cds-services — Discovery (public, per spec)
# ===========================================================================


@router.get(
    "/cds-services",
    response_model=CDSServicesDiscovery,
    response_model_exclude_none=True,
    summary="CDS Hooks discovery endpoint",
)
async def discover_cds_services() -> CDSServicesDiscovery:
    """Advertise the CDS services this server exposes (CDS Hooks 2.0
    discovery). Public by spec — no patient/auth context exists yet at
    discovery time, and this response carries no PHI."""
    return CDSServicesDiscovery(
        services=[
            CDSService(
                hook="patient-view",
                title="IntensiCare Pathway Alerts",
                description=(
                    "Retorna um card por pathway clínico ativo (sepse, ventilação, "
                    "sedação, profilaxia, etc.) com severidade watch ou superior "
                    "para o paciente em visualização, com base na Trilhas Engine "
                    "declarativa do IntensiCare."
                ),
                id=SERVICE_ID,
            )
        ]
    )


# ===========================================================================
# Helpers — pure translation from internal pathway-service shapes to cards.
# No clinical logic lives here; it is all delegated to the existing
# pathway_enrollment service.
# ===========================================================================


async def _resolve_state_name(
    repo: PathwayRepository,
    pathway_id: int,
    state_id: str,
    cache: dict[int, Pathway | None],
) -> str:
    """Resolve a pathway state id (e.g. ``confirmacao``) to its
    human-readable name (e.g. ``Confirmação Diagnóstica``), caching the
    owning ``Pathway`` per request to avoid N duplicate lookups when a
    patient has multiple enrollments in the same pathway."""
    if pathway_id not in cache:
        cache[pathway_id] = await repo.get_pathway(pathway_id)
    pathway = cache[pathway_id]
    if pathway is not None:
        for s in pathway.states or []:
            if s.get("id") == state_id:
                return str(s.get("name") or state_id)
    return state_id.replace("_", " ").title() if state_id else "Desconhecido"


def _build_detail(pathway_name: str, progress: PathwayProgressResult) -> str:
    """Build the card's markdown ``detail`` from the criteria/recommendation
    already computed by ``get_pathway_progress`` — reused as-is, not
    recomputed here."""
    summary = progress.criteria_summary or {}
    lines = [
        f"**{pathway_name}** — {summary.get('met', 0)}/{summary.get('total', 0)} "
        "critérios atendidos.",
    ]
    unmet = [c for c in progress.criteria if c.get("met") is False]
    if unmet:
        lines.append("\n**Critérios disparados:**")
        lines.extend(f"- {c.get('name') or c.get('id')}: {c.get('value')}" for c in unmet)
    if progress.recommendation:
        lines.append(f"\n**Recomendação:** {progress.recommendation}")
    return "\n".join(lines)


def _truncate_summary(text: str) -> str:
    if len(text) <= _SUMMARY_MAX_LEN:
        return text
    return text[: _SUMMARY_MAX_LEN - 1] + "…"


async def _build_cards(db: AsyncSession, mpi_id: str) -> list[CDSHooksCard]:
    """Build one CDS Hooks card per active pathway enrollment with severity
    >= watch, reusing ``pathway_enrollment.get_patient_pathways`` and
    ``get_pathway_progress`` (same services backing the internal pathways
    API) — no duplicated business/clinical logic."""
    pathways = await get_patient_pathways(db, mpi_id, status_filter="active")
    repo = PathwayRepository(db)
    state_cache: dict[int, Pathway | None] = {}
    cards: list[CDSHooksCard] = []

    for pp in pathways:
        severity = pp.get("severity") or "normal"
        if not SeverityLevel(severity).is_at_least(SeverityLevel.WATCH):
            continue

        progress = await get_pathway_progress(db, mpi_id, pp["id"])
        state_name = await _resolve_state_name(
            repo, pp["pathway_id"], pp["current_state"], state_cache
        )

        summary = _truncate_summary(
            f"{pp['pathway_name']} — estado {state_name}, severidade {severity.upper()}"
        )
        detail = _build_detail(pp["pathway_name"], progress)
        link_url = f"{settings.frontend_base_url}/patient/{mpi_id}/pathway/{pp['id']}"

        cards.append(
            CDSHooksCard(
                uuid=str(uuid4()),
                summary=summary,
                detail=detail,
                indicator=_INDICATOR_BY_SEVERITY.get(severity, "info"),  # type: ignore[arg-type]
                source=CDSHooksSource(label="IntensiCare", url=settings.frontend_base_url),
                links=[CDSHooksLink(label="Abrir no IntensiCare", url=link_url, type="absolute")],
            )
        )

    return cards


# ===========================================================================
# POST /cds-services/intensicare-pathway-alerts — patient-view service
# ===========================================================================


@router.post(
    SERVICE_PATH,
    response_model=CDSHooksCardResponse,
    summary="IntensiCare Pathway Alerts (patient-view)",
)
async def patient_view_pathway_alerts(
    body: CDSHookRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CDSHooksCardResponse:
    """CDS Hooks 2.0 ``patient-view`` service: returns one card per active
    pathway with severity >= watch for the patient in ``context.patientId``.
    Returns ``{"cards": []}`` when the patient has no clinically-relevant
    active pathways.
    """
    cards = await _build_cards(db, body.context.patientId)
    return CDSHooksCardResponse(cards=cards)
