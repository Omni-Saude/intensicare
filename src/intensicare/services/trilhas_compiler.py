"""Secure AST-based predicate compiler for YAML pathway definitions.

Per ADR-0020: NO eval()/exec(). Uses Python operator module + safe dict lookup.

Supports predicate types:
  - threshold: single value comparison
  - graded: band-based evaluation with severity/score
  - boolean: simple truthy/falsy check from patient data
  - composite: AND/OR combinations of sub-predicates

Reference schema: /_work/alerts/schema/pathway.schema.json
"""

from __future__ import annotations

import hashlib
import json
import logging
import operator
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safe operator map — NO eval/exec, only Python operator module
# ---------------------------------------------------------------------------

_OPS: dict[str, Callable[[Any, Any], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}

_VALID_OPERATORS: frozenset[str] = frozenset(_OPS.keys())


# ---------------------------------------------------------------------------
# Content-addressing: SHA-256 hash for pathway definitions
# ---------------------------------------------------------------------------


def compute_content_hash(definition: dict) -> str:
    """Compute SHA-256 content hash for a pathway definition.

    Produces a deterministic, content-addressed hash that uniquely
    identifies the semantic content of a pathway definition. The same
    definition will always produce the same hash regardless of dict
    key ordering, whitespace in YAML serialisation, or platform.

    Used by the YAML loading flow to stamp definition_version_id
    on compiled PathwayDefinition instances, providing immutable
    content-addressed traceability per ADR-020/ADR-021.

    Args:
        definition: A pathway definition dict (typically the raw YAML
                    content loaded via yaml.safe_load).

    Returns:
        64-character lowercase hex SHA-256 digest.
    """
    canonical = json.dumps(definition, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

# ---------------------------------------------------------------------------
# AST Nodes
# ---------------------------------------------------------------------------


class ASTNode:
    """Base class for predicate AST nodes."""
    __slots__ = ()


@dataclass(frozen=True)
class Band:
    """A single severity band for graded predicates.

    lower: inclusive lower bound
    upper: exclusive upper bound (None = +∞)
    """
    lower: float
    upper: float | None
    severity: str
    score: int
    label: str | None = None

    def contains(self, value: float) -> bool:
        """Check if value falls within this band: lower ≤ value < upper."""
        if value < self.lower:
            return False
        if self.upper is not None and value >= self.upper:
            return False
        return True


@dataclass(frozen=True)
class ThresholdNode(ASTNode):
    """Threshold predicate: single value comparison."""
    input_name: str
    operator: str
    value: float
    unit: str


@dataclass(frozen=True)
class GradedNode(ASTNode):
    """Graded predicate: band-based evaluation.

    Bands are stored sorted by lower bound.
    """
    input_name: str
    bands: tuple[Band, ...]
    unit: str


@dataclass(frozen=True)
class BooleanNode(ASTNode):
    """Boolean predicate: check truthiness of a data field."""
    input_name: str


@dataclass(frozen=True)
class CompositeNode(ASTNode):
    """Composite predicate: AND/OR combination of sub-predicates.

    Each sub_predicate is a CompiledPredicate instance.
    """
    combinator: str  # "AND" or "OR"
    sub_predicates: tuple[CompiledPredicate, ...]


# ---------------------------------------------------------------------------
# Compiled form and evaluation result
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluationResult:
    """Result of evaluating a compiled predicate against patient data.

    Attributes:
        met: Whether the predicate condition is satisfied.
             - threshold: comparison result
             - graded: True if severity is not 'normal'
             - boolean: truthiness of the data field
             - composite: combined AND/OR result
        severity: Canonical severity (normal, watch, urgent, critical).
        score: Numeric score (0 for non-graded, band score for graded).
        actual_value: The value retrieved from patient_data.
        input_name: Which input field was evaluated.
        unit: Canonical unit string.
        band_label: Optional human-readable band label (graded only).
    """
    met: bool
    severity: str = "normal"
    score: int = 0
    actual_value: Any = None
    input_name: str = ""
    unit: str = ""
    band_label: str | None = None


@dataclass(frozen=True)
class CompiledPredicate:
    """Compiled, evaluable form of a predicate.

    Holds the AST node plus metadata needed for evaluation.
    """
    ast_node: ASTNode
    input_name: str
    unit: str
    predicate_type: str  # "threshold" | "graded" | "boolean" | "composite"


# ---------------------------------------------------------------------------
# PredicateCompiler
# ---------------------------------------------------------------------------


class PredicateCompiler:
    """Secure, AST-based predicate compiler.

    Reads predicate dicts (from YAML pathway definitions) and compiles
    them into CompiledPredicate instances that can be evaluated safely
    against patient data dicts.

    Usage::

        compiler = PredicateCompiler()
        compiled = compiler.compile(predicate_dict)
        result = compiler.evaluate(compiled, patient_data)
    """

    def compile(self, predicate: dict) -> CompiledPredicate:
        """Compile a predicate dict into an evaluable CompiledPredicate.

        Args:
            predicate: Dict matching the JSON Schema predicate definition
                       (type, input, unit, operator, value, bands, etc.)

        Returns:
            CompiledPredicate ready for evaluation.

        Raises:
            ValueError: If the predicate dict is structurally invalid.
        """
        ptype = predicate.get("type")
        if not ptype:
            raise ValueError("Predicate must have a 'type' field")

        if ptype == "threshold":
            return self._compile_threshold(predicate)
        elif ptype == "graded":
            return self._compile_graded(predicate)
        elif ptype == "boolean":
            return self._compile_boolean(predicate)
        elif ptype == "composite":
            return self._compile_composite(predicate)
        else:
            raise ValueError(f"Unknown predicate type: {ptype}")

    def evaluate(
        self, compiled: CompiledPredicate, patient_data: dict
    ) -> EvaluationResult:
        """Evaluate a compiled predicate against patient data.

        Args:
            compiled: A CompiledPredicate from compile().
            patient_data: Dict mapping input names to their values.

        Returns:
            EvaluationResult with met, severity, score, actual_value, etc.

        Raises:
            KeyError: If the required input is missing from patient_data.
        """
        node = compiled.ast_node

        if isinstance(node, ThresholdNode):
            return self._evaluate_threshold(node, patient_data)
        elif isinstance(node, GradedNode):
            return self._evaluate_graded(node, patient_data)
        elif isinstance(node, BooleanNode):
            return self._evaluate_boolean(node, patient_data)
        elif isinstance(node, CompositeNode):
            return self._evaluate_composite(node, patient_data)
        else:
            raise ValueError(f"Unknown AST node type: {type(node).__name__}")

    # ── Compile helpers ────────────────────────────────────────────────

    def _compile_threshold(self, pred: dict) -> CompiledPredicate:
        """Compile a threshold predicate."""
        input_name = pred.get("input", "")
        if not input_name:
            raise ValueError("threshold predicate missing 'input' field")

        op = pred.get("operator", ">=")
        if op not in _VALID_OPERATORS:
            raise ValueError(f"Invalid operator '{op}'. Valid: {sorted(_VALID_OPERATORS)}")

        raw_value = pred.get("value")
        if raw_value is None:
            raise ValueError("threshold predicate missing 'value' field")

        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"threshold predicate 'value' must be numeric, got {raw_value!r}"
            ) from exc

        unit = pred.get("unit", "")

        node = ThresholdNode(
            input_name=input_name,
            operator=op,
            value=value,
            unit=unit,
        )
        return CompiledPredicate(
            ast_node=node,
            input_name=input_name,
            unit=unit,
            predicate_type="threshold",
        )

    def _compile_graded(self, pred: dict) -> CompiledPredicate:
        """Compile a graded predicate with band validation."""
        input_name = pred.get("input", "")
        if not input_name:
            raise ValueError("graded predicate missing 'input' field")

        unit = pred.get("unit", "")
        raw_bands: list[dict] = pred.get("bands", [])

        if not raw_bands:
            raise ValueError("graded predicate must have at least one band")

        bands: list[Band] = []
        for i, bd in enumerate(raw_bands):
            rng: list = bd.get("range", [])
            if len(rng) != 2:
                raise ValueError(
                    f"Band {i} range must have exactly 2 elements [lower, upper]"
                )

            lower = float(rng[0])
            upper_raw = rng[1]
            upper: float | None = None if upper_raw is None else float(upper_raw)

            if upper is not None and lower >= upper:
                raise ValueError(
                    f"Band {i} has invalid range: lower ({lower}) >= upper ({upper})"
                )

            severity = bd.get("severity", "normal")
            score = int(bd.get("score", 0))
            label = bd.get("label")

            bands.append(Band(
                lower=lower,
                upper=upper,
                severity=severity,
                score=score,
                label=label,
            ))

        # Validate band continuity (Gate B logic inlined for efficiency)
        sorted_bands = sorted(bands, key=lambda b: b.lower)
        for i in range(len(sorted_bands) - 1):
            curr = sorted_bands[i]
            nxt = sorted_bands[i + 1]
            if curr.upper is None:
                raise ValueError(
                    f"Band {i} (lower={curr.lower}) has null upper bound but is not "
                    f"the last band — band {i + 1} (lower={nxt.lower}) follows it"
                )
            if curr.upper != nxt.lower:
                raise ValueError(
                    f"Band gap or overlap between band {i} (upper={curr.upper}) "
                    f"and band {i + 1} (lower={nxt.lower})"
                )

        if sorted_bands[-1].upper is not None:
            raise ValueError(
                "Last band must have null upper bound (cover to +∞)"
            )

        node = GradedNode(
            input_name=input_name,
            bands=tuple(sorted_bands),
            unit=unit,
        )
        return CompiledPredicate(
            ast_node=node,
            input_name=input_name,
            unit=unit,
            predicate_type="graded",
        )

    def _compile_boolean(self, pred: dict) -> CompiledPredicate:
        """Compile a boolean predicate."""
        input_name = pred.get("input", "")
        if not input_name:
            raise ValueError("boolean predicate missing 'input' field")

        node = BooleanNode(input_name=input_name)
        return CompiledPredicate(
            ast_node=node,
            input_name=input_name,
            unit=pred.get("unit", ""),
            predicate_type="boolean",
        )

    def _compile_composite(self, pred: dict) -> CompiledPredicate:
        """Compile a composite predicate (AND/OR).

        Composite predicates are compiled but evaluation may be deferred
        to M3. The structure is fully supported in the AST.
        """
        combinator = pred.get("combinator", "AND")
        if combinator not in ("AND", "OR"):
            raise ValueError(
                f"Composite combinator must be 'AND' or 'OR', got '{combinator}'"
            )

        sub_preds: list[dict] = pred.get("sub_predicates", [])
        if not sub_preds:
            raise ValueError("composite predicate must have at least one sub_predicate")

        compiled_subs: list[CompiledPredicate] = []
        for i, sp in enumerate(sub_preds):
            try:
                compiled_subs.append(self.compile(sp))
            except ValueError as exc:
                raise ValueError(
                    f"sub_predicate[{i}]: {exc}"
                ) from exc

        node = CompositeNode(
            combinator=combinator,
            sub_predicates=tuple(compiled_subs),
        )
        return CompiledPredicate(
            ast_node=node,
            input_name="",  # composite has no single input
            unit="",
            predicate_type="composite",
        )

    # ── Evaluate helpers ───────────────────────────────────────────────

    def _evaluate_threshold(
        self, node: ThresholdNode, patient_data: dict
    ) -> EvaluationResult:
        """Evaluate a threshold node against patient data."""
        actual_value = self._lookup(node.input_name, patient_data)
        op_func = _OPS[node.operator]

        try:
            met = bool(op_func(actual_value, node.value))
        except TypeError:
            # Non-numeric comparison attempt — treat as not met
            logger.warning(
                "Cannot compare %r %s %r for input '%s'",
                actual_value, node.operator, node.value, node.input_name,
            )
            met = False

        severity = "urgent" if met else "normal"
        score = 1 if met else 0

        return EvaluationResult(
            met=met,
            severity=severity,
            score=score,
            actual_value=actual_value,
            input_name=node.input_name,
            unit=node.unit,
        )

    def _evaluate_graded(
        self, node: GradedNode, patient_data: dict
    ) -> EvaluationResult:
        """Evaluate a graded node against patient data.

        Finds the band containing the actual value. If no band matches
        (shouldn't happen with valid bands), defaults to normal.
        """
        actual_value = self._lookup(node.input_name, patient_data)

        try:
            val = float(actual_value)
        except (TypeError, ValueError):
            return EvaluationResult(
                met=False,
                severity="normal",
                score=0,
                actual_value=actual_value,
                input_name=node.input_name,
                unit=node.unit,
            )

        # Find matching band (binary search not needed — typical band count ≤ 10)
        matched_band: Band | None = None
        for band in node.bands:
            if band.contains(val):
                matched_band = band
                break

        if matched_band is None:
            # Shouldn't happen if bands are continuous, but guard
            return EvaluationResult(
                met=False,
                severity="normal",
                score=0,
                actual_value=actual_value,
                input_name=node.input_name,
                unit=node.unit,
            )

        met = matched_band.severity != "normal"

        return EvaluationResult(
            met=met,
            severity=matched_band.severity,
            score=matched_band.score,
            actual_value=actual_value,
            input_name=node.input_name,
            unit=node.unit,
            band_label=matched_band.label,
        )

    def _evaluate_boolean(
        self, node: BooleanNode, patient_data: dict
    ) -> EvaluationResult:
        """Evaluate a boolean node against patient data."""
        actual_value = self._lookup(node.input_name, patient_data)
        met = bool(actual_value)

        severity = "urgent" if met else "normal"
        score = 1 if met else 0

        return EvaluationResult(
            met=met,
            severity=severity,
            score=score,
            actual_value=actual_value,
            input_name=node.input_name,
        )

    def _evaluate_composite(
        self, node: CompositeNode, patient_data: dict
    ) -> EvaluationResult:
        """Evaluate a composite (AND/OR) node.

        For AND: all sub-predicates must be met.
        For OR: at least one sub-predicate must be met.

        Severity is the maximum severity among sub-results.
        Score is the sum of sub-scores.
        """
        sub_results: list[EvaluationResult] = []
        for cp in node.sub_predicates:
            sub_results.append(self.evaluate(cp, patient_data))

        if node.combinator == "AND":
            met = all(r.met for r in sub_results)
        else:  # OR
            met = any(r.met for r in sub_results)

        # Aggregate severity: maximum severity across sub-results
        severity_order = {"normal": 0, "watch": 1, "urgent": 2, "critical": 3}
        max_severity = "normal"
        for r in sub_results:
            if severity_order.get(r.severity, 0) > severity_order.get(max_severity, 0):
                max_severity = r.severity

        total_score = sum(r.score for r in sub_results)

        # For composite, actual_value is a list of sub-results
        return EvaluationResult(
            met=met,
            severity=max_severity,
            score=total_score,
            actual_value=[r.actual_value for r in sub_results],
            input_name="composite",
            unit="",
        )

    # ── Utilities ──────────────────────────────────────────────────────

    @staticmethod
    def _lookup(input_name: str, patient_data: dict) -> Any:
        """Safely look up an input from patient_data.

        Only supports direct key lookup in the patient_data dict.
        No attribute chaining, no eval, no exec.
        """
        if input_name not in patient_data:
            raise KeyError(
                f"Required input '{input_name}' not found in patient_data. "
                f"Available keys: {sorted(patient_data.keys())}"
            )
        return patient_data[input_name]
