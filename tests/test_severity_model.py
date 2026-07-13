"""
Testes para o modelo canônico de severidade (WO-011).

Cobre:
- Validação do enum SeverityLevel (4 valores: normal, watch, urgent, critical)
- P0-10 highest-severity-wins (nunca last-writer-wins)
- Triple-encoding (color + icon + shape)
- Regressão de downgrade: urgent nunca deve ser rebaixado para watch
- Integração com alert_engine (severidade válida nos thresholds)
- AUDIT-008: alinhamento backend/frontend
"""

import pytest

from intensicare.schemas.severity import (
    CANONICAL_SEVERITIES,
    SeverityLevel,
    TripleEncoder,
    highest_severity,
    max_severity,
)


class TestSeverityLevelEnum:
    """Testes do enum SeverityLevel."""

    def test_all_four_values_exist(self):
        """O enum deve ter exatamente 4 valores canônicos (AUDIT-008)."""
        values = [s.value for s in SeverityLevel]
        assert len(values) == 4
        assert "normal" in values
        assert "watch" in values
        assert "urgent" in values
        assert "critical" in values

    def test_canonical_severities_tuple(self):
        """CANONICAL_SEVERITIES deve ter os 4 valores na ordem correta."""
        assert CANONICAL_SEVERITIES == ("normal", "watch", "urgent", "critical")

    def test_rank_ordering(self):
        """O rank deve refletir a ordem: normal(0) < watch(1) < urgent(2) < critical(3)."""
        assert SeverityLevel.NORMAL.rank == 0
        assert SeverityLevel.WATCH.rank == 1
        assert SeverityLevel.URGENT.rank == 2
        assert SeverityLevel.CRITICAL.rank == 3

    def test_p10_score_mapping(self):
        """P0-10 scores: normal=0, watch=3, urgent=7, critical=10."""
        assert SeverityLevel.NORMAL.p10_score == 0
        assert SeverityLevel.WATCH.p10_score == 3
        assert SeverityLevel.URGENT.p10_score == 7
        assert SeverityLevel.CRITICAL.p10_score == 10

    def test_is_more_severe_than(self):
        """Comparação de severidade: critical é mais severo que os outros."""
        assert SeverityLevel.CRITICAL.is_more_severe_than(SeverityLevel.URGENT)
        assert SeverityLevel.CRITICAL.is_more_severe_than(SeverityLevel.WATCH)
        assert SeverityLevel.CRITICAL.is_more_severe_than(SeverityLevel.NORMAL)
        assert SeverityLevel.URGENT.is_more_severe_than(SeverityLevel.WATCH)
        assert SeverityLevel.URGENT.is_more_severe_than(SeverityLevel.NORMAL)
        assert SeverityLevel.WATCH.is_more_severe_than(SeverityLevel.NORMAL)

        # Não deve ser mais severo que si mesmo
        assert not SeverityLevel.CRITICAL.is_more_severe_than(SeverityLevel.CRITICAL)
        assert not SeverityLevel.WATCH.is_more_severe_than(SeverityLevel.URGENT)
        assert not SeverityLevel.NORMAL.is_more_severe_than(SeverityLevel.WATCH)

    def test_is_at_least(self):
        """Comparação >= severidade."""
        assert SeverityLevel.CRITICAL.is_at_least(SeverityLevel.CRITICAL)
        assert SeverityLevel.CRITICAL.is_at_least(SeverityLevel.URGENT)
        assert SeverityLevel.URGENT.is_at_least(SeverityLevel.URGENT)
        assert not SeverityLevel.WATCH.is_at_least(SeverityLevel.URGENT)

    def test_from_string(self):
        """Deve ser possível construir o enum a partir de string."""
        assert SeverityLevel("normal") == SeverityLevel.NORMAL
        assert SeverityLevel("watch") == SeverityLevel.WATCH
        assert SeverityLevel("urgent") == SeverityLevel.URGENT
        assert SeverityLevel("critical") == SeverityLevel.CRITICAL

    def test_from_string_case_sensitive(self):
        """Strings devem ser exatas (lowercase)."""
        with pytest.raises(ValueError):
            SeverityLevel("CRITICAL")
        with pytest.raises(ValueError):
            SeverityLevel("Critical")

    def test_string_value(self):
        """O valor string do enum deve ser a string lowercase."""
        assert str(SeverityLevel.CRITICAL.value) == "critical"
        # Como SeverityLevel herda de str, o próprio enum age como string
        assert SeverityLevel.CRITICAL == "critical"

    def test_invalid_severity_raises(self):
        """Valores inválidos devem lançar ValueError."""
        with pytest.raises(ValueError):
            SeverityLevel("info")
        with pytest.raises(ValueError):
            SeverityLevel("warning")
        with pytest.raises(ValueError):
            SeverityLevel("unknown")


class TestP0MostSeverityWins:
    """Testes de P0-10: highest-severity-wins aggregation."""

    def test_highest_severity_single(self):
        """Uma única severidade retorna ela mesma."""
        result = highest_severity("critical")
        assert result == SeverityLevel.CRITICAL

        result = highest_severity("normal")
        assert result == SeverityLevel.NORMAL

    def test_highest_severity_multiple_returns_max(self):
        """Múltiplas severidades retornam a maior (MAX)."""
        # critical deve ganhar de urgent
        result = highest_severity("watch", "critical", "urgent")
        assert result == SeverityLevel.CRITICAL

        # urgent deve ganhar de watch
        result = highest_severity("normal", "watch", "urgent")
        assert result == SeverityLevel.URGENT

        # watch deve ganhar de normal
        result = highest_severity("normal", "watch")
        assert result == SeverityLevel.WATCH

    def test_highest_severity_order_independent(self):
        """A ordem dos argumentos não importa (não é last-writer-wins)."""
        # critical por último
        result1 = highest_severity("watch", "urgent", "critical")
        # critical no meio
        result2 = highest_severity("watch", "critical", "urgent")
        # critical primeiro
        result3 = highest_severity("critical", "watch", "urgent")

        assert result1 == SeverityLevel.CRITICAL
        assert result2 == SeverityLevel.CRITICAL
        assert result3 == SeverityLevel.CRITICAL

    def test_highest_severity_with_none(self):
        """None values devem ser ignorados."""
        result = highest_severity(None, "watch", None, "urgent")
        assert result == SeverityLevel.URGENT

        result = highest_severity(None, None)
        assert result is None

    def test_highest_severity_empty_returns_none(self):
        """Lista vazia retorna None."""
        result = highest_severity()
        assert result is None

    def test_max_severity_returns_string(self):
        """max_severity deve retornar string (ou None)."""
        result = max_severity("watch", "critical")
        assert result == "critical"
        assert isinstance(result, str)

        result = max_severity(None, "normal")
        assert result == "normal"

        result = max_severity(None, None)
        assert result is None

    def test_max_severity_duplicates(self):
        """Severidades duplicadas não devem causar problemas."""
        result = max_severity("urgent", "urgent", "urgent", "watch")
        assert result == "urgent"

    # ------------------------------------------------------------------
    # P0-10: downgrade regression tests
    # ------------------------------------------------------------------

    def test_urgent_never_downgraded_to_watch(self):
        """P0-10: urgent nunca deve ser rebaixado para watch.

        Se existir um alerta urgent e um watch para o mesmo paciente,
        o resultado agregado deve ser urgent (nunca watch).
        Este é o teste de regressão de downgrade.
        """
        # Caso 1: urgent + watch → urgent
        result = max_severity("urgent", "watch")
        assert result == "urgent", (
            f"P0-10 VIOLATION: urgent + watch retornou '{result}', "
            f"mas deveria ser 'urgent' (highest-severity-wins)"
        )

        # Caso 2: watch + urgent → urgent (ordem inversa)
        result = max_severity("watch", "urgent")
        assert result == "urgent", (
            f"P0-10 VIOLATION: watch + urgent retornou '{result}' (possível last-writer-wins)"
        )

        # Caso 3: urgent + watch + normal → urgent
        result = max_severity("normal", "watch", "urgent")
        assert result == "urgent"

        # Caso 4: critical + urgent + watch → critical (critical nunca downgrade)
        result = max_severity("watch", "urgent", "critical")
        assert result == "critical"

    def test_normal_never_upgraded_unless_warranted(self):
        """normal só deve aparecer quando não há severidades maiores."""
        result = max_severity("normal", "normal", "normal")
        assert result == "normal"

        result = max_severity("normal", "watch")
        assert result == "watch"  # watch > normal

    def test_critical_dominates_all(self):
        """critical deve sempre dominar qualquer combinação."""
        result = max_severity("normal", "watch", "urgent", "critical")
        assert result == "critical"

        result = max_severity("critical", "normal")
        assert result == "critical"


class TestTripleEncoding:
    """Testes de triple-encoding (color + icon + shape)."""

    def test_all_severities_have_encoding(self):
        """Cada severidade deve ter triple-encoding completo."""
        for sev in SeverityLevel:
            enc = TripleEncoder.encode(sev)
            assert "color" in enc
            assert "icon" in enc
            assert "shape" in enc
            assert "label" in enc
            assert "description" in enc

            # Validações de formato
            assert enc["color"].startswith("#"), f"Cor inválida para {sev}: {enc['color']}"
            assert len(enc["color"]) == 7, f"Cor deve ter 7 caracteres (#RRGGBB): {enc['color']}"
            assert len(enc["icon"]) > 0, f"Ícone vazio para {sev}"
            assert len(enc["shape"]) > 0, f"Shape vazio para {sev}"

    def test_normal_encoding(self):
        """Encoding para normal: verde, check-circle, circle."""
        enc = TripleEncoder.encode(SeverityLevel.NORMAL)
        assert enc["color"] == "#2DD269"
        assert enc["icon"] == "check-circle"
        assert enc["shape"] == "circle"
        assert enc["label"] == "Normal"

    def test_watch_encoding(self):
        """Encoding para watch: amarelo, eye, rounded-square."""
        enc = TripleEncoder.encode(SeverityLevel.WATCH)
        assert enc["color"] == "#F2B90D"
        assert enc["icon"] == "eye"
        assert enc["shape"] == "rounded-square"
        assert enc["label"] == "Observação"

    def test_urgent_encoding(self):
        """Encoding para urgent: laranja, alert-triangle, triangle."""
        enc = TripleEncoder.encode(SeverityLevel.URGENT)
        assert enc["color"] == "#F96F06"
        assert enc["icon"] == "alert-triangle"
        assert enc["shape"] == "triangle"
        assert enc["label"] == "Urgente"

    def test_critical_encoding(self):
        """Encoding para critical: vermelho, alert-octagon, octagon."""
        enc = TripleEncoder.encode(SeverityLevel.CRITICAL)
        assert enc["color"] == "#F5828F"
        assert enc["icon"] == "alert-octagon"
        assert enc["shape"] == "octagon"
        assert enc["label"] == "Crítico"

    def test_encode_from_string(self):
        """encode deve aceitar string também."""
        enc = TripleEncoder.encode("critical")
        assert enc["color"] == "#F5828F"

    def test_encode_invalid_string_raises(self):
        """String inválida deve lançar ValueError."""
        with pytest.raises(ValueError):
            TripleEncoder.encode("invalid")

    def test_color_helper(self):
        """Helper color() deve retornar a cor correta."""
        assert TripleEncoder.color("normal") == "#2DD269"
        assert TripleEncoder.color("watch") == "#F2B90D"
        assert TripleEncoder.color("urgent") == "#F96F06"
        assert TripleEncoder.color("critical") == "#F5828F"

    def test_icon_helper(self):
        """Helper icon() deve retornar o ícone correto."""
        assert TripleEncoder.icon("critical") == "alert-octagon"
        assert TripleEncoder.icon("watch") == "eye"

    def test_shape_helper(self):
        """Helper shape() deve retornar a forma correta."""
        assert TripleEncoder.shape("urgent") == "triangle"
        assert TripleEncoder.shape("normal") == "circle"

    def test_label_helper(self):
        """Helper label() deve retornar o label correto."""
        assert TripleEncoder.label("critical") == "Crítico"
        assert TripleEncoder.label("normal") == "Normal"

    def test_all_severities_list(self):
        """all_severities deve retornar 4 entradas completas."""
        all_sev = TripleEncoder.all_severities()
        assert len(all_sev) == 4
        severities_in_list = {s["severity"] for s in all_sev}
        assert severities_in_list == {"normal", "watch", "urgent", "critical"}

    def test_encoding_is_distinct_per_severity(self):
        """Cada severidade deve ter encoding único (cores diferentes)."""
        colors = {TripleEncoder.color(s) for s in SeverityLevel}
        assert len(colors) == 4, "Cada severidade deve ter cor única"

        icons = {TripleEncoder.icon(s) for s in SeverityLevel}
        assert len(icons) == 4, "Cada severidade deve ter ícone único"

        shapes = {TripleEncoder.shape(s) for s in SeverityLevel}
        assert len(shapes) == 4, "Cada severidade deve ter shape único"


class TestAUDIT008Resolution:
    """Testes de resolução do AUDIT-008: alinhamento backend/frontend."""

    def test_no_info_severity(self):
        """'info' não é uma severidade canônica (era do frontend antigo)."""
        assert "info" not in CANONICAL_SEVERITIES
        with pytest.raises(ValueError):
            SeverityLevel("info")

    def test_no_warning_severity(self):
        """'warning' não é uma severidade canônica (era do frontend antigo)."""
        assert "warning" not in CANONICAL_SEVERITIES
        with pytest.raises(ValueError):
            SeverityLevel("warning")

    def test_backend_and_frontend_use_same_enum(self):
        """Backend e frontend agora usam o mesmo enum canônico.

        O backend usava: watch/urgent/critical (faltava 'normal').
        O frontend usava: info/warning/critical.
        Agora ambos usam: normal/watch/urgent/critical.
        """
        canonical = set(CANONICAL_SEVERITIES)
        expected = {"normal", "watch", "urgent", "critical"}
        assert canonical == expected, (
            f"AUDIT-008: severidades canônicas são {canonical}, esperado {expected}"
        )

    def test_normal_is_valid_backend_severity(self):
        """'normal' deve ser uma severidade válida (antes faltava no backend)."""
        assert "normal" in CANONICAL_SEVERITIES
        sev = SeverityLevel("normal")
        assert sev == SeverityLevel.NORMAL
        assert sev.rank == 0  # menor severidade
