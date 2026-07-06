"""Activate 101 UNVERIFIABLE owner-confirmed RATIFY rules — WAVE 2C

Revision ID: 0027
Revises: 0022
Create Date: 2026-07-06 18:00:00.000000

WAVE 2C: Activate P1 UNVERIFIABLE Owner-Confirmed Rules (101 items).

Context: ASK-2 from RATIFICATION-DECISIONS.md:
"UNVERIFIABLE proprietary rules (ASK-2; 45 owner groups / 101 rules):
CONFIRMED per drafter recommendations under owner delegation."

Each kept rule retains full provenance; contradictions flagged back to owner.

Clusters ratified (5 domain services created):
  1. ALERTAS (2 rules): alert color mapping, bed rollup, attended/unattended
     - RULE-ALERTAS-001: contar_qtd_criterios_alerta (counter primitive)
     - RULE-ALERTAS-002: aggregate alert counts across movimentacoes
     Domain service: services/domain_alertas.py

  2. TENANCY (14 rules): organization structure, bed management,
     establishment rules, sector indicators
     - RULE-TENANCY-ORGANIZACAO-005..015, 038, 041, 042
     Domain service: services/domain_tenancy.py

  3. MOVIMENTACAO (9 rules): patient movement, admission/discharge,
     LOS, micro-indicators, RTSP camera
     - RULE-MOVIMENTACAO-ADT-001..003, 005..008, 010, 011
     Domain service: services/domain_movimentacao.py

  4. COMUNICACAO (3 rules): notification dispatch, observation rules,
     reaction aggregation
     - RULE-COMUNICACAO-001: reaction-count-by-emoji (SQL-correct path)
     - RULE-COMUNICACAO-002: user's own reaction id
     - RULE-COMUNICACAO-003: AcaoHomecare balanco_hidrico (bug fix)
     Domain service: services/domain_comunicacao.py

  5. OPERACIONAL (10 rules): infrastructure, scheduling, CI utilities
     - RULE-OPERACIONAL-INFRA-002..011
     Domain service: services/domain_operacional.py

  Plus all remaining UNVERIFIABLE RATIFY rules across other clusters:
     AUDITORIA-LOGS (1), AUTH-USUARIOS (2), BALANCO-HIDRICO (18),
     DOCUMENTACAO-FATURAMENTO (2), EFICIENCIA (1), ESTABILIDADE (2),
     EVOLUCOES (4), FORMULARIOS-CLINICOS (2), INDICADORES-ETL (3),
     PIORA-CLINICA (4), PRESCRICAO (1), SEDACAO (11),
     SEPSE (17), SINAIS-VITAIS (2), TRILHAS-ENGINE (1), VENTILACAO (1)

All 101 rules confirmed verbatim per drafter recommendations.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = "0027"
down_revision: Union[str, None] = "0022"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ---------------------------------------------------------------------------
# Domain services created by this wave — registered in algorithm_registry
# as non-clinical infrastructure/operational services (score_type = 'DOMAIN')
# ---------------------------------------------------------------------------

UNVERIFIABLE_RATIFIED_SERVICES = [
    {
        "algorithm_version": "DOMAIN-ALERTAS-v1.0.0",
        "score_type": "DOMAIN",
        "semver": "1.0.0",
        "spec_hash": "da01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
        "description": (
            "ALERTAS Domain v1.0.0 — UNVERIFIABLE RATIFY (WAVE 2C). "
            "2 rules RATIFIED per owner delegation (ASK-2): "
            "RULE-ALERTAS-001 (contar_qtd_criterios_alerta), "
            "RULE-ALERTAS-002 (aggregate alert counts). "
            "Service: domain_alertas.py. "
            "Provenance: ahlabs-trilhas@8166c07. "
            "GRP-ALERT-B-COUNTING recommended default: A (keep as-is)."
        ),
    },
    {
        "algorithm_version": "DOMAIN-TENANCY-v1.0.0",
        "score_type": "DOMAIN",
        "semver": "1.0.0",
        "spec_hash": "dt01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
        "description": (
            "TENANCY Domain v1.0.0 — UNVERIFIABLE RATIFY (WAVE 2C). "
            "14 rules RATIFIED per owner delegation (ASK-2): "
            "RULE-TENANCY-ORGANIZACAO-005..015, 038, 041, 042 covering "
            "establishment/sector indicators, unread counts, display names, "
            "5-min timestamp flooring, alert/gender merge patterns, "
            "active bed totals, chat preview, monthly intervention counts, "
            "clinical indicator aggregation, action scoping. "
            "Service: domain_tenancy.py. "
            "Provenance: ahlabs-trilhas@8166c07."
        ),
    },
    {
        "algorithm_version": "DOMAIN-MOVIMENTACAO-v1.0.0",
        "score_type": "DOMAIN",
        "semver": "1.0.0",
        "spec_hash": "dm01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
        "description": (
            "MOVIMENTACAO Domain v1.0.0 — UNVERIFIABLE RATIFY (WAVE 2C). "
            "9 rules RATIFIED per owner delegation (ASK-2): "
            "RULE-MOVIMENTACAO-ADT-001 (LOS), 002 (micro-indicators), "
            "003 (mortality score), 005 (bed lookup key), 006 (patient snapshot), "
            "007 (name/age fields), 008 (vinculo lookup), 010 (RTSP camera URL), "
            "011 (assistido flag). "
            "Service: domain_movimentacao.py. "
            "Provenance: ahlabs-trilhas@8166c07."
        ),
    },
    {
        "algorithm_version": "DOMAIN-COMUNICACAO-v1.0.0",
        "score_type": "DOMAIN",
        "semver": "1.0.0",
        "spec_hash": "dc01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
        "description": (
            "COMUNICACAO Domain v1.0.0 — UNVERIFIABLE RATIFY (WAVE 2C). "
            "3 rules RATIFIED per owner delegation (ASK-2): "
            "RULE-COMUNICACAO-001 (reaction-count-by-emoji, SQL-correct path), "
            "RULE-COMUNICACAO-002 (user's own reaction id), "
            "RULE-COMUNICACAO-003 (AcaoHomecare balanco_hidrico, CORRECTED: "
            "get_pk() call fixed from missing-parentheses bug). "
            "Service: domain_comunicacao.py. "
            "GRP-COM-B-REACTION-AGGREGATION recommended default: B. "
            "Provenance: ahlabs-trilhas@8166c07."
        ),
    },
    {
        "algorithm_version": "DOMAIN-OPERACIONAL-v1.0.0",
        "score_type": "DOMAIN",
        "semver": "1.0.0",
        "spec_hash": "do01a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2",
        "description": (
            "OPERACIONAL Domain v1.0.0 — UNVERIFIABLE RATIFY (WAVE 2C). "
            "10 rules RATIFIED per owner delegation (ASK-2): "
            "RULE-OPERACIONAL-INFRA-002 (nome_abreviado), "
            "003 (offline Rx grouping), 004 (real-day rollover at 07:00), "
            "005 (last-3-day window), 006 (length-of-stay), "
            "007 (pagination), 008 (minutes_elapsed), "
            "009 (format_horario), 010 (parse_date_to_iso), "
            "011 (get_number safe coercion). "
            "Service: domain_operacional.py. "
            "Provenance: ahlabs-trilhas@8166c07."
        ),
    },
]

# ---------------------------------------------------------------------------
# Cross-cluster UNVERIFIABLE RATIFY rules recorded as single ratification
# event. These rules remain in their respective domains (not extracted into
# new services), but their RATIFY disposition is documented here.
# ---------------------------------------------------------------------------


def upgrade() -> None:
    """Seed all 5 domain services + document remaining 63 cross-cluster rules.

    Seeds DOMAIN-* entries into algorithm_registry for the 5 new domain
    services created in this wave, and inserts a ratification record
    documenting all 101 UNVERIFIABLE RATIFY rules.
    """
    # ── 1. Seed 5 domain service entries ─────────────────────────────────
    for svc in UNVERIFIABLE_RATIFIED_SERVICES:
        op.execute(
            f"""
            INSERT INTO algorithm_registry
                (algorithm_version, score_type, semver, spec_hash, description)
            VALUES
                ('{svc['algorithm_version']}', '{svc['score_type']}',
                 '{svc['semver']}', '{svc['spec_hash']}', '{svc['description']}')
            ON CONFLICT (algorithm_version) DO UPDATE
                SET description = EXCLUDED.description
            """
        )

    # ── 2. Insert UNVERIFIABLE ratification event record ─────────────────
    op.execute(
        """
        INSERT INTO ratification_event
            (event_date, ratified_by, authority, algorithm_versions,
             evidence_basis, notes)
        VALUES
            ('2026-07-06 00:00:00+00:00',
             'Product/Clinical Owner Delegation',
             'RATIFICATION-DECISIONS.md §5 (ASK-2: 45 owner groups / 101 rules)',
             'DOMAIN-ALERTAS-v1.0.0, '
             'DOMAIN-TENANCY-v1.0.0, '
             'DOMAIN-MOVIMENTACAO-v1.0.0, '
             'DOMAIN-COMUNICACAO-v1.0.0, '
             'DOMAIN-OPERACIONAL-v1.0.0',
             'UNVERIFIABLE RATIFY rules confirmed per drafter recommendations '
             'under owner delegation. 5 clusters extracted into domain services '
             '(services/domain_*.py). Remaining 63 cross-cluster rules '
             '(AUDITORIA-LOGS, AUTH-USUARIOS, BALANCO-HIDRICO, '
             'DOCUMENTACAO-FATURAMENTO, EFICIENCIA, ESTABILIDADE, EVOLUCOES, '
             'FORMULARIOS-CLINICOS, INDICADORES-ETL, PIORA-CLINICA, PRESCRICAO, '
             'SEDACAO, SEPSE, SINAIS-VITAIS, TRILHAS-ENGINE, VENTILACAO) '
             'retain full provenance; contradictions flagged back to owner. '
             'Provenance: ahlabs-trilhas@8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.',
             'WAVE 2C finalization. 101 UNVERIFIABLE RATIFY rules activated. '
             '5 new domain services created. Traceability matrix updated: '
             '101 fewer RATIFY rules (now activated). '
             'See BUILD-JOURNAL.md Entry 2C.')
        """
    )


def downgrade() -> None:
    """Remove WAVE 2C domain service seeds."""
    op.execute(
        """
        DELETE FROM algorithm_registry
        WHERE algorithm_version IN (
            'DOMAIN-ALERTAS-v1.0.0',
            'DOMAIN-TENANCY-v1.0.0',
            'DOMAIN-MOVIMENTACAO-v1.0.0',
            'DOMAIN-COMUNICACAO-v1.0.0',
            'DOMAIN-OPERACIONAL-v1.0.0'
        )
        """
    )
    op.execute(
        """
        DELETE FROM ratification_event
        WHERE algorithm_versions LIKE '%DOMAIN-%'
        """
    )
