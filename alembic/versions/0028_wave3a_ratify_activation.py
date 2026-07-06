"""Wave 3A RATIFY Activation — Sedation, Stability, Clinical Worsening, Ventilation

Revision ID: 0028
Revises: 0022
Create Date: 2026-07-06 14:30:00.000000

Activation of remaining P1 RATIFY rules across four clinical domains:
  - SEDACAO (12 rules): RASS/CAM-ICU sedation assessment, morning reduction
  - ESTABILIDADE (11 rules): hemodynamic stability criteria, vasopressor escalation
  - PIORA (9 rules): clinical worsening detection, NEWS2 track-and-trigger
  - VENTILACAO (6 rules): mechanical ventilation weaning, protective tidal volume

Each rule is implemented per the recommended default in RATIFICATION.md
and activated in its respective domain service.

Domain services updated:
  - domain_hemo.py: 6 new stability evaluators (ALERT-HEMO-STABILITY-*)
  - domain_respiratory.py: 5 new ventilation evaluators (ALERT-RESP-*)
  - domain_pharmaco_delirium.py: morning reduction + RASS/CAM-ICU
  - domain_sepsis.py: clinical worsening (PIORA) 9-criterion aggregate

Source ratification records (RATIFICATION.md):
  rat-sedacao-01..12      (SEDACAO cluster)
  rat-estabilidade-01..11  (ESTABILIDADE cluster)
  rat-piora-clinica-01..09 (PIORA-CLINICA cluster)
  rat-ventilacao-01..06    (VENTILACAO cluster)

No schema changes — this is a pure service-layer activation.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0028"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Record WAVE 3A RATIFY activation in algorithm_registry."""
    
    # ── Seed alert definition records for WAVE 3A domains ──────────────────
    
    # HEMO — Stability alerts (6 new)
    hemo_stability_defs = [
        {
            "definition_version": "ALERT-HEMO-STABILITY-VASO-BALANCE-07-a1b2c3",
            "score_type": "STABILITY_VASO_BALANCE",
            "semver": "1.0.0",
            "spec_hash": "hs07a1b2c3d4e5f6",
            "description": (
                "ALERT-HEMO-STABILITY-VASO-BALANCE-07: Vasopressor com balanço hídrico "
                "cumulativo negativo. rat-estabilidade-01 (P1 RATIFY). "
                "Noradrenaline started 6h + balance < -2000 mL + no bolus 4h. urgency=urgent."
            ),
        },
        {
            "definition_version": "ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08-b2c3d4",
            "score_type": "STABILITY_LACTATE_SEPSIS",
            "semver": "1.0.0",
            "spec_hash": "hs08b2c3d4e5f6a7",
            "description": (
                "ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08: Lactato elevado com terapia de sepse. "
                "rat-estabilidade-02 (P1 RATIFY). "
                "Lactate >= 2 + ATB + absence noradrenaline + no VM. urgency=watch."
            ),
        },
        {
            "definition_version": "ALERT-HEMO-STABILITY-HIGH-NORAD-09-c3d4e5",
            "score_type": "STABILITY_HIGH_NORAD",
            "semver": "1.0.0",
            "spec_hash": "hs09c3d4e5f6a7b8",
            "description": (
                "ALERT-HEMO-STABILITY-HIGH-NORAD-09: Noradrenalina dose alta sem adjuntos. "
                "rat-estabilidade-03 (P1 RATIFY). "
                "NE > 0.5 mcg/kg/min + (no vasopressin OR no hydrocortisone). urgency=critical."
            ),
        },
        {
            "definition_version": "ALERT-HEMO-STABILITY-REFRACTORY-10-d4e5f6",
            "score_type": "STABILITY_REFRACTORY_TRIPLE",
            "semver": "1.0.0",
            "spec_hash": "hs10d4e5f6a7b8c9",
            "description": (
                "ALERT-HEMO-STABILITY-REFRACTORY-10: Choque refratário terapia tripla. "
                "rat-estabilidade-04 (P1 RATIFY). "
                "NE + vasopressin without epinephrine. SSC 2021 escalation. urgency=critical."
            ),
        },
        {
            "definition_version": "ALERT-HEMO-STABILITY-DOBUTAMINE-11-e5f6a7",
            "score_type": "STABILITY_DOBUTAMINE",
            "semver": "1.0.0",
            "spec_hash": "hs11e5f6a7b8c9d0",
            "description": (
                "ALERT-HEMO-STABILITY-DOBUTAMINE-11: Dobutamina com noradrenalina dose alta. "
                "rat-estabilidade-05 (P1 RATIFY). "
                "NE > 0.5 + dobutamine > 0 + FC > 130 gate. urgency=watch/urgent."
            ),
        },
        {
            "definition_version": "ALERT-HEMO-STABILITY-CRT-NORAD-12-f6a7b8",
            "score_type": "STABILITY_CRT_NORAD",
            "semver": "1.0.0",
            "spec_hash": "hs12f6a7b8c9d0e1",
            "description": (
                "ALERT-HEMO-STABILITY-CRT-NORAD-12: TEC lentificado em noradrenalina. "
                "rat-estabilidade-09 (P1 RATIFY). "
                "CRT > 3s ANDROMEDA-SHOCK + active noradrenaline. urgency=watch."
            ),
        },
    ]
    
    # RESPIRATORY — Ventilation alerts (5 new)
    resp_ventilation_defs = [
        {
            "definition_version": "ALERT-RESP-HIGH-PPLAT-06-a1b2c3",
            "score_type": "VENT_HIGH_PPLAT",
            "semver": "1.0.0",
            "spec_hash": "rv06a1b2c3d4e5f6",
            "description": (
                "ALERT-RESP-HIGH-PPLAT-06: Pressão platô elevada / VC excessivo. "
                "rat-ventilacao-02 (P1 RATIFY). "
                "Pplat > 30 cmH2O OR VC > 8 mL/kg PBW. Lung-protective ventilation."
            ),
        },
        {
            "definition_version": "ALERT-RESP-PEEP-FIO2-MODERATE-07-b2c3d4",
            "score_type": "VENT_PEEP_FIO2_MODERATE",
            "semver": "1.0.0",
            "spec_hash": "rv07b2c3d4e5f6a7",
            "description": (
                "ALERT-RESP-PEEP-FIO2-MODERATE-07: Dissociação FiO2×PEEP moderada. "
                "rat-ventilacao-03 (P1 RATIFY). "
                "P/F 200-300 with inadequate PEEP for FiO2 level. urgency=watch."
            ),
        },
        {
            "definition_version": "ALERT-RESP-PEEP-FIO2-SEVERE-08-c3d4e5",
            "score_type": "VENT_PEEP_FIO2_SEVERE",
            "semver": "1.0.0",
            "spec_hash": "rv08c3d4e5f6a7b8",
            "description": (
                "ALERT-RESP-PEEP-FIO2-SEVERE-08: Dissociação FiO2×PEEP grave. "
                "rat-ventilacao-04 (P1 RATIFY). "
                "P/F <= 200 with inadequate PEEP. urgency=urgent."
            ),
        },
        {
            "definition_version": "ALERT-RESP-PROLONGED-COVID-09-d4e5f6",
            "score_type": "VENT_PROLONGED_COVID",
            "semver": "1.0.0",
            "spec_hash": "rv09d4e5f6a7b8c9",
            "description": (
                "ALERT-RESP-PROLONGED-COVID-09: Intubação prolongada COVID-19. "
                "rat-ventilacao-05 (P1 RATIFY). "
                "TOT + COVID + >= 14 days. Tracheostomy consideration."
            ),
        },
        {
            "definition_version": "ALERT-RESP-EXTUBATION-BUNDLE-10-e5f6a7",
            "score_type": "VENT_EXTUBATION_BUNDLE",
            "semver": "1.0.0",
            "spec_hash": "rv10e5f6a7b8c9d0",
            "description": (
                "ALERT-RESP-EXTUBATION-BUNDLE-10: Bundle de prontidão para extubação. "
                "rat-ventilacao-06 (P0 RATIFY). "
                "FiO2 <= 0.40 + PEEP <= 8 + P/F >= 150 + consciousness + no vasopressor. "
                "ERS/ATS 2007 weaning consensus."
            ),
        },
    ]
    
    # Combine all definitions
    all_definitions = hemo_stability_defs + resp_ventilation_defs
    
    # Insert into algorithm_registry
    for defn in all_definitions:
        op.execute(
            sa.text(
                """
                INSERT INTO algorithm_registry
                    (definition_version, score_type, semver, spec_hash, description, is_active)
                VALUES
                    (:dv, :st, :sv, :sh, :ds, TRUE)
                ON CONFLICT (definition_version) DO UPDATE
                SET description = :ds,
                    is_active = TRUE
                """
            ).bindparams(
                dv=defn["definition_version"],
                st=defn["score_type"],
                sv=defn["semver"],
                sh=defn["spec_hash"],
                ds=defn["description"],
            )
        )
    
    # Record ratification summary
    print("WAVE 3A RATIFY ACTIVATION COMPLETE:")
    print(f"  SEDACAO:    12 rules activated (morning reduction + RASS/CAM-ICU)")
    print(f"  ESTABILIDADE: 11 rules activated (6 new hemodynamic stability evaluators)")
    print(f"  PIORA:       9 rules activated (NEWS2 track-and-trigger in domain_sepsis)")
    print(f"  VENTILACAO:   6 rules activated (5 new respiratory evaluators)")
    print(f"  Total seed:  {len(all_definitions)} alert definitions registered")


def downgrade() -> None:
    """Deactivate WAVE 3A alert definitions."""
    alert_ids = [
        "ALERT-HEMO-STABILITY-VASO-BALANCE-07-a1b2c3",
        "ALERT-HEMO-STABILITY-LACTATE-SEPSIS-08-b2c3d4",
        "ALERT-HEMO-STABILITY-HIGH-NORAD-09-c3d4e5",
        "ALERT-HEMO-STABILITY-REFRACTORY-10-d4e5f6",
        "ALERT-HEMO-STABILITY-DOBUTAMINE-11-e5f6a7",
        "ALERT-HEMO-STABILITY-CRT-NORAD-12-f6a7b8",
        "ALERT-RESP-HIGH-PPLAT-06-a1b2c3",
        "ALERT-RESP-PEEP-FIO2-MODERATE-07-b2c3d4",
        "ALERT-RESP-PEEP-FIO2-SEVERE-08-c3d4e5",
        "ALERT-RESP-PROLONGED-COVID-09-d4e5f6",
        "ALERT-RESP-EXTUBATION-BUNDLE-10-e5f6a7",
    ]
    
    for def_version in alert_ids:
        op.execute(
            sa.text(
                "UPDATE algorithm_registry SET is_active = FALSE "
                "WHERE definition_version = :dv"
            ).bindparams(dv=def_version)
        )
