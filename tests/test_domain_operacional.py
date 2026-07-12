"""Tests for domain_operacional — WAVE 2C UNVERIFIABLE RATIFY rules."""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from intensicare.services.domain_operacional import (
    compute_length_of_stay,
    compute_pagination,
    filter_prescriptions_last_3_days,
    format_horario,
    get_number,
    get_real_day,
    group_prescriptions_by_day,
    minutes_elapsed,
    nome_abreviado,
    parse_date_to_iso,
)


class TestNomeAbreviado:
    """RULE-OPERACIONAL-INFRA-002."""

    def test_normal(self) -> None:
        result = nome_abreviado("Joao Paulo Silva Santos")
        assert "Joao Paulo" in result
        assert "S." in result

    def test_with_connective(self) -> None:
        result = nome_abreviado("Maria da Silva")
        assert "Maria da" in result or "Maria" in result

    def test_single_name(self) -> None:
        result = nome_abreviado("Joao")
        assert result == "Joao"

    def test_empty(self) -> None:
        assert nome_abreviado("") == ""
        assert nome_abreviado("   ") == ""


class TestGroupPrescriptionsByDay:
    """RULE-OPERACIONAL-INFRA-003."""

    def test_groups(self) -> None:
        rx_list = [
            {"atendimento": "A1", "data": date(2026, 7, 6)},
            {"atendimento": "A1", "data": date(2026, 7, 6)},
            {"atendimento": "A2", "data": date(2026, 7, 5)},
        ]
        result = group_prescriptions_by_day(rx_list)
        assert "A1" in result
        assert len(result["A1"]["2026-07-06"]) == 2
        assert len(result["A2"]["2026-07-05"]) == 1

    def test_empty(self) -> None:
        assert group_prescriptions_by_day([]) == {}

    def test_datetime_input(self) -> None:
        rx_list = [
            {"atendimento": "A1", "data": datetime(2026, 7, 6, 14, 0, tzinfo=timezone.utc)},
        ]
        result = group_prescriptions_by_day(rx_list)
        assert "2026-07-06" in result["A1"]


class TestGetRealDay:
    """RULE-OPERACIONAL-INFRA-004."""

    def test_after_7am(self) -> None:
        dt = datetime(2026, 7, 6, 8, 0, tzinfo=timezone.utc)
        assert get_real_day(dt) == date(2026, 7, 6)

    def test_before_7am(self) -> None:
        dt = datetime(2026, 7, 6, 3, 0, tzinfo=timezone.utc)
        assert get_real_day(dt) == date(2026, 7, 5)

    def test_exactly_7am(self) -> None:
        dt = datetime(2026, 7, 6, 7, 0, tzinfo=timezone.utc)
        assert get_real_day(dt) == date(2026, 7, 6)


class TestFilterPrescriptionsLast3Days:
    """RULE-OPERACIONAL-INFRA-005."""

    def test_filters_old(self) -> None:
        ref = datetime(2026, 7, 6, 12, 0, tzinfo=timezone.utc)
        rx_list = [
            {"data": date(2026, 7, 6), "id": 1},
            {"data": date(2026, 7, 5), "id": 2},
            {"data": date(2026, 7, 4), "id": 3},
            {"data": date(2026, 7, 3), "id": 4},
            {"data": date(2026, 7, 1), "id": 5},
        ]
        result = filter_prescriptions_last_3_days(rx_list, ref)
        ids = {r["id"] for r in result}
        # 2026-07-06 (today), 07-05 (-1), 07-04 (-2), 07-03 (-3) = 4 days (today + 3 prior)
        assert ids == {1, 2, 3, 4}

    def test_empty(self) -> None:
        assert filter_prescriptions_last_3_days([]) == []


class TestComputeLengthOfStay:
    """RULE-OPERACIONAL-INFRA-006."""

    def test_now(self) -> None:
        assert compute_length_of_stay(datetime.now(timezone.utc)) == 0

    def test_date_input(self) -> None:
        from datetime import timedelta

        past = date.today() - timedelta(days=5)
        assert compute_length_of_stay(past) == 5


class TestComputePagination:
    """RULE-OPERACIONAL-INFRA-007."""

    def test_basic(self) -> None:
        result = compute_pagination(100, page=1, page_size=10)
        assert result["total_pages"] == 10
        assert result["page"] == 1
        assert result["offset"] == 0

    def test_single_page(self) -> None:
        result = compute_pagination(5, page_size=10)
        assert result["total_pages"] == 1

    def test_last_page(self) -> None:
        result = compute_pagination(25, page=3, page_size=10)
        assert result["page"] == 3
        assert result["offset"] == 20

    def test_empty(self) -> None:
        result = compute_pagination(0)
        assert result["total_pages"] == 1
        assert result["total_items"] == 0

    def test_max_page_size(self) -> None:
        result = compute_pagination(200, page_size=200)
        assert result["page_size"] == 100  # capped


class TestMinutesElapsed:
    """RULE-OPERACIONAL-INFRA-008."""

    def test_one_hour(self) -> None:
        start = datetime(2026, 7, 6, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 7, 6, 11, 0, 0, tzinfo=timezone.utc)
        assert minutes_elapsed(start, end) == 60

    def test_90_seconds(self) -> None:
        start = datetime(2026, 7, 6, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 7, 6, 10, 1, 30, tzinfo=timezone.utc)
        assert minutes_elapsed(start, end) == 1  # floor


class TestFormatHorario:
    """RULE-OPERACIONAL-INFRA-009."""

    def test_hour_only(self) -> None:
        assert format_horario("7") == "07:00"

    def test_hour_minute(self) -> None:
        assert format_horario("7:30") == "07:30"

    def test_two_digit(self) -> None:
        assert format_horario("19") == "19:00"

    def test_full(self) -> None:
        assert format_horario("23:59") == "23:59"

    def test_invalid_hour(self) -> None:
        with pytest.raises(ValueError):
            format_horario("25:00")

    def test_invalid_minute(self) -> None:
        with pytest.raises(ValueError):
            format_horario("12:60")


class TestParseDateToIso:
    """RULE-OPERACIONAL-INFRA-010."""

    def test_iso_date(self) -> None:
        result = parse_date_to_iso("2026-07-06")
        assert result is not None
        assert result.startswith("2026-07-06T")

    def test_br_format(self) -> None:
        result = parse_date_to_iso("06/07/2026")
        assert result is not None
        assert "2026-07-06" in result

    def test_br_dash(self) -> None:
        result = parse_date_to_iso("06-07-2026")
        assert result is not None
        assert "2026-07-06" in result

    def test_none(self) -> None:
        assert parse_date_to_iso(None) is None

    def test_empty(self) -> None:
        assert parse_date_to_iso("") is None

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            parse_date_to_iso("not a date")


class TestGetNumber:
    """RULE-OPERACIONAL-INFRA-011."""

    def test_int(self) -> None:
        assert get_number(10) == 10.0

    def test_float(self) -> None:
        assert get_number(3.14) == 3.14

    def test_str_int(self) -> None:
        assert get_number("42") == 42.0

    def test_str_float(self) -> None:
        assert get_number("10.5") == 10.5

    def test_br_comma(self) -> None:
        assert get_number("10,5") == 10.5

    def test_none(self) -> None:
        assert get_number(None) == 0.0

    def test_invalid(self) -> None:
        assert get_number("abc") == 0.0

    def test_zero(self) -> None:
        assert get_number(0) == 0.0
