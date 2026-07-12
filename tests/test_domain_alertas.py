"""Tests for domain_alertas — WAVE 2C UNVERIFIABLE RATIFY rules."""

from __future__ import annotations

from intensicare.services.domain_alertas import (
    aggregate_alert_counts,
    contar_qtd_criterios_alerta,
)


class TestContarQtdCriteriosAlerta:
    """RULE-ALERTAS-001: Count triggered criteria."""

    def test_two_alerts_one_neutral(self) -> None:
        """[
            {esta_alerta:1},{esta_alerta:1},{esta_alerta:0}
        ] -> 2"""
        criterios = [
            {"esta_alerta": 1},
            {"esta_alerta": 1},
            {"esta_alerta": 0},
        ]
        assert contar_qtd_criterios_alerta(criterios) == 2

    def test_empty_list(self) -> None:
        """[] -> 0"""
        assert contar_qtd_criterios_alerta([]) == 0

    def test_strict_equality_excludes_nontrivial(self) -> None:
        """[
            {esta_alerta:1},{esta_alerta:2},{esta_alerta:None},{esta_alerta:0}
        ] -> 1 (only exact ==1)"""
        criterios: list[dict] = [
            {"esta_alerta": 1},
            {"esta_alerta": 2},
            {"esta_alerta": None},
            {"esta_alerta": 0},
        ]
        assert contar_qtd_criterios_alerta(criterios) == 1

    def test_all_alerts(self) -> None:
        """All esta_alerta == 1 -> count = len."""
        criterios = [{"esta_alerta": 1}] * 5
        assert contar_qtd_criterios_alerta(criterios) == 5

    def test_no_alerts(self) -> None:
        """All esta_alerta == 0 -> 0."""
        criterios = [{"esta_alerta": 0}] * 3
        assert contar_qtd_criterios_alerta(criterios) == 0

    def test_missing_key(self) -> None:
        """Criteria dict without 'esta_alerta' key -> 0 (get returns None)."""
        criterios = [{"other": 1}]
        assert contar_qtd_criterios_alerta(criterios) == 0


class TestAggregateAlertCounts:
    """RULE-ALERTAS-002: Aggregate alert counts across movimentacoes."""

    def test_vermelho_precedence(self) -> None:
        """(VERMELHO, NEUTRO, AMARELO, NEUTRO) -> VERMELHO += 1"""
        counts = aggregate_alert_counts([("VERMELHO", "NEUTRO", "AMARELO", "NEUTRO")])
        assert counts == {"VERMELHO": 1, "AMARELO": 0, "NEUTRO": 0}

    def test_amarelo_precedence(self) -> None:
        """(NEUTRO, AMARELO, NEUTRO, None) -> AMARELO += 1"""
        counts = aggregate_alert_counts([("NEUTRO", "AMARELO", "NEUTRO", None)])
        assert counts == {"VERMELHO": 0, "AMARELO": 1, "NEUTRO": 0}

    def test_all_null(self) -> None:
        """(None, None, None, None) -> NEUTRO += 1"""
        counts = aggregate_alert_counts([(None, None, None, None)])
        assert counts == {"VERMELHO": 0, "AMARELO": 0, "NEUTRO": 1}

    def test_all_neutro(self) -> None:
        """(NEUTRO, NEUTRO, NEUTRO, NEUTRO) -> NEUTRO += 1"""
        counts = aggregate_alert_counts([("NEUTRO", "NEUTRO", "NEUTRO", "NEUTRO")])
        assert counts == {"VERMELHO": 0, "AMARELO": 0, "NEUTRO": 1}

    def test_mixed_count(self) -> None:
        """3 movimentacoes: 1 VERMELHO, 1 AMARELO, 1 NEUTRO."""
        counts = aggregate_alert_counts(
            [
                ("VERMELHO", "AMARELO", "NEUTRO", "NEUTRO"),
                ("NEUTRO", "AMARELO", "NEUTRO", None),
                (None, None, None, None),
            ]
        )
        assert counts == {"VERMELHO": 1, "AMARELO": 1, "NEUTRO": 1}

    def test_empty_list(self) -> None:
        """Empty list -> all zeros."""
        counts = aggregate_alert_counts([])
        assert counts == {"VERMELHO": 0, "AMARELO": 0, "NEUTRO": 0}
