"""Drug interaction knowledge base and detection logic.

Extracted from domain_prescricao.py as part of F-CODE-004 component refactoring.

Contains:
- DRUG_INTERACTIONS: pairwise drug interaction knowledge base (local ANVISA subset)
- DRUG_CLASSES: therapeutic class groupings
- DRUG_ALLERGY_GROUPS: cross-reactivity allergy groups
- _check_interactions: drug-drug, drug-allergy, duplicate detection (R17-R26)

ANVISA Integration (H5):
    This module currently uses a hardcoded local knowledge base. To integrate
    with the ANVISA Bulário Eletrônico API, import the facade from
    ``intensicare.services.anvisa_drug_database`` and call
    ``get_anvisa_database()`` to obtain the configured backend. The factory
    returns ``LocalDrugDatabase`` (in-memory stub) by default and
    ``ANVISADrugAPIClient`` (real HTTPS client) when ANVISA_API_KEY is set.

    See ``_check_interactions_via_anvisa()`` below for the integration point.
    See ``anvisa_drug_database.py`` for the full stub implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from intensicare.services.domain_prescricao import PrescriptionRecord

logger = logging.getLogger(__name__)


# =============================================================================
# ANVISA fallback import (H5)
# =============================================================================
#
# When ANVISA API credentials are provisioned, uncomment the import below
# and call _check_interactions_via_anvisa() instead of using the local
# DRUG_INTERACTIONS dict.
#
# from intensicare.services.anvisa_drug_database import (
#     ANVISAInteractionResult,
#     get_anvisa_database,
# )


@dataclass
class InteractionAlert:
    """Drug interaction alert matching OpenAPI InteracaoAlerta schema."""

    id: int | None = None
    severity: str = "moderate"
    interaction_type: str = "drug-drug"
    description: str = ""
    resolved: bool = False


# =============================================================================
# Drug interaction knowledge base (ANVISA/DDI)
# =============================================================================

# (drug_a, drug_b) -> (severity, interaction_type, description)
DRUG_INTERACTIONS: dict[tuple[str, str], tuple[str, str, str]] = {
    # Drug-Drug interactions
    ("vancomicina", "amiodarona"): (
        "severe",
        "drug-drug",
        "Risco aumentado de prolongamento QT e Torsades de Pointes com vancomicina + amiodarona.",
    ),
    ("amiodarona", "vancomicina"): (
        "severe",
        "drug-drug",
        "Risco aumentado de prolongamento QT e Torsades de Pointes com vancomicina + amiodarona.",
    ),
    ("midazolam", "fentanil"): (
        "severe",
        "drug-drug",
        "Depressão respiratória aditiva — risco de apneia com midazolam + fentanil. Monitorar SpO2 continuamente.",
    ),
    ("fentanil", "midazolam"): (
        "severe",
        "drug-drug",
        "Depressão respiratória aditiva — risco de apneia com midazolam + fentanil. Monitorar SpO2 continuamente.",
    ),
    ("propofol", "midazolam"): (
        "severe",
        "drug-drug",
        "Sedação profunda excessiva com propofol + midazolam. Risco de hipotensão e bradicardia.",
    ),
    ("midazolam", "propofol"): (
        "severe",
        "drug-drug",
        "Sedação profunda excessiva com propofol + midazolam. Risco de hipotensão e bradicardia.",
    ),
    ("heparina_nao_fracionada", "enoxaparina"): (
        "contraindicated",
        "drug-drug",
        "Contraindicação absoluta: heparina não fracionada + enoxaparina — risco de sangramento grave.",
    ),
    ("enoxaparina", "heparina_nao_fracionada"): (
        "contraindicated",
        "drug-drug",
        "Contraindicação absoluta: heparina não fracionada + enoxaparina — risco de sangramento grave.",
    ),
    ("morfina", "midazolam"): (
        "severe",
        "drug-drug",
        "Depressão respiratória e sedação excessiva com morfina + midazolam. Risco de PCR.",
    ),
    ("midazolam", "morfina"): (
        "severe",
        "drug-drug",
        "Depressão respiratória e sedação excessiva com morfina + midazolam. Risco de PCR.",
    ),
    ("morfina", "fentanil"): (
        "moderate",
        "drug-drug",
        "Efeito opioide aditivo — considerar redução de dose de ambos. Aumenta risco de íleo paralítico.",
    ),
    ("fentanil", "morfina"): (
        "moderate",
        "drug-drug",
        "Efeito opioide aditivo — considerar redução de dose de ambos. Aumenta risco de íleo paralítico.",
    ),
    ("noradrenalina", "dobutamina"): (
        "moderate",
        "drug-drug",
        "Incompatibilidade física na mesma via — usar acessos venosos distintos. Risco de cristalização.",
    ),
    ("dobutamina", "noradrenalina"): (
        "moderate",
        "drug-drug",
        "Incompatibilidade física na mesma via — usar acessos venosos distintos. Risco de cristalização.",
    ),
    ("amiodarona", "heparina_nao_fracionada"): (
        "moderate",
        "drug-drug",
        "Amiodarona potencializa efeito anticoagulante da heparina. Monitorar PTTa/TAP a cada 6h.",
    ),
    ("heparina_nao_fracionada", "amiodarona"): (
        "moderate",
        "drug-drug",
        "Amiodarona potencializa efeito anticoagulante da heparina. Monitorar PTTa/TAP a cada 6h.",
    ),
    ("meropenem", "vancomicina"): (
        "minor",
        "drug-drug",
        "Sinergismo antimicrobiano esperado para cobertura ampla de gram-positivos e gram-negativos.",
    ),
    ("vancomicina", "meropenem"): (
        "minor",
        "drug-drug",
        "Sinergismo antimicrobiano esperado para cobertura ampla de gram-positivos e gram-negativos.",
    ),
    ("cloreto_de_potassio", "insulina_regular"): (
        "moderate",
        "drug-drug",
        "Insulina + K+ IV: risco de hipocalemia rebote se infusão rápida. Monitorar K+ sérico antes e após.",
    ),
    ("insulina_regular", "cloreto_de_potassio"): (
        "moderate",
        "drug-drug",
        "Insulina + K+ IV: risco de hipocalemia rebote se infusão rápida. Monitorar K+ sérico antes e após.",
    ),
    ("ceftriaxona", "cloreto_de_sodio_3%"): (
        "contraindicated",
        "drug-drug",
        "Ceftriaxona + soluções contendo cálcio (incluindo NaCl 3%) — risco de precipitação e embolia pulmonar.",
    ),
    ("cloreto_de_sodio_3%", "ceftriaxona"): (
        "contraindicated",
        "drug-drug",
        "Ceftriaxona + soluções contendo cálcio (incluindo NaCl 3%) — risco de precipitação e embolia pulmonar.",
    ),
    ("propofol", "fentanil"): (
        "moderate",
        "drug-drug",
        "Potencialização de sedação e hipotensão. Reduzir dose de propofol em 20-30% se coadministrado com fentanil.",
    ),
    ("fentanil", "propofol"): (
        "moderate",
        "drug-drug",
        "Potencialização de sedação e hipotensão. Reduzir dose de propofol em 20-30% se coadministrado com fentanil.",
    ),
    # Duplicate class interactions
    ("piperacilina_tazobactam", "meropenem"): (
        "moderate",
        "duplicate",
        "Duplicação de cobertura beta-lactâmica (ambos carbapenêmicos/ureidopenicilinas). Reavaliar necessidade.",
    ),
    ("meropenem", "piperacilina_tazobactam"): (
        "moderate",
        "duplicate",
        "Duplicação de cobertura beta-lactâmica (ambos carbapenêmicos/ureidopenicilinas). Reavaliar necessidade.",
    ),
    ("ceftriaxona", "meropenem"): (
        "moderate",
        "duplicate",
        "Duplicação de cobertura beta-lactâmica de amplo espectro. Restringir a um agente se cultura dirigida disponível.",
    ),
    ("meropenem", "ceftriaxona"): (
        "moderate",
        "duplicate",
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
# Drug interaction detection (R17-R26)
# =============================================================================


def _check_interactions(
    drug: str,
    mpi_id: str,
    active_prescriptions: list["PrescriptionRecord"],
) -> list[InteractionAlert]:
    """R17-R26: Check drug-drug and duplicate interactions against local ANVISA base.

    Scans all active prescriptions for the patient and checks each pair
    against the DRUG_INTERACTIONS knowledge base.

    Args:
        drug: New drug name being added.
        mpi_id: Patient identifier.
        active_prescriptions: List of active PrescriptionRecord objects for the patient.

    Returns:
        List of InteractionAlert objects.
    """
    alerts: list[InteractionAlert] = []
    drug_key = drug.lower().replace(" ", "_")

    # Filter to active prescriptions for this patient
    active_rx = [rx for rx in active_prescriptions if rx.mpi_id == mpi_id and rx.status == "active"]

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
    opioid_count = sum(1 for d in seen_drugs if DRUG_CLASSES.get(d) == "opioide")
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
    sedative_count = sum(1 for d in seen_drugs if DRUG_CLASSES.get(d) in sedative_classes)
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
        1 for d in seen_drugs if DRUG_CLASSES.get(d) in ("anticoagulante", "anticoagulante_hbpm")
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
# ANVISA-backed interaction checker (H5 — integration point)
# =============================================================================
#
# This function demonstrates how the local DRUG_INTERACTIONS dict would be
# replaced by a call to the ANVISA API when credentials are provisioned.
#
# To activate:
#   1. Set environment variables:
#        export ANVISA_ENABLED=true
#        export ANVISA_API_KEY="your-api-key"
#   2. Uncomment the ANVISA imports at the top of this file.
#   3. Replace calls to _check_interactions() with
#      _check_interactions_via_anvisa() in domain_prescricao.py.


async def _check_interactions_via_anvisa(
    drug: str,
    mpi_id: str,
    active_prescriptions: list["PrescriptionRecord"],
) -> list[InteractionAlert]:
    """Check drug interactions using ANVISA API (when available).

    This function mirrors ``_check_interactions()`` but delegates pairwise
    interaction lookups to the ANVISA Bulário Eletrônico API instead of
    the hardcoded ``DRUG_INTERACTIONS`` dict.

    The ANVISA API is expected to support:
        POST /v2/interactions/check        — pairwise check
        POST /v2/interactions/check-bulk   — bulk pairwise check

    When ANVISA is unavailable, this falls back to the local knowledge base.

    Args:
        drug: New drug name being added.
        mpi_id: Patient identifier.
        active_prescriptions: List of active PrescriptionRecord objects.

    Returns:
        List of InteractionAlert objects.
    """
    # ── ANVISA path (future) ──────────────────────────────────────────────
    # from intensicare.services.anvisa_drug_database import (
    #     ANVISAInteractionResult,
    #     get_anvisa_database,
    # )
    #
    # anvisa_db = get_anvisa_database()
    # if await anvisa_db.is_available():
    #     alerts: list[InteractionAlert] = []
    #     for rx in active_prescriptions:
    #         if rx.mpi_id != mpi_id or rx.status != "active":
    #             continue
    #         result = await anvisa_db.check_interaction(drug, rx.drug)
    #         if result:
    #             alerts.append(InteractionAlert(
    #                 severity=result.severity,
    #                 interaction_type="drug-drug",
    #                 description=(
    #                     f"[{result.drug_a} × {result.drug_b}] "
    #                     f"{result.description}"
    #                 ),
    #                 resolved=False,
    #             ))
    #     return alerts
    # ────────────────────────────────────────────────────────────────────────

    # Fallback: use local knowledge base (current behavior)
    logger.info(
        "ANVISA API not available — falling back to local interaction database "
        "for drug=%s patient=%s",
        drug,
        mpi_id,
    )
    return _check_interactions(drug, mpi_id, active_prescriptions)
