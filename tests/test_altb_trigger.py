"""Testes para o trigger Alternativa-B — WO-040.

Cobre os cenários da tabela de decisão system-architecture.md §6.1 T1:
- Latência abaixo do threshold → sem trigger
- Latência acima do threshold por 7 dias consecutivos → trigger dispara
- Dados insuficientes (< 7 dias) → DEFER
- Violação intermitente → sem trigger
- MLLP indisponível > 0.5% → trigger dispara (T1b)
- Cálculo correto da janela rolante
- Geração de recomendação com evidências
- Journal da recomendação no BUILD-JOURNAL.md
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from intensicare.services.altb_trigger import (
    AltBDecision,
    AltBTrigger,
    AltBTriggerState,
    LatencyObservation,
    fetch_p95_from_otel,
)

# ═══════════════════════════════════════════════════════════════════════════
# LatencyObservation
# ═══════════════════════════════════════════════════════════════════════════


class TestLatencyObservation:
    """Testes para a estrutura LatencyObservation."""

    def test_create_observation(self) -> None:
        """Deve criar uma observação de latência com todos os campos."""
        ts = datetime.now(timezone.utc)
        obs = LatencyObservation(
            timestamp=ts,
            p95_seconds=25.0,
            mllp_healthy=True,
            mllp_unavailable_pct=0.1,
        )
        assert obs.timestamp == ts
        assert obs.p95_seconds == 25.0
        assert obs.mllp_healthy is True
        assert obs.mllp_unavailable_pct == 0.1

    def test_default_values_healthy(self) -> None:
        """Valores padrão devem representar estado saudável."""
        obs = LatencyObservation(
            timestamp=datetime.now(timezone.utc),
            p95_seconds=10.0,
        )
        assert obs.mllp_healthy is True
        assert obs.mllp_unavailable_pct == 0.0


# ═══════════════════════════════════════════════════════════════════════════
# AltBTriggerState
# ═══════════════════════════════════════════════════════════════════════════


class TestAltBTriggerState:
    """Testes para o AltBTriggerState."""

    def test_initial_state_defaults(self) -> None:
        """Estado inicial deve ter valores padrão conforme §6 T1."""
        state = AltBTriggerState()
        assert state.observations == []
        assert state.window_days == 7
        assert state.threshold_seconds == 30.0
        assert state.mllp_unavailability_threshold_pct == 0.5
        assert state.triggered is False
        assert state.last_evaluation is None
        assert state.decision is None

    def test_custom_thresholds(self) -> None:
        """Deve aceitar thresholds customizados."""
        state = AltBTriggerState(
            window_days=14,
            threshold_seconds=45.0,
            mllp_unavailability_threshold_pct=1.0,
        )
        assert state.window_days == 14
        assert state.threshold_seconds == 45.0
        assert state.mllp_unavailability_threshold_pct == 1.0


# ═══════════════════════════════════════════════════════════════════════════
# AltBTrigger — inicialização e ingestão
# ═══════════════════════════════════════════════════════════════════════════


class TestAltBTriggerInit:
    """Testes de inicialização do AltBTrigger."""

    def test_init_defaults(self) -> None:
        """Inicialização com valores padrão do system-architecture.md §6."""
        trigger = AltBTrigger()
        assert trigger.state.window_days == 7
        assert trigger.state.threshold_seconds == 30.0
        assert trigger.state.mllp_unavailability_threshold_pct == 0.5
        assert trigger.state.observations == []

    def test_init_custom(self) -> None:
        """Inicialização com valores customizados."""
        trigger = AltBTrigger(
            window_days=14,
            threshold_seconds=60.0,
            mllp_unavailability_threshold_pct=1.0,
        )
        assert trigger.state.window_days == 14
        assert trigger.state.threshold_seconds == 60.0
        assert trigger.state.mllp_unavailability_threshold_pct == 1.0

    def test_journal_path_optional(self) -> None:
        """journal_path é opcional."""
        trigger = AltBTrigger()
        assert trigger._journal_path is None

    def test_journal_path_set(self, tmp_path: Path) -> None:
        """journal_path deve ser armazenado como Path."""
        trigger = AltBTrigger(journal_path=str(tmp_path / "journal.md"))
        assert trigger._journal_path == tmp_path / "journal.md"


class TestAltBTriggerIngestion:
    """Testes de ingestão de observações."""

    def test_add_observation(self) -> None:
        """Deve adicionar observação à lista."""
        trigger = AltBTrigger(window_days=7)
        trigger.add_observation(p95_seconds=25.0)
        assert len(trigger.state.observations) == 1
        assert trigger.state.observations[0].p95_seconds == 25.0

    def test_add_observation_with_timestamp(self) -> None:
        """Deve aceitar timestamp customizado."""
        trigger = AltBTrigger()
        # Timestamp relativo (não hardcoded): add_observation() poda
        # observações fora da janela rolante de window_days (default 7,
        # ver altb_trigger.py:137-138) a cada chamada, então uma data fixa
        # eventualmente cai fora da janela e o observations[0] abaixo
        # lança IndexError. now() - 1 dia sempre fica dentro da janela.
        ts = datetime.now(timezone.utc) - timedelta(days=1)
        trigger.add_observation(p95_seconds=10.0, timestamp=ts)
        assert trigger.state.observations[0].timestamp == ts

    def test_add_multiple_observations(self) -> None:
        """Deve armazenar múltiplas observações em ordem."""
        trigger = AltBTrigger(window_days=7)
        for p95 in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]:
            trigger.add_observation(p95_seconds=p95)
        assert len(trigger.state.observations) == 7
        assert trigger.state.observations[0].p95_seconds == 10.0
        assert trigger.state.observations[-1].p95_seconds == 70.0


# ═══════════════════════════════════════════════════════════════════════════
# Janela rolante
# ═══════════════════════════════════════════════════════════════════════════


class TestRollingWindow:
    """Testes para a janela rolante de 7 dias."""

    def test_prune_removes_old_observations(self) -> None:
        """Deve remover observações com mais de 7 dias."""
        trigger = AltBTrigger(window_days=7)
        now = datetime.now(timezone.utc)

        # Observação de 8 dias atrás
        old_obs = LatencyObservation(
            timestamp=now - timedelta(days=8),
            p95_seconds=10.0,
        )
        trigger.state.observations.append(old_obs)

        # Observação recente
        trigger.add_observation(p95_seconds=10.0)

        trigger._prune_old_observations()
        assert len(trigger.state.observations) == 1

    def test_window_observations_property(self) -> None:
        """window_observations deve retornar apenas dados na janela."""
        trigger = AltBTrigger(window_days=7)
        now = datetime.now(timezone.utc)

        trigger.state.observations.append(
            LatencyObservation(
                timestamp=now - timedelta(days=10),
                p95_seconds=99.0,
            )
        )
        trigger.add_observation(p95_seconds=15.0)

        window = trigger.window_observations
        assert len(window) == 1
        assert window[0].p95_seconds == 15.0

    def test_exact_boundary_included(self) -> None:
        """Observações exatamente no limite da janela devem ser incluídas."""
        trigger = AltBTrigger(window_days=7)
        now = datetime.now(timezone.utc)

        # 6 dias e 23 horas atrás (dentro da janela)
        trigger.state.observations.append(
            LatencyObservation(
                timestamp=now - timedelta(days=6, hours=23),
                p95_seconds=35.0,
            )
        )

        assert len(trigger.window_observations) == 1

    def test_rolling_window_ignores_stale_data(self) -> None:
        """Dados fora da janela não devem influenciar a decisão."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)
        now = datetime.now(timezone.utc)

        # Preenche com 7 observações antigas (8-14 dias) — todas acima do threshold
        for i in range(8, 15):
            trigger.state.observations.append(
                LatencyObservation(
                    timestamp=now - timedelta(days=i),
                    p95_seconds=35.0,
                )
            )

        # 7 observações recentes abaixo do threshold
        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0)

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE


# ═══════════════════════════════════════════════════════════════════════════
# Cenários de decisão — system-architecture.md §6.1 T1
# ═══════════════════════════════════════════════════════════════════════════


class TestT1a_LatencyAboveThreshold:
    """T1(a): p95 > 30s por 7 dias consecutivos com MLLP saudável."""

    def test_seven_days_above_triggers(self) -> None:
        """p95 > 30s por 7 dias consecutivos: DEVE disparar ACTIVATE."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0, mllp_healthy=True)

        decision = trigger.evaluate()
        assert decision == AltBDecision.ACTIVATE
        assert trigger.state.triggered is True
        assert trigger.state.decision == AltBDecision.ACTIVATE

    def test_all_days_exactly_at_threshold_no_trigger(self) -> None:
        """p95 == 30s (não estritamente maior): NÃO deve disparar."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=30.0, mllp_healthy=True)

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE

    def test_high_latency_but_mllp_unhealthy_no_trigger_via_t1a(self) -> None:
        """p95 > 30s mas MLLP não saudável: T1(a) não dispara (mas T1(b) pode)."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(
                p95_seconds=50.0,
                mllp_healthy=False,
                mllp_unavailable_pct=0.1,  # abaixo de 0.5% → T1(b) também não
            )

        decision = trigger.evaluate()
        # T1(a) requer MLLP healthy; T1(b) requer >0.5%, nenhum satisfeito
        assert decision == AltBDecision.DO_NOT_ACTIVATE

    def test_mixed_mllp_states_no_trigger(self) -> None:
        """MLLP healthy em alguns dias, unhealthy em outros: T1(a) requer todos healthy."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for i in range(7):
            trigger.add_observation(
                p95_seconds=35.0,
                mllp_healthy=(i != 3),  # dia 3 unhealthy
            )

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE


class TestT1b_MLLPUnavailable:
    """T1(b): MLLP feed indisponível > 0.5% bed-hours."""

    def test_mllp_unavailable_triggers(self) -> None:
        """MLLP indisponível > 0.5%: DEVE disparar mesmo com latência OK."""
        trigger = AltBTrigger(
            window_days=7,
            threshold_seconds=30.0,
            mllp_unavailability_threshold_pct=0.5,
        )

        for _ in range(6):
            trigger.add_observation(p95_seconds=15.0, mllp_healthy=True)

        # Último dia: MLLP indisponível > 0.5%
        trigger.add_observation(
            p95_seconds=15.0,
            mllp_healthy=False,
            mllp_unavailable_pct=1.0,
        )

        decision = trigger.evaluate()
        assert decision == AltBDecision.ACTIVATE

    def test_mllp_exactly_at_threshold_no_trigger(self) -> None:
        """MLLP == 0.5% (não estritamente maior): NÃO deve disparar."""
        trigger = AltBTrigger(window_days=7)

        for _ in range(7):
            trigger.add_observation(
                p95_seconds=15.0,
                mllp_unavailable_pct=0.5,
            )

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE

    def test_mllp_below_threshold_no_trigger(self) -> None:
        """MLLP < 0.5% e latência OK: NÃO deve disparar."""
        trigger = AltBTrigger(window_days=7)

        for _ in range(7):
            trigger.add_observation(
                p95_seconds=15.0,
                mllp_unavailable_pct=0.2,
            )

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE


class TestDeferInsufficientData:
    """DEFER: dados insuficientes (< 7 dias)."""

    def test_zero_observations_defers(self) -> None:
        """Sem observações: DEFER."""
        trigger = AltBTrigger(window_days=7)
        decision = trigger.evaluate()
        assert decision == AltBDecision.DEFER

    def test_one_observation_defers(self) -> None:
        """1 observação: DEFER."""
        trigger = AltBTrigger(window_days=7)
        trigger.add_observation(p95_seconds=50.0)
        decision = trigger.evaluate()
        assert decision == AltBDecision.DEFER

    def test_six_observations_defers(self) -> None:
        """6 observações: DEFER (precisa de 7)."""
        trigger = AltBTrigger(window_days=7)
        for _ in range(6):
            trigger.add_observation(p95_seconds=35.0)
        decision = trigger.evaluate()
        assert decision == AltBDecision.DEFER

    def test_seven_observations_evaluates(self) -> None:
        """7 observações: deve avaliar (não DEFER)."""
        trigger = AltBTrigger(window_days=7)
        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0)
        decision = trigger.evaluate()
        assert decision != AltBDecision.DEFER


class TestDoNotActivate:
    """DO_NOT_ACTIVATE: condições não satisfeitas."""

    def test_all_low_latency_no_trigger(self) -> None:
        """Latência consistentemente baixa: DO_NOT_ACTIVATE."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0, mllp_healthy=True)

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE
        assert trigger.state.triggered is False

    def test_intermittent_breach_no_trigger(self) -> None:
        """Violação intermitente (não consecutiva): DO_NOT_ACTIVATE."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        values = [35.0, 35.0, 15.0, 35.0, 35.0, 35.0, 15.0]
        for v in values:
            trigger.add_observation(p95_seconds=v, mllp_healthy=True)

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE

    def test_single_day_below_breaks_streak(self) -> None:
        """Um único dia abaixo do threshold quebra a sequência."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(6):
            trigger.add_observation(p95_seconds=35.0)
        trigger.add_observation(p95_seconds=29.0)  # quebra a sequência

        decision = trigger.evaluate()
        assert decision == AltBDecision.DO_NOT_ACTIVATE


class TestStateTracking:
    """Rastreamento de estado pós-avaliação."""

    def test_decision_stored_in_state(self) -> None:
        """Decisão deve ser armazenada no estado após evaluate."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        trigger.evaluate()
        assert trigger.state.decision == AltBDecision.ACTIVATE

    def test_last_evaluation_timestamp_set(self) -> None:
        """last_evaluation deve ser atualizado a cada evaluate."""
        trigger = AltBTrigger(window_days=7)
        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0)

        before = datetime.now(timezone.utc)
        trigger.evaluate()
        after = datetime.now(timezone.utc)

        assert trigger.state.last_evaluation is not None
        assert before <= trigger.state.last_evaluation <= after

    def test_triggered_flag_persists(self) -> None:
        """triggered=True deve persistir entre avaliações."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        trigger.evaluate()
        assert trigger.state.triggered is True

        # Segunda avaliação mantém o flag
        trigger.evaluate()
        assert trigger.state.triggered is True


# ═══════════════════════════════════════════════════════════════════════════
# Geração de recomendação
# ═══════════════════════════════════════════════════════════════════════════


class TestBuildRecommendation:
    """Testes para build_recommendation()."""

    def test_activate_includes_evidence(self) -> None:
        """Recomendação de ACTIVATE deve conter evidências detalhadas."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0, mllp_healthy=True)

        rec = trigger.build_recommendation()
        assert "ACTIVATE" in rec
        assert "WO-040" in rec
        assert "35.0" in rec
        assert "system-architecture.md" in rec
        assert "ADR001-F-08" in rec
        assert "CTO Office" in rec
        assert "T1(a)" in rec

    def test_activate_includes_daily_breakdown(self) -> None:
        """Recomendação deve incluir tabela de detalhamento diário."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        rec = trigger.build_recommendation()
        assert "Detalhamento Diário" in rec
        assert "| Dia |" in rec
        assert "| p95 (s) |" in rec

    def test_activate_includes_signoff_table(self) -> None:
        """Recomendação deve incluir tabela de sign-off."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        rec = trigger.build_recommendation()
        assert "Sign-off Obrigatório" in rec
        assert "CTO Office" in rec
        assert "AMH Engineering Lead" in rec
        assert "amh-integration-architect" in rec

    def test_do_not_activate_message(self) -> None:
        """Sem trigger: texto informativo (não ativação)."""
        trigger = AltBTrigger(window_days=7, threshold_seconds=30.0)

        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0)

        rec = trigger.build_recommendation()
        assert "DO_NOT_ACTIVATE" in rec

    def test_mllp_unavailable_trigger_shows_t1b(self) -> None:
        """Trigger T1(b) deve referenciar T1(b) na recomendação."""
        trigger = AltBTrigger(window_days=7)

        for _ in range(6):
            trigger.add_observation(p95_seconds=15.0)
        trigger.add_observation(
            p95_seconds=15.0,
            mllp_healthy=False,
            mllp_unavailable_pct=1.0,
        )

        rec = trigger.build_recommendation()
        assert "T1(b)" in rec
        assert "DEGRADADO" in rec


# ═══════════════════════════════════════════════════════════════════════════
# Journal
# ═══════════════════════════════════════════════════════════════════════════


class TestJournalRecommendation:
    """Testes para journal_recommendation()."""

    def test_write_to_journal(self, tmp_path: Path) -> None:
        """Deve escrever recomendação no arquivo de journal."""
        journal = tmp_path / "BUILD-JOURNAL.md"
        journal.write_text("# Test Journal\n", encoding="utf-8")

        trigger = AltBTrigger(
            window_days=7,
            threshold_seconds=30.0,
            journal_path=str(journal),
        )

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        result = trigger.journal_recommendation()
        assert result is True

        content = journal.read_text(encoding="utf-8")
        assert "ACTIVATE" in content
        assert "WO-040" in content

    def test_no_journal_path_returns_false(self) -> None:
        """Sem journal_path, journal_recommendation retorna False."""
        trigger = AltBTrigger()

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        result = trigger.journal_recommendation()
        assert result is False

    def test_journal_appends_not_overwrites(self, tmp_path: Path) -> None:
        """journal_recommendation deve fazer append, não sobrescrever."""
        journal = tmp_path / "BUILD-JOURNAL.md"
        original = "# Original Content\n"
        journal.write_text(original, encoding="utf-8")

        trigger = AltBTrigger(
            window_days=7,
            threshold_seconds=30.0,
            journal_path=str(journal),
        )

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        trigger.journal_recommendation()

        content = journal.read_text(encoding="utf-8")
        assert content.startswith(original)
        assert "ACTIVATE" in content

    def test_do_not_activate_still_writes(self, tmp_path: Path) -> None:
        """Mesmo DO_NOT_ACTIVATE deve escrever no journal (rastreabilidade)."""
        journal = tmp_path / "BUILD-JOURNAL.md"
        journal.write_text("", encoding="utf-8")

        trigger = AltBTrigger(
            window_days=7,
            threshold_seconds=30.0,
            journal_path=str(journal),
        )

        for _ in range(7):
            trigger.add_observation(p95_seconds=15.0)

        result = trigger.journal_recommendation()
        assert result is True

        content = journal.read_text(encoding="utf-8")
        assert "DO_NOT_ACTIVATE" in content

    def test_journal_handles_os_error(self, tmp_path: Path) -> None:
        """Erro de I/O no journal deve retornar False sem lançar exceção."""
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        journal = read_only_dir / "BUILD-JOURNAL.md"
        journal.write_text("", encoding="utf-8")
        journal.chmod(0o444)  # read-only

        trigger = AltBTrigger(
            window_days=7,
            threshold_seconds=30.0,
            journal_path=str(journal),
        )

        for _ in range(7):
            trigger.add_observation(p95_seconds=35.0)

        # Não deve lançar exceção
        result = trigger.journal_recommendation()
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════
# Funções auxiliares
# ═══════════════════════════════════════════════════════════════════════════


class TestFetchP95:
    """Testes para fetch_p95_from_otel."""

    def test_returns_none_by_default(self) -> None:
        """Em modo simulação/ausência de AMP, retorna None."""
        result = fetch_p95_from_otel()
        assert result is None

    def test_accepts_custom_metric_name(self) -> None:
        """Deve aceitar nome de métrica customizado."""
        result = fetch_p95_from_otel(
            metric_name="custom_metric_p95",
            lookback_hours=48,
        )
        assert result is None  # simulação sempre retorna None
