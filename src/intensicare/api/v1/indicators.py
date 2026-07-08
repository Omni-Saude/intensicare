"""Indicators API Router — 31 clinical quality indicators (ETL legacy rules).

3 endpoints:
  GET  /indicators          — List catalogue (paginated, filterable by category)
  GET  /indicators/{id}     — Indicator detail with computed value & history
  GET  /indicators/summary  — Aggregated dashboard summary

All endpoints require authentication (Depends(get_current_user)).
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from intensicare.auth.dependencies import get_current_user
from intensicare.models.user import User

router = APIRouter(prefix="/api/v1", tags=["indicators"])


# ============================================================================
# Indicator catalogue — 31 indicators across 10 clinical categories
# ============================================================================

INDICATORS: list[dict] = [
    # ── TLP (Lesão por Pressão) — 3 indicators ──
    {
        "id": "ind-tlp-001",
        "name": "Taxa de Lesão por Pressão",
        "category": "TLP",
        "description": (
            "Percentual de pacientes que desenvolveram lesão por pressão "
            "durante a internação na UTI."
        ),
        "unit": "%",
        "target": "< 5%",
        "reference_range": {"low": 0, "high": 5},
    },
    {
        "id": "ind-tlp-002",
        "name": "Incidência de Úlcera por Pressão",
        "category": "TLP",
        "description": (
            "Número de novos casos de úlcera por pressão "
            "por 1000 pacientes-dia."
        ),
        "unit": "/1000 pac-dia",
        "target": "< 10",
        "reference_range": {"low": 0, "high": 10},
    },
    {
        "id": "ind-tlp-003",
        "name": "Prevalência de Lesão por Pressão",
        "category": "TLP",
        "description": (
            "Percentual de pacientes com lesão por pressão "
            "no momento da avaliação."
        ),
        "unit": "%",
        "target": "< 3%",
        "reference_range": {"low": 0, "high": 3},
    },

    # ── Ocupação — 3 indicators ──
    {
        "id": "ind-ocup-001",
        "name": "Taxa de Ocupação",
        "category": "Ocupação",
        "description": "Percentual de leitos operacionais ocupados no período.",
        "unit": "%",
        "target": "< 85%",
        "reference_range": {"low": 75, "high": 85},
    },
    {
        "id": "ind-ocup-002",
        "name": "Tempo Médio de Permanência",
        "category": "Ocupação",
        "description": "Média de dias de internação dos pacientes na UTI.",
        "unit": "dias",
        "target": "< 7 dias",
        "reference_range": {"low": 3, "high": 7},
    },
    {
        "id": "ind-ocup-003",
        "name": "Taxa de Rotatividade de Leitos",
        "category": "Ocupação",
        "description": "Número de admissões por leito no período.",
        "unit": "adm/leito",
        "target": "> 4",
        "reference_range": {"low": 4, "high": 8},
    },

    # ── Sedação — 3 indicators ──
    {
        "id": "ind-sed-001",
        "name": "Taxa de Sedação Adequada (RASS)",
        "category": "Sedação",
        "description": (
            "Percentual de avaliações RASS dentro da faixa-alvo prescrita."
        ),
        "unit": "%",
        "target": "> 80%",
        "reference_range": {"low": 80, "high": 100},
    },
    {
        "id": "ind-sed-002",
        "name": "Tempo de Despertar Diário",
        "category": "Sedação",
        "description": (
            "Percentual de dias com interrupção diária da sedação realizada."
        ),
        "unit": "%",
        "target": "> 90%",
        "reference_range": {"low": 90, "high": 100},
    },
    {
        "id": "ind-sed-003",
        "name": "Incidência de Delirium",
        "category": "Sedação",
        "description": (
            "Percentual de pacientes com diagnóstico de delirium "
            "durante a internação."
        ),
        "unit": "%",
        "target": "< 20%",
        "reference_range": {"low": 0, "high": 20},
    },

    # ── Ventilação — 4 indicators ──
    {
        "id": "ind-vent-001",
        "name": "Taxa de Pneumonia Associada à VM (PAV)",
        "category": "Ventilação",
        "description": (
            "Densidade de incidência de PAV por 1000 dias "
            "de ventilação mecânica."
        ),
        "unit": "/1000 VM-dia",
        "target": "< 5",
        "reference_range": {"low": 0, "high": 5},
    },
    {
        "id": "ind-vent-002",
        "name": "Duração Média de Ventilação Mecânica",
        "category": "Ventilação",
        "description": (
            "Média de dias em ventilação mecânica invasiva por paciente."
        ),
        "unit": "dias",
        "target": "< 7 dias",
        "reference_range": {"low": 3, "high": 7},
    },
    {
        "id": "ind-vent-003",
        "name": "Taxa de Sucesso de Extubação",
        "category": "Ventilação",
        "description": (
            "Percentual de extubações bem-sucedidas sem necessidade "
            "de reintubação em 48h."
        ),
        "unit": "%",
        "target": "> 85%",
        "reference_range": {"low": 85, "high": 100},
    },
    {
        "id": "ind-vent-004",
        "name": "Taxa de Reintubação em 48h",
        "category": "Ventilação",
        "description": (
            "Percentual de pacientes reintubados "
            "em até 48 horas após extubação."
        ),
        "unit": "%",
        "target": "< 10%",
        "reference_range": {"low": 0, "high": 10},
    },

    # ── Hemodinâmica — 3 indicators ──
    {
        "id": "ind-hemo-001",
        "name": "Tempo de PAM < 65 mmHg",
        "category": "Hemodinâmica",
        "description": (
            "Percentual do tempo de internação com pressão arterial média "
            "abaixo de 65 mmHg."
        ),
        "unit": "%",
        "target": "< 10%",
        "reference_range": {"low": 0, "high": 10},
    },
    {
        "id": "ind-hemo-002",
        "name": "Uso de Vasopressores",
        "category": "Hemodinâmica",
        "description": (
            "Percentual de pacientes em uso de drogas vasoativas "
            "por mais de 24 horas."
        ),
        "unit": "%",
        "target": "< 30%",
        "reference_range": {"low": 0, "high": 30},
    },
    {
        "id": "ind-hemo-003",
        "name": "Taxa de Choque Séptico",
        "category": "Hemodinâmica",
        "description": "Incidência de choque séptico entre pacientes admitidos na UTI.",
        "unit": "%",
        "target": "< 15%",
        "reference_range": {"low": 0, "high": 15},
    },

    # ── Nutrição — 3 indicators ──
    {
        "id": "ind-nutr-001",
        "name": "Taxa de Nutrição Enteral Precoce",
        "category": "Nutrição",
        "description": (
            "Percentual de pacientes com início de nutrição enteral "
            "em até 48h da admissão."
        ),
        "unit": "%",
        "target": "> 70%",
        "reference_range": {"low": 70, "high": 100},
    },
    {
        "id": "ind-nutr-002",
        "name": "Adequação Calórica",
        "category": "Nutrição",
        "description": (
            "Percentual da meta calórica prescrita efetivamente administrada."
        ),
        "unit": "%",
        "target": "> 80%",
        "reference_range": {"low": 80, "high": 100},
    },
    {
        "id": "ind-nutr-003",
        "name": "Tempo para Início de Nutrição Enteral",
        "category": "Nutrição",
        "description": (
            "Tempo médio em horas entre a admissão e o início "
            "da nutrição enteral."
        ),
        "unit": "horas",
        "target": "< 48h",
        "reference_range": {"low": 0, "high": 48},
    },

    # ── Infecção — 3 indicators ──
    {
        "id": "ind-infec-001",
        "name": "Taxa de IPCS (Cateter Central)",
        "category": "Infecção",
        "description": (
            "Densidade de incidência de infecção primária de corrente "
            "sanguínea por 1000 cateteres-dia."
        ),
        "unit": "/1000 CVC-dia",
        "target": "< 2.5",
        "reference_range": {"low": 0, "high": 2.5},
    },
    {
        "id": "ind-infec-002",
        "name": "Taxa de ITU Associada a Cateter Vesical",
        "category": "Infecção",
        "description": (
            "Densidade de incidência de infecção do trato urinário "
            "por 1000 cateteres vesicais-dia."
        ),
        "unit": "/1000 CVD-dia",
        "target": "< 3",
        "reference_range": {"low": 0, "high": 3},
    },
    {
        "id": "ind-infec-003",
        "name": "Densidade de Uso de Antimicrobianos (DOT)",
        "category": "Infecção",
        "description": (
            "Dias de terapia antimicrobiana por 1000 pacientes-dia."
        ),
        "unit": "DOT/1000 pac-dia",
        "target": "< 800",
        "reference_range": {"low": 0, "high": 800},
    },

    # ── Segurança — 3 indicators ──
    {
        "id": "ind-safe-001",
        "name": "Taxa de Eventos Adversos",
        "category": "Segurança",
        "description": (
            "Número de eventos adversos notificados por 1000 pacientes-dia."
        ),
        "unit": "/1000 pac-dia",
        "target": "< 5",
        "reference_range": {"low": 0, "high": 5},
    },
    {
        "id": "ind-safe-002",
        "name": "Taxa de Quedas",
        "category": "Segurança",
        "description": (
            "Número de quedas de pacientes por 1000 pacientes-dia."
        ),
        "unit": "/1000 pac-dia",
        "target": "< 2",
        "reference_range": {"low": 0, "high": 2},
    },
    {
        "id": "ind-safe-003",
        "name": "Taxa de Erros de Medicação",
        "category": "Segurança",
        "description": (
            "Número de erros de medicação notificados por 1000 pacientes-dia."
        ),
        "unit": "/1000 pac-dia",
        "target": "< 3",
        "reference_range": {"low": 0, "high": 3},
    },

    # ── Mobilidade — 3 indicators ──
    {
        "id": "ind-mob-001",
        "name": "Taxa de Mobilização Precoce",
        "category": "Mobilidade",
        "description": (
            "Percentual de pacientes mobilizados fora do leito "
            "em até 72h da admissão."
        ),
        "unit": "%",
        "target": "> 60%",
        "reference_range": {"low": 60, "high": 100},
    },
    {
        "id": "ind-mob-002",
        "name": "Dias até Primeira Deambulação",
        "category": "Mobilidade",
        "description": (
            "Média de dias entre a admissão e a primeira "
            "deambulação assistida."
        ),
        "unit": "dias",
        "target": "< 5 dias",
        "reference_range": {"low": 0, "high": 5},
    },
    {
        "id": "ind-mob-003",
        "name": "Taxa de Pacientes Mobilizados",
        "category": "Mobilidade",
        "description": (
            "Percentual de pacientes elegíveis que receberam mobilização "
            "durante a internação."
        ),
        "unit": "%",
        "target": "> 75%",
        "reference_range": {"low": 75, "high": 100},
    },

    # ── Outros — 3 indicators ──
    {
        "id": "ind-other-001",
        "name": "Taxa de Mortalidade Padronizada (SMR)",
        "category": "Outros",
        "description": (
            "Razão entre mortalidade observada e mortalidade esperada (SAPS 3)."
        ),
        "unit": "razão",
        "target": "< 1.0",
        "reference_range": {"low": 0, "high": 1.0},
    },
    {
        "id": "ind-other-002",
        "name": "Taxa de Readmissão em 48h",
        "category": "Outros",
        "description": (
            "Percentual de pacientes readmitidos na UTI "
            "em até 48 horas após a alta."
        ),
        "unit": "%",
        "target": "< 2%",
        "reference_range": {"low": 0, "high": 2},
    },
    {
        "id": "ind-other-003",
        "name": "Índice de Satisfação Familiar (FS-ICU 24)",
        "category": "Outros",
        "description": (
            "Pontuação média de satisfação familiar na escala FS-ICU 24."
        ),
        "unit": "score",
        "target": "> 80",
        "reference_range": {"low": 80, "high": 100},
    },
]

# Build lookup index for O(1) detail access
_INDICATORS_BY_ID: dict[str, dict] = {i["id"]: i for i in INDICATORS}

# Ordered category list (contract order)
CATEGORY_ORDER = [
    "TLP",
    "Ocupação",
    "Sedação",
    "Ventilação",
    "Hemodinâmica",
    "Nutrição",
    "Infecção",
    "Segurança",
    "Mobilidade",
    "Outros",
]


# ============================================================================
# Helpers
# ============================================================================


def _random_float(lo: float, hi: float) -> float:
    """Deterministic pseudorandom float seeded by indicator id."""
    return round(lo + random.random() * (hi - lo), 2)


def _mock_trend() -> str:
    """Return a random trend value."""
    return random.choice(["improving", "stable", "declining", "unknown"])


def _mock_history(
    ref_range: dict, *, points: int = 30
) -> list[dict]:
    """Generate 30 mock historical data points within the reference range."""
    now = datetime.now(timezone.utc)
    lo, hi = ref_range["low"], ref_range["high"]
    history = []
    for i in range(points):
        ts = now - timedelta(hours=(points - 1 - i) * 4)
        # Occasionally spike outside the reference range for realism
        if random.random() < 0.1:
            val = round(lo - random.random() * hi * 0.5, 2)
        elif random.random() < 0.1:
            val = round(hi + random.random() * hi * 0.5, 2)
        else:
            val = round(random.uniform(lo, hi), 2)
        history.append({"timestamp": ts.isoformat(), "value": val})
    return history


def _build_indicator_item(ind: dict) -> dict:
    """Build a list-level indicator item (without history)."""
    ref = ind.get("reference_range", {"low": 0, "high": 100})
    current_value = _random_float(ref["low"], ref["high"])
    return {
        "id": ind["id"],
        "name": ind["name"],
        "category": ind["category"],
        "description": ind["description"],
        "current_value": current_value,
        "target": ind["target"],
        "unit": ind["unit"],
        "trend": _mock_trend(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def _build_detail(ind: dict) -> dict:
    """Build a full detail response including history."""
    base = _build_indicator_item(ind)
    base["reference_range"] = ind.get(
        "reference_range", {"low": 0, "high": 100}
    )
    # Seed with the indicator's own ID hash so history is deterministic-ish
    random.seed(hash(ind["id"]) % (2**31))
    base["history"] = _mock_history(base["reference_range"])
    random.seed()  # reset seed
    return base


# ============================================================================
# GET /indicators — List catalogue (paginated, filterable by category)
# ============================================================================


@router.get("/indicators")
async def list_indicators(
    category: str | None = Query(
        None,
        description="Filter indicators by category (e.g. TLP, Ocupação, Sedação)",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return the full catalogue of 31 clinical quality indicators.

    Supports optional filtering by category and pagination via page / page_size.
    Response shape: {data: [...], pagination: {...}}.
    """
    # Filter
    if category:
        filtered = [
            ind for ind in INDICATORS if ind["category"].lower() == category.lower()
        ]
        if not filtered:
            # Unknown category → return empty list (not 400)
            return {
                "data": [],
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_items": 0,
                    "total_pages": 0,
                },
            }
    else:
        filtered = list(INDICATORS)

    total_items = len(filtered)
    total_pages = max(1, math.ceil(total_items / page_size))

    # Clamp page
    if page > total_pages:
        page = total_pages

    start = (page - 1) * page_size
    end = start + page_size
    page_items = filtered[start:end]

    # Build response items with mock computed values
    data = [_build_indicator_item(ind) for ind in page_items]

    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    }


# ============================================================================
# GET /indicators/summary — Aggregated dashboard
# ============================================================================


@router.get("/indicators/summary")
async def get_indicators_summary(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return an aggregated dashboard summary of all 31 indicators.

    Includes:
      - category_counts: number of indicators per category
      - total_indicators: overall count
      - categories: ordered list of category names
      - alerts: count of indicators currently outside target range (mock)
      - last_updated: timestamp of this summary generation
    """
    total = len(INDICATORS)

    # Count per category preserving contract order
    category_counts: dict[str, int] = {}
    for ind in INDICATORS:
        cat = ind["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Build ordered category breakdown
    categories_summary = []
    for cat_name in CATEGORY_ORDER:
        if cat_name in category_counts:
            categories_summary.append({
                "category": cat_name,
                "count": category_counts[cat_name],
            })

    # Mock alert count: indicators with "declining" trend
    alerts = sum(
        1 for ind in INDICATORS
        if _mock_trend() == "declining"
    )

    return {
        "total_indicators": total,
        "categories": categories_summary,
        "category_count": len(categories_summary),
        "alerts_out_of_range": alerts,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# GET /indicators/{id} — Indicator detail
# ============================================================================


@router.get("/indicators/{indicator_id}")
async def get_indicator(
    indicator_id: str,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Return a single indicator with current value, target, trend, and history.

    Includes 30 historical data points for trend visualization.
    Returns 404 if the indicator ID is not found in the catalogue.
    """
    ind = _INDICATORS_BY_ID.get(indicator_id)
    if ind is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator not found: {indicator_id}",
        )

    return _build_detail(ind)
