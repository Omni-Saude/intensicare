"""Gold Writer — write-back unidirecional para as tabelas de gold layer.

Garante:
- PHI provably absent from write-back payload (REQ-INV-4-S3)
- algorithm_version presente em todo fact_patient_score
- definition_version presente em todo fact_alert
- Idempotente: ON CONFLICT DO NOTHING
- One-directional: writer nunca lê de volta para scoring
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import insert as pg_insert

from intensicare.services.gold_schema import FactAlert, FactPatientScore

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from intensicare.models.alert import Alert
    from intensicare.models.clinical_score import ClinicalScore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PHI field denylist — campos que NUNCA podem aparecer no payload de write-back
# ---------------------------------------------------------------------------

PHI_DENYLIST: frozenset[str] = frozenset(
    {
        "patient_name",
        "full_name",
        "first_name",
        "last_name",
        "date_of_birth",
        "dob",
        "birth_date",
        "ssn",
        "cpf",
        "national_id",
        "address",
        "phone",
        "email",
        "medical_record_number",
        "mrn",
    }
)


def _assert_phi_absent(payload: dict[str, object]) -> None:
    """Garante que nenhum campo PHI está presente no payload.

    Levanta ValueError se qualquer chave no PHI_DENYLIST for encontrada.
    """
    found = PHI_DENYLIST & set(payload.keys())
    if found:
        raise ValueError(
            f"PHI fields found in write-back payload: {sorted(found)}. "
            f"REQ-INV-4-S3 violation."
        )


# ---------------------------------------------------------------------------
# GoldWriter
# ---------------------------------------------------------------------------


class GoldWriter:
    """Serviço de write-back para as tabelas gold (fact_patient_score, fact_alert).

    Fluxo unidirecional: os dados são escritos nas tabelas fact_* e nunca
    lidos de volta para scoring. As tabelas fact_* são exclusivamente para
    analytics/auditoria.

    Idempotência: usa INSERT ... ON CONFLICT DO NOTHING baseado em
    source_score_id (fact_patient_score) e source_alert_id (fact_alert).
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # write_scores
    # ------------------------------------------------------------------

    async def write_scores(self, scores: list[ClinicalScore]) -> int:
        """Escreve scores clínicos na tabela fact_patient_score.

        Cada registro carrega algorithm_version do ClinicalScore de origem.
        PHI é validada como ausente antes do INSERT (REQ-INV-4-S3).
        Idempotente via ON CONFLICT (source_score_id) DO NOTHING.

        Returns:
            Número de linhas efetivamente inseridas (exclui conflitos).
        """
        if not scores:
            return 0

        rows: list[dict[str, object]] = []
        for score in scores:
            payload = {
                "mpi_id": score.mpi_id,
                "score_type": score.score_type,
                "score_value": score.score_value,
                "algorithm_version": score.algorithm_version,
                "calculated_at": score.calculated_at,
                "source_score_id": score.id,
            }
            _assert_phi_absent(payload)
            rows.append(payload)

        stmt = (
            pg_insert(FactPatientScore)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["source_score_id"])
        )
        result = await self.db.execute(stmt)
        inserted = result.rowcount  # type: ignore[union-attr]
        logger.info(
            "GoldWriter: wrote %d scores to fact_patient_score (%d skipped)",
            inserted,
            len(scores) - (inserted or 0),
        )
        return inserted or 0

    # ------------------------------------------------------------------
    # write_alerts
    # ------------------------------------------------------------------

    async def write_alerts(self, alerts: list[Alert]) -> int:
        """Escreve alertas na tabela fact_alert.

        Cada registro carrega definition_version_id do Alert de origem
        (FK para alert_definition_version).
        Se um Alert não tiver definition_version_id, usa fallback "unknown".
        PHI é validada como ausente antes do INSERT (REQ-INV-4-S3).
        Idempotente via ON CONFLICT (source_alert_id) DO NOTHING.

        Returns:
            Número de linhas efetivamente inseridas (exclui conflitos).
        """
        if not alerts:
            return 0

        rows: list[dict[str, object]] = []
        for alert in alerts:
            payload = {
                "mpi_id": alert.mpi_id,
                "severity": alert.severity,
                "status": alert.status,
                "title": alert.title,
                "definition_version": alert.definition_version_id or "unknown",
                "created_at": alert.created_at,
                "source_alert_id": alert.id,
            }
            _assert_phi_absent(payload)
            rows.append(payload)

        stmt = (
            pg_insert(FactAlert)
            .values(rows)
            .on_conflict_do_nothing(index_elements=["source_alert_id"])
        )
        result = await self.db.execute(stmt)
        inserted = result.rowcount  # type: ignore[union-attr]
        logger.info(
            "GoldWriter: wrote %d alerts to fact_alert (%d skipped)",
            inserted,
            len(alerts) - (inserted or 0),
        )
        return inserted or 0
