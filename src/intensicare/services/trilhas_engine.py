"""Trilhas Engine — stateless declarative rule engine for care pathways.

Replaces the imperative PathwayStore state machine with a stateless,
YAML-driven evaluation engine per ADR-0020.

Pipeline:  YAML definitions → Compiler → Predicate AST → Evaluator → Alert instances

Public API:
  - evaluate(mpi_id, patient_data) → list[AlertFiring]  (async — awaits the
    underlying TrilhasEvaluator.evaluate_and_build)
  - get_pathways() → list[PathwayDefinition]
  - get_pathway(pathway_id) → PathwayDefinition
  - get_patient_pathways(mpi_id) → list  (delegates to legacy store)

Load-failure policy (fail-fast, hybrid — see ADR-0020 addendum):
  - If ANY predicate of a pathway fails to compile, the WHOLE pathway is
    marked inactive in memory (never partial evaluation of a clinical
    pathway). The failure is logged at ERROR level and recorded in the
    public ``load_failures`` attribute (list of dicts with pathway slug,
    criterion id, and error message) so it can later be surfaced via
    /health.
  - If ZERO pathways load with at least one active definition, engine
    construction raises RuntimeError — this is a deploy defect and boot
    must fail loudly rather than serve an engine with no active pathways.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
import os
from pathlib import Path
from typing import Any

import yaml

from intensicare.services.trilhas_compiler import PredicateCompiler, compute_content_hash
from intensicare.services.trilhas_evaluator import (
    AlertFiring,
    TrilhasEvaluator,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PathwayDefinition — loaded YAML pathway in compiled form
# ---------------------------------------------------------------------------


@dataclass
class PathwayDefinition:
    """A loaded and compiled pathway definition ready for evaluation.

    Holds the raw YAML metadata plus pre-compiled predicates for each criterion.
    """

    id: int
    name: str
    slug: str
    version: str
    content_hash: str
    description: str = ""
    active: bool = True
    evaluation_mode: str = "micro-batch"
    inputs: list[dict[str, Any]] = field(default_factory=list)
    criteria: list[dict[str, Any]] = field(default_factory=list)
    states: list[dict[str, Any]] = field(default_factory=list)
    suppression: dict[str, Any] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_raw(self) -> dict[str, Any]:
        """Return the raw YAML dict for use with TrilhasEvaluator."""
        return self._raw


# ---------------------------------------------------------------------------
# TrilhasEngine
# ---------------------------------------------------------------------------

# Default directories to search for YAML pathway definitions
_DEFAULT_YAML_DIRS: list[str] = [
    "_work/alerts/pathways/",
]


class TrilhasEngine:
    """Stateless declarative rule engine for care pathways.

    Loads YAML pathway definitions, compiles their predicates, and evaluates
    them against patient data. Produces AlertFiring instances with
    definition_version + content_hash stamping.

    Usage::

        engine = TrilhasEngine()
        alerts = await engine.evaluate("patient-123", {"pf_ratio": 150, "peep": 8})

    Attributes:
        load_failures: Public list of dicts (slug, criterion_id, error) for
            every pathway that had at least one predicate fail to compile.
            Such pathways are loaded but marked ``active=False``.
    """

    def __init__(
        self,
        definitions_path: str | None = None,
        *,
        compiler: PredicateCompiler | None = None,
        evaluator: TrilhasEvaluator | None = None,
    ) -> None:
        """Initialize the engine.

        Args:
            definitions_path: Directory containing YAML pathway definitions.
                              If None, searches _DEFAULT_YAML_DIRS relative
                              to the repository root.
            compiler: PredicateCompiler instance. Created if None.
            evaluator: TrilhasEvaluator instance. Created if None.
        """
        self._compiler = compiler or PredicateCompiler()
        self._evaluator = evaluator or TrilhasEvaluator(compiler=self._compiler)
        self._definitions: dict[int, PathwayDefinition] = {}
        self._definitions_by_slug: dict[str, PathwayDefinition] = {}
        self.load_failures: list[dict[str, str]] = []

        # Resolve and load definitions
        if definitions_path is not None:
            self._load_all(definitions_path)
        else:
            self._load_from_default_dirs()

        # Fail-fast: an engine with zero active pathways is a deploy defect
        # (missing/corrupt YAML, or every pathway failed predicate
        # compilation). Boot must fail loudly rather than silently serve
        # an engine that can never fire an alert.
        if not any(pdef.active for pdef in self._definitions.values()):
            raise RuntimeError(
                "TrilhasEngine loaded zero active pathway definitions "
                f"(loaded={len(self._definitions)}, "
                f"load_failures={len(self.load_failures)}). "
                "Refusing to boot with an engine that cannot fire any alert. "
                f"load_failures={self.load_failures!r}"
            )

    # ── Public API ───────────────────────────────────────────────────────

    async def evaluate(self, mpi_id: str, patient_data: dict[str, Any]) -> list[AlertFiring]:
        """Evaluate all pathway definitions for a patient. Stateless.

        NOTE: async — ``TrilhasEvaluator.evaluate_and_build`` is a coroutine
        (it awaits suppression/cooldown checks), so this method must be
        awaited by callers.

        Args:
            mpi_id: Patient identifier.
            patient_data: Dict mapping input names to their values
                          (e.g. {"pf_ratio": 150.0, "peep": 8}).

        Returns:
            List of AlertFiring instances — one per pathway that had
            at least one firing criterion. Pathways with zero firings
            are omitted.
        """
        alerts: list[AlertFiring] = []

        for pdef in self._definitions.values():
            if not pdef.active:
                continue

            alert = await self._evaluator.evaluate_and_build(
                pdef.to_raw(),
                mpi_id,
                patient_data,
            )

            # Only include pathways that actually fired
            if alert.firings:
                alerts.append(alert)

        return alerts

    def get_pathways(self) -> list[PathwayDefinition]:
        """Return all loaded pathway definitions.

        Returns:
            List of PathwayDefinition objects.
        """
        return list(self._definitions.values())

    def get_pathway(self, pathway_id: int) -> PathwayDefinition | None:
        """Get a single pathway definition by ID.

        Args:
            pathway_id: Numeric pathway ID.

        Returns:
            PathwayDefinition or None if not found.
        """
        return self._definitions.get(pathway_id)

    def get_pathway_by_slug(self, slug: str) -> PathwayDefinition | None:
        """Get a single pathway definition by slug.

        Args:
            slug: URL-safe pathway slug (e.g. "ventilacao").

        Returns:
            PathwayDefinition or None if not found.
        """
        return self._definitions_by_slug.get(slug)

    def get_patient_pathways(self, mpi_id: str) -> list[dict[str, Any]]:
        """Get all pathways a patient is enrolled in.

        Delegates to the legacy PathwayStore for backward compatibility.
        The legacy store tracks enrollments independently of the stateless
        evaluation engine.

        Args:
            mpi_id: Patient identifier.

        Returns:
            List of enrollment dicts from the legacy store.
        """
        try:
            from intensicare.services.domain_trilhas_engine import (
                get_patient_pathways as legacy_get,
            )

            return legacy_get(mpi_id, status_filter="all")
        except ImportError:
            logger.warning("Legacy domain_trilhas_engine not available for get_patient_pathways")
            return []

    async def reset_suppression(self) -> None:
        """Reset in-memory suppression state (useful for tests)."""
        await self._evaluator.reset_suppression()

    # ── Internal: YAML loading ──────────────────────────────────────────

    def _load_all(self, definitions_path: str) -> None:
        """Load all YAML pathway definitions from a directory.

        Args:
            definitions_path: Absolute or relative path to a directory
                              containing *.yaml pathway definition files.
        """
        full_path = Path(definitions_path)
        if not full_path.is_absolute():
            # Resolve relative to CWD
            full_path = Path(os.getcwd()) / full_path
        full_path = full_path.resolve()

        if not full_path.is_dir():
            logger.warning("Pathway definitions directory not found: %s", full_path)
            return

        yaml_files = sorted(full_path.glob("*.yaml")) + sorted(full_path.glob("*.yml"))
        if not yaml_files:
            logger.warning("No YAML files found in %s", full_path)
            return

        for yf in yaml_files:
            self._load_file(str(yf))

        logger.info(
            "TrilhasEngine loaded %d pathway definitions from %s",
            len(self._definitions),
            full_path,
        )

    def _load_file(self, filepath: str) -> None:
        """Load and compile a single YAML pathway definition.

        Args:
            filepath: Path to a .yaml pathway definition file.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except (yaml.YAMLError, OSError) as exc:
            logger.warning("Failed to load YAML pathway %s: %s", filepath, exc)
            return

        if not isinstance(raw, dict):
            logger.warning("YAML pathway %s is not a dict, skipping", filepath)
            return

        pathway_meta: dict[str, Any] = raw.get("pathway", {})
        evaluation: dict[str, Any] = raw.get("evaluation", {})
        criteria: list[dict[str, Any]] = raw.get("criteria", [])

        pathway_id: int = pathway_meta.get("id", 0)
        if pathway_id == 0:
            logger.warning("YAML pathway %s missing pathway.id, skipping", filepath)
            return

        name: str = pathway_meta.get("name", "")
        slug: str = pathway_meta.get("slug", "")
        version: str = pathway_meta.get("version", "0.0.0")

        # Compute content hash from the full raw YAML dict for
        # content-addressed traceability (ADR-020/ADR-021).
        # If the YAML already provides a content_hash, prefer it
        # (enables pre-computed / signed hashes). Otherwise, derive
        # the hash from the canonical JSON form of the raw dict.
        content_hash: str = pathway_meta.get("content_hash", "") or compute_content_hash(raw)
        description: str = pathway_meta.get("description", "")
        active: bool = pathway_meta.get("active", True)
        states: list[dict[str, Any]] = raw.get("states", [])
        suppression: dict[str, Any] = raw.get("suppression", {})
        evidence: dict[str, Any] = raw.get("evidence", {})
        inputs: list[dict[str, Any]] = evaluation.get("inputs", [])
        evaluation_mode: str = evaluation.get("mode", "micro-batch")

        # Pre-compile predicates for each criterion. Fail-fast hybrid policy:
        # if ANY predicate fails to compile, the whole pathway is marked
        # inactive in memory — never partial evaluation of a clinical
        # pathway. Every other criterion is still attempted (for accurate
        # compiled_count / diagnostics), but the pathway as a whole cannot
        # be trusted and is deactivated.
        compiled_count = 0
        compile_failed = False
        for criterion in criteria:
            pred_dict = criterion.get("predicate", {})
            if not pred_dict:
                continue
            criterion_id = criterion.get("id", "?")
            try:
                self._compiler.compile(pred_dict)
                compiled_count += 1
            except ValueError as exc:
                compile_failed = True
                logger.error(
                    "Failed to compile predicate for criterion %s in pathway "
                    "%s (%s): %s — deactivating pathway (fail-fast, no partial "
                    "evaluation of a clinical pathway)",
                    criterion_id,
                    slug or name,
                    filepath,
                    exc,
                )
                self.load_failures.append(
                    {
                        "slug": slug,
                        "criterion_id": str(criterion_id),
                        "error": str(exc),
                    }
                )

        if compile_failed:
            active = False

        pdef = PathwayDefinition(
            id=pathway_id,
            name=name,
            slug=slug,
            version=version,
            content_hash=content_hash,
            description=description,
            active=active,
            evaluation_mode=evaluation_mode,
            inputs=inputs,
            criteria=criteria,
            states=states,
            suppression=suppression,
            evidence=evidence,
            _raw=raw,
        )

        self._definitions[pathway_id] = pdef
        if slug:
            self._definitions_by_slug[slug] = pdef

        logger.debug(
            "Loaded pathway '%s' (id=%d, %d/%d criteria compiled)",
            name,
            pathway_id,
            compiled_count,
            len(criteria),
        )

    def _load_from_default_dirs(self) -> None:
        """Search default directories for YAML pathway definitions."""
        repo_root = self._find_repo_root()
        loaded_any = False

        for yaml_dir in _DEFAULT_YAML_DIRS:
            full_dir = os.path.join(repo_root, yaml_dir)
            if os.path.isdir(full_dir):
                self._load_all(full_dir)
                loaded_any = True

        if not loaded_any:
            logger.warning("No YAML pathway directories found. Engine has zero definitions.")

    @staticmethod
    def _find_repo_root() -> str:
        """Auto-detect the repository root directory."""
        this_file = Path(__file__).resolve()
        # trilhas_engine.py is at <repo>/src/intensicare/services/
        # → 4 levels up from the file = repo root
        candidate = this_file.parent.parent.parent.parent
        for marker in (".git", "pyproject.toml", "setup.py", "setup.cfg"):
            if (candidate / marker).exists():
                return str(candidate)
        return str(candidate)
