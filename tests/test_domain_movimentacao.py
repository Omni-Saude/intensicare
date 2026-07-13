"""Tests for domain_movimentacao — WAVE 2C UNVERIFIABLE RATIFY rules."""

from __future__ import annotations

from datetime import datetime, timezone

from intensicare.services.domain_movimentacao import (
    bed_patient_snapshot,
    build_bed_lookup_key,
    build_camera_rtsp_url,
    build_micro_indicators_payload,
    build_vinculo_lookup,
    buscar_dias_internacao,
    compute_assistido_flag,
    patient_basic_fields,
    surface_expected_mortality,
    tempo_permanencia,
)


class TestTempoPermanencia:
    """RULE-MOVIMENTACAO-ADT-001."""

    def test_tempo_permanencia_now(self) -> None:
        now = datetime.now(timezone.utc)
        # Admission now -> should be 0 days
        result = tempo_permanencia(now)
        assert result == 0

    def test_tempo_permanencia_3_days_ago(self) -> None:
        from datetime import timedelta

        three_days = datetime.now(timezone.utc) - timedelta(days=3)
        result = tempo_permanencia(three_days)
        assert result >= 3  # >=3 because whole-day truncation

    def test_buscar_dias_internacao_none(self) -> None:
        assert buscar_dias_internacao(None) == 0

    def test_buscar_dias_internacao_value(self) -> None:
        from datetime import timedelta

        one_day = datetime.now(timezone.utc) - timedelta(days=1)
        result = buscar_dias_internacao(one_day)
        assert result >= 1


class TestMicroIndicatorsPayload:
    """RULE-MOVIMENTACAO-ADT-002."""

    def test_basic(self) -> None:
        payload = build_micro_indicators_payload(vm=True, noradrenalina=False, tempo_internacao=5)
        assert payload["vm"] is True
        assert payload["noradrenalina"] is False
        assert payload["tempo_internacao"] == 5
        assert "mortalidade_esperada" not in payload

    def test_with_mortality(self) -> None:
        payload = build_micro_indicators_payload(mortalidade_esperada=0.15)
        assert payload["mortalidade_esperada"] == 0.15

    def test_all_false_defaults(self) -> None:
        payload = build_micro_indicators_payload()
        for key in ["vm", "noradrenalina", "dialise", "sedacao", "droga_vasoativa", "antibiotico"]:
            assert payload[key] is False
        assert payload["tempo_internacao"] == 0


class TestSurfaceExpectedMortality:
    """RULE-MOVIMENTACAO-ADT-003."""

    def test_with_value(self) -> None:
        result = surface_expected_mortality(0.23)
        assert result["value"] == 0.23
        assert "label" in result

    def test_none_value(self) -> None:
        result = surface_expected_mortality(None)
        assert result["value"] is None

    def test_without_label(self) -> None:
        result = surface_expected_mortality(0.5, with_label=False)
        assert "label" not in result


class TestBuildBedLookupKey:
    """RULE-MOVIMENTACAO-ADT-005."""

    def test_normal(self) -> None:
        key = build_bed_lookup_key("12345", "UTI-01")
        assert key == "12345:UTI-01"


class TestPatientSnapshot:
    """RULE-MOVIMENTACAO-ADT-006."""

    def test_with_data(self) -> None:
        data = {"nome": "Joao"}
        assert bed_patient_snapshot(data) == data

    def test_none(self) -> None:
        assert bed_patient_snapshot(None) == {}


class TestPatientBasicFields:
    """RULE-MOVIMENTACAO-ADT-007."""

    def test_full(self) -> None:
        birth = datetime(1980, 1, 15, tzinfo=timezone.utc)
        result = patient_basic_fields("Joao", "Silva", birth)
        assert result["nome_completo"] == "Joao Silva"
        assert result["idade"] is not None
        assert isinstance(result["idade"], int)
        assert result["idade"] >= 46

    def test_name_only(self) -> None:
        result = patient_basic_fields(nome="Maria")
        assert result["nome_completo"] == "Maria"
        assert result["idade"] is None

    def test_no_data(self) -> None:
        result = patient_basic_fields()
        assert result["nome_completo"] is None
        assert result["idade"] is None


class TestBuildVinculoLookup:
    """RULE-MOVIMENTACAO-ADT-008."""

    def test_builds_dict(self) -> None:
        movs = [
            {"leito_id": 10, "paciente_id": 100, "nr_atendimento": "A1"},
            {"leito_id": 20, "paciente_id": 200, "nr_atendimento": "A2"},
        ]
        result = build_vinculo_lookup(movs)
        assert "10" in result
        assert result["10"]["paciente_id"] == 100
        assert "20" in result

    def test_skips_no_leito(self) -> None:
        movs = [
            {"leito_id": None, "paciente_id": 100},
            {"leito_id": 10, "paciente_id": 200, "nr_atendimento": "A2"},
        ]
        result = build_vinculo_lookup(movs)
        assert len(result) == 1
        assert "10" in result


class TestBuildCameraRtspUrl:
    """RULE-MOVIMENTACAO-ADT-010."""

    def test_default(self) -> None:
        # Default creds hardened from admin:admin to RTSP_USER default
        # "intensicare_cam" / RTSP_PASS default "" — see
        # domain_movimentacao.py:328-329 (build_camera_rtsp_url).
        url = build_camera_rtsp_url("192.168.1.100")
        assert url == ("rtsp://intensicare_cam:@192.168.1.100/cam/realmonitor?channel=1&subtype=0")

    def test_custom_creds(self) -> None:
        url = build_camera_rtsp_url("10.0.0.1", "user", "pass", 2, 1)
        assert "rtsp://user:pass@10.0.0.1" in url
        assert "channel=2" in url
        assert "subtype=1" in url


class TestComputeAssistidoFlag:
    """RULE-MOVIMENTACAO-ADT-011."""

    def test_assistido(self) -> None:
        assert compute_assistido_flag(True, True) is True

    def test_not_assistido_no_pathway(self) -> None:
        assert compute_assistido_flag(False, True) is False

    def test_not_assistido_no_attended(self) -> None:
        assert compute_assistido_flag(True, False) is False

    def test_not_assistido_none(self) -> None:
        assert compute_assistido_flag(False, False) is False
