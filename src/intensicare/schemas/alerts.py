"""Pydantic schemas para Alerts — resposta individual e agregação por sinal (ADR-0039).

``AlertResponse``/``AlertListResponse`` movidos de ``api/v1/alerts.py`` (sem
mudança de forma) para que ``AlertGroupResponse`` possa referenciá-los sem
import circular (o router importa schemas de ``schemas/``, nunca o inverso).
"""

from __future__ import annotations

from pydantic import BaseModel


class AlertResponse(BaseModel):
    """Alert response schema — shape matches frontend AlertInfo (api.ts:91-105)."""

    id: int
    type: str = "clinical"
    severity: str
    title: str
    message: str | None
    mpi_id: str | None = None
    patient_name: str | None = None
    pathway_name: str | None = None
    created_at: str
    acknowledged_at: str | None = None
    resolved_at: str | None = None
    resolved_by: str | None = None
    resolution: str | None = None

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    """Wrapped list response — frontend expects {items, total} (AUDIT-007)."""

    items: list[AlertResponse]
    total: int


class AlertGroupResponse(BaseModel):
    """Aggregated alert group — one row per (mpi_id, score_type) signal.

    ADR-0039 §2 (contract adjudicated): aggregation happens at READ time
    only — the underlying ``alert`` rows are never merged/mutated (zero
    information-loss invariant). ``members`` carries every original alert
    belonging to the group, so nothing is hidden; only the *presentation*
    is collapsed by (patient, score_type) for the alert-fatigue view.

    ``escalating`` fura o rollup (ADR-0039 §3): it is True when the
    severity of the newest ``active``-status member is strictly higher
    (canonical ordinal normal<watch<urgent<critical) than the oldest
    ``active``-status member — i.e. the signal is still getting worse
    among the alerts nobody has acted on yet. Acknowledged/resolved/
    escalated members never suppress this signal, and are never excluded
    from ``members`` — only excluded from the escalating comparison
    itself.
    """

    mpi_id: str
    patient_name: str | None = None
    score_type: str
    max_severity: str
    count: int
    first_created_at: str
    latest_created_at: str
    escalating: bool
    members: list[AlertResponse]


class AlertGroupedListResponse(BaseModel):
    """Response shape for ``GET /alerts?group_by=signal`` (ADR-0039 §2)."""

    groups: list[AlertGroupResponse]
    total_groups: int
    total_alerts: int
