"""Tests for trilhas_compiler — secure AST-based predicate compiler.

Covers:
  - Threshold predicates: compilation, evaluation, edge cases
  - Graded predicates: band matching, continuity validation, severity assignment
  - Boolean predicates: truthy/falsy evaluation
  - Composite predicates: AND/OR combination logic
  - Error cases: missing fields, invalid operators, bad bands
  - Integration: evaluate YAML-like dicts end-to-end
  - Security: NO eval/exec in the module source
"""

from __future__ import annotations

import ast
import textwrap

import pytest

from intensicare.services.trilhas_compiler import (
    ASTNode,
    BooleanNode,
    CompiledPredicate,
    CompositeNode,
    GradedNode,
    PredicateCompiler,
    ThresholdNode,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def compiler() -> PredicateCompiler:
    """Return a fresh PredicateCompiler instance."""
    return PredicateCompiler()


@pytest.fixture
def patient_data() -> dict:
    """Sample patient data for evaluation tests."""
    return {
        "pf_ratio": 150.0,
        "peep": 8,
        "lactate": 3.5,
        "heart_rate": 110,
        "spo2": 94,
        "suspected_infection": True,
        "culturas_coletadas": True,
        "antibiotico_1h": False,
        "glasgow": 12,
    }


# =============================================================================
# Threshold Predicate Tests
# =============================================================================


class TestThresholdCompilation:
    """Compilation of threshold predicates."""

    def test_compile_simple_threshold(self, compiler: PredicateCompiler) -> None:
        """Basic threshold: lactate > 2 mmol/L."""
        pred = {
            "type": "threshold",
            "input": "lactate",
            "operator": ">",
            "value": 2,
            "unit": "mmol/L",
        }
        compiled = compiler.compile(pred)
        assert compiled.predicate_type == "threshold"
        assert compiled.input_name == "lactate"
        assert compiled.unit == "mmol/L"

        node = compiled.ast_node
        assert isinstance(node, ThresholdNode)
        assert node.input_name == "lactate"
        assert node.operator == ">"
        assert node.value == 2.0
        assert node.unit == "mmol/L"

    def test_all_valid_operators(self, compiler: PredicateCompiler) -> None:
        """All six operators compile successfully."""
        for op in ("<", "<=", ">", ">=", "==", "!="):
            pred = {
                "type": "threshold",
                "input": "x",
                "operator": op,
                "value": 10,
                "unit": "bpm",
            }
            compiled = compiler.compile(pred)
            node = compiled.ast_node
            assert isinstance(node, ThresholdNode)
            assert node.operator == op

    def test_invalid_operator_raises(self, compiler: PredicateCompiler) -> None:
        """Unknown operator raises ValueError."""
        pred = {
            "type": "threshold",
            "input": "x",
            "operator": "contains",
            "value": 10,
            "unit": "",
        }
        with pytest.raises(ValueError, match="Invalid operator"):
            compiler.compile(pred)

    def test_missing_input_raises(self, compiler: PredicateCompiler) -> None:
        """Missing 'input' raises ValueError."""
        pred = {
            "type": "threshold",
            "operator": ">",
            "value": 10,
            "unit": "bpm",
        }
        with pytest.raises(ValueError, match="missing 'input'"):
            compiler.compile(pred)

    def test_missing_value_raises(self, compiler: PredicateCompiler) -> None:
        """Missing 'value' raises ValueError."""
        pred = {
            "type": "threshold",
            "input": "x",
            "operator": ">",
            "unit": "bpm",
        }
        with pytest.raises(ValueError, match="missing 'value'"):
            compiler.compile(pred)

    def test_float_value(self, compiler: PredicateCompiler) -> None:
        """Float threshold values are preserved."""
        pred = {
            "type": "threshold",
            "input": "pf_ratio",
            "operator": "<",
            "value": 200.5,
            "unit": "mmHg",
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, ThresholdNode)
        assert node.value == 200.5

    def test_default_operator(self, compiler: PredicateCompiler) -> None:
        """Missing operator defaults to '>=' per schema."""
        pred = {
            "type": "threshold",
            "input": "spo2",
            "value": 92,
            "unit": "%",
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, ThresholdNode)
        assert node.operator == ">="


class TestThresholdEvaluation:
    """Evaluation of threshold predicates."""

    def test_greater_than_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """lactate > 2 → 3.5 > 2 → met."""
        pred = {
            "type": "threshold",
            "input": "lactate",
            "operator": ">",
            "value": 2,
            "unit": "mmol/L",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is True
        assert result.severity == "urgent"
        assert result.score == 1
        assert result.actual_value == 3.5
        assert result.input_name == "lactate"
        assert result.unit == "mmol/L"

    def test_less_than_not_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """pf_ratio < 100 → 150 < 100 → not met."""
        pred = {
            "type": "threshold",
            "input": "pf_ratio",
            "operator": "<",
            "value": 100,
            "unit": "mmHg",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is False
        assert result.severity == "normal"
        assert result.score == 0

    def test_greater_equal_boundary(self, compiler: PredicateCompiler) -> None:
        """peep >= 8 → 8 >= 8 → met."""
        pred = {
            "type": "threshold",
            "input": "peep",
            "operator": ">=",
            "value": 8,
            "unit": "cmH2O",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"peep": 8})
        assert result.met is True

    def test_equal_operator(self, compiler: PredicateCompiler) -> None:
        """spo2 == 94 → met."""
        pred = {
            "type": "threshold",
            "input": "spo2",
            "operator": "==",
            "value": 94,
            "unit": "%",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"spo2": 94})
        assert result.met is True

        result2 = compiler.evaluate(compiled, {"spo2": 95})
        assert result2.met is False

    def test_not_equal_operator(self, compiler: PredicateCompiler) -> None:
        """spo2 != 90 → 94 != 90 → met."""
        pred = {
            "type": "threshold",
            "input": "spo2",
            "operator": "!=",
            "value": 90,
            "unit": "%",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"spo2": 94})
        assert result.met is True

    def test_missing_key_raises(self, compiler: PredicateCompiler) -> None:
        """Missing input in patient_data raises KeyError."""
        pred = {
            "type": "threshold",
            "input": "nonexistent",
            "operator": ">",
            "value": 5,
            "unit": "",
        }
        compiled = compiler.compile(pred)
        with pytest.raises(KeyError, match="nonexistent"):
            compiler.evaluate(compiled, {})


# =============================================================================
# Graded Predicate Tests
# =============================================================================


class TestGradedCompilation:
    """Compilation of graded predicates with band validation."""

    def test_compile_valid_graded(self, compiler: PredicateCompiler) -> None:
        """Well-formed PF ratio graded predicate compiles."""
        pred = {
            "type": "graded",
            "input": "pf_ratio",
            "unit": "mmHg",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, 200], "severity": "urgent", "score": 2},
                {"range": [200, 300], "severity": "watch", "score": 1},
                {"range": [300, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        assert compiled.predicate_type == "graded"
        node = compiled.ast_node
        assert isinstance(node, GradedNode)
        assert len(node.bands) == 4
        assert node.bands[0].severity == "critical"
        assert node.bands[-1].severity == "normal"
        assert node.bands[-1].upper is None

    def test_bands_sorted_after_compilation(self, compiler: PredicateCompiler) -> None:
        """Bands are sorted by lower bound regardless of input order."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [300, None], "severity": "normal", "score": 0},
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, 200], "severity": "urgent", "score": 2},
                {"range": [200, 300], "severity": "watch", "score": 1},
            ],
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, GradedNode)
        # Should be sorted by lower bound
        lowers = [b.lower for b in node.bands]
        assert lowers == [0, 100, 200, 300]

    def test_gap_between_bands_raises(self, compiler: PredicateCompiler) -> None:
        """Gap between bands raises ValueError."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [101, None], "severity": "normal", "score": 0},  # gap at 100-101
            ],
        }
        with pytest.raises(ValueError, match=r"gap|overlap"):
            compiler.compile(pred)

    def test_overlap_between_bands_raises(self, compiler: PredicateCompiler) -> None:
        """Overlap between bands raises ValueError."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0, 150], "severity": "critical", "score": 3},
                {"range": [100, None], "severity": "normal", "score": 0},  # overlap 100-150
            ],
        }
        with pytest.raises(ValueError, match=r"gap|overlap"):
            compiler.compile(pred)

    def test_last_band_not_null_raises(self, compiler: PredicateCompiler) -> None:
        """Last band must have null upper bound."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, 200], "severity": "urgent", "score": 2},
            ],
        }
        with pytest.raises(ValueError, match="null upper"):
            compiler.compile(pred)

    def test_zero_width_band_raises(self, compiler: PredicateCompiler) -> None:
        """Band with lower >= upper raises ValueError."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [100, 100], "severity": "critical", "score": 3},
                {"range": [100, None], "severity": "normal", "score": 0},
            ],
        }
        with pytest.raises(ValueError, match="invalid range"):
            compiler.compile(pred)

    def test_empty_bands_raises(self, compiler: PredicateCompiler) -> None:
        """Empty bands list raises ValueError."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [],
        }
        with pytest.raises(ValueError, match="at least one band"):
            compiler.compile(pred)

    def test_missing_input_raises(self, compiler: PredicateCompiler) -> None:
        """Missing 'input' in graded raises ValueError."""
        pred = {
            "type": "graded",
            "unit": "",
            "bands": [
                {"range": [0, None], "severity": "normal", "score": 0},
            ],
        }
        with pytest.raises(ValueError, match="missing 'input'"):
            compiler.compile(pred)

    def test_band_with_label(self, compiler: PredicateCompiler) -> None:
        """Band label is preserved during compilation."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "mmHg",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3, "label": "Severa"},
                {"range": [100, None], "severity": "normal", "score": 0, "label": "Normal"},
            ],
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, GradedNode)
        assert node.bands[0].label == "Severa"
        assert node.bands[1].label == "Normal"


class TestGradedEvaluation:
    """Evaluation of graded predicates against patient data."""

    def test_graded_critical(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """pf_ratio=150 falls in [100, 200) → urgent."""
        pred = {
            "type": "graded",
            "input": "pf_ratio",
            "unit": "mmHg",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, 200], "severity": "urgent", "score": 2},
                {"range": [200, 300], "severity": "watch", "score": 1},
                {"range": [300, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is True  # not normal
        assert result.severity == "urgent"
        assert result.score == 2
        assert result.actual_value == 150.0

    def test_graded_normal(self, compiler: PredicateCompiler) -> None:
        """Value in normal band → met=False, severity=normal, score=0."""
        pred = {
            "type": "graded",
            "input": "pf_ratio",
            "unit": "mmHg",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, 200], "severity": "urgent", "score": 2},
                {"range": [200, 300], "severity": "watch", "score": 1},
                {"range": [300, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"pf_ratio": 350})
        assert result.met is False
        assert result.severity == "normal"
        assert result.score == 0

    def test_graded_boundary_lower(self, compiler: PredicateCompiler) -> None:
        """Value exactly at lower bound is included."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"x": 100})
        # 100 ≥ 100, 100 < None → second band (normal)
        assert result.severity == "normal"
        assert result.score == 0

        result2 = compiler.evaluate(compiled, {"x": 0})
        assert result2.severity == "critical"
        assert result2.score == 3

    def test_graded_non_numeric_value(self, compiler: PredicateCompiler) -> None:
        """Non-numeric value returns normal with met=False."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0, 100], "severity": "critical", "score": 3},
                {"range": [100, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"x": "invalid"})
        assert result.met is False
        assert result.severity == "normal"
        assert result.score == 0
        assert result.actual_value == "invalid"

    def test_graded_float_boundaries(self, compiler: PredicateCompiler) -> None:
        """Float boundaries work correctly."""
        pred = {
            "type": "graded",
            "input": "x",
            "unit": "",
            "bands": [
                {"range": [0.0, 1.5], "severity": "critical", "score": 3},
                {"range": [1.5, None], "severity": "normal", "score": 0},
            ],
        }
        compiled = compiler.compile(pred)
        assert compiler.evaluate(compiled, {"x": 1.499}).severity == "critical"
        assert compiler.evaluate(compiled, {"x": 1.5}).severity == "normal"


# =============================================================================
# Boolean Predicate Tests
# =============================================================================


class TestBooleanCompilation:
    """Compilation of boolean predicates."""

    def test_compile_boolean(self, compiler: PredicateCompiler) -> None:
        """Boolean predicate compiles with input name."""
        pred = {
            "type": "boolean",
            "input": "suspected_infection",
        }
        compiled = compiler.compile(pred)
        assert compiled.predicate_type == "boolean"
        assert compiled.input_name == "suspected_infection"
        assert isinstance(compiled.ast_node, BooleanNode)


class TestBooleanEvaluation:
    """Evaluation of boolean predicates."""

    def test_boolean_true(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """True value → met=True."""
        pred = {"type": "boolean", "input": "suspected_infection"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is True
        assert result.severity == "urgent"
        assert result.score == 1

    def test_boolean_false(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """False value → met=False."""
        pred = {"type": "boolean", "input": "antibiotico_1h"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is False
        assert result.severity == "normal"
        assert result.score == 0

    def test_boolean_truthy_number(self, compiler: PredicateCompiler) -> None:
        """Non-zero number is truthy."""
        pred = {"type": "boolean", "input": "count"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"count": 42})
        assert result.met is True

    def test_boolean_falsy_zero(self, compiler: PredicateCompiler) -> None:
        """Zero is falsy."""
        pred = {"type": "boolean", "input": "count"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"count": 0})
        assert result.met is False

    def test_boolean_falsy_empty_string(self, compiler: PredicateCompiler) -> None:
        """Empty string is falsy."""
        pred = {"type": "boolean", "input": "note"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"note": ""})
        assert result.met is False

    def test_boolean_truthy_nonempty_string(self, compiler: PredicateCompiler) -> None:
        """Non-empty string is truthy."""
        pred = {"type": "boolean", "input": "note"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"note": "ok"})
        assert result.met is True


# =============================================================================
# Composite Predicate Tests
# =============================================================================


class TestCompositeCompilation:
    """Compilation of composite predicates."""

    def test_compile_and_composite(self, compiler: PredicateCompiler) -> None:
        """AND composite compiles with sub-predicates."""
        pred = {
            "type": "composite",
            "combinator": "AND",
            "sub_predicates": [
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 2,
                    "unit": "mmol/L",
                },
                {"type": "boolean", "input": "suspected_infection"},
            ],
        }
        compiled = compiler.compile(pred)
        assert compiled.predicate_type == "composite"
        node = compiled.ast_node
        assert isinstance(node, CompositeNode)
        assert node.combinator == "AND"
        assert len(node.sub_predicates) == 2

    def test_compile_or_composite(self, compiler: PredicateCompiler) -> None:
        """OR composite compiles."""
        pred = {
            "type": "composite",
            "combinator": "OR",
            "sub_predicates": [
                {"type": "threshold", "input": "spo2", "operator": "<", "value": 92, "unit": "%"},
                {
                    "type": "threshold",
                    "input": "heart_rate",
                    "operator": ">",
                    "value": 120,
                    "unit": "bpm",
                },
            ],
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, CompositeNode)
        assert node.combinator == "OR"

    def test_invalid_combinator_raises(self, compiler: PredicateCompiler) -> None:
        """Invalid combinator raises ValueError."""
        pred = {
            "type": "composite",
            "combinator": "XOR",
            "sub_predicates": [{"type": "boolean", "input": "x"}],
        }
        with pytest.raises(ValueError, match="combinator"):
            compiler.compile(pred)

    def test_empty_sub_predicates_raises(self, compiler: PredicateCompiler) -> None:
        """Empty sub_predicates raises ValueError."""
        pred = {
            "type": "composite",
            "combinator": "AND",
            "sub_predicates": [],
        }
        with pytest.raises(ValueError, match="at least one sub_predicate"):
            compiler.compile(pred)

    def test_nested_composite(self, compiler: PredicateCompiler) -> None:
        """Nested composite (AND inside OR) compiles."""
        pred = {
            "type": "composite",
            "combinator": "OR",
            "sub_predicates": [
                {
                    "type": "composite",
                    "combinator": "AND",
                    "sub_predicates": [
                        {"type": "boolean", "input": "fever"},
                        {
                            "type": "threshold",
                            "input": "wbc",
                            "operator": ">",
                            "value": 12000,
                            "unit": "/mm3",
                        },
                    ],
                },
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 4,
                    "unit": "mmol/L",
                },
            ],
        }
        compiled = compiler.compile(pred)
        node = compiled.ast_node
        assert isinstance(node, CompositeNode)
        assert node.combinator == "OR"
        inner = node.sub_predicates[0].ast_node
        assert isinstance(inner, CompositeNode)
        assert inner.combinator == "AND"


class TestCompositeEvaluation:
    """Evaluation of composite predicates."""

    def test_and_both_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """AND with both sub-predicates met → met=True."""
        pred = {
            "type": "composite",
            "combinator": "AND",
            "sub_predicates": [
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 2,
                    "unit": "mmol/L",
                },
                {"type": "boolean", "input": "suspected_infection"},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is True
        assert result.severity == "urgent"  # max of urgent+urgent
        assert result.score == 2  # 1 + 1

    def test_and_one_not_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """AND with one sub-predicate not met → met=False."""
        pred = {
            "type": "composite",
            "combinator": "AND",
            "sub_predicates": [
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 2,
                    "unit": "mmol/L",
                },
                {"type": "boolean", "input": "antibiotico_1h"},  # False
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is False

    def test_or_one_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """OR with one sub-predicate met → met=True."""
        pred = {
            "type": "composite",
            "combinator": "OR",
            "sub_predicates": [
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 10,
                    "unit": "mmol/L",
                },  # False
                {"type": "boolean", "input": "suspected_infection"},  # True
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is True

    def test_or_none_met(self, compiler: PredicateCompiler, patient_data: dict) -> None:
        """OR with no sub-predicates met → met=False."""
        pred = {
            "type": "composite",
            "combinator": "OR",
            "sub_predicates": [
                {
                    "type": "threshold",
                    "input": "lactate",
                    "operator": ">",
                    "value": 10,
                    "unit": "mmol/L",
                },
                {"type": "boolean", "input": "antibiotico_1h"},
            ],
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        assert result.met is False

    def test_composite_severity_aggregation(self, compiler: PredicateCompiler) -> None:
        """Composite severity is the max severity among sub-results."""
        pred = {
            "type": "composite",
            "combinator": "OR",
            "sub_predicates": [
                {
                    "type": "graded",
                    "input": "pf_ratio",
                    "unit": "mmHg",
                    "bands": [
                        {"range": [0, 100], "severity": "critical", "score": 3},
                        {"range": [100, 200], "severity": "urgent", "score": 2},
                        {"range": [200, None], "severity": "normal", "score": 0},
                    ],
                },
                {"type": "boolean", "input": "suspected_infection"},
            ],
        }
        # pf_ratio=50 → critical(3), suspected_infection=True → urgent(1)
        compiled = compiler.compile(pred)
        result = compiler.evaluate(
            compiled,
            {
                "pf_ratio": 50,
                "suspected_infection": True,
            },
        )
        assert result.met is True
        assert result.severity == "critical"  # max(critical, urgent) → critical
        assert result.score == 4  # 3 + 1


# =============================================================================
# Edge Cases and Error Handling
# =============================================================================


class TestEdgeCases:
    """Edge cases for PredicateCompiler."""

    def test_unknown_predicate_type_raises(self, compiler: PredicateCompiler) -> None:
        """Unknown predicate type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown predicate type"):
            compiler.compile({"type": "imaginary", "input": "x"})

    def test_missing_type_raises(self, compiler: PredicateCompiler) -> None:
        """Missing 'type' field raises ValueError."""
        with pytest.raises(ValueError, match="must have a 'type'"):
            compiler.compile({"input": "x"})

    def test_unknown_node_type_in_evaluate(self, compiler: PredicateCompiler) -> None:
        """Unknown AST node type in evaluate raises ValueError."""

        class BogusNode(ASTNode):
            pass

        bogus = CompiledPredicate(
            ast_node=BogusNode(),
            input_name="x",
            unit="",
            predicate_type="bogus",
        )
        with pytest.raises(ValueError, match="Unknown AST node"):
            compiler.evaluate(bogus, {"x": 1})

    def test_compiled_predicate_is_hashable(self, compiler: PredicateCompiler) -> None:
        """CompiledPredicate is frozen/hashable (can be used as dict key)."""
        pred = {"type": "threshold", "input": "x", "operator": ">", "value": 5, "unit": ""}
        compiled = compiler.compile(pred)
        # If not hashable, this will raise TypeError
        d = {compiled: "test"}
        assert d[compiled] == "test"

    def test_evaluation_result_is_hashable(
        self, compiler: PredicateCompiler, patient_data: dict
    ) -> None:
        """EvaluationResult is frozen/hashable."""
        pred = {
            "type": "threshold",
            "input": "lactate",
            "operator": ">",
            "value": 2,
            "unit": "mmol/L",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, patient_data)
        d = {result: "test"}
        assert d[result] == "test"

    def test_threshold_infinity_value(self, compiler: PredicateCompiler) -> None:
        """Threshold with float('inf') works."""
        pred = {
            "type": "threshold",
            "input": "x",
            "operator": "<",
            "value": float("inf"),
            "unit": "",
        }
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"x": 1e9})
        assert result.met is True

    def test_threshold_negative_value(self, compiler: PredicateCompiler) -> None:
        """Negative threshold values work."""
        pred = {"type": "threshold", "input": "nif", "operator": "<", "value": -25, "unit": "cmH2O"}
        compiled = compiler.compile(pred)
        result = compiler.evaluate(compiled, {"nif": -30})
        assert result.met is True

        result2 = compiler.evaluate(compiled, {"nif": -20})
        assert result2.met is False


# =============================================================================
# End-to-end: YAML-like pathway evaluation
# =============================================================================


class TestEndToEndPathway:
    """Realistic pathway evaluation from YAML-like definitions."""

    def test_ventilacao_pf_ratio_graded(self, compiler: PredicateCompiler) -> None:
        """PF ratio graded predicate from ventilacao.yaml."""
        crit = {
            "id": "crit-vent-pf",
            "name": "Relação PaO₂/FiO₂",
            "category": "oxigenacao",
            "predicate": {
                "type": "graded",
                "input": "pf_ratio",
                "bands": [
                    {"range": [0, 100], "severity": "critical", "score": 3},
                    {"range": [100, 200], "severity": "urgent", "score": 2},
                    {"range": [200, 300], "severity": "watch", "score": 1},
                    {"range": [300, None], "severity": "normal", "score": 0},
                ],
                "unit": "mmHg",
            },
        }
        compiled = compiler.compile(crit["predicate"])

        # Patient with severe ARDS
        result = compiler.evaluate(compiled, {"pf_ratio": 85})
        assert result.met is True
        assert result.severity == "critical"
        assert result.score == 3

        # Patient with normal oxygenation
        result = compiler.evaluate(compiled, {"pf_ratio": 350})
        assert result.met is False
        assert result.severity == "normal"
        assert result.score == 0

    def test_ventilacao_peep_threshold(self, compiler: PredicateCompiler) -> None:
        """PEEP threshold from ventilacao.yaml."""
        crit = {
            "id": "crit-vent-peep",
            "name": "PEEP",
            "category": "parametros",
            "predicate": {
                "type": "threshold",
                "input": "peep",
                "operator": ">=",
                "value": 5,
                "unit": "cmH2O",
            },
        }
        compiled = compiler.compile(crit["predicate"])

        assert compiler.evaluate(compiled, {"peep": 8}).met is True
        assert compiler.evaluate(compiled, {"peep": 5}).met is True  # boundary
        assert compiler.evaluate(compiled, {"peep": 3}).met is False

    def test_multiple_criteria_evaluation(self, compiler: PredicateCompiler) -> None:
        """Evaluate all criteria from a simplified pathway."""
        criteria = [
            {
                "id": "crit-pf",
                "predicate": {
                    "type": "graded",
                    "input": "pf_ratio",
                    "unit": "mmHg",
                    "bands": [
                        {"range": [0, 100], "severity": "critical", "score": 3},
                        {"range": [100, 200], "severity": "urgent", "score": 2},
                        {"range": [200, None], "severity": "normal", "score": 0},
                    ],
                },
            },
            {
                "id": "crit-peep",
                "predicate": {
                    "type": "threshold",
                    "input": "peep",
                    "operator": ">=",
                    "value": 5,
                    "unit": "cmH2O",
                },
            },
            {
                "id": "crit-infection",
                "predicate": {
                    "type": "boolean",
                    "input": "suspected_infection",
                },
            },
        ]

        patient = {
            "pf_ratio": 150,
            "peep": 8,
            "suspected_infection": True,
        }

        compiled_criteria = [(c["id"], compiler.compile(c["predicate"])) for c in criteria]

        results = {cid: compiler.evaluate(compiled, patient) for cid, compiled in compiled_criteria}

        assert results["crit-pf"].severity == "urgent"
        assert results["crit-peep"].met is True
        assert results["crit-infection"].met is True


# =============================================================================
# Security: NO eval/exec
# =============================================================================


class TestSecurityNoEvalExec:
    """Verify no eval() or exec() in the compiler module."""

    def test_no_eval_in_source(self) -> None:
        """The source file of trilhas_compiler must not contain eval( or exec( calls."""
        import intensicare.services.trilhas_compiler as compiler_mod

        source_path = compiler_mod.__file__
        assert source_path is not None

        with open(source_path, "r") as f:
            source = f.read()

        # Use AST to check for actual function calls — more robust than string scan
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in ("eval", "exec"):
                    pytest.fail(f"eval()/exec() call found at line {node.lineno}")
                if (
                    isinstance(func, ast.Attribute)
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "builtins"
                    and func.attr in ("eval", "exec")
                ):
                    pytest.fail(f"builtins.eval()/exec() call found at line {node.lineno}")

    def test_only_operator_module_for_comparisons(self) -> None:
        """Comparisons should use operator module, not dynamic dispatch."""
        import intensicare.services.trilhas_compiler as compiler_mod

        source_path = compiler_mod.__file__
        assert source_path is not None

        with open(source_path, "r") as f:
            source = f.read()

        # The operator module is imported
        assert "import operator" in source or "from operator import" in source

        # _OPS dict maps strings to operator functions
        assert "_OPS" in source

    def test_no_dynamic_attribute_access(self) -> None:
        """The compiler must not use getattr(obj, user_input) patterns."""
        import intensicare.services.trilhas_compiler as compiler_mod

        source_path = compiler_mod.__file__
        assert source_path is not None

        with open(source_path, "r") as f:
            source = f.read()

        # getattr is used internally by dataclasses, but should not be used
        # for dynamic dispatch from user input
        # We check there's no getattr with a variable second argument
        assert "getattr(" not in source, "getattr() found in source"

    def test_safe_dict_lookup_only(self, compiler: PredicateCompiler) -> None:
        """_lookup only does dict key access via patient_data[input_name]."""
        import inspect

        import intensicare.services.trilhas_compiler as compiler_mod

        # Parse the AST of the _lookup method to verify no attribute chaining
        lookup_source = inspect.getsource(compiler_mod.PredicateCompiler._lookup)
        tree = ast.parse(textwrap.dedent(lookup_source))

        # Check for any attribute access on patient_data (except dict operations)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and (
                isinstance(node.value, ast.Name)
                and node.value.id == "patient_data"
                and node.attr not in ("keys", "get", "items", "values")
            ):
                pytest.fail(
                    f"Dangerous attribute access on patient_data: "
                    f"patient_data.{node.attr} at line {node.lineno}"
                )
