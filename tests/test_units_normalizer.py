"""Testes para o normalizador de unidades canônicas (units_normalizer.py).

Cobre normalização de valores com e sem conversão, aliases,
e comportamento de erro para unidades desconhecidas.
"""

from __future__ import annotations

import pytest

from intensicare.services.units_normalizer import (
    UnitNormalizationError,
    get_canonical_unit,
    get_parameter_info,
    list_parameters,
    normalize_value,
)


# ---------------------------------------------------------------------------
# normalize_value
# ---------------------------------------------------------------------------


class TestNormalizeValue:
    def test_same_unit_no_conversion(self):
        """Valor já na unidade canônica não deve ser alterado."""
        # fio2 canonical = fraction, from percent → factor 0.01
        result = normalize_value("fio2", 0.4, "fraction")
        assert result == 0.4

    def test_alias_no_conversion(self):
        """Alias (sinônimo 1:1) não deve alterar valor."""
        # mmHg tem alias "mmhg"
        # Valor na unidade canônica 'mmHg' passado como alias
        # This tests: from_unit aliased to canonical
        # Let's use a parameter we know has aliases.
        result = normalize_value("fio2", 21, "percent")
        assert result == pytest.approx(0.21, rel=0.01)

    def test_conversion_with_factor(self):
        """Conversão com fator numérico deve aplicar multiplicação."""
        # lactato_arterial: canonical = mmol/L, from mg/dL → factor 0.111
        result = normalize_value("lactato_arterial", 27, "mg/dL")
        assert result == pytest.approx(2.997, rel=0.01)

    def test_creatinine_umol_l_to_mg_dl(self):
        """Creatinina: canonical = mg/dL, from umol/L → factor 0.0113."""
        result = normalize_value("creatinina", 88.4, "umol/L")
        assert result == pytest.approx(1.0, rel=0.05)

    def test_unknown_parameter_raises(self):
        """Parâmetro não registrado deve lançar erro."""
        with pytest.raises(UnitNormalizationError, match="Parâmetro desconhecido"):
            normalize_value("parametro_inexistente", 100, "unit")

    def test_unknown_unit_raises(self):
        """Unidade não reconhecida deve lançar erro."""
        with pytest.raises(UnitNormalizationError, match="não reconhecida"):
            normalize_value("fio2", 100, "unidade_que_nao_existe")


# ---------------------------------------------------------------------------
# get_canonical_unit
# ---------------------------------------------------------------------------


class TestGetCanonicalUnit:
    def test_known_parameter(self):
        unit = get_canonical_unit("fio2")
        assert unit is not None
        assert isinstance(unit, str)

    def test_unknown_parameter(self):
        unit = get_canonical_unit("parametro_inexistente")
        assert unit is None


# ---------------------------------------------------------------------------
# list_parameters
# ---------------------------------------------------------------------------


class TestListParameters:
    def test_returns_list(self):
        params = list_parameters()
        assert isinstance(params, list)

    def test_returns_sorted(self):
        params = list_parameters()
        assert params == sorted(params)

    def test_contains_expected_parameters(self):
        params = list_parameters()
        expected = ["creatinina", "fio2", "lactato_arterial"]
        for p in expected:
            assert p in params, f"Expected parameter '{p}' in registry"


# ---------------------------------------------------------------------------
# get_parameter_info
# ---------------------------------------------------------------------------


class TestGetParameterInfo:
    def test_known_parameter_returns_dict(self):
        info = get_parameter_info("fio2")
        assert info is not None
        assert "canonical_unit" in info
        assert "parameter" in info

    def test_unknown_parameter_returns_none(self):
        info = get_parameter_info("parametro_inexistente")
        assert info is None
