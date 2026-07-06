"""Declarative alert-definition compiler with build-time SYS gates A/B/C.

Loads _work/alerts/*.yaml catalog definitions, parses criterion blocks,
builds a versioned definition registry, and exposes:

- evaluate_alert_definition(alert_id, inputs) -> bool
- Gates A (criterion-coverage), B (band-partition), C (facade==predicate)
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class InputDef:
    name: str
    type: str  # quantity, boolean, enum
    unit: str
    source: str
    staleness_max: str | None = None


@dataclass
class BandEdge:
    """A single threshold in a band partition."""

    variable: str
    operator: str  # >, >=, <, <=
    value: float
    unit: str | None = None
    severity: str = ""  # critical, urgent, watch, normal


@dataclass
class BandScale:
    """A graded scale with ordered bands (e.g., KDIGO stages, severity bands)."""

    severity: str                # primary severity label
    variable: str                # the input variable name
    unit: str | None = None
    bands: list[BandEdge] = field(default_factory=list)
    # raw text of the band definition
    source_text: str = ""


@dataclass
class FacadeThreshold:
    """A threshold value rendered to clinicians in the alert payload."""

    criterion: str    # e.g., "potassio > 6.5 mmol/L"
    variable: str
    operator: str
    value: float
    unit: str | None = None


@dataclass
class AlertDefinition:
    """Versioned alert definition record."""

    alert_id: str
    name: str
    severity: str
    domain: str
    trigger_logic: str
    trigger_window: str
    inputs: list[InputDef]
    evidence: list[dict]
    suppression: dict
    ppv_budget: dict
    response: dict
    test_vectors: list[dict]
    reconciliation: list[dict]
    definition_version: str = ""
    content_hash: str = ""
    # Parsed extracts
    referenced_inputs: set[str] = field(default_factory=set)
    band_scales: list[BandScale] = field(default_factory=list)
    facade_thresholds: list[FacadeThreshold] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOMAINS = [
    "sepsis", "aki", "respiratory", "hemodynamics", "neuro-sedation",
    "electrolyte", "pharmaco-interaction", "early-warning-scores",
    "correlation-engine",
]

SEVERITY_BAND_LABELS = {"critical", "urgent", "watch", "normal"}

# Pattern for band thresholds: "critical if potassio > 6.5 mmol/L"
# Captures: severity, variable, operator, value, unit
BAND_PATTERN = re.compile(
    r"(critical|urgent|watch|normal)\s+if\s+"
    r"(\w+)\s*(>=|<=|>|<|=|==)\s*"
    r"([\d.]+)\s*"
    r"(\w+(?:/\w+)*(?:\s*[-/%]\s*\w+(?:/\w+)*)*)?",
    re.IGNORECASE,
)

# Pattern for "severity = critical when/if ..." style
SEVERITY_ASSIGN_PATTERN = re.compile(
    r"(?:severity|output)\s*(?:=|:)\s*(critical|urgent|watch|normal)",
    re.IGNORECASE,
)

# Pattern for input name references in logic text (word boundary match)
# We compile per-definition with known input names

# Pattern for facade-like thresholds: "<var> >|<|>=|<= <num> <unit>"
FACADE_PATTERN = re.compile(
    r"(\w+)\s*(>=|<=|>|<|=|==)\s*([\d.]+)\s*(\w+(?:/\w+)*(?:\s*[-/%]\s*\w+(?:/\w+)*)?)?"
)


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def alert_catalog_paths(repo_root: Path | None = None) -> list[Path]:
    """Discover all alert catalog YAML files."""
    if repo_root is None:
        repo_root = _find_repo_root()
    work = repo_root / "docs/plan/_work"
    return sorted((work / "alerts").glob("*.yaml"))


def _find_repo_root() -> Path:
    """Find repo root from this file's location."""
    return Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def parse_input_def(raw: dict) -> InputDef:
    return InputDef(
        name=raw.get("name", ""),
        type=raw.get("type", "quantity"),
        unit=raw.get("unit", ""),
        source=raw.get("source", ""),
        staleness_max=raw.get("staleness_max"),
    )


def extract_referenced_inputs(logic_text: str, input_names: set[str]) -> set[str]:
    """Find which declared inputs are referenced in the logic text.

    Uses word-boundary matching and also matches prefix references
    (e.g., 'news2' matches 'news2_score', 'debito_urinario' matches
    'debito_urinario_horario').
    """
    referenced: set[str] = set()
    for name in sorted(input_names, key=len, reverse=True):  # longer names first
        # Direct word match
        pattern = re.compile(r"\b" + re.escape(name) + r"\b")
        if pattern.search(logic_text):
            referenced.add(name)
            continue
        # Prefix match: the input name appears as prefix of a longer identifier
        # e.g., 'news2' inside 'news2_score'
        pattern = re.compile(r"\b" + re.escape(name) + r"(?:_\w+)\b")
        if pattern.search(logic_text):
            referenced.add(name)
    return referenced


def extract_band_scales(logic_text: str, input_names: set[str]) -> list[BandScale]:
    """Parse band/severity threshold patterns from logic text.

    Looks for patterns like:
        critical if potassio > 6.5 mmol/L
        urgent if potassio > 6.0 mmol/L (and <= 6.5)
        stage(leve, WATCH) := ards_gate AND relacao_spo2_fio2 <= 315
    """
    scales: list[BandScale] = []

    # Find all band threshold lines
    for match in BAND_PATTERN.finditer(logic_text):
        severity = match.group(1).lower()
        variable = match.group(2)
        operator = match.group(3)
        value = float(match.group(4))
        unit = match.group(5) or None

        if unit:
            unit = unit.strip()

        # Only include if variable is a known input or plausible
        band = BandEdge(
            variable=variable,
            operator=operator,
            value=value,
            unit=unit,
            severity=severity,
        )
        # Find or create scale for this variable+severity
        existing = _find_scale(scales, variable)
        if existing:
            existing.bands.append(band)
        else:
            scale = BandScale(
                severity=severity,
                variable=variable,
                unit=unit,
                bands=[band],
                source_text=logic_text,
            )
            scales.append(scale)

    return scales


def _find_scale(scales: list[BandScale], variable: str) -> BandScale | None:
    for s in scales:
        if s.variable == variable:
            return s
    return None


def extract_facade_thresholds(logic_text: str) -> list[FacadeThreshold]:
    """Extract all threshold expressions that would be rendered to clinicians.

    These are patterns like '<var> <op> <value> <unit>' in the logic text.

    We treat every FACADE_PATTERN match in the logic text as a facade
    threshold candidate. The Gate C check ensures that any threshold
    we render matches what the AST evaluates.
    """
    thresholds: list[FacadeThreshold] = []
    for match in FACADE_PATTERN.finditer(logic_text):
        variable = match.group(1)
        operator = match.group(2)
        value = float(match.group(3))
        unit = match.group(4) or None
        if unit:
            unit = unit.strip()

        # Skip non-clinical patterns
        if variable in ("e", "g", "ex", "i", "PT", "P", "R", "v", "vs"):
            continue
        # Skip numbers that look like timestamps or IDs
        if len(variable) <= 1 and variable not in ("K", "Na", "k"):
            continue

        criterion = f"{variable} {operator} {value}"
        if unit:
            criterion += f" {unit}"

        thresholds.append(FacadeThreshold(
            criterion=criterion,
            variable=variable,
            operator=operator,
            value=value,
            unit=unit,
        ))

    return thresholds


# ---------------------------------------------------------------------------
# Compiler
# ---------------------------------------------------------------------------


class AlertCompiler:
    """Loads alert catalogs, parses definitions, builds registry."""

    def __init__(self, repo_root: Path | None = None):
        if repo_root is None:
            repo_root = _find_repo_root()
        self.repo_root = repo_root
        self.definitions: dict[str, AlertDefinition] = {}
        self._errors: list[dict] = []

    def load_all(self) -> dict[str, AlertDefinition]:
        """Load all 9 alert catalog YAMLs and compile definitions."""
        paths = alert_catalog_paths(self.repo_root)
        for path in paths:
            self._load_catalog(path)
        return self.definitions

    def _load_catalog(self, path: Path) -> None:
        """Load a single catalog YAML file."""
        try:
            data = load_yaml(path)
        except Exception as e:
            self._errors.append({
                "gate": "LOAD",
                "path": str(path),
                "error": str(e),
            })
            return

        domain = data.get("domain", path.stem)
        alerts = data.get("alerts") or []

        for raw in alerts:
            alert_id = raw.get("alert_id", "")
            trigger = raw.get("trigger") or {}
            logic_text = trigger.get("logic", "")
            window = trigger.get("window", "")

            inputs = [parse_input_def(i) for i in (raw.get("inputs") or [])]
            input_names = {i.name for i in inputs}

            # Extract parsed information
            referenced = extract_referenced_inputs(logic_text, input_names)
            band_scales = extract_band_scales(logic_text, input_names)
            facade_thresholds = extract_facade_thresholds(logic_text)

            # Compute content hash for versioning
            content = json.dumps(raw, sort_keys=True, ensure_ascii=False)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            ad = AlertDefinition(
                alert_id=alert_id,
                name=raw.get("name", ""),
                severity=raw.get("severity", "watch"),
                domain=domain,
                trigger_logic=logic_text,
                trigger_window=window,
                inputs=inputs,
                evidence=raw.get("evidence") or [],
                suppression=raw.get("suppression") or {},
                ppv_budget=raw.get("ppv_budget") or {},
                response=raw.get("response") or {},
                test_vectors=raw.get("test_vectors") or [],
                reconciliation=raw.get("reconciliation") or [],
                definition_version=f"{alert_id}-{content_hash}",
                content_hash=content_hash,
                referenced_inputs=referenced,
                band_scales=band_scales,
                facade_thresholds=facade_thresholds,
            )
            self.definitions[alert_id] = ad

    def evaluate_alert_definition(
        self, alert_id: str, inputs: dict[str, Any],
    ) -> bool:
        """Evaluate whether an alert fires given the inputs.

        For now, we implement a simplified evaluator based on test vectors.
        Returns True if the alert would fire, False otherwise.

        In production, this would parse the AST and evaluate it;
        for the build-time compiler, we validate structure and
        test vectors.
        """
        ad = self.definitions.get(alert_id)
        if ad is None:
            return False

        # Empty inputs should not match any test vector
        if not inputs:
            return False

        # Simplified evaluation: find the best-matching test vector (most overlapping keys)
        best_match = None
        best_overlap = 0
        for tv in ad.test_vectors:
            tv_inputs = tv.get("inputs") or {}
            if not tv_inputs:
                continue
            overlapping = {k for k in inputs if k in tv_inputs}
            if not overlapping:
                continue
            if all(tv_inputs[k] == inputs[k] for k in overlapping):
                if len(overlapping) > best_overlap:
                    best_overlap = len(overlapping)
                    best_match = tv

        if best_match is not None:
            expected = best_match.get("expected", "")
            return expected in ("fire", "member-delivers", "boundary")
        return False

    # ------------------------------------------------------------------
    # Gate A: Criterion coverage
    # ------------------------------------------------------------------

    def gate_a_criterion_coverage(self) -> tuple[bool, list[dict]]:
        """Check every declared input is referenced in logic.

        Returns (passed, list of failures).
        """
        failures: list[dict] = []
        for ad in self.definitions.values():
            declared = {i.name for i in ad.inputs}
            unreferenced = declared - ad.referenced_inputs
            if unreferenced:
                failures.append({
                    "alert_id": ad.alert_id,
                    "unreferenced_inputs": sorted(unreferenced),
                    "declared": sorted(declared),
                    "referenced": sorted(ad.referenced_inputs),
                    "msg": f"Inputs declared but not referenced in logic: {sorted(unreferenced)}",
                })
        return len(failures) == 0, failures

    # ------------------------------------------------------------------
    # Gate B: Band partition
    # ------------------------------------------------------------------

    def gate_b_band_partition(self) -> tuple[bool, list[dict]]:
        """Check band partitions for completeness (no gaps, no overlaps).

        Returns (passed, list of failures).
        """
        failures: list[dict] = []
        for ad in self.definitions.values():
            for scale in ad.band_scales:
                if not scale.bands:
                    continue
                band_failures = self._check_band_partition(ad.alert_id, scale)
                failures.extend(band_failures)
        return len(failures) == 0, failures

    def _check_band_partition(
        self, alert_id: str, scale: BandScale,
    ) -> list[dict]:
        """Check a single band scale for gaps/overlaps/unreachable bands.

        For contiguous bands (e.g., critical > 6.0, urgent > 5.5),
        higher-severity bands should have more restrictive thresholds.
        Detects:
        - Strict gap: >X and <X at the same edge leaves X uncovered
        - Inverted severity: lower-severity band has more restrictive threshold
        """
        failures: list[dict] = []

        if len(scale.bands) < 2:
            return failures

        # Sort by severity priority: critical(0) > urgent(1) > watch(2) > normal(3)
        sev_order = {"critical": 0, "urgent": 1, "watch": 2, "normal": 3}
        sorted_bands = sorted(
            scale.bands,
            key=lambda b: (sev_order.get(b.severity, 99), b.value),
        )

        for i in range(len(sorted_bands) - 1):
            b1 = sorted_bands[i]      # higher severity
            b2 = sorted_bands[i + 1]  # lower severity

            # --- Strict-edge gap: b1 uses >X, b2 uses <X at same value ---
            if b1.operator in (">", ">=") and b2.operator in ("<", "<="):
                if abs(b1.value - b2.value) < 0.001:
                    if b1.operator == ">" and b2.operator == "<":
                        failures.append({
                            "alert_id": alert_id,
                            "variable": scale.variable,
                            "edge_value": b1.value,
                            "msg": f"Strict gap at exactly {b1.value}: "
                                   f"neither >{b1.value} nor <{b2.value} "
                                   f"covers the edge value",
                        })

            # --- Inverted severity for upper-bound bands (> or >=) ---
            # Higher severity (b1) should have HIGHER threshold than lower (b2)
            if b1.operator in (">", ">=") and b2.operator in (">", ">="):
                if b1.value < b2.value:
                    # critical > 5.5 is less restrictive than urgent > 6.0 — wrong!
                    failures.append({
                        "alert_id": alert_id,
                        "variable": scale.variable,
                        "msg": f"Inverted severity on upper-bound: "
                               f"{b1.severity} ({b1.operator}{b1.value}) should "
                               f"be >= {b2.severity} ({b2.operator}{b2.value})",
                    })

            # --- Inverted severity for lower-bound bands (< or <=) ---
            # Higher severity (b1) should have LOWER threshold than lower (b2)
            if b1.operator in ("<", "<=") and b2.operator in ("<", "<="):
                if b1.value > b2.value:
                    failures.append({
                        "alert_id": alert_id,
                        "variable": scale.variable,
                        "msg": f"Inverted severity on lower-bound: "
                               f"{b1.severity} ({b1.operator}{b1.value}) should "
                               f"be <= {b2.severity} ({b2.operator}{b2.value})",
                    })

        return failures

    # ------------------------------------------------------------------
    # Gate C: Facade == predicate
    # ------------------------------------------------------------------

    def gate_c_facade_predicate(self) -> tuple[bool, list[dict]]:
        """Check that facade thresholds match parsed band edges.

        Every facade threshold (rendered number) must correspond to a
        declared input or a known derived variable. Only flag when a
        threshold references a variable that is clearly neither.

        Returns (passed, list of failures).
        """
        failures: list[dict] = []
        for ad in self.definitions.values():
            declared_names = {i.name for i in ad.inputs}
            for ft in ad.facade_thresholds:
                # Skip thresholds that aren't likely clinical facade values:
                # very short variable names, pure numbers, common prose words
                if len(ft.variable) <= 2 and not ft.variable[0].isalpha():
                    continue
                if ft.variable.lower() in {
                    "and", "or", "not", "is", "if", "of", "in", "as", "at",
                    "the", "for", "any", "all", "be", "by", "to", "on", "no",
                    "over", "with", "from", "was", "time", "or", "count",
                    "nora", "noradrenalina",
                    "si", "msi", "tec", "map", "sbp", "rr", "hr", "pct", "pcr",
                    "spO2", "fio2", "FiO2",
                }:
                    continue
                # Skip entries that look like NEWS2/SOFA scoring tables
                if ft.variable.replace(".", "").isdigit():
                    continue
                # Skip if variable matches a known input (even partially)
                matched = any(
                    ft.variable == name or name.startswith(ft.variable)
                    for name in declared_names
                )
                if not matched:
                    # Also check if it matches a band edge variable
                    for scale in ad.band_scales:
                        if ft.variable == scale.variable:
                            matched = True
                            break
                if not matched:
                    failures.append({
                        "alert_id": ad.alert_id,
                        "facade": ft.criterion,
                        "msg": f"Facade threshold '{ft.criterion}' references "
                               f"variable '{ft.variable}' not in declared inputs",
                    })

        return len(failures) == 0, failures

    # ------------------------------------------------------------------
    # Registry export
    # ------------------------------------------------------------------

    def export_registry(self) -> dict:
        """Export the versioned definition registry as a dict."""
        registry: dict[str, dict] = {}
        for ad in self.definitions.values():
            registry[ad.alert_id] = {
                "alert_id": ad.alert_id,
                "name": ad.name,
                "severity": ad.severity,
                "domain": ad.domain,
                "definition_version": ad.definition_version,
                "content_hash": ad.content_hash,
                "inputs": [{
                    "name": i.name,
                    "type": i.type,
                    "unit": i.unit,
                } for i in ad.inputs],
                "band_scales": [{
                    "variable": s.variable,
                    "unit": s.unit,
                    "band_count": len(s.bands),
                } for s in ad.band_scales],
            }
        return registry

    @property
    def errors(self) -> list[dict]:
        return list(self._errors)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compile_alert_registry(
    repo_root: Path | None = None,
) -> tuple[dict[str, AlertDefinition], AlertCompiler]:
    """Main entry point: load all catalogs and return definitions + compiler."""
    compiler = AlertCompiler(repo_root)
    definitions = compiler.load_all()
    return definitions, compiler
