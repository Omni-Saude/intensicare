"""Units normalizer — validates and normalizes clinical measurement units.

Provides guard functions to catch common unit-conversion bugs (e.g.,
FiO2 passed as percentage instead of fraction), plus a small registry-based
normalizer (``normalize_value``) used at the Gold-layer read boundary
(``services.gold_reader``) to convert whatever unit a source system reports
into each parameter's canonical unit.

Conversion factors here are simple fixed multipliers (``value * factor ==
value_in_canonical_unit``). Affine conversions (e.g. Fahrenheit → Celsius,
which requires an offset, not just a multiplier) are intentionally not
supported — a unit registered with a ``None`` factor is recognized but
rejected with a clear error rather than silently producing a wrong value.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# validate_fio2_fraction
# ---------------------------------------------------------------------------


def validate_fio2_fraction(value: float) -> float:
    """Validate that an FiO2 value is a fraction (0.0–1.0), not a percentage.

    Args:
        value: FiO2 value to validate.

    Returns:
        The validated FiO2 fraction.

    Raises:
        ValueError: If value > 1.0 (likely a percentage that should be divided by 100).
    """
    if value > 1.0:
        raise ValueError("FiO2 fraction must be ≤ 1.0; percent values should be divided by 100")
    return value


# ---------------------------------------------------------------------------
# normalize_value / canonical-unit registry
# ---------------------------------------------------------------------------


class UnitNormalizationError(ValueError):
    """Raised when a clinical parameter or its unit cannot be normalized."""


# parameter -> {canonical_unit, units: {lowercased_unit_name: factor_to_canonical}}
# A ``None`` factor means the unit is a recognized-but-unsupported affine
# conversion (needs an offset, not just a multiplier).
_PARAMETER_REGISTRY: dict[str, dict[str, Any]] = {
    "creatinina": {
        "canonical_unit": "mg/dL",
        "units": {
            "mg/dl": 1.0,
            "umol/l": 0.0113,
        },
    },
    "fio2": {
        "canonical_unit": "fraction",
        "units": {
            "fraction": 1.0,
            "percent": 0.01,
            "%": 0.01,
        },
    },
    "lactato_arterial": {
        "canonical_unit": "mmol/L",
        "units": {
            "mmol/l": 1.0,
            "mg/dl": 0.111,
        },
    },
    "pao2": {
        "canonical_unit": "mmHg",
        "units": {
            "mmhg": 1.0,
            "kpa": 7.50062,
        },
    },
    "temperatura": {
        "canonical_unit": "°C",
        "units": {
            "°c": 1.0,
            "degc": 1.0,
            # Fahrenheit → Celsius is affine ((F-32) * 5/9), not a fixed
            # multiplicative factor — recognized but unsupported.
            "degf": None,
        },
    },
}


def normalize_value(parameter: str, value: float, from_unit: str) -> float:
    """Convert ``value`` from ``from_unit`` to ``parameter``'s canonical unit.

    Unit matching is case-insensitive.

    Raises:
        UnitNormalizationError: If ``parameter`` is not registered, if
            ``from_unit`` is not a recognized unit for it, or if the unit is
            recognized but only convertible via an affine (non-multiplicative)
            transform that this function does not support.
    """
    param_info = _PARAMETER_REGISTRY.get(parameter)
    if param_info is None:
        raise UnitNormalizationError(f"Parâmetro desconhecido: '{parameter}'")

    units: dict[str, float | None] = param_info["units"]
    unit_key = from_unit.strip().lower()
    if unit_key not in units:
        raise UnitNormalizationError(
            f"Unidade '{from_unit}' não reconhecida para o parâmetro '{parameter}'"
        )

    factor = units[unit_key]
    if factor is None:
        raise UnitNormalizationError(
            f"Conversão de '{from_unit}' para o parâmetro '{parameter}' "
            "NÃO é um fator fixo (conversão affine não suportada)"
        )
    return value * factor


def get_canonical_unit(parameter: str) -> str | None:
    """Return the canonical unit for ``parameter``, or None if unregistered."""
    param_info = _PARAMETER_REGISTRY.get(parameter)
    return param_info["canonical_unit"] if param_info else None


def list_parameters() -> list[str]:
    """Return all registered parameter names, sorted."""
    return sorted(_PARAMETER_REGISTRY.keys())


def get_parameter_info(parameter: str) -> dict[str, Any] | None:
    """Return a small info dict for ``parameter``, or None if unregistered."""
    param_info = _PARAMETER_REGISTRY.get(parameter)
    if param_info is None:
        return None
    return {"parameter": parameter, "canonical_unit": param_info["canonical_unit"]}
