"""
Prophylaxis Bundles — domain logic for the 5 ICU prophylaxis bundles.

Bundles:
  1. LAMGD — Stress Ulcer Prophylaxis (4 criteria)
  2. TEV  — Venous Thromboembolism Prophylaxis (5 criteria)
  3. Hiperglicemia — Glycemic Control (3 criteria)
  4. Mobilização Precoce — Early Mobilization (3 criteria)
  5. Dispositivos Invasivos — Invasive Devices (5 criteria, all na by default)

Scoring: score = met_count / applicable_count * 100 (applicable = not na).
Status: complete (100%), partial (>0% <100%), pending (0%), na (all na).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Catalog: static bundle definitions (criteria labels + na defaults)
# ---------------------------------------------------------------------------

BUNDLE_CATALOG: dict[str, dict[str, Any]] = {
    "lamgd": {
        "name": "LAMGD — Úlcera de Estresse",
        "criteria": [
            {"id": "lamgd-vm", "label": "Ventilação mecânica > 48h", "na_default": False},
            {"id": "lamgd-coag", "label": "Coagulopatia (INR > 1.5 ou Plq < 50k)", "na_default": False},
            {"id": "lamgd-choque", "label": "Choque (vasopressor)", "na_default": False},
            {"id": "lamgd-cortico", "label": "Corticoterapia (hidrocortisona > 300mg/dia)", "na_default": False},
        ],
    },
    "tev": {
        "name": "TEV — Tromboembolismo Venoso",
        "criteria": [
            {"id": "tev-heparina", "label": "Heparina não fracionada ou HBPM prescrita", "na_default": False},
            {"id": "tev-deamb", "label": "Deambulação contraindicada (ajuste de dose)", "na_default": False},
            {"id": "tev-imc", "label": "Ajuste para IMC > 40 (dose aumentada)", "na_default": False},
            {"id": "tev-renal", "label": "Ajuste renal (ClCr < 30 — HNF em vez de HBPM)", "na_default": False},
            {"id": "tev-cpi", "label": "Compressão pneumática intermitente (se contraindicação)", "na_default": False},
        ],
    },
    "hiperglicemia": {
        "name": "Hiperglicemia — Controle Glicêmico",
        "criteria": [
            {"id": "hg-insulina", "label": "Protocolo de insulina NPH ou escala móvel ativo", "na_default": False},
            {"id": "hg-meta", "label": "Meta glicêmica 140-180 mg/dL", "na_default": False},
            {"id": "hg-monitor", "label": "Monitorização glicêmica a cada 4-6h", "na_default": False},
        ],
    },
    "mobilizacao": {
        "name": "Mobilização Precoce",
        "criteria": [
            {"id": "mob-avaliacao", "label": "Avaliação de mobilidade documentada nas últimas 24h", "na_default": False},
            {"id": "mob-contraindic", "label": "Sem contraindicação absoluta", "na_default": False},
            {"id": "mob-meta", "label": "Meta de saída do leito atingida", "na_default": False},
        ],
    },
    "dispositivos": {
        "name": "Dispositivos Invasivos",
        "criteria": [
            {"id": "disp-cvc-barreira", "label": "CVC: inserção com barreira máxima", "na_default": True},
            {"id": "disp-cvc-curativo", "label": "CVC: curativo transparente (troca a cada 7 dias)", "na_default": True},
            {"id": "disp-cvc-revisao", "label": "CVC: revisão diária de necessidade", "na_default": True},
            {"id": "disp-svd", "label": "SVD: sistema fechado, fixação, abaixo do nível da bexiga", "na_default": True},
            {"id": "disp-tot", "label": "TOT: pressão do cuff 20-30 cmH2O, cabeceira 30-45°", "na_default": True},
        ],
    },
}


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------


@dataclass
class CriterionResult:
    """Result for a single criterion."""

    id: str
    label: str
    met: bool
    na: bool = False


@dataclass
class BundleResult:
    """Result of evaluating a single prophylaxis bundle."""

    id: str
    name: str
    status: str  # complete, partial, pending, na
    score: int = 0
    criteria: list[CriterionResult] = field(default_factory=list)


@dataclass
class BundlesResult:
    """Aggregate result for all 5 bundles."""

    bundles: list[BundleResult] = field(default_factory=list)
    overall_status: str = "all_pending"  # all_complete, partial, all_pending
    overall_score: int = 0


# ---------------------------------------------------------------------------
# Scoring logic
# ---------------------------------------------------------------------------


def compute_score_and_status(criteria: list[CriterionResult]) -> tuple[int, str]:
    """Compute score (0-100) and status from a list of criteria results.

    Rules:
      - Applicable criteria = those with na == False
      - score = round(met_count / applicable_count * 100)
      - status:
          complete (100%), partial (>0% <100%), pending (0%), na (all na)
    """
    applicable = [c for c in criteria if not c.na]

    if not applicable:
        # All criteria are N/A — entire bundle is N/A
        return 0, "na"

    met_count = sum(1 for c in applicable if c.met)
    score = round(met_count / len(applicable) * 100)

    if score == 100:
        status = "complete"
    elif score > 0:
        status = "partial"
    else:
        status = "pending"

    return score, status


def compute_overall(bundles: list[BundleResult]) -> tuple[str, int]:
    """Compute overall_status and overall_score from a list of bundle results.

    - overall_status: all_complete (all 100%), all_pending (all 0%), partial (otherwise)
    - overall_score: average of the 5 bundle scores (0-100)
    """
    if not bundles:
        return "all_pending", 0

    scores = [b.score for b in bundles]
    avg_score = round(sum(scores) / len(scores))

    if all(s == 100 for s in scores):
        overall_status = "all_complete"
    elif all(s == 0 for s in scores):
        overall_status = "all_pending"
    else:
        overall_status = "partial"

    return overall_status, avg_score


# ---------------------------------------------------------------------------
# Bundle evaluator
# ---------------------------------------------------------------------------


def build_default_criteria(bundle_id: str) -> list[CriterionResult]:
    """Build the default criteria list for a bundle from the catalog.

    Uses na_default from the catalog to preset the na flag for each criterion.
    All met values start as False.
    """
    bundle_def = BUNDLE_CATALOG.get(bundle_id)
    if bundle_def is None:
        raise ValueError(f"Unknown bundle_id: {bundle_id}")

    return [
        CriterionResult(
            id=c["id"],
            label=c["label"],
            met=False,
            na=c.get("na_default", False),
        )
        for c in bundle_def["criteria"]
    ]


def evaluate_bundle(
    bundle_id: str,
    criteria_inputs: list[dict[str, Any]] | None = None,
) -> BundleResult:
    """Evaluate a single prophylaxis bundle given optional criteria overrides.

    Args:
        bundle_id: One of lamgd, tev, hiperglicemia, mobilizacao, dispositivos.
        criteria_inputs: Optional list of {id, met, na?} dicts. If None,
            the default catalog criteria are used (all met=False).

    Returns:
        BundleResult with computed score and status.
    """
    bundle_def = BUNDLE_CATALOG.get(bundle_id)
    if bundle_def is None:
        raise ValueError(f"Unknown bundle_id: {bundle_id}")

    # Start with the catalog defaults
    catalog_criteria = build_default_criteria(bundle_id)
    catalog_map: dict[str, CriterionResult] = {c.id: c for c in catalog_criteria}

    # Apply overrides from inputs
    if criteria_inputs:
        for inp in criteria_inputs:
            crit_id = inp.get("id")
            if crit_id is None or crit_id not in catalog_map:
                continue  # unknown or missing criterion — ignore
            catalog_map[crit_id].met = inp.get("met", False)
            if "na" in inp:
                catalog_map[crit_id].na = inp["na"]

    criteria = list(catalog_map.values())
    score, status = compute_score_and_status(criteria)

    return BundleResult(
        id=bundle_id,
        name=bundle_def["name"],
        status=status,
        score=score,
        criteria=criteria,
    )


def evaluate_all_bundles(
    bundle_inputs: dict[str, list[dict[str, Any]]] | None = None,
) -> BundlesResult:
    """Evaluate all 5 prophylaxis bundles.

    Args:
        bundle_inputs: Optional dict mapping bundle_id → list of criterion
            overrides. Bundles not present in the dict are evaluated with
            their catalog defaults (all met=False).

    Returns:
        BundlesResult with all bundles, overall_status, and overall_score.
    """
    bundle_ids = list(BUNDLE_CATALOG.keys())
    inputs = bundle_inputs or {}

    bundles = [
        evaluate_bundle(bid, inputs.get(bid))
        for bid in bundle_ids
    ]

    overall_status, overall_score = compute_overall(bundles)

    return BundlesResult(
        bundles=bundles,
        overall_status=overall_status,
        overall_score=overall_score,
    )


# ---------------------------------------------------------------------------
# Catalog helper
# ---------------------------------------------------------------------------


def get_bundle_catalog(bundle_id: str | None = None) -> dict[str, Any]:
    """Return static bundle catalog (all or one).

    Args:
        bundle_id: If provided, return only that bundle's definition.

    Returns:
        Catalog dict with keys: id, name, criteria (list of {id, label, na_default}).
    """
    if bundle_id:
        bundle_def = BUNDLE_CATALOG.get(bundle_id)
        if bundle_def is None:
            raise ValueError(f"Unknown bundle_id: {bundle_id}")
        return {
            "bundle_id": bundle_id,
            "bundle_name": bundle_def["name"],
            "criteria": bundle_def["criteria"],
        }

    return {
        bid: {
            "bundle_id": bid,
            "bundle_name": bdef["name"],
            "criteria": bdef["criteria"],
        }
        for bid, bdef in BUNDLE_CATALOG.items()
    }
