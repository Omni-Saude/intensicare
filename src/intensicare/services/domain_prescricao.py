"""Prescription domain service — state machine, drug interaction, dose calculator.

43 rules implemented across validation, state transitions, drug interactions,
and dose safety calculations for ICU prescriptions.

State machine (ADR-027):
    draft → active → completed  (auto end_time)
                   → discontinued (requires reason)
                   → suspended (requires reason)
    suspended → active (resume)
    completed/discontinued → [terminal, no further transitions]

Drug interactions (ADR-026): local ANVISA base with 4 severity levels.
Dose calculator: weight-based, renal-adjusted, age-adjusted, infusion limits.
"""

from __future__ import annotations

import logging
import math
import re
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

VALID_ROUTES: list[str] = ["IV", "IM", "SC", "PO", "SN", "IT", "TOP", "INAL"]
VALID_STATUSES: list[str] = [
    "draft", "active", "completed", "discontinued", "suspended",
]
VALID_FREQUENCIES: list[str] = [
    "QID", "TID", "BID", "QD", "QOD", "PRN", "continuous",
    "8/8h", "6/6h", "12/12h", "24/24h", "4/4h", "1/1h", "48/48h",
]
VALID_UNITS: list[str] = [
    "mg", "g", "mcg", "ng", "mL", "L", "UI", "mEq", "mmol",
    "mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h",
]
VALID_SEVERITIES: list[str] = [
    "contraindicated", "severe", "moderate", "minor",
]
VALID_INTERACTION_TYPES: list[str] = [
    "drug-drug", "drug-allergy", "drug-food", "duplicate",
]

# Routes that support continuous infusion
INFUSION_ROUTES: set[str] = {"IV", "SC"}

# Terminal states — no further transitions allowed
TERMINAL_STATES: set[str] = {"completed", "discontinued"}

# =============================================================================
# State machine transition map (ADR-027)
# =============================================================================

STATE_TRANSITIONS: dict[str, set[str]] = {
    "draft":       {"active", "draft"},
    "active":      {"completed", "discontinued", "suspended", "active"},
    "suspended":   {"active", "discontinued"},
    "completed":   set(),  # terminal
    "discontinued": set(),  # terminal
}

# Transitions that require a clinical reason
TRANSITIONS_REQUIRING_REASON: set[tuple[str, str]] = {
    ("active", "discontinued"),
    ("active", "suspended"),
    ("suspended", "discontinued"),
}

# Transitions that auto-set end_time
TRANSITIONS_SETTING_END_TIME: set[str] = {"completed", "discontinued"}

# =============================================================================
# Drug safety ranges (dose, unit, route) — Rule base for dose validation
# =============================================================================

# Format: (min_single_dose, max_single_dose, unit, max_daily_dose, max_infusion_rate)
# Doses in the drug's native unit
DRUG_SAFETY: dict[str, dict[str, Any]] = {
    "meropenem": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 6000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "IM"],
    },
    "vancomicina": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": True,
        "weight_dose_mg_per_kg": 15,
        "typical_routes": ["IV"],
        "infusion_rate_max_mg_h": 1000,  # max 1g/h (red man syndrome)
    },
    "noradrenalina": {
        "min_single_mcg_kg_min": 0.01,
        "max_single_mcg_kg_min": 3.0,
        "unit": "mcg/kg/min",
        "renal_adjust": False,
        "weight_based": True,
        "continuous_only": True,
        "typical_routes": ["IV"],
    },
    "dobutamina": {
        "min_single_mcg_kg_min": 2.5,
        "max_single_mcg_kg_min": 20.0,
        "unit": "mcg/kg/min",
        "renal_adjust": False,
        "weight_based": True,
        "continuous_only": True,
        "typical_routes": ["IV"],
    },
    "midazolam": {
        "min_single_mg": 1,
        "max_single_mg": 10,
        "max_daily_mg": 240,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "IM", "PO"],
        "elderly_reduce_pct": 50,  # 50% reduction for >65
    },
    "fentanil": {
        "min_single_mcg": 25,
        "max_single_mcg": 200,
        "max_daily_mcg": 1200,
        "unit": "mcg",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_mcg_per_kg": 1,
        "typical_routes": ["IV"],
        "continuous_mcg_kg_h_max": 10,
    },
    "propofol": {
        "min_single_mg": 10,
        "max_single_mg": 200,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_mg_per_kg": 2,
        "typical_routes": ["IV"],
        "continuous_mg_kg_h_max": 4,
        "max_daily_mg": 6000,
    },
    "insulina_regular": {
        "min_single_ui": 1,
        "max_single_ui": 50,
        "unit": "UI",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "SC"],
        "max_infusion_ui_h": 10,
    },
    "heparina_nao_fracionada": {
        "min_single_ui": 5000,
        "max_single_ui": 25000,
        "unit": "UI",
        "renal_adjust": False,
        "weight_based": True,
        "weight_dose_ui_per_kg": 80,  # bolus
        "typical_routes": ["IV", "SC"],
        "max_infusion_ui_h": 1500,
    },
    "amiodarona": {
        "min_single_mg": 150,
        "max_single_mg": 450,
        "max_daily_mg": 1200,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "omeprazol": {
        "min_single_mg": 20,
        "max_single_mg": 80,
        "max_daily_mg": 80,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "dexametasona": {
        "min_single_mg": 4,
        "max_single_mg": 20,
        "max_daily_mg": 40,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "ceftriaxona": {
        "min_single_mg": 1000,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "IM"],
    },
    "piperacilina_tazobactam": {
        "min_single_mg": 2250,
        "max_single_mg": 4500,
        "max_daily_mg": 18000,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV"],
    },
    "metoclopramida": {
        "min_single_mg": 5,
        "max_single_mg": 20,
        "max_daily_mg": 60,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "dipirona": {
        "min_single_mg": 500,
        "max_single_mg": 2000,
        "max_daily_mg": 4000,
        "unit": "mg",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
    },
    "morfina": {
        "min_single_mg": 2,
        "max_single_mg": 10,
        "max_daily_mg": 60,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "SC", "PO"],
        "elderly_reduce_pct": 50,
    },
    "enoxaparina": {
        "min_single_mg": 20,
        "max_single_mg": 150,
        "unit": "mg",
        "renal_adjust": True,
        "weight_based": True,
        "weight_dose_mg_per_kg": 1.5,
        "typical_routes": ["SC"],
    },
    "cloreto_de_potassio": {
        "min_single_mEq": 10,
        "max_single_mEq": 40,
        "max_daily_mEq": 200,
        "unit": "mEq",
        "renal_adjust": True,
        "weight_based": False,
        "typical_routes": ["IV", "PO"],
        "infusion_rate_max_mEq_h": 20,
    },
    "cloreto_de_sodio_3%": {
        "min_single_mL": 50,
        "max_single_mL": 500,
        "unit": "mL",
        "renal_adjust": False,
        "weight_based": False,
        "typical_routes": ["IV"],
        "infusion_rate_max_mL_h": 100,
    },
}

# =============================================================================
# Drug interaction knowledge base (ANVISA/DDI)
# =============================================================================

# (drug_a, drug_b) -> (severity, interaction_type, description)
DRUG_INTERACTIONS: dict[tuple[str, str], tuple[str, str, str]] = {
    # Drug-Drug interactions
    ("vancomicina", "amiodarona"): (
        "severe", "drug-drug",
        "Risco aumentado de prolongamento QT e Torsades de Pointes com vancomicina + amiodarona.",
    ),
    ("amiodarona", "vancomicina"): (
        "severe", "drug-drug",
        "Risco aumentado de prolongamento QT e Torsades de Pointes com vancomicina + amiodarona.",
    ),
    ("midazolam", "fentanil"): (
        "severe", "drug-drug",
        "Depressão respiratória aditiva — risco de apneia com midazolam + fentanil. Monitorar SpO2 continuamente.",
    ),
    ("fentanil", "midazolam"): (
        "severe", "drug-drug",
        "Depressão respiratória aditiva — risco de apneia com midazolam + fentanil. Monitorar SpO2 continuamente.",
    ),
    ("propofol", "midazolam"): (
        "severe", "drug-drug",
        "Sedação profunda excessiva com propofol + midazolam. Risco de hipotensão e bradicardia.",
    ),
    ("midazolam", "propofol"): (
        "severe", "drug-drug",
        "Sedação profunda excessiva com propofol + midazolam. Risco de hipotensão e bradicardia.",
    ),
    ("heparina_nao_fracionada", "enoxaparina"): (
        "contraindicated", "drug-drug",
        "Contraindicação absoluta: heparina não fracionada + enoxaparina — risco de sangramento grave.",
    ),
    ("enoxaparina", "heparina_nao_fracionada"): (
        "contraindicated", "drug-drug",
        "Contraindicação absoluta: heparina não fracionada + enoxaparina — risco de sangramento grave.",
    ),
    ("morfina", "midazolam"): (
        "severe", "drug-drug",
        "Depressão respiratória e sedação excessiva com morfina + midazolam. Risco de PCR.",
    ),
    ("midazolam", "morfina"): (
        "severe", "drug-drug",
        "Depressão respiratória e sedação excessiva com morfina + midazolam. Risco de PCR.",
    ),
    ("morfina", "fentanil"): (
        "moderate", "drug-drug",
        "Efeito opioide aditivo — considerar redução de dose de ambos. Aumenta risco de íleo paralítico.",
    ),
    ("fentanil", "morfina"): (
        "moderate", "drug-drug",
        "Efeito opioide aditivo — considerar redução de dose de ambos. Aumenta risco de íleo paralítico.",
    ),
    ("noradrenalina", "dobutamina"): (
        "moderate", "drug-drug",
        "Incompatibilidade física na mesma via — usar acessos venosos distintos. Risco de cristalização.",
    ),
    ("dobutamina", "noradrenalina"): (
        "moderate", "drug-drug",
        "Incompatibilidade física na mesma via — usar acessos venosos distintos. Risco de cristalização.",
    ),
    ("amiodarona", "heparina_nao_fracionada"): (
        "moderate", "drug-drug",
        "Amiodarona potencializa efeito anticoagulante da heparina. Monitorar PTTa/TAP a cada 6h.",
    ),
    ("heparina_nao_fracionada", "amiodarona"): (
        "moderate", "drug-drug",
        "Amiodarona potencializa efeito anticoagulante da heparina. Monitorar PTTa/TAP a cada 6h.",
    ),
    ("meropenem", "vancomicina"): (
        "minor", "drug-drug",
        "Sinergismo antimicrobiano esperado para cobertura ampla de gram-positivos e gram-negativos.",
    ),
    ("vancomicina", "meropenem"): (
        "minor", "drug-drug",
        "Sinergismo antimicrobiano esperado para cobertura ampla de gram-positivos e gram-negativos.",
    ),
    ("cloreto_de_potassio", "insulina_regular"): (
        "moderate", "drug-drug",
        "Insulina + K+ IV: risco de hipocalemia rebote se infusão rápida. Monitorar K+ sérico antes e após.",
    ),
    ("insulina_regular", "cloreto_de_potassio"): (
        "moderate", "drug-drug",
        "Insulina + K+ IV: risco de hipocalemia rebote se infusão rápida. Monitorar K+ sérico antes e após.",
    ),
    ("ceftriaxona", "cloreto_de_sodio_3%"): (
        "contraindicated", "drug-drug",
        "Ceftriaxona + soluções contendo cálcio (incluindo NaCl 3%) — risco de precipitação e embolia pulmonar.",
    ),
    ("cloreto_de_sodio_3%", "ceftriaxona"): (
        "contraindicated", "drug-drug",
        "Ceftriaxona + soluções contendo cálcio (incluindo NaCl 3%) — risco de precipitação e embolia pulmonar.",
    ),
    ("propofol", "fentanil"): (
        "moderate", "drug-drug",
        "Potencialização de sedação e hipotensão. Reduzir dose de propofol em 20-30% se coadministrado com fentanil.",
    ),
    ("fentanil", "propofol"): (
        "moderate", "drug-drug",
        "Potencialização de sedação e hipotensão. Reduzir dose de propofol em 20-30% se coadministrado com fentanil.",
    ),
    # Duplicate class interactions
    ("piperacilina_tazobactam", "meropenem"): (
        "moderate", "duplicate",
        "Duplicação de cobertura beta-lactâmica (ambos carbapenêmicos/ureidopenicilinas). Reavaliar necessidade.",
    ),
    ("meropenem", "piperacilina_tazobactam"): (
        "moderate", "duplicate",
        "Duplicação de cobertura beta-lactâmica (ambos carbapenêmicos/ureidopenicilinas). Reavaliar necessidade.",
    ),
    ("ceftriaxona", "meropenem"): (
        "moderate", "duplicate",
        "Duplicação de cobertura beta-lactâmica de amplo espectro. Restringir a um agente se cultura dirigida disponível.",
    ),
    ("meropenem", "ceftriaxona"): (
        "moderate", "duplicate",
        "Duplicação de cobertura beta-lactâmica de amplo espectro. Restringir a um agente se cultura dirigida disponível.",
    ),
}

# Drug class groupings for duplicate checks
DRUG_CLASSES: dict[str, str] = {
    "meropenem": "carbapenem",
    "piperacilina_tazobactam": "ureidopenicilina",
    "ceftriaxona": "cefalosporina_3g",
    "vancomicina": "glicopeptideo",
    "midazolam": "benzodiazepinico",
    "propofol": "anestesico_geral",
    "fentanil": "opioide",
    "morfina": "opioide",
    "noradrenalina": "catecolamina",
    "dobutamina": "catecolamina",
    "amiodarona": "antiarritmico_classe_iii",
    "heparina_nao_fracionada": "anticoagulante",
    "enoxaparina": "anticoagulante_hbpm",
    "insulina_regular": "insulina",
    "omeprazol": "inibidores_bomba_protons",
    "dexametasona": "corticoide",
    "metoclopramida": "antiemetico",
    "dipirona": "analgesico_nao_opioide",
    "cloreto_de_potassio": "eletrolito",
    "cloreto_de_sodio_3%": "eletrolito_hipertonico",
}

# Drug-allergy cross-reactivity groups
DRUG_ALLERGY_GROUPS: dict[str, list[str]] = {
    "penicilina": ["meropenem", "piperacilina_tazobactam"],
    "cefalosporina": ["ceftriaxona", "meropenem"],
    "opioide": ["morfina", "fentanil"],
    "sulfa": [],
    "aines": ["dipirona"],
    "benzodiazepinico": ["midazolam"],
    "heparina": ["heparina_nao_fracionada", "enoxaparina"],
}

# =============================================================================
# Renal adjustment table (GFR-based dose multipliers)
# =============================================================================

# GFR thresholds in mL/min
RENAL_ADJUSTMENTS: dict[str, Any] = {
    "meropenem": {
        "gfr_normal": 1.0,   # GFR 90-119: normal renal function
        "gfr_arc": 1.0,      # GFR >=120: ARC — standard dose (no increase)
        "gfr_50_90": 1.0,    # full dose
        "gfr_26_50": 1.0,    # full dose
        "gfr_10_25": 0.5,    # 50% dose
        "gfr_below_10": 0.25,  # 25% dose
    },
    "vancomicina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.2,      # ARC: higher doses may be needed
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.5,
        "gfr_10_25": 0.25,
        "gfr_below_10": 0.15,
    },
    "piperacilina_tazobactam": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.2,      # ARC: higher doses may be needed
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.33,
    },
    "morfina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.5,
    },
    "insulina_regular": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.25,
    },
    "enoxaparina": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.75,
        "gfr_10_25": 0.5,
        "gfr_below_10": 0.5,
    },
    "cloreto_de_potassio": {
        "gfr_normal": 1.0,
        "gfr_arc": 1.0,
        "gfr_50_90": 1.0,
        "gfr_26_50": 0.5,
        "gfr_10_25": 0.25,
        "gfr_below_10": 0.1,
    },
}

# =============================================================================
# Pediatric and elderly adjustments
# =============================================================================

# Pediatric dose adjustment by age brackets (multiplier of adult dose)
PEDIATRIC_ADJUSTMENTS: dict[str, dict[str, float]] = {
    "neonate": 0.05,     # 0-28 days
    "infant": 0.15,      # 1-12 months
    "toddler": 0.25,     # 1-3 years
    "child": 0.5,        # 4-12 years
    "adolescent": 0.75,  # 13-17 years
}

# =============================================================================
# Dataclasses
# =============================================================================


@dataclass
class PrescriptionRecord:
    """In-memory prescription record matching OpenAPI Prescription schema."""

    id: int | None = None
    mpi_id: str = ""
    drug: str = ""
    dose: float = 0.0
    unit: str = ""
    route: str = ""
    frequency: str = ""
    start_time: str = ""
    end_time: str | None = None
    status: str = "active"
    version: int = 1
    notes: str | None = None
    prescribed_by: str = "system"
    created_at: str = ""
    updated_at: str = ""


@dataclass
class InteractionAlert:
    """Drug interaction alert matching OpenAPI InteracaoAlerta schema."""

    id: int | None = None
    severity: str = "moderate"
    interaction_type: str = "drug-drug"
    description: str = ""
    resolved: bool = False


@dataclass
class PrescriptionResult:
    """Result of creating a prescription with dose validation and alerts."""

    prescription: PrescriptionRecord
    alerts: list[InteractionAlert] = field(default_factory=list)
    dose_valid: bool = True
    dose_warnings: list[str] = field(default_factory=list)


@dataclass
class PrescriptionListResult:
    """Paginated list of prescriptions."""

    prescriptions: list[PrescriptionRecord] = field(default_factory=list)
    total: int = 0


# =============================================================================
# In-memory store (to be replaced by DB via API router)
# =============================================================================

_prescriptions: dict[int, PrescriptionRecord] = {}
_alerts: dict[int, list[InteractionAlert]] = {}
_next_id: int = 1


def _generate_id() -> int:
    """Generate next sequential prescription ID."""
    global _next_id
    pid = _next_id
    _next_id += 1
    return pid


def _now_iso() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


# =============================================================================
# Rule R01-R10: Input validation
# =============================================================================


def _validate_input(
    mpi_id: str,
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    notes: str | None = None,
    prescribed_by: str = "",
) -> list[str]:
    """R01-R10: Validate all input fields. Returns list of error messages."""
    errors: list[str] = []

    # R01: mpi_id required and non-empty
    if not mpi_id or not mpi_id.strip():
        errors.append("R01: mpi_id é obrigatório e não pode estar vazio.")

    # R02: drug name required and non-empty
    if not drug or not drug.strip():
        errors.append("R02: Nome do fármaco é obrigatório e não pode estar vazio.")

    # R03: dose must be a positive number
    if dose <= 0:
        errors.append(f"R03: Dose deve ser um número positivo (recebido: {dose}).")

    # R04: unit must be valid
    if unit not in VALID_UNITS:
        errors.append(
            f"R04: Unidade '{unit}' inválida. Unidades válidas: {', '.join(VALID_UNITS)}."
        )

    # R05: route must be a valid administration route
    if route not in VALID_ROUTES:
        errors.append(
            f"R05: Via '{route}' inválida. Vias válidas: {', '.join(VALID_ROUTES)}."
        )

    # R06: frequency must be valid
    if frequency not in VALID_FREQUENCIES:
        errors.append(
            f"R06: Frequência '{frequency}' inválida. "
            f"Válidas: {', '.join(VALID_FREQUENCIES)}."
        )

    # R07: route must be compatible with drug's typical routes
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if safety and route not in safety.get("typical_routes", [route]):
        errors.append(
            f"R07: Via '{route}' não é típica para {drug}. "
            f"Vias esperadas: {', '.join(safety['typical_routes'])}."
        )

    # R08: continuous-only drugs must use infusion routes
    if safety and safety.get("continuous_only") and route not in INFUSION_ROUTES:
        errors.append(
            f"R08: {drug} requer infusão contínua e a via '{route}' não suporta infusão."
        )

    # R09: notes length validation (max 1024 chars per schema)
    if notes and len(notes) > 1024:
        errors.append(
            f"R09: Observações excedem o limite de 1024 caracteres "
            f"(recebido: {len(notes)})."
        )

    # R10: prescribed_by required and non-empty
    if not prescribed_by or not prescribed_by.strip():
        errors.append("R10: Nome do prescritor (prescribed_by) é obrigatório.")

    return errors


# =============================================================================
# Rule R11-R16: Duplicate and conflict detection
# =============================================================================


def _check_duplicate(mpi_id: str, drug: str, route: str) -> list[str]:
    """R11: Check for duplicate active prescription for same drug+route+patient."""
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    for rx in _prescriptions.values():
        if (
            rx.mpi_id == mpi_id
            and rx.drug.lower().replace(" ", "_") == drug_key
            and rx.route == route
            and rx.status == "active"
        ):
            warnings.append(
                f"R11: Paciente {mpi_id} já possui prescrição ativa de {drug} "
                f"via {route} (ID: {rx.id}). Verificar duplicidade."
            )
    return warnings


def _check_same_class_duplicate(mpi_id: str, drug: str) -> list[str]:
    """R12: Check for duplicate therapeutic class."""
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    new_class = DRUG_CLASSES.get(drug_key)
    if not new_class:
        return warnings

    for rx in _prescriptions.values():
        if rx.mpi_id == mpi_id and rx.status == "active":
            rx_key = rx.drug.lower().replace(" ", "_")
            rx_class = DRUG_CLASSES.get(rx_key)
            if rx_class and rx_class == new_class and rx_key != drug_key:
                warnings.append(
                    f"R12: Duplicação de classe terapêutica '{new_class}': "
                    f"{drug} + {rx.drug} já ativos para o paciente {mpi_id}."
                )
    return warnings


def _validate_temporal_constraints(
    start_time: str,
    end_time: str | None = None,
) -> list[str]:
    """R13-R14: Validate temporal constraints on prescription dates."""
    warnings: list[str] = []

    # R13: Validate start_time is a valid ISO-8601 datetime string
    if start_time:
        try:
            datetime.fromisoformat(start_time)
        except (ValueError, TypeError):
            warnings.append(
                f"R13: start_time '{start_time}' não é uma data ISO-8601 válida."
            )

    # R14: end_time must be after start_time
    if end_time:
        try:
            dt_end = datetime.fromisoformat(end_time)
            dt_start = datetime.fromisoformat(start_time) if start_time else datetime.now(timezone.utc)
            if dt_end <= dt_start:
                warnings.append(
                    f"R14: end_time ({end_time}) deve ser posterior a "
                    f"start_time ({start_time})."
                )
        except (ValueError, TypeError):
            pass  # format error, already handled or irrelevant

    return warnings


def _validate_prescription_limits(mpi_id: str) -> list[str]:
    """R15-R16: Prescription safety limits.

    R15: Maximum active prescriptions per patient (15).
    R16: Polypharmacy alert threshold (8 active drugs).
    """
    warnings: list[str] = []
    active_count = count_active_prescriptions(mpi_id)

    # R15: Hard limit — max 15 active prescriptions
    if active_count >= 15:
        warnings.append(
            f"R15: Limite máximo de 15 prescrições ativas atingido para o paciente "
            f"{mpi_id} ({active_count} ativas). Não é possível criar nova prescrição."
        )

    # R16: Polypharmacy alert — warning at 8 active drugs
    if active_count >= 8:
        warnings.append(
            f"R16: Polifarmácia detectada — {active_count} prescrições ativas para "
            f"o paciente {mpi_id}. Revisar necessidade de todas as terapias."
        )

    return warnings


# =============================================================================
# Rule R17-R26: Drug interaction checks
# =============================================================================


def _check_interactions(drug: str, mpi_id: str) -> list[InteractionAlert]:
    """R17-R26: Check drug-drug and duplicate interactions against local ANVISA base.

    Scans all active prescriptions for the patient and checks each pair
    against the DRUG_INTERACTIONS knowledge base.
    """
    alerts: list[InteractionAlert] = []
    drug_key = drug.lower().replace(" ", "_")

    # Get all active prescriptions for this patient
    active_rx: list[PrescriptionRecord] = [
        rx
        for rx in _prescriptions.values()
        if rx.mpi_id == mpi_id and rx.status == "active"
    ]

    seen_drugs: set[str] = {drug_key}

    for rx in active_rx:
        other_key = rx.drug.lower().replace(" ", "_")

        # R17: Look up direct drug-drug interaction pair
        pair = (drug_key, other_key)
        if pair in DRUG_INTERACTIONS:
            severity, itype, desc = DRUG_INTERACTIONS[pair]
            alerts.append(
                InteractionAlert(
                    severity=severity,
                    interaction_type=itype,
                    description=f"[{drug} × {rx.drug}] {desc}",
                )
            )

        # R18: Check drug-allergy via cross-reactivity groups
        for allergy_group, drugs_in_group in DRUG_ALLERGY_GROUPS.items():
            if drug_key in drugs_in_group and other_key in drugs_in_group:
                alerts.append(
                    InteractionAlert(
                        severity="moderate",
                        interaction_type="drug-allergy",
                        description=(
                            f"R18: Alergia cruzada potencial: {drug} e {rx.drug} "
                            f"compartilham grupo alergênico '{allergy_group}'."
                        ),
                    )
                )

        # R19: Check therapeutic class duplication
        new_class = DRUG_CLASSES.get(drug_key)
        other_class = DRUG_CLASSES.get(other_key)
        if new_class and other_class and new_class == other_class and drug_key != other_key:
            if other_key not in seen_drugs:
                alerts.append(
                    InteractionAlert(
                        severity="moderate",
                        interaction_type="duplicate",
                        description=(
                            f"R19: Duplicação terapêutica: {drug} e {rx.drug} "
                            f"são da mesma classe '{new_class}'."
                        ),
                    )
                )

        # R20: Catecholamine incompatibility (same IV line)
        if new_class == "catecolamina" and other_class == "catecolamina":
            if drug_key != other_key:
                alerts.append(
                    InteractionAlert(
                        severity="moderate",
                        interaction_type="drug-drug",
                        description=(
                            f"R20: Duas catecolaminas ativas ({drug} + {rx.drug}) — "
                            "usar acessos venosos distintos."
                        ),
                    )
                )

        seen_drugs.add(other_key)

    # R21: Opioid stacking risk
    opioid_count = sum(
        1 for d in seen_drugs
        if DRUG_CLASSES.get(d) == "opioide"
    )
    if opioid_count >= 2:
        alerts.append(
            InteractionAlert(
                severity="severe",
                interaction_type="drug-drug",
                description=(
                    f"R21: {opioid_count} opioides ativos simultaneamente — "
                    "risco elevado de depressão respiratória. Reavaliar analgesia."
                ),
            )
        )

    # R22: Sedative stacking risk (benzo + opioid + anesthetic)
    sedative_classes = {"benzodiazepinico", "opioide", "anestesico_geral"}
    sedative_count = sum(
        1 for d in seen_drugs
        if DRUG_CLASSES.get(d) in sedative_classes
    )
    if sedative_count >= 3:
        alerts.append(
            InteractionAlert(
                severity="severe",
                interaction_type="drug-drug",
                description=(
                    f"R22: {sedative_count} sedativos ativos simultaneamente — "
                    "risco de sedação profunda e depressão respiratória."
                ),
            )
        )

    # R23: Anticoagulant stacking
    anticoag_count = sum(
        1 for d in seen_drugs
        if DRUG_CLASSES.get(d) in ("anticoagulante", "anticoagulante_hbpm")
    )
    if anticoag_count >= 2:
        alerts.append(
            InteractionAlert(
                severity="contraindicated",
                interaction_type="drug-drug",
                description=(
                    f"R23: {anticoag_count} anticoagulantes ativos simultaneamente — "
                    "contraindicação absoluta por risco de sangramento grave."
                ),
            )
        )

    # R24: Polypharmacy alert (>= 8 active drugs)
    total_active = len(seen_drugs)
    if total_active >= 8:
        alerts.append(
            InteractionAlert(
                severity="moderate",
                interaction_type="drug-drug",
                description=(
                    f"R24: Polifarmácia ({total_active} fármacos ativos) — "
                    "risco aumentado de interações adversas. Revisar prescrição."
                ),
            )
        )

    # R25: Electrolyte concentration interaction
    if drug_key == "cloreto_de_potassio" and "insulina_regular" in seen_drugs:
        alerts.append(
            InteractionAlert(
                severity="moderate",
                interaction_type="drug-drug",
                description=(
                    "R25: K+ IV + insulina ativa: risco de hipocalemia. "
                    "Monitorar K+ sérico antes da administração."
                ),
            )
        )

    # R26: Ceftriaxone + calcium-containing solutions
    if drug_key == "ceftriaxona" and "cloreto_de_sodio_3%" in seen_drugs:
        alerts.append(
            InteractionAlert(
                severity="contraindicated",
                interaction_type="drug-drug",
                description=(
                    "R26: Ceftriaxona + solução com cálcio: risco de precipitação "
                    "e embolia pulmonar por cristais de ceftriaxona-cálcio."
                ),
            )
        )

    return alerts


# =============================================================================
# Rule R27-R35: Dose validation and calculation
# =============================================================================


def _validate_dose(
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    weight_kg: float | None = None,
    gfr: float | None = None,
    age_years: float | None = None,
) -> tuple[bool, list[str]]:
    """R27-R35: Validate dose against known safety ranges.

    Returns (valid, warnings). A dose may be flagged with warnings but still
    considered technically valid (clinician override possible).
    """
    warnings: list[str] = []
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)

    if not safety:
        # Drug not in our safety database — can't validate, assume valid
        return True, warnings

    # R27: Convert dose to mg equivalent for comparison
    dose_mg = _to_mg(dose, unit, weight_kg=weight_kg)

    # R28: Max single dose check
    max_single = safety.get("max_single_mg")
    min_single = safety.get("min_single_mg")
    if max_single is not None and dose_mg > max_single:
        warnings.append(
            f"R28: Dose única de {dose} {unit} ({dose_mg} mg equiv.) excede "
            f"o limite máximo de {max_single} mg para {drug}."
        )
    if min_single is not None and dose_mg < min_single:
        warnings.append(
            f"R28: Dose única de {dose} {unit} ({dose_mg} mg equiv.) abaixo "
            f"do limite mínimo de {min_single} mg para {drug}."
        )

    # R29: Max daily dose estimation
    max_daily = safety.get("max_daily_mg")
    if max_daily is not None:
        doses_per_day = _estimate_daily_doses(frequency)
        daily_mg = dose_mg * doses_per_day
        if daily_mg > max_daily:
            warnings.append(
                f"R29: Dose diária estimada ({daily_mg} mg) excede o limite "
                f"máximo diário de {max_daily} mg para {drug}."
            )

    # R30: Weight-based dose validation
    if safety.get("weight_based") and weight_kg and weight_kg > 0:
        expected = _calculate_dose_weight_based(weight_kg, drug_key)
        if expected > 0:
            ratio = dose_mg / expected
            if ratio < 0.5:
                warnings.append(
                    f"R30: Dose ({dose_mg} mg) é {ratio:.0%} da dose calculada "
                    f"por peso ({expected:.0f} mg para {weight_kg} kg). Possível subdose."
                )
            elif ratio > 2.0:
                warnings.append(
                    f"R30: Dose ({dose_mg} mg) é {ratio:.0%} da dose calculada "
                    f"por peso ({expected:.0f} mg para {weight_kg} kg). Possível sobredose."
                )

    # R31: Renal-adjusted dose check
    if safety.get("renal_adjust") and gfr is not None and gfr > 0:
        adjusted = _calculate_dose_renal_adjusted(gfr, drug_key, dose_mg)
        if adjusted != dose_mg:
            ratio = adjusted / dose_mg
            warnings.append(
                f"R31: Dose ajustada para função renal (GFR={gfr} mL/min): "
                f"{adjusted:.0f} mg (fator {ratio:.0%}). Dose atual: {dose_mg} mg."
            )

    # R32: Elderly dose reduction alert
    if age_years and age_years >= 65 and safety.get("elderly_reduce_pct"):
        reduce_pct = safety["elderly_reduce_pct"]
        recommended = dose_mg * (1 - reduce_pct / 100)
        warnings.append(
            f"R32: Paciente idoso ({age_years:.0f} anos). Considerar redução de "
            f"{reduce_pct}% na dose de {drug} → dose recomendada: ~{recommended:.0f} mg."
        )

    # R33: Pediatric dose adjustment
    if age_years is not None and age_years < 18:
        bracket = _pediatric_age_bracket(age_years)
        factor = PEDIATRIC_ADJUSTMENTS.get(bracket, 1.0)
        if factor < 1.0:
            pediatric_dose = dose_mg * factor
            warnings.append(
                f"R33: Paciente pediátrico ({bracket}, {age_years:.1f} anos). "
                f"Dose pediátrica estimada: ~{pediatric_dose:.0f} mg "
                f"(fator {factor:.0%} da dose adulta)."
            )

    # R34: Infusion rate limit for IV drugs
    if route == "IV" and frequency == "continuous":
        max_rate = safety.get("infusion_rate_max_mg_h")
        if max_rate and dose_mg > max_rate:
            warnings.append(
                f"R34: Taxa de infusão ({dose_mg} mg/h) excede o limite "
                f"de segurança de {max_rate} mg/h para {drug}."
            )

    # R35: Concentration limit check for specific routes
    if drug_key == "cloreto_de_potassio" and route == "IV":
        max_rate = safety.get("infusion_rate_max_mEq_h", 20)
        if dose > max_rate:
            warnings.append(
                f"R35: Infusão de K+ ({dose} mEq/h) excede {max_rate} mEq/h. "
                "Risco de arritmia por hipercalemia aguda."
            )

    # Dose is valid if no warnings are critical (all are advisory)
    valid = True
    return valid, warnings


def _mass_to_mg(dose: float, unit: str) -> float:
    """Convert a mass or volume dose to mg equivalent for comparison.

    Handles mass/volume units only (mg, g, mcg, ng, mL, L, UI, mEq, mmol).
    For rate or weight-based units, use ``_rate_to_mg()`` instead.

    Parameters
    ----------
    dose:
        The numeric dose value.
    unit:
        Unit string (e.g. "mg", "g", "mcg", "mL").

    Returns
    -------
    float
        Dose expressed in mg equivalent.
    """
    conversion: dict[str, float] = {
        "mg": 1.0,
        "g": 1000.0,
        "mcg": 0.001,
        "ng": 1e-6,
        "mL": 1.0,   # context-dependent, assume 1 mg/mL
        "L": 1000.0,
        "UI": 1.0,   # cannot directly convert to mg
        "mEq": 1.0,  # context-dependent
        "mmol": 1.0,  # context-dependent
    }
    return dose * conversion.get(unit, 1.0)


def _rate_to_mg(
    rate: float,
    unit: str,
    weight_kg: float | None = None,
    duration_h: float = 1.0,
) -> float:
    """Convert a rate or weight-based dose to total mg equivalent.

    Unlike ``_mass_to_mg()``, this function correctly incorporates patient
    weight and infusion duration for clinically meaningful dose comparisons.

    Parameters
    ----------
    rate:
        The numeric rate (or weight-adjusted dose) value.
    unit:
        Unit string — must be a rate or weight-based unit:
        ``mg/kg``, ``mcg/kg``, ``mcg/kg/min``, ``mg/h``, ``mL/h``.
    weight_kg:
        Patient weight in kg. Required for ``mg/kg``, ``mcg/kg``,
        and ``mcg/kg/min``.
    duration_h:
        Duration in hours for the administration (default 1.0).

    Returns
    -------
    float
        Total mg equivalent over the given duration.

    Raises
    ------
    ValueError
        If ``weight_kg`` is missing for weight-dependent units.
    """
    known_rate_units = {"mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h"}

    if unit not in known_rate_units:
        # Not a rate unit — fall back to mass conversion
        return _mass_to_mg(rate, unit)

    # Weight-based units require weight
    weight_dependent = {"mg/kg", "mcg/kg", "mcg/kg/min"}
    if unit in weight_dependent and (weight_kg is None or weight_kg <= 0):
        raise ValueError(
            f"Unit '{unit}' requires patient weight_kg (got {weight_kg!r}). "
            "Cannot compute clinically meaningful mg equivalent without weight."
        )

    if unit == "mg/kg":
        return rate * weight_kg  # type: ignore[operator]
    elif unit == "mcg/kg":
        return rate * weight_kg * 0.001  # type: ignore[operator]
    elif unit == "mcg/kg/min":
        return rate * weight_kg * duration_h * 60.0 * 0.001  # type: ignore[operator]
    elif unit == "mg/h":
        return rate * duration_h
    elif unit == "mL/h":
        # Assume 1 mg/mL concentration
        return rate * duration_h

    # Should not reach here; fallback
    return rate


def _to_mg(
    dose: float,
    unit: str,
    weight_kg: float | None = None,
    duration_h: float = 1.0,
) -> float:
    """Convert dose to mg equivalent, delegating to the correct converter.

    Dispatches to :func:`_rate_to_mg` for rate/weight-based units
    (mg/kg, mcg/kg, mcg/kg/min, mg/h, mL/h) and to :func:`_mass_to_mg`
    for mass/volume units.
    """
    rate_units = {"mg/kg", "mcg/kg", "mcg/kg/min", "mg/h", "mL/h"}

    if unit in rate_units:
        return _rate_to_mg(dose, unit, weight_kg=weight_kg, duration_h=duration_h)
    return _mass_to_mg(dose, unit)


def _estimate_daily_doses(frequency: str) -> int:
    """Estimate number of doses per 24h from frequency string."""
    freq_map: dict[str, int] = {
        "QID": 4,
        "TID": 3,
        "BID": 2,
        "QD": 1,
        "QOD": 1,  # every other day ~0.5, but use 1 for estimation
        "PRN": 1,  # as needed, assume max 1
        "continuous": 24,  # hourly rate
        "8/8h": 3,
        "6/6h": 4,
        "12/12h": 2,
        "24/24h": 1,
        "4/4h": 6,
        "1/1h": 24,
        "48/48h": 1,
    }
    return freq_map.get(frequency, 1)


def _pediatric_age_bracket(age_years: float) -> str:
    """Determine pediatric age bracket."""
    age_days = age_years * 365.25
    if age_days <= 28:
        return "neonate"
    if age_days <= 365:
        return "infant"
    if age_years <= 3:
        return "toddler"
    if age_years <= 12:
        return "child"
    return "adolescent"


# =============================================================================
# Rule R36-R40: State machine transitions
# =============================================================================


def _transition_state(
    prescription: PrescriptionRecord,
    new_status: str,
    reason: str | None = None,
    changed_by: str = "system",
) -> PrescriptionRecord:
    """R36-R40: State machine transition with validation.

    Returns updated PrescriptionRecord. Raises ValueError on invalid transition.
    """
    old_status = prescription.status

    # R36: Validate new_status is a known state
    if new_status not in VALID_STATUSES:
        raise ValueError(
            f"R36: Status '{new_status}' inválido. Status válidos: "
            f"{', '.join(VALID_STATUSES)}."
        )

    # R37: Terminal states cannot transition
    if old_status in TERMINAL_STATES:
        raise ValueError(
            f"R37: Prescrição {prescription.id} está em estado terminal "
            f"('{old_status}') e não pode ser modificada."
        )

    # R38: Validate transition is allowed
    allowed = STATE_TRANSITIONS.get(old_status, set())
    if new_status not in allowed and new_status != old_status:
        raise ValueError(
            f"R38: Transição '{old_status} → {new_status}' não é permitida. "
            f"Transições válidas de '{old_status}': {sorted(allowed)}."
        )

    # R39: Some transitions require clinical reason
    if (old_status, new_status) in TRANSITIONS_REQUIRING_REASON:
        if not reason or not reason.strip():
            raise ValueError(
                f"R39: Transição '{old_status} → {new_status}' requer "
                "justificativa clínica (reason)."
            )

    # R40: Auto-set end_time for terminal transitions
    if new_status in TRANSITIONS_SETTING_END_TIME:
        prescription.end_time = _now_iso()

    # Apply transition
    prescription.status = new_status
    prescription.version += 1
    prescription.updated_at = _now_iso()

    logger.info(
        "State transition: prescription %s: %s → %s (by %s, reason=%s)",
        prescription.id, old_status, new_status, changed_by, reason,
    )

    return prescription


# =============================================================================
# Weight-based and renal dose calculators
# =============================================================================


def _calculate_dose_weight_based(weight_kg: float, drug: str) -> float:
    """Calculate weight-based dose for a given drug.

    Returns dose in mg (or native unit as defined in DRUG_SAFETY).
    """
    drug_key = drug.lower().replace(" ", "_")
    safety = DRUG_SAFETY.get(drug_key)
    if not safety or not safety.get("weight_based"):
        return 0.0

    if "weight_dose_mg_per_kg" in safety:
        return weight_kg * safety["weight_dose_mg_per_kg"]
    if "weight_dose_mcg_per_kg" in safety:
        return weight_kg * safety["weight_dose_mcg_per_kg"] / 1000.0
    if "weight_dose_ui_per_kg" in safety:
        return weight_kg * safety["weight_dose_ui_per_kg"]

    return 0.0


def _calculate_dose_renal_adjusted(gfr: float, drug: str, base_dose: float) -> float:
    """Adjust dose for renal function based on GFR.

    Returns adjusted dose in same unit as base_dose.
    """
    drug_key = drug.lower().replace(" ", "_")
    adjustments = RENAL_ADJUSTMENTS.get(drug_key)
    if not adjustments:
        return base_dose

    if gfr >= 120:
        factor = adjustments.get("gfr_arc", adjustments.get("gfr_normal", 1.0))
    elif gfr >= 90:
        factor = adjustments.get("gfr_normal", 1.0)
    elif gfr >= 50:
        factor = adjustments.get("gfr_50_90", 1.0)
    elif gfr >= 26:
        factor = adjustments.get("gfr_26_50", 1.0)
    elif gfr >= 10:
        factor = adjustments.get("gfr_10_25", 1.0)
    else:
        factor = adjustments.get("gfr_below_10", 1.0)

    return base_dose * factor


# =============================================================================
# Public API — Main functions
# =============================================================================


def create_prescription(
    mpi_id: str,
    drug: str,
    dose: float,
    unit: str,
    route: str,
    frequency: str,
    start_time: str = "",
    notes: str | None = None,
    prescribed_by: str = "system",
    weight_kg: float | None = None,
    gfr: float | None = None,
    age_years: float | None = None,
) -> PrescriptionResult:
    """R41: Create a new prescription with full validation pipeline.

    Order of operations:
    1. Validate input fields (R01-R10)
    2. Check duplicates (R11-R12)
    3. Check drug interactions (R17-R26)
    4. Validate dose (R27-R35)
    5. Create record in in-memory store

    Args:
        mpi_id: Patient identifier (MPI — Master Patient Index).
        drug: Drug name (e.g., 'Meropenem', 'vancomicina').
        dose: Numeric dose value.
        unit: Dose unit (mg, g, mcg, UI, mEq, etc.).
        route: Administration route (IV, PO, SC, etc.).
        frequency: Dosing frequency (8/8h, QID, continuous, etc.).
        start_time: ISO-8601 timestamp. Defaults to now.
        notes: Optional clinical notes.
        prescribed_by: Prescribing clinician identifier.
        weight_kg: Patient weight for weight-based dose validation.
        gfr: Glomerular filtration rate for renal adjustment.
        age_years: Patient age for pediatric/elderly adjustments.

    Returns:
        PrescriptionResult with created prescription, interaction alerts,
        dose validity flag and warnings.

    Raises:
        ValueError: On invalid input (dose <= 0, empty fields, etc.).
    """
    # Step 1: Validate inputs
    errors = _validate_input(mpi_id, drug, dose, unit, route, frequency, notes, prescribed_by)
    if errors:
        raise ValueError("Erro de validação:\n" + "\n".join(f"  - {e}" for e in errors))

    # Step 2: Check duplicates and temporal constraints
    dup_warnings = _check_duplicate(mpi_id, drug, route)
    dup_warnings += _check_same_class_duplicate(mpi_id, drug)
    dup_warnings += _validate_temporal_constraints(start_time)
    dup_warnings += _validate_prescription_limits(mpi_id)

    # Step 3: Check drug interactions
    alerts = _check_interactions(drug, mpi_id)

    # Step 4: Validate dose
    dose_valid, dose_warnings = _validate_dose(
        drug, dose, unit, route, frequency, weight_kg, gfr, age_years
    )

    # Merge duplicate warnings into dose_warnings
    all_warnings = dup_warnings + dose_warnings

    # Check for contraindicated interactions — hard stop
    contraindicated = [a for a in alerts if a.severity == "contraindicated"]
    if contraindicated:
        raise ValueError(
            "Interação medicamentosa CONTRAINDICADA detectada:\n"
            + "\n".join(f"  - {a.description}" for a in contraindicated)
        )

    # Step 5: Create prescription record
    now = _now_iso()
    record = PrescriptionRecord(
        id=_generate_id(),
        mpi_id=mpi_id,
        drug=drug,
        dose=dose,
        unit=unit,
        route=route,
        frequency=frequency,
        start_time=start_time or now,
        status="active",
        version=1,
        notes=notes,
        prescribed_by=prescribed_by,
        created_at=now,
        updated_at=now,
    )

    # Store in memory (id is guaranteed set by _generate_id above)
    assert record.id is not None
    _prescriptions[record.id] = record
    _alerts[record.id] = alerts

    logger.info(
        "Prescription created: id=%s, patient=%s, drug=%s, dose=%s %s, route=%s, "
        "alerts=%d, warnings=%d",
        record.id, mpi_id, drug, dose, unit, route, len(alerts), len(all_warnings),
    )

    return PrescriptionResult(
        prescription=record,
        alerts=alerts,
        dose_valid=dose_valid,
        dose_warnings=all_warnings,
    )


def get_prescription(prescription_id: int) -> PrescriptionRecord | None:
    """Get a single prescription by ID from in-memory store."""
    return _prescriptions.get(prescription_id)


def list_prescriptions(
    mpi_id: str,
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> PrescriptionListResult:
    """R42: List prescriptions for a patient with optional status filter.

    Args:
        mpi_id: Patient identifier. If empty string, returns all patients.
        status: Filter by status. Use 'all' to include all statuses.
        limit: Max prescriptions to return.
        offset: Pagination offset.

    Returns:
        PrescriptionListResult with prescriptions and total count.
    """
    # Filter by patient
    if mpi_id:
        candidates = [rx for rx in _prescriptions.values() if rx.mpi_id == mpi_id]
    else:
        candidates = list(_prescriptions.values())

    # Filter by status
    if status and status != "all":
        candidates = [rx for rx in candidates if rx.status == status]

    # Sort by created_at descending (newest first)
    candidates.sort(key=lambda rx: rx.created_at, reverse=True)

    total = len(candidates)

    # Paginate
    paginated = candidates[offset : offset + limit]

    return PrescriptionListResult(prescriptions=paginated, total=total)


def update_prescription(
    prescription_id: int,
    updates: dict[str, Any],
    changed_by: str = "system",
) -> PrescriptionRecord:
    """R43: Update a prescription with state transition support.

    Handles partial updates (only provided fields are changed).
    Supports state transitions via 'status' field in updates dict.
    Validates optimistic locking via 'version' field.

    Args:
        prescription_id: ID of prescription to update.
        updates: Dict of fields to update. May include:
            - dose, unit, route, frequency, notes (value updates)
            - status (state transition)
            - version (optimistic locking)
            - reason (required for discontinued/suspended transitions)
        changed_by: Clinician executing the update.

    Returns:
        Updated PrescriptionRecord.

    Raises:
        ValueError: On validation errors, invalid transitions, or version mismatch.
        KeyError: If prescription_id not found.
    """
    record = _prescriptions.get(prescription_id)
    if record is None:
        raise KeyError(f"Prescrição {prescription_id} não encontrada.")

    # Optimistic locking check
    expected_version = updates.pop("version", None)
    if expected_version is not None and expected_version != record.version:
        raise ValueError(
            f"Conflito de versão: esperado={expected_version}, atual={record.version}. "
            "A prescrição foi modificada por outro usuário. Recarregue e tente novamente."
        )

    # Extract state transition parameters
    new_status = updates.pop("status", None)
    reason = updates.pop("reason", None)
    if new_status is not None:
        _transition_state(record, new_status, reason, changed_by)

    # Apply value updates
    updatable_fields = {"dose", "unit", "route", "frequency", "notes"}
    for field, value in updates.items():
        if field in updatable_fields:
            # Validate if updating critical fields
            if field == "route" and value not in VALID_ROUTES:
                raise ValueError(
                    f"Via '{value}' inválida. Válidas: {', '.join(VALID_ROUTES)}."
                )
            if field == "frequency" and value not in VALID_FREQUENCIES:
                raise ValueError(
                    f"Frequência '{value}' inválida. "
                    f"Válidas: {', '.join(VALID_FREQUENCIES)}."
                )
            setattr(record, field, value)

    record.version += 1
    record.updated_at = _now_iso()

    logger.info(
        "Prescription updated: id=%s, fields=%s, by=%s",
        prescription_id, list(updates.keys()), changed_by,
    )

    return record


def count_active_prescriptions(mpi_id: str) -> int:
    """Count active prescriptions for a patient."""
    return sum(
        1 for rx in _prescriptions.values()
        if rx.mpi_id == mpi_id and rx.status == "active"
    )


def get_alerts_for_prescription(prescription_id: int) -> list[InteractionAlert]:
    """Get all interaction alerts for a prescription."""
    return _alerts.get(prescription_id, [])


def resolve_alert(
    prescription_id: int,
    alert_index: int,
) -> InteractionAlert | None:
    """Mark an interaction alert as resolved."""
    alerts = _alerts.get(prescription_id, [])
    if not alerts or alert_index < 0 or alert_index >= len(alerts):
        return None
    alerts[alert_index].resolved = True
    return alerts[alert_index]


# =============================================================================
# Export
# =============================================================================

__all__ = [
    # Dataclasses
    "PrescriptionRecord",
    "InteractionAlert",
    "PrescriptionResult",
    "PrescriptionListResult",
    # Constants
    "VALID_ROUTES",
    "VALID_STATUSES",
    "VALID_FREQUENCIES",
    "VALID_UNITS",
    "STATE_TRANSITIONS",
    "DRUG_SAFETY",
    "DRUG_INTERACTIONS",
    "RENAL_ADJUSTMENTS",
    # Public API
    "create_prescription",
    "get_prescription",
    "list_prescriptions",
    "update_prescription",
    "count_active_prescriptions",
    "get_alerts_for_prescription",
    "resolve_alert",
    # Dose calculators (public for external use)
    "_calculate_dose_weight_based",
    "_calculate_dose_renal_adjusted",
    # Validation (public for testing)
    "_validate_dose",
    "_check_interactions",
    "_transition_state",
]
