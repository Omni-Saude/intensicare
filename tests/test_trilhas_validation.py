"""Tests for Trilhas Engine CI validation gates (F-ARCH-001/002).

Covers all three CI gates with valid-pass and invalid-fail fixtures:

  Gate A — Unit Resolution:
    - valid: all units resolve in canonical registry
    - invalid: non-canonical unit fails

  Gate B — Band Partition:
    - valid: bands cover domain without gaps/overlaps, last band null-infinity
    - invalid: gapped bands fail, overlapping bands fail, non-null last band fails

  Gate C — Facade ≡ Predicate:
    - valid: rationale matches rendered predicate
    - invalid: rationale mismatch fails
"""

from __future__ import annotations

import pytest

# Import validation functions directly
from scripts.validate_alerts import (
    ALL_CANONICAL,
    _collect_units,
    _normalize,
    _render_predicate_rationale,
    _validate_bands,
    gate_a_unit_resolution,
    gate_b_band_partition,
    gate_c_facade_predicate,
)


# =============================================================================
# Gate A — Unit Resolution
# =============================================================================

class TestGateAUnitResolution:
    """Unit resolution: every input.unit and predicate.unit must be canonical."""

    def test_valid_units_all_canonical(self) -> None:
        """All units in a well-formed definition are canonical."""
        definition = {
            "_source_file": "test.yaml",
            "evaluation": {
                "mode": "hybrid",
                "inputs": [
                    {"name": "pf_ratio", "source": "amh_gold", "unit": "mmHg"},
                    {"name": "lactate", "source": "amh_gold", "unit": "mmol/L"},
                    {"name": "heart_rate", "source": "vitals", "unit": "bpm"},
                ],
            },
            "criteria": [
                {
                    "id": "crit-1",
                    "name": "PF Ratio",
                    "category": "oxigenacao",
                    "predicate": {
                        "type": "graded",
                        "input": "pf_ratio",
                        "unit": "mmHg",
                        "bands": [
                            {"range": [0, 100], "severity": "critical", "score": 3},
                            {"range": [100, 200], "severity": "urgent", "score": 2},
                            {"range": [200, 300], "severity": "watch", "score": 1},
                            {"range": [300, None], "severity": "normal", "score": 0},
                        ],
                    },
                },
            ],
        }
        units = _collect_units(definition)
        for _, _, unit in units:
            assert unit in ALL_CANONICAL, f"Unit '{unit}' not canonical"

    def test_invalid_unit_fails(self) -> None:
        """A non-canonical unit is detected."""
        definition = {
            "_source_file": "test.yaml",
            "evaluation": {
                "mode": "hybrid",
                "inputs": [
                    {"name": "pf_ratio", "source": "amh_gold", "unit": "furlongs_per_fortnight"},
                ],
            },
            "criteria": [],
        }
        units = _collect_units(definition)
        non_canonical = [(p, u) for _, p, u in units if u not in ALL_CANONICAL]
        assert len(non_canonical) > 0, "Expected non-canonical unit to be flagged"
        assert non_canonical[0][1] == "furlongs_per_fortnight"

    def test_gate_a_pass_with_valid_defs(self) -> None:
        """gate_a_unit_resolution returns 0 for valid definitions."""
        defs = [
            {
                "_source_file": "test.yaml",
                "evaluation": {
                    "mode": "hybrid",
                    "inputs": [
                        {"name": "spo2", "source": "vitals", "unit": "%"},
                    ],
                },
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "SpO2",
                        "category": "oxigenacao",
                        "predicate": {
                            "type": "threshold",
                            "input": "spo2",
                            "operator": "<",
                            "value": 92,
                            "unit": "%",
                        },
                    },
                ],
            },
        ]
        assert gate_a_unit_resolution(defs) == 0

    def test_gate_a_fails_with_invalid_defs(self) -> None:
        """gate_a_unit_resolution returns 1 for invalid units."""
        defs = [
            {
                "_source_file": "test.yaml",
                "evaluation": {
                    "mode": "hybrid",
                    "inputs": [
                        {"name": "bad", "source": "vitals", "unit": "nonexistent_unit_xyz"},
                    ],
                },
                "criteria": [],
            },
        ]
        assert gate_a_unit_resolution(defs) == 1


# =============================================================================
# Gate B — Band Partition
# =============================================================================

class TestGateBBandPartition:
    """Band partition: graded bands must cover domain without gaps or overlaps."""

    def test_valid_bands_continuous(self) -> None:
        """Well-formed bands with contiguous ranges and null-infinity last pass."""
        bands = [
            {"range": [0, 100], "severity": "critical", "score": 3},
            {"range": [100, 200], "severity": "urgent", "score": 2},
            {"range": [200, 300], "severity": "watch", "score": 1},
            {"range": [300, None], "severity": "normal", "score": 0},
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert not errors, f"Expected no errors, got: {errors}"

    def test_valid_bands_float_boundaries(self) -> None:
        """Bands with float boundaries that are contiguous pass."""
        bands = [
            {"range": [0.0, 1.0], "severity": "critical", "score": 3},
            {"range": [1.0, 2.0], "severity": "urgent", "score": 2},
            {"range": [2.0, None], "severity": "normal", "score": 0},
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert not errors, f"Expected no errors, got: {errors}"

    def test_invalid_gapped_bands_fails(self) -> None:
        """Gap between bands should produce an error."""
        bands = [
            {"range": [0, 100], "severity": "critical", "score": 3},
            {"range": [101, 200], "severity": "urgent", "score": 2},  # gap at 100-101
            {"range": [200, None], "severity": "normal", "score": 0},
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert len(errors) > 0, "Expected gap error"
        assert any("GAP" in e.upper() or "gap" in e for e in errors), (
            f"Expected gap-related error, got: {errors}"
        )

    def test_invalid_overlapping_bands_fails(self) -> None:
        """Overlapping bands should produce an error."""
        bands = [
            {"range": [0, 150], "severity": "critical", "score": 3},
            {"range": [100, 200], "severity": "urgent", "score": 2},  # overlap 100-150
            {"range": [200, None], "severity": "normal", "score": 0},
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert len(errors) > 0, "Expected overlap error"
        assert any("OVERLAP" in e.upper() or "overlap" in e for e in errors), (
            f"Expected overlap-related error, got: {errors}"
        )

    def test_invalid_last_band_not_null_fails(self) -> None:
        """Last band without null upper bound fails."""
        bands = [
            {"range": [0, 100], "severity": "critical", "score": 3},
            {"range": [100, 200], "severity": "urgent", "score": 2},
            {"range": [200, 300], "severity": "watch", "score": 1},  # not null
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert len(errors) > 0, "Expected error about last band not covering to +∞"
        assert any("+∞" in e or "infinity" in e.lower() or "last" in e.lower() or "cover" in e.lower() for e in errors), (
            f"Expected last-band-coverage error, got: {errors}"
        )

    def test_invalid_unreachable_band_zero_width_fails(self) -> None:
        """A band with zero width (low == high) should be flagged."""
        bands = [
            {"range": [100, 100], "severity": "critical", "score": 3},  # zero width
            {"range": [100, None], "severity": "normal", "score": 0},
        ]
        errors = _validate_bands(bands, "test.yaml", "criteria[0].predicate")
        assert len(errors) > 0, "Expected zero-width/unreachable band error"

    def test_gate_b_pass_with_valid_defs(self) -> None:
        """gate_b_band_partition returns 0 for valid definitions."""
        defs = [
            {
                "_source_file": "test.yaml",
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "Test",
                        "category": "test",
                        "predicate": {
                            "type": "graded",
                            "input": "x",
                            "unit": "mmHg",
                            "bands": [
                                {"range": [0, 100], "severity": "critical", "score": 3},
                                {"range": [100, 200], "severity": "urgent", "score": 2},
                                {"range": [200, None], "severity": "normal", "score": 0},
                            ],
                        },
                    },
                ],
            },
        ]
        assert gate_b_band_partition(defs) == 0

    def test_gate_b_fails_with_gapped_bands(self) -> None:
        """gate_b_band_partition returns 1 for gapped bands."""
        defs = [
            {
                "_source_file": "test.yaml",
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "Test",
                        "category": "test",
                        "predicate": {
                            "type": "graded",
                            "input": "x",
                            "unit": "mmHg",
                            "bands": [
                                {"range": [0, 100], "severity": "critical", "score": 3},
                                {"range": [101, 200], "severity": "urgent", "score": 2},  # gap
                                {"range": [200, None], "severity": "normal", "score": 0},
                            ],
                        },
                    },
                ],
            },
        ]
        assert gate_b_band_partition(defs) == 1


# =============================================================================
# Gate C — Facade ≡ Predicate
# =============================================================================

class TestGateCFacadePredicate:
    """Facade ≡ Predicate: rendered rationale must match predicate AST."""

    def test_render_threshold_predicate(self) -> None:
        """Threshold predicate renders correctly."""
        pred = {
            "type": "threshold",
            "input": "lactate",
            "operator": ">",
            "value": 2,
            "unit": "mmol/L",
        }
        rendered = _render_predicate_rationale(pred)
        assert "lactate" in rendered
        assert ">" in rendered
        assert "2" in rendered
        assert "mmol/L" in rendered

    def test_render_graded_predicate(self) -> None:
        """Graded predicate renders with band info."""
        pred = {
            "type": "graded",
            "input": "pf_ratio",
            "unit": "mmHg",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, None], "severity": "normal", "score": 0},
            ],
        }
        rendered = _render_predicate_rationale(pred)
        assert "graded(pf_ratio" in rendered
        assert "critical(3)" in rendered
        assert "normal(0)" in rendered
        assert "mmHg" in rendered

    def test_render_boolean_predicate(self) -> None:
        """Boolean predicate renders correctly."""
        pred = {"type": "boolean", "input": "suspected_infection"}
        rendered = _render_predicate_rationale(pred)
        assert "boolean(suspected_infection)" in rendered

    def test_matching_rationale_passes(self) -> None:
        """When rationale matches rendered facade, it passes."""
        defs = [
            {
                "_source_file": "test.yaml",
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "Lactate",
                        "category": "lab",
                        "predicate": {
                            "type": "threshold",
                            "input": "lactate",
                            "operator": ">",
                            "value": 2,
                            "unit": "mmol/L",
                            "rationale": "lactate > 2 mmol/L",
                        },
                    },
                ],
            },
        ]
        assert gate_c_facade_predicate(defs) == 0

    def test_mismatched_rationale_fails(self) -> None:
        """When rationale does NOT match rendered facade, it fails."""
        defs = [
            {
                "_source_file": "test.yaml",
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "Lactate",
                        "category": "lab",
                        "predicate": {
                            "type": "threshold",
                            "input": "lactate",
                            "operator": ">",
                            "value": 2,
                            "unit": "mmol/L",
                            # Wrong rationale — says "lactate < 2" but predicate is ">"
                            "rationale": "lactate < 2 mmol/L",
                        },
                    },
                ],
            },
        ]
        assert gate_c_facade_predicate(defs) == 1

    def test_gate_c_no_rationale_passes(self) -> None:
        """Definitions without rationale field pass Gate C (nothing to check)."""
        defs = [
            {
                "_source_file": "test.yaml",
                "criteria": [
                    {
                        "id": "crit-1",
                        "name": "Lactate",
                        "category": "lab",
                        "predicate": {
                            "type": "threshold",
                            "input": "lactate",
                            "operator": ">",
                            "value": 2,
                            "unit": "mmol/L",
                            # no rationale
                        },
                    },
                ],
            },
        ]
        assert gate_c_facade_predicate(defs) == 0

    def test_normalize_handles_whitespace(self) -> None:
        """_normalize handles extra whitespace and case."""
        a = "  Lactate   > 2 mmol/L  "
        b = "lactate > 2 mmol/l"
        assert _normalize(a) == _normalize(b)

    def test_render_composite_predicate(self) -> None:
        """Composite predicate renders with combinator and sub-predicates."""
        pred = {
            "type": "composite",
            "combinator": "AND",
            "sub_predicates": [
                {"type": "threshold", "input": "lactate", "operator": ">", "value": 2, "unit": "mmol/L"},
                {"type": "boolean", "input": "suspected_infection"},
            ],
        }
        rendered = _render_predicate_rationale(pred)
        assert "composite(AND:" in rendered
        assert "lactate > 2 mmol/L" in rendered
        assert "boolean(suspected_infection)" in rendered
