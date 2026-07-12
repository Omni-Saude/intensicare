"""Tests for domain_tenancy — WAVE 2C UNVERIFIABLE RATIFY rules."""

from __future__ import annotations

from datetime import datetime, timezone

from intensicare.services.domain_tenancy import (
    active_bed_count,
    aggregate_establishment_indicators,
    combined_setor_display_name,
    company_indicadores_scopes,
    establishment_indicadores_scopes,
    establishment_unread_count,
    fetch_sector_indicator,
    floor_to_5min_bucket,
    merge_sector_alert_counts,
    merge_sector_gender_counts,
    monthly_intervention_count,
    sector_chat_preview,
    sector_clinical_indicator_aggregation,
    sector_unread_count,
)


class TestAggregateEstablishmentIndicators:
    """RULE-TENANCY-ORGANIZACAO-005."""

    def test_normal(self) -> None:
        result = aggregate_establishment_indicators([10.0, 20.0, 30.0])
        assert result["sum"] == 60.0
        assert result["avg"] == 20.0

    def test_empty(self) -> None:
        result = aggregate_establishment_indicators([])
        assert result == {"sum": 0.0, "avg": 0.0}

    def test_single(self) -> None:
        result = aggregate_establishment_indicators([42.5])
        assert result["sum"] == 42.5
        assert result["avg"] == 42.5

    def test_rounding(self) -> None:
        result = aggregate_establishment_indicators([10.0 / 3, 20.0 / 3])
        assert result["sum"] == round(10.0, 2)
        assert result["avg"] == round(5.0, 2)


class TestFetchSectorIndicator:
    """RULE-TENANCY-ORGANIZACAO-006."""

    def test_returns_first(self) -> None:
        indicators = [{"id": 1}, {"id": 2}]
        assert fetch_sector_indicator(indicators) == {"id": 1}

    def test_empty_list(self) -> None:
        assert fetch_sector_indicator([]) is None

    def test_none(self) -> None:
        assert fetch_sector_indicator(None) is None


class TestUnreadCounts:
    """RULE-TENANCY-ORGANIZACAO-007, 008."""

    def test_establishment_sum(self) -> None:
        assert establishment_unread_count([5, 3, 2]) == 10

    def test_establishment_empty(self) -> None:
        assert establishment_unread_count([]) == 0

    def test_sector_count(self) -> None:
        assert sector_unread_count({"s1": 5, "s2": 3}) == 8

    def test_sector_none(self) -> None:
        assert sector_unread_count(None) == 0


class TestCombinedSetorDisplayName:
    """RULE-TENANCY-ORGANIZACAO-009."""

    def test_normal(self) -> None:
        result = combined_setor_display_name("Hospital A", "UTI")
        assert result == "Hospital A - UTI"


class TestFloorTo5MinBucket:
    """RULE-TENANCY-ORGANIZACAO-010."""

    def test_exact_bucket(self) -> None:
        ts = datetime(2026, 7, 6, 14, 0, 30, 123456, tzinfo=timezone.utc)
        result = floor_to_5min_bucket(ts)
        assert result.minute == 0
        assert result.second == 0
        assert result.microsecond == 0

    def test_floor_2_to_0(self) -> None:
        ts = datetime(2026, 7, 6, 14, 2, 0, tzinfo=timezone.utc)
        assert floor_to_5min_bucket(ts).minute == 0

    def test_floor_7_to_5(self) -> None:
        ts = datetime(2026, 7, 6, 14, 7, 0, tzinfo=timezone.utc)
        assert floor_to_5min_bucket(ts).minute == 5

    def test_floor_59_to_55(self) -> None:
        ts = datetime(2026, 7, 6, 14, 59, 0, tzinfo=timezone.utc)
        assert floor_to_5min_bucket(ts).minute == 55


class TestMergeCounts:
    """RULE-TENANCY-ORGANIZACAO-011, 013."""

    def test_merge_alerts(self) -> None:
        manual = {"VERMELHO": 2, "AMARELO": 3}
        automatica = {"VERMELHO": 1, "NEUTRO": 5}
        result = merge_sector_alert_counts(manual, automatica)
        assert result == {"VERMELHO": 3, "AMARELO": 3, "NEUTRO": 5}

    def test_merge_genders(self) -> None:
        manual = {"M": 3, "F": 2}
        automatica = {"M": 1, "O": 1}
        result = merge_sector_gender_counts(manual, automatica)
        assert result == {"M": 4, "F": 2, "O": 1}

    def test_merge_empty_manual(self) -> None:
        result = merge_sector_alert_counts({}, {"A": 1})
        assert result == {"A": 1}

    def test_merge_empty_both(self) -> None:
        result = merge_sector_alert_counts({}, {})
        assert result == {}


class TestActiveBedCount:
    """RULE-TENANCY-ORGANIZACAO-012."""

    def test_count_active(self) -> None:
        beds = [
            {"ativo": True, "nome": "L1"},
            {"ativo": False, "nome": "L2"},
            {"ativo": True, "nome": "L3"},
        ]
        assert active_bed_count(beds) == 2

    def test_all_inactive(self) -> None:
        assert active_bed_count([{"ativo": False}]) == 0

    def test_empty(self) -> None:
        assert active_bed_count([]) == 0


class TestSectorChatPreview:
    """RULE-TENANCY-ORGANIZACAO-014."""

    def test_returns_first(self) -> None:
        obs = [{"text": "first"}, {"text": "second"}]
        assert sector_chat_preview(obs) == {"text": "first"}

    def test_empty(self) -> None:
        assert sector_chat_preview([]) is None


class TestMonthlyInterventionCount:
    """RULE-TENANCY-ORGANIZACAO-015."""

    def test_current_month(self) -> None:
        ref = datetime(2026, 7, 6, tzinfo=timezone.utc)
        interventions = [
            {"data": datetime(2026, 7, 1, tzinfo=timezone.utc)},
            {"data": datetime(2026, 7, 15, tzinfo=timezone.utc)},
            {"data": datetime(2026, 6, 30, tzinfo=timezone.utc)},
        ]
        assert monthly_intervention_count(interventions, ref) == 2

    def test_empty(self) -> None:
        assert monthly_intervention_count([], datetime.now(timezone.utc)) == 0

    def test_no_data_field(self) -> None:
        interventions = [{"other": True}]
        assert monthly_intervention_count(interventions) == 0


class TestSectorClinicalIndicatorAggregation:
    """RULE-TENANCY-ORGANIZACAO-038."""

    def test_aggregates(self) -> None:
        indicators = {
            "sepse": {"alerts": 5.0, "bundle_compliance": 80.0},
            "sedacao": {"alerts": 2.0, "rass_score": 3.5},
        }
        result = sector_clinical_indicator_aggregation(indicators)
        assert result["alerts"] == 7.0
        assert result["bundle_compliance"] == 80.0
        assert result["rass_score"] == 3.5

    def test_empty(self) -> None:
        assert sector_clinical_indicator_aggregation({}) == {}


class TestCompanyIndicadoresScopes:
    """RULE-TENANCY-ORGANIZACAO-041."""

    def test_filters(self) -> None:
        establishments = [
            {"id": 1, "name": "Est A"},
            {"id": 2, "name": "Est B"},
            {"id": 3, "name": "Est C"},
        ]
        result = company_indicadores_scopes([1, 3], establishments)
        assert len(result) == 2
        assert {e["id"] for e in result} == {1, 3}


class TestEstablishmentIndicadoresScopes:
    """RULE-TENANCY-ORGANIZACAO-042."""

    def test_scopes(self) -> None:
        movs = [
            {"id": 1, "estabelecimento_id": 10},
            {"id": 2, "estabelecimento_id": 20},
            {"id": 3, "estabelecimento_id": 10},
        ]
        sectors = [
            {"id": 1, "estabelecimento_id": 10},
            {"id": 2, "estabelecimento_id": 20},
        ]
        result = establishment_indicadores_scopes(10, movs, sectors)
        assert len(result["movimentacoes"]) == 2
        assert len(result["setores"]) == 1
