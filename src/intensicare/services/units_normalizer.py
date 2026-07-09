"""Units normalizer — validates and normalizes clinical measurement units.

Provides guard functions to catch common unit-conversion bugs (e.g.,
FiO2 passed as percentage instead of fraction).
"""


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
        raise ValueError(
            "FiO2 fraction must be ≤ 1.0; percent values should be divided by 100"
        )
    return value
