"""Alternativa-B trigger instrumentation — monitora latência p95 e dispara recomendação ALT-B.

Implementa o trigger quantificado em system-architecture.md §6 T1:
- Monitora latência p95 end-to-end bedside→alert via métricas OTEL/AMP
- Janela rolante de 7 dias (rolling window)
- Se p95 > 30s por 7 dias consecutivos com MLLP saudável → ACTIVATE Alternativa B
- Se MLLP indisponível > 0.5% das bed-hours em 7 dias → ACTIVATE Alternativa B
- Journal da recomendação com evidências no BUILD-JOURNAL.md

References:
    - system-architecture.md §6 — Alternativa-B decision table (T1)
    - ADR-001 (ADR001-F-08) — dedicated MSK topic mechanism
    - _work/budgets/latency.yaml — canonical latency budget
    - observability-slo.md §3-4 — OTEL metrics instrumentation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path


class AltBDecision(str, Enum):
    """Decisão do trigger Alternativa-B conforme system-architecture.md §6.1."""

    DEFER = "DEFER"                # Dados insuficientes (menos de 7 dias)
    ACTIVATE = "ACTIVATE"          # Condição T1(a) ou T1(b) satisfeita
    ESCALATE = "ESCALATE"          # Escalar para AMH platform team (T3/T4)
    DO_NOT_ACTIVATE = "DO_NOT_ACTIVATE"  # Condições não satisfeitas (T6)


@dataclass
class LatencyObservation:
    """Uma observação diária de latência p95.

    Attributes:
        timestamp: Momento da coleta (UTC).
        p95_seconds: Latência p95 bedside→alert em segundos.
        mllp_healthy: Se o feed MLLP está operacional e saudável.
        mllp_unavailable_pct: Percentual de bed-hours indisponíveis no período.
    """

    timestamp: datetime
    p95_seconds: float
    mllp_healthy: bool = True
    mllp_unavailable_pct: float = 0.0


@dataclass
class AltBTriggerState:
    """Estado interno do trigger Alternativa-B.

    Attributes:
        observations: Série temporal de observações diárias.
        window_days: Tamanho da janela rolante em dias (default: 7).
        threshold_seconds: Limiar de latência p95 em segundos (default: 30).
        mllp_unavailability_threshold_pct: Limiar de indisponibilidade MLLP (default: 0.5%).
        triggered: Se o trigger já foi disparado.
        last_evaluation: Timestamp da última avaliação.
        decision: Última decisão calculada.
    """

    observations: list[LatencyObservation] = field(default_factory=list)
    window_days: int = 7
    threshold_seconds: float = 30.0
    mllp_unavailability_threshold_pct: float = 0.5
    triggered: bool = False
    last_evaluation: datetime | None = None
    decision: AltBDecision | None = None


class AltBTrigger:
    """Monitor de latência para o trigger Alternativa-B.

    Implementa a tabela de decisão §6.1 do system-architecture.md:

    **T1(a)** — Vitals end-to-end bedside→alert p95 > 30s (VIS-C-09)
    sustentado por 7 dias consecutivos com feed MLLP saudável.

    **T1(b)** — Feed MLLP indisponível > 0.5% das monitored bed-hours
    na mesma janela de 7 dias (espelha ADR001-C-10, 99.5% availability floor).

    Ambos resultam em **ACTIVATE Alternativa B** — provisionar um tópico
    MSK dedicado (ADR001-F-08) para o feed operacional de vitals.
    """

    def __init__(
        self,
        window_days: int = 7,
        threshold_seconds: float = 30.0,
        mllp_unavailability_threshold_pct: float = 0.5,
        journal_path: str | Path | None = None,
    ) -> None:
        self.state = AltBTriggerState(
            window_days=window_days,
            threshold_seconds=threshold_seconds,
            mllp_unavailability_threshold_pct=mllp_unavailability_threshold_pct,
        )
        self._journal_path = Path(journal_path) if journal_path else None

    # ------------------------------------------------------------------
    # Ingestão de observações
    # ------------------------------------------------------------------

    def add_observation(
        self,
        p95_seconds: float,
        mllp_healthy: bool = True,
        mllp_unavailable_pct: float = 0.0,
        timestamp: datetime | None = None,
    ) -> None:
        """Registra uma observação diária de latência.

        Args:
            p95_seconds: Latência p95 bedside→alert em segundos.
            mllp_healthy: Se o feed MLLP está saudável.
            mllp_unavailable_pct: Percentual de bed-hours indisponíveis.
            timestamp: Timestamp da observação (default: now UTC).
        """
        obs = LatencyObservation(
            timestamp=timestamp or datetime.now(timezone.utc),
            p95_seconds=p95_seconds,
            mllp_healthy=mllp_healthy,
            mllp_unavailable_pct=mllp_unavailable_pct,
        )
        self.state.observations.append(obs)
        self._prune_old_observations()

    # ------------------------------------------------------------------
    # Janela rolante
    # ------------------------------------------------------------------

    def _prune_old_observations(self) -> None:
        """Remove observações fora da janela rolante de window_days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.state.window_days)
        self.state.observations = [
            obs
            for obs in self.state.observations
            if obs.timestamp > cutoff
        ]

    @property
    def window_observations(self) -> list[LatencyObservation]:
        """Observações dentro da janela rolante atual."""
        self._prune_old_observations()
        return self.state.observations

    # ------------------------------------------------------------------
    # Avaliação do trigger (T1)
    # ------------------------------------------------------------------

    def evaluate(self) -> AltBDecision:
        """Avalia se as condições T1(a) ou T1(b) estão satisfeitas.

        Returns:
            AltBDecision.ACTIVATE se trigger disparou,
            AltBDecision.DEFER se dados insuficientes,
            AltBDecision.DO_NOT_ACTIVATE caso contrário.
        """
        self._prune_old_observations()
        self.state.last_evaluation = datetime.now(timezone.utc)

        recent = self.state.observations[-self.state.window_days :]

        # ── Dados insuficientes ──────────────────────────────────
        if len(recent) < self.state.window_days:
            self.state.decision = AltBDecision.DEFER
            return AltBDecision.DEFER

        # ── T1(b): MLLP feed indisponível > 0.5% das bed-hours ──
        mllp_breach = any(
            obs.mllp_unavailable_pct > self.state.mllp_unavailability_threshold_pct
            for obs in recent
        )
        if mllp_breach:
            self.state.triggered = True
            self.state.decision = AltBDecision.ACTIVATE
            return AltBDecision.ACTIVATE

        # ── T1(a): p95 > 30s por 7 dias consecutivos com MLLP saudável ──
        all_above_threshold = all(
            obs.p95_seconds > self.state.threshold_seconds for obs in recent
        )
        all_mllp_healthy = all(obs.mllp_healthy for obs in recent)

        if all_above_threshold and all_mllp_healthy:
            self.state.triggered = True
            self.state.decision = AltBDecision.ACTIVATE
            return AltBDecision.ACTIVATE

        # ── Condições não satisfeitas ────────────────────────────
        self.state.decision = AltBDecision.DO_NOT_ACTIVATE
        return AltBDecision.DO_NOT_ACTIVATE

    # ------------------------------------------------------------------
    # Geração de recomendação com evidências
    # ------------------------------------------------------------------

    def build_recommendation(self) -> str:
        """Constrói o texto de recomendação com evidências para o BUILD-JOURNAL.

        Returns:
            Texto formatado em Markdown com decisão, evidências e ações recomendadas.
        """
        decision = self.evaluate()

        if decision != AltBDecision.ACTIVATE:
            return (
                f"// ALT-B evaluation at "
                f"{datetime.now(timezone.utc).isoformat()}: "
                f"{decision.value} — conditions not met.\n"
            )

        # ── Coleta de evidências ─────────────────────────────────
        recent = self.state.observations[-self.state.window_days :]
        avg_p95 = sum(o.p95_seconds for o in recent) / len(recent)
        max_p95 = max(o.p95_seconds for o in recent)
        min_p95 = min(o.p95_seconds for o in recent)
        days_above = sum(
            1 for o in recent if o.p95_seconds > self.state.threshold_seconds
        )

        mllp_breach = any(
            o.mllp_unavailable_pct > self.state.mllp_unavailability_threshold_pct
            for o in recent
        )
        max_mllp_unavailability = max(o.mllp_unavailable_pct for o in recent)

        trigger_condition = (
            "T1(b) — MLLP feed unavailable > 0.5% bed-hours"
            if mllp_breach
            else "T1(a) — p95 bedside→alert > 30s por 7 dias consecutivos com MLLP saudável"
        )

        lines = [
            "## WO-040: Alternativa-B Trigger — RECOMENDAÇÃO DE ATIVAÇÃO",
            "",
            f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}",
            f"**Decisão:** ACTIVATE Alternativa B",
            f"**Gatilho:** system-architecture.md §6 {trigger_condition}",
            f"**Estado MLLP:** {'DEGRADADO' if mllp_breach else 'SAUDÁVEL'}",
            "",
            "### Evidências — Janela Rolante de 7 Dias",
            "",
            "| Métrica | Valor | Threshold | Status |",
            "|---|---|---|---|",
            f"| p95 médio (bedside→alert) | {avg_p95:.1f}s | {self.state.threshold_seconds}s | {'🔴 BREACH' if avg_p95 > self.state.threshold_seconds else '🟢 OK'} |",
            f"| p95 máximo | {max_p95:.1f}s | {self.state.threshold_seconds}s | {'🔴 BREACH' if max_p95 > self.state.threshold_seconds else '🟢 OK'} |",
            f"| p95 mínimo | {min_p95:.1f}s | — | — |",
            f"| Dias consecutivos acima do threshold | {days_above}/{self.state.window_days} | {self.state.window_days} | {'🔴 BREACH' if days_above >= self.state.window_days else '🟢 OK'} |",
            f"| MLLP indisponibilidade (max) | {max_mllp_unavailability:.2f}% | {self.state.mllp_unavailability_threshold_pct}% | {'🔴 BREACH' if max_mllp_unavailability > self.state.mllp_unavailability_threshold_pct else '🟢 OK'} |",
            "",
            "### Detalhamento Diário",
            "",
            "| Dia | p95 (s) | MLLP Healthy | MLLP Unavail % |",
            "|---|---|---|---|",
        ]

        for obs in recent:
            lines.append(
                f"| {obs.timestamp.strftime('%Y-%m-%d')} "
                f"| {obs.p95_seconds:.1f} "
                f"| {'✅' if obs.mllp_healthy else '❌'} "
                f"| {obs.mllp_unavailable_pct:.2f} |"
            )

        lines.extend([
            "",
            "### Ação Recomendada",
            "",
            "1. **Provisionar um tópico MSK dedicado** (ADR001-F-08) para o feed operacional de vitals",
            "2. **Escopo:** sinais vitais operacionais (MEWS/NEWS2/qSOFA, hemodynamic NRT)",
            "3. **Manter Gold como fonte analítica canônica** (ADR001-C-01/04) — sem alteração",
            "4. **Submeter para sign-off:** CTO Office + Time de Engenharia AMH",
            "5. **Não provisionar broker próprio** — o tópico é provisionado pelo AMH platform team (§6.2, §7)",
            "",
            "### Invariantes Preservados",
            "",
            "- Gold write-back (`ADR001-C-04`) mantido — sem alteração",
            "- Athena analytics (`ADR001-C-01`) mantido — sem alteração",
            "- `mpi_id` permanece como chave única (`ADR001-C-02`)",
            "- Nenhum broker infra próprio além do tópico provisionado (`ADR001-F-10`)",
            "",
            "### Sign-off Obrigatório",
            "",
            "| Papel | Nome | Assinatura | Data |",
            "|---|---|---|---|",
            "| CTO Office | ___________ | ___________ | ___/___/____ |",
            "| AMH Engineering Lead | ___________ | ___________ | ___/___/____ |",
            "| amh-integration-architect | ___________ | ___________ | ___/___/____ |",
            "",
            "### Referências",
            "",
            "- [system-architecture.md §6](../architecture/system-architecture.md) — Alternativa-B decision table",
            "- [ADR-001](../adr/ADR-001-amh-data-platform-consumer.md) — IntensiCare as AMH Data-Platform Consumer",
            "- [_work/budgets/latency.yaml](../_work/budgets/latency.yaml) — canonical latency budget",
            "- [BUILD-JOURNAL.md](BUILD-JOURNAL.md) — registro de decisão",
        ])

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Journal
    # ------------------------------------------------------------------

    def journal_recommendation(self) -> bool:
        """Registra a recomendação no BUILD-JOURNAL.md.

        Returns:
            True se o registro foi bem-sucedido, False caso contrário.
        """
        if self._journal_path is None:
            return False

        text = self.build_recommendation()

        try:
            with open(self._journal_path, "a", encoding="utf-8") as f:
                f.write("\n\n---\n\n")
                f.write(text)
                f.write("\n")
            return True
        except OSError:
            return False


# ---------------------------------------------------------------------------
# Função de conveniência — leitura simulada de métricas OTEL/AMP
# ---------------------------------------------------------------------------


def fetch_p95_from_otel(
    metric_name: str = "intensicare_ingest_to_alert_p95_seconds",
    lookback_hours: int = 24,
) -> float | None:
    """Simula a leitura de p95 do OTEL/AMP/Grafana.

    Em produção, consultaria o AMP via API (ADR001-C-06). Para testes e
    ambientes sem AMP, retorna None — deve ser substituído por mock ou
    pelo histograma real ``source_freshness`` quando disponível
    (system-architecture.md §6.1 OQ-1).

    Args:
        metric_name: Nome da métrica Prometheus/OTEL.
        lookback_hours: Janela de lookback em horas.

    Returns:
        p95 em segundos, ou None se indisponível.
    """
    return None
