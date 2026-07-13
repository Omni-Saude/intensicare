"""Tests for trilhas_evaluator — stateless evaluation loop.

Covers:
  - TrilhasEvaluator with real YAML pathway definitions
  - Threshold predicate evaluation through the evaluator
  - Graded band evaluation through the evaluator
  - Boolean predicate evaluation through the evaluator
  - definition_version + content_hash stamping on firings
  - Suppression (cooldown, rate limit) — Redis-backed with in-memory fallback
  - AlertFiring aggregation (severity, score, recommendations)
  - Edge cases: missing inputs, non-numeric graded values
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
import pytest_asyncio

from intensicare.services.trilhas_compiler import PredicateCompiler
from intensicare.services.trilhas_evaluator import (
    AlertFiring,
    SuppressionTracker,
    TrilhasEvaluator,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def evaluator() -> TrilhasEvaluator:
    """Return a fresh TrilhasEvaluator with reset suppression state."""
    ev = TrilhasEvaluator()
    await ev.reset_suppression()
    return ev


@pytest.fixture
def compiler() -> PredicateCompiler:
    """Return a fresh PredicateCompiler."""
    return PredicateCompiler()


@pytest.fixture
def suppression() -> SuppressionTracker:
    """Return a fresh SuppressionTracker."""
    return SuppressionTracker()


@pytest.fixture
def ventilacao_yaml() -> dict[str, Any]:
    """Minimal YAML pathway dict matching ventilacao structure."""
    return {
        "pathway": {
            "id": 1,
            "name": "Ventilação Mecânica",
            "slug": "ventilacao",
            "version": "3.0.0",
            "content_hash": "sha256:abc123def4567890abc123def4567890abc123def4567890abc123def4567890",
        },
        "evaluation": {
            "mode": "hybrid",
            "inputs": [
                {"name": "pf_ratio", "source": "amh_gold", "unit": "mmHg"},
                {"name": "peep", "source": "amh_gold", "unit": "cmH2O"},
            ],
        },
        "criteria": [
            {
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
            },
            {
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
            },
        ],
        "states": [
            {"id": "initial", "name": "Avaliação Inicial", "order": 0, "is_terminal": False},
            {"id": "alta", "name": "Alta do Pathway", "order": 1, "is_terminal": True},
        ],
        "suppression": {
            "cooldown_minutes": 30,
            "rate_limit_per_hour": 4,
            "dedup_key": ["mpi_id", "criteria_id"],
        },
        "evidence": {
            "guideline": "ARDSNet Protocol (2000)",
            "doi": "10.1056/NEJM200005043421801",
            "recommendations": [
                "Manter PEEP ≥ 5 cmH₂O",
                "Avaliar relação PaO₂/FiO₂ diariamente",
            ],
        },
    }


@pytest.fixture
def sepse_yaml() -> dict[str, Any]:
    """Minimal YAML pathway dict matching sepse structure with boolean criteria."""
    return {
        "pathway": {
            "id": 2,
            "name": "Sepse",
            "slug": "sepse",
            "version": "3.0.0",
            "content_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000002",
        },
        "evaluation": {
            "mode": "near-real-time",
            "inputs": [
                {"name": "qsofa_score", "source": "vitals_stream", "unit": "points"},
                {"name": "lactato", "source": "amh_gold", "unit": "mmol/L"},
                {"name": "culturas_status", "source": "amh_gold", "unit": "ratio"},
            ],
        },
        "criteria": [
            {
                "id": "crit-sep-qsofa",
                "name": "qSOFA ≥ 2",
                "category": "triagem",
                "predicate": {
                    "type": "graded",
                    "input": "qsofa_score",
                    "bands": [
                        {"range": [0, 2], "severity": "normal", "score": 0},
                        {"range": [2, 3], "severity": "urgent", "score": 2},
                        {"range": [3, None], "severity": "critical", "score": 3},
                    ],
                    "unit": "points",
                },
            },
            {
                "id": "crit-sep-lactato",
                "name": "Lactato Sérico",
                "category": "laboratorial",
                "predicate": {
                    "type": "graded",
                    "input": "lactato",
                    "bands": [
                        {"range": [0, 2.0], "severity": "normal", "score": 0},
                        {"range": [2.0, 4.0], "severity": "watch", "score": 1},
                        {"range": [4.0, None], "severity": "critical", "score": 3},
                    ],
                    "unit": "mmol/L",
                },
            },
            {
                "id": "crit-sep-culturas",
                "name": "Culturas Coletadas",
                "category": "microbiologia",
                "predicate": {
                    "type": "boolean",
                    "input": "culturas_status",
                    "unit": "ratio",
                },
            },
        ],
        "states": [
            {"id": "initial", "name": "Triagem Inicial", "order": 0, "is_terminal": False},
            {"id": "alta", "name": "Resolução", "order": 1, "is_terminal": True},
        ],
        "suppression": {
            "cooldown_minutes": 15,
            "rate_limit_per_hour": 6,
            "dedup_key": ["mpi_id", "criteria_id"],
        },
        "evidence": {
            "guideline": "SSC-2021",
            "recommendations": ["Coletar lactato", "ATB em 1h"],
        },
    }


@pytest.fixture
def composite_yaml() -> dict[str, Any]:
    """Pathway with a composite (AND/OR) predicate."""
    return {
        "pathway": {
            "id": 99,
            "name": "Test Composite",
            "slug": "test-composite",
            "version": "1.0.0",
            "content_hash": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        },
        "evaluation": {
            "mode": "micro-batch",
            "inputs": [
                {"name": "fever", "source": "vitals", "unit": "celsius"},
                {"name": "tachycardia", "source": "vitals", "unit": "bpm"},
            ],
        },
        "criteria": [
            {
                "id": "crit-comp-sirs",
                "name": "SIRS Criteria",
                "category": "triagem",
                "predicate": {
                    "type": "composite",
                    "combinator": "AND",
                    "sub_predicates": [
                        {
                            "type": "threshold",
                            "input": "fever",
                            "operator": ">=",
                            "value": 38,
                            "unit": "celsius",
                        },
                        {
                            "type": "threshold",
                            "input": "tachycardia",
                            "operator": ">=",
                            "value": 90,
                            "unit": "bpm",
                        },
                    ],
                    "input": "fever",  # dummy for schema compat
                    "unit": "",
                },
            },
        ],
        "states": [
            {"id": "initial", "name": "Start", "order": 0, "is_terminal": False},
        ],
        "suppression": {},
        "evidence": {},
    }


# ---------------------------------------------------------------------------
# Real YAML file tests
# ---------------------------------------------------------------------------


class TestRealYamlDefinitions:
    """Verify evaluator works with real YAML pathway definitions from disk."""

    @pytest.fixture(scope="class")
    def real_ventilacao(self) -> dict[str, Any]:
        """Load the real ventilacao.yaml from disk."""
        from pathlib import Path

        import yaml

        repo_root = Path(__file__).resolve().parent.parent
        yaml_path = repo_root / "_work" / "alerts" / "pathways" / "ventilacao.yaml"
        if not yaml_path.exists():
            pytest.skip(f"Real YAML not found: {yaml_path}")
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def real_sepse(self) -> dict[str, Any]:
        """Load the real sepse.yaml from disk."""
        from pathlib import Path

        import yaml

        repo_root = Path(__file__).resolve().parent.parent
        yaml_path = repo_root / "_work" / "alerts" / "pathways" / "sepse.yaml"
        if not yaml_path.exists():
            pytest.skip(f"Real YAML not found: {yaml_path}")
        with open(yaml_path, "r") as f:
            return yaml.safe_load(f)

    async def test_ventilacao_real_yaml_evaluates(
        self, evaluator: TrilhasEvaluator, real_ventilacao: dict[str, Any]
    ) -> None:
        """PF ratio 150 → graded(urgent), PEEP 8 → threshold(met)."""
        patient_data = {"pf_ratio": 150.0, "peep": 8}
        firings = await evaluator.evaluate_pathway(
            real_ventilacao,
            "patient-real-1",
            patient_data,
            apply_suppression=False,
        )

        assert len(firings) == 2

        # Check PF ratio firing
        pf_firing = next(f for f in firings if f.criterion_id == "crit-vent-pf")
        assert pf_firing.result.met is True
        assert pf_firing.result.severity == "urgent"
        assert pf_firing.result.score == 2
        assert pf_firing.definition_version == "3.0.0"
        assert pf_firing.content_hash.startswith("sha256:")

        # Check PEEP firing
        peep_firing = next(f for f in firings if f.criterion_id == "crit-vent-peep")
        assert peep_firing.result.met is True

    async def test_ventilacao_normal_no_firing(
        self, evaluator: TrilhasEvaluator, real_ventilacao: dict[str, Any]
    ) -> None:
        """Normal PF ratio (350) → not met. PEEP < 5 → not met. Zero firings."""
        patient_data = {"pf_ratio": 350.0, "peep": 3}
        firings = await evaluator.evaluate_pathway(
            real_ventilacao,
            "patient-normal",
            patient_data,
            apply_suppression=False,
        )
        assert len(firings) == 0

    async def test_sepse_real_yaml_evaluates(
        self, evaluator: TrilhasEvaluator, real_sepse: dict[str, Any]
    ) -> None:
        """qSOFA=2 (urgent), lactate=4.5 (critical), culturas_status=True (met)."""
        patient_data = {
            "qsofa_score": 2.5,
            "lactato": 4.5,
            "pct": 0.3,
            "pam": 70,
            "culturas_status": True,
            "atb_status": False,
            "fluid_volume": 15,
        }
        firings = await evaluator.evaluate_pathway(
            real_sepse,
            "patient-sep-1",
            patient_data,
            apply_suppression=False,
        )

        # Should have multiple firings since several criteria are met
        assert len(firings) >= 3

        # Verify stamping
        # sepse.yaml v4.0.0 (Sprint 3 sepsis governance): version bumped from
        # 3.0.0 when the rich domain_sepsis.py alert logic was ported to
        # declarative criteria — see tests/test_sepse_yaml_parity.py.
        for f in firings:
            assert f.definition_version == "4.0.0"
            assert f.content_hash.startswith("sha256:")

    async def test_build_alert_from_real_yaml(
        self, evaluator: TrilhasEvaluator, real_ventilacao: dict[str, Any]
    ) -> None:
        """Build an AlertFiring from evaluated criteria with real YAML."""
        patient_data = {"pf_ratio": 150.0, "peep": 8}
        firings = await evaluator.evaluate_pathway(
            real_ventilacao,
            "patient-alert-1",
            patient_data,
            apply_suppression=False,
        )
        alert = evaluator.build_alert("patient-alert-1", real_ventilacao, firings)

        assert alert.mpi_id == "patient-alert-1"
        assert alert.pathway_id == 1
        assert alert.pathway_name == "Ventilação Mecânica"
        assert alert.definition_version == "3.0.0"
        assert alert.overall_severity == "urgent"  # max of urgent + urgent
        assert alert.total_score == 3  # 2 (PF) + 1 (PEEP)
        # Real YAML may or may not have evidence.recommendations
        assert isinstance(alert.recommendations, list)


# ---------------------------------------------------------------------------
# Threshold evaluation tests
# ---------------------------------------------------------------------------


class TestThresholdThroughEvaluator:
    """Threshold predicates evaluated through TrilhasEvaluator."""

    async def test_peep_threshold_met(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PEEP >= 5 with peep=8 → met, severity=urgent, score=1."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 350.0, "peep": 8},
            apply_suppression=False,
        )

        peep_firings = [f for f in firings if f.criterion_id == "crit-vent-peep"]
        assert len(peep_firings) == 1
        f = peep_firings[0]
        assert f.result.met is True
        assert f.result.severity == "urgent"
        assert f.result.score == 1
        assert f.result.actual_value == 8
        assert f.result.unit == "cmH2O"

    async def test_peep_threshold_not_met(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PEEP >= 5 with peep=3 → not met → no firing."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 350.0, "peep": 3},
            apply_suppression=False,
        )
        peep_firings = [f for f in firings if f.criterion_id == "crit-vent-peep"]
        assert len(peep_firings) == 0

    async def test_peep_at_boundary(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PEEP >= 5 with peep=5 → met (boundary inclusive)."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 350.0, "peep": 5},
            apply_suppression=False,
        )
        peep_firings = [f for f in firings if f.criterion_id == "crit-vent-peep"]
        assert len(peep_firings) == 1

    async def test_missing_input_produces_no_firing(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Missing 'peep' in patient_data → criterion skipped, no firing."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 350.0},
            apply_suppression=False,
        )
        # PF ratio is normal (350 in [300, None) → not met)
        # peep is missing → skipped
        assert len(firings) == 0


# ---------------------------------------------------------------------------
# Graded band evaluation tests
# ---------------------------------------------------------------------------


class TestGradedThroughEvaluator:
    """Graded predicates evaluated through TrilhasEvaluator."""

    async def test_pf_ratio_critical(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF ratio 50 → band [0, 100) → critical, score=3."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 50.0, "peep": 3},
            apply_suppression=False,
        )
        pf_firings = [f for f in firings if f.criterion_id == "crit-vent-pf"]
        assert len(pf_firings) == 1
        f = pf_firings[0]
        assert f.result.met is True
        assert f.result.severity == "critical"
        assert f.result.score == 3
        assert f.result.actual_value == 50.0
        assert f.result.unit == "mmHg"

    async def test_pf_ratio_urgent(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF ratio 150 → band [100, 200) → urgent, score=2."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 3},
            apply_suppression=False,
        )
        pf_firings = [f for f in firings if f.criterion_id == "crit-vent-pf"]
        assert len(pf_firings) == 1
        assert pf_firings[0].result.severity == "urgent"
        assert pf_firings[0].result.score == 2

    async def test_pf_ratio_watch(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF ratio 250 → band [200, 300) → watch, score=1."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 250.0, "peep": 3},
            apply_suppression=False,
        )
        pf_firings = [f for f in firings if f.criterion_id == "crit-vent-pf"]
        assert len(pf_firings) == 1
        assert pf_firings[0].result.severity == "watch"
        assert pf_firings[0].result.score == 1

    async def test_pf_ratio_normal_no_firing(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF ratio 350 → band [300, None) → normal → no firing."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 350.0, "peep": 3},
            apply_suppression=False,
        )
        pf_firings = [f for f in firings if f.criterion_id == "crit-vent-pf"]
        assert len(pf_firings) == 0

    async def test_qsofa_band(
        self, evaluator: TrilhasEvaluator, sepse_yaml: dict[str, Any]
    ) -> None:
        """qSOFA ≥ 2: qsofa_score=2.5 → band [2, 3) → urgent."""
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 2.5, "lactato": 1.0, "culturas_status": False},
            apply_suppression=False,
        )
        qsofa_firings = [f for f in firings if f.criterion_id == "crit-sep-qsofa"]
        assert len(qsofa_firings) == 1
        assert qsofa_firings[0].result.severity == "urgent"

    async def test_lactate_critical_band(
        self, evaluator: TrilhasEvaluator, sepse_yaml: dict[str, Any]
    ) -> None:
        """Lactate 4.5 → band [4.0, None) → critical."""
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 1.0, "lactato": 4.5, "culturas_status": False},
            apply_suppression=False,
        )
        lac_firings = [f for f in firings if f.criterion_id == "crit-sep-lactato"]
        assert len(lac_firings) == 1
        assert lac_firings[0].result.severity == "critical"
        assert lac_firings[0].result.score == 3

    async def test_graded_non_numeric(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Non-numeric PF ratio → no band match → no firing."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": "unknown", "peep": 3},
            apply_suppression=False,
        )
        pf_firings = [f for f in firings if f.criterion_id == "crit-vent-pf"]
        assert len(pf_firings) == 0


# ---------------------------------------------------------------------------
# Boolean evaluation tests
# ---------------------------------------------------------------------------


class TestBooleanThroughEvaluator:
    """Boolean predicates evaluated through TrilhasEvaluator."""

    async def test_boolean_true_fires(
        self, evaluator: TrilhasEvaluator, sepse_yaml: dict[str, Any]
    ) -> None:
        """culturas_status=True → boolean met → fires with severity=urgent."""
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 1.0, "lactato": 1.0, "culturas_status": True},
            apply_suppression=False,
        )
        cult_firings = [f for f in firings if f.criterion_id == "crit-sep-culturas"]
        assert len(cult_firings) == 1
        assert cult_firings[0].result.met is True
        assert cult_firings[0].result.severity == "urgent"
        assert cult_firings[0].result.score == 1

    async def test_boolean_false_no_firing(
        self, evaluator: TrilhasEvaluator, sepse_yaml: dict[str, Any]
    ) -> None:
        """culturas_status=False → boolean not met → no firing."""
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 1.0, "lactato": 1.0, "culturas_status": False},
            apply_suppression=False,
        )
        cult_firings = [f for f in firings if f.criterion_id == "crit-sep-culturas"]
        assert len(cult_firings) == 0

    async def test_boolean_truthy_fires(
        self, evaluator: TrilhasEvaluator, sepse_yaml: dict[str, Any]
    ) -> None:
        """Truthy non-boolean value (1) also fires."""
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 1.0, "lactato": 1.0, "culturas_status": 1},
            apply_suppression=False,
        )
        cult_firings = [f for f in firings if f.criterion_id == "crit-sep-culturas"]
        assert len(cult_firings) == 1


# ---------------------------------------------------------------------------
# Composite (AND/OR) evaluation tests
# ---------------------------------------------------------------------------


class TestCompositeThroughEvaluator:
    """Composite predicates evaluated through TrilhasEvaluator."""

    async def test_and_both_met(
        self, evaluator: TrilhasEvaluator, composite_yaml: dict[str, Any]
    ) -> None:
        """fever >= 38 AND tachycardia >= 90 → both met → fires."""
        firings = await evaluator.evaluate_pathway(
            composite_yaml,
            "test-mpi",
            {"fever": 39.0, "tachycardia": 100},
            apply_suppression=False,
        )
        crit_firings = [f for f in firings if f.criterion_id == "crit-comp-sirs"]
        assert len(crit_firings) == 1
        assert crit_firings[0].result.met is True

    async def test_and_one_not_met(
        self, evaluator: TrilhasEvaluator, composite_yaml: dict[str, Any]
    ) -> None:
        """fever >= 38 AND tachycardia >= 90 → fever not met → no firing."""
        firings = await evaluator.evaluate_pathway(
            composite_yaml,
            "test-mpi",
            {"fever": 37.0, "tachycardia": 100},
            apply_suppression=False,
        )
        crit_firings = [f for f in firings if f.criterion_id == "crit-comp-sirs"]
        assert len(crit_firings) == 0

    async def test_or_one_met(
        self, evaluator: TrilhasEvaluator, composite_yaml: dict[str, Any]
    ) -> None:
        """Modify to OR: fever >= 38 OR tachycardia >= 90 → tachycardia met → fires."""
        or_yaml = copy.deepcopy(composite_yaml)
        or_yaml["criteria"][0]["predicate"]["combinator"] = "OR"

        firings = await evaluator.evaluate_pathway(
            or_yaml,
            "test-mpi",
            {"fever": 37.0, "tachycardia": 100},
            apply_suppression=False,
        )
        crit_firings = [f for f in firings if f.criterion_id == "crit-comp-sirs"]
        assert len(crit_firings) == 1
        assert crit_firings[0].result.met is True

    async def test_or_none_met(
        self, evaluator: TrilhasEvaluator, composite_yaml: dict[str, Any]
    ) -> None:
        """Modify to OR: neither met → no firing."""
        or_yaml = copy.deepcopy(composite_yaml)
        or_yaml["criteria"][0]["predicate"]["combinator"] = "OR"

        firings = await evaluator.evaluate_pathway(
            or_yaml,
            "test-mpi",
            {"fever": 37.0, "tachycardia": 80},
            apply_suppression=False,
        )
        crit_firings = [f for f in firings if f.criterion_id == "crit-comp-sirs"]
        assert len(crit_firings) == 0


# ---------------------------------------------------------------------------
# Version + content_hash stamping tests
# ---------------------------------------------------------------------------


class TestVersionAndHashStamping:
    """Verify all CriterionFiring instances carry definition_version + content_hash."""

    async def test_firings_have_version_and_hash(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Every CriterionFiring must include definition_version and content_hash."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        for f in firings:
            assert f.definition_version == "3.0.0", f"Missing/invalid version in {f.criterion_id}"
            assert f.content_hash.startswith("sha256:"), (
                f"Missing/invalid content_hash in {f.criterion_id}: {f.content_hash}"
            )

    async def test_alert_has_version_and_hash(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """AlertFiring includes definition_version and content_hash."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, firings)

        assert alert.definition_version == "3.0.0"
        assert alert.content_hash.startswith("sha256:")

    def test_zero_firings_still_stamped(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Even with no firings, build_alert stamps version+hash."""
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, [])

        assert alert.definition_version == "3.0.0"
        assert alert.content_hash.startswith("sha256:")
        assert len(alert.firings) == 0


# ---------------------------------------------------------------------------
# Suppression tests (cooldown + rate limit)
# ---------------------------------------------------------------------------


class TestSuppression:
    """Redis-backed suppression (cooldown and rate limit) with in-memory fallback."""

    async def test_suppression_tracker_cooldown(self, suppression: SuppressionTracker) -> None:
        """First fire allowed; second within cooldown is suppressed."""
        allowed1, reason1 = await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-1",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        assert allowed1 is True
        assert reason1 == ""

        # Immediate second fire — should be suppressed
        allowed2, reason2 = await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-1",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        assert allowed2 is False
        assert "Cooldown" in reason2
        assert "30" in reason2

    async def test_suppression_different_criteria_not_affected(
        self,
        suppression: SuppressionTracker,
    ) -> None:
        """Cooldown on crit-1 doesn't affect crit-2."""
        await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-1",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        allowed, _ = await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-2",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        assert allowed is True

    async def test_suppression_different_patients_not_affected(
        self,
        suppression: SuppressionTracker,
    ) -> None:
        """Cooldown on patient-A doesn't affect patient-B."""
        await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-1",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        allowed, _ = await suppression.check_and_record(
            "mpi-B",
            1,
            "crit-1",
            cooldown_minutes=30,
            rate_limit_per_hour=100,
        )
        assert allowed is True

    async def test_rate_limit(self, suppression: SuppressionTracker) -> None:
        """Rate limit of 2/hour — 3rd fire suppressed."""
        for i in range(2):
            allowed, _ = await suppression.check_and_record(
                "mpi-A",
                1,
                "crit-1",
                cooldown_minutes=0,
                rate_limit_per_hour=2,
            )
            assert allowed is True, f"Fire {i} should be allowed"

        allowed3, reason3 = await suppression.check_and_record(
            "mpi-A",
            1,
            "crit-1",
            cooldown_minutes=0,
            rate_limit_per_hour=2,
        )
        assert allowed3 is False
        assert "Rate limit" in reason3

    async def test_suppression_disabled(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """apply_suppression=False always allows firings."""
        for i in range(10):
            firings = await evaluator.evaluate_pathway(
                ventilacao_yaml,
                "test-mpi",
                {"pf_ratio": 150.0, "peep": 8},
                apply_suppression=False,
            )
            assert len(firings) == 2, f"Iteration {i}: expected 2 firings"
            for f in firings:
                assert f.suppressed is False

    async def test_suppression_via_evaluator(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """First call fires; second within 30min cooldown suppresses pf_ratio."""
        patient_data = {"pf_ratio": 150.0, "peep": 8}

        # First evaluation — both should fire
        firings1 = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-supp",
            patient_data,
            apply_suppression=True,
        )
        assert len(firings1) == 2
        for f in firings1:
            assert f.suppressed is False

        # Second evaluation within cooldown — pf_ratio suppressed
        firings2 = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-supp",
            patient_data,
            apply_suppression=True,
        )
        assert len(firings2) == 2  # still 2 firings, but some suppressed
        suppressed = [f for f in firings2 if f.suppressed]
        assert len(suppressed) >= 1
        assert "Cooldown" in suppressed[0].suppress_reason

    async def test_reset_suppression(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """reset_suppression clears all tracking."""
        patient_data = {"pf_ratio": 150.0, "peep": 8}

        # Fire once
        await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-reset",
            patient_data,
            apply_suppression=True,
        )
        # Reset
        await evaluator.reset_suppression()
        # Should fire again without suppression
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-reset",
            patient_data,
            apply_suppression=True,
        )
        assert len(firings) == 2
        for f in firings:
            assert f.suppressed is False


# ---------------------------------------------------------------------------
# AlertFiring aggregation tests
# ---------------------------------------------------------------------------


class TestAlertAggregation:
    """AlertFiring severity/score aggregation and recommendations."""

    async def test_aggregate_severity_max(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF(urgent) + PEEP(urgent) → overall severity = urgent."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, firings)
        assert alert.overall_severity == "urgent"

    async def test_aggregate_severity_critical_wins(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF(critical) + PEEP(urgent) → overall severity = critical."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 50.0, "peep": 8},
            apply_suppression=False,
        )
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, firings)
        assert alert.overall_severity == "critical"

    async def test_aggregate_score_sums(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """PF(score=2) + PEEP(score=1) → total_score = 3."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, firings)
        assert alert.total_score == 3

    async def test_suppressed_not_counted_in_score(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Suppressed firings don't contribute to score or severity."""
        patient_data = {"pf_ratio": 150.0, "peep": 8}

        # Fire once
        await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-sc",
            patient_data,
            apply_suppression=True,
        )
        # Fire again — pf_ratio will be suppressed
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi-sc",
            patient_data,
            apply_suppression=True,
        )
        alert = evaluator.build_alert("test-mpi-sc", ventilacao_yaml, firings)

        # Only unsuppressed firings count
        assert alert.suppressed_count >= 1
        active_firings = [f for f in firings if not f.suppressed]
        expected_score = sum(f.result.score for f in active_firings)
        assert alert.total_score == expected_score

    async def test_recommendations_from_evidence(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Recommendations from evidence.recommendations are included."""
        firings = await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, firings)
        assert len(alert.recommendations) > 0
        assert any("PEEP" in r for r in alert.recommendations)

    def test_empty_firings_alert(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """Alert with no firings has severity=normal, score=0."""
        alert = evaluator.build_alert("test-mpi", ventilacao_yaml, [])
        assert alert.overall_severity == "normal"
        assert alert.total_score == 0
        assert alert.suppressed_count == 0


# ---------------------------------------------------------------------------
# evaluate_and_build convenience method
# ---------------------------------------------------------------------------


class TestEvaluateAndBuild:
    """Convenience method evaluate_and_build()."""

    async def test_evaluate_and_build_returns_alert(
        self, evaluator: TrilhasEvaluator, ventilacao_yaml: dict[str, Any]
    ) -> None:
        """evaluate_and_build returns AlertFiring directly."""
        alert = await evaluator.evaluate_and_build(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=False,
        )
        assert isinstance(alert, AlertFiring)
        assert alert.mpi_id == "test-mpi"
        assert len(alert.firings) == 2
        assert alert.overall_severity == "urgent"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling in the evaluator."""

    async def test_pathway_with_no_criteria(
        self,
        evaluator: TrilhasEvaluator,
    ) -> None:
        """Pathway with empty criteria list → no firings."""
        empty_yaml = {
            "pathway": {
                "id": 99,
                "name": "Empty",
                "slug": "empty",
                "version": "1.0.0",
                "content_hash": "sha256:" + "aa" * 64,
            },
            "criteria": [],
            "states": [],
        }
        firings = await evaluator.evaluate_pathway(
            empty_yaml,
            "test-mpi",
            {},
            apply_suppression=False,
        )
        assert len(firings) == 0

    async def test_criterion_with_no_predicate(
        self,
        evaluator: TrilhasEvaluator,
    ) -> None:
        """Criterion without a predicate dict → skipped gracefully."""
        yaml_def = {
            "pathway": {
                "id": 99,
                "name": "Test",
                "slug": "test",
                "version": "1.0.0",
                "content_hash": "sha256:" + "bb" * 64,
            },
            "criteria": [
                {"id": "crit-no-pred", "name": "No Pred", "category": "test"},
            ],
            "states": [],
        }
        firings = await evaluator.evaluate_pathway(
            yaml_def,
            "test-mpi",
            {},
            apply_suppression=False,
        )
        assert len(firings) == 0

    async def test_invalid_predicate_skipped(
        self,
        evaluator: TrilhasEvaluator,
    ) -> None:
        """Invalid predicate (unknown type) → logged warning, no crash."""
        yaml_def = {
            "pathway": {
                "id": 99,
                "name": "Test",
                "slug": "test",
                "version": "1.0.0",
                "content_hash": "sha256:" + "cc" * 64,
            },
            "criteria": [
                {
                    "id": "crit-bad",
                    "name": "Bad",
                    "category": "test",
                    "predicate": {"type": "nonexistent", "input": "x", "unit": ""},
                },
            ],
            "states": [],
        }
        # Should not raise — just skip the bad predicate
        firings = await evaluator.evaluate_pathway(
            yaml_def,
            "test-mpi",
            {"x": 5},
            apply_suppression=False,
        )
        assert len(firings) == 0

    async def test_multiple_pathways_independent_suppression(
        self,
        evaluator: TrilhasEvaluator,
        ventilacao_yaml: dict[str, Any],
        sepse_yaml: dict[str, Any],
    ) -> None:
        """Suppression tracks per-pathway; firing in one doesn't suppress another."""
        # Fire ventilacao
        await evaluator.evaluate_pathway(
            ventilacao_yaml,
            "test-mpi",
            {"pf_ratio": 150.0, "peep": 8},
            apply_suppression=True,
        )
        # Fire sepse — different pathway, should not be suppressed
        firings = await evaluator.evaluate_pathway(
            sepse_yaml,
            "test-mpi",
            {"qsofa_score": 2.5, "lactato": 4.5, "culturas_status": True},
            apply_suppression=True,
        )
        # All sepse criteria should fire (not suppressed by ventilacao)
        assert len(firings) == 3
        for f in firings:
            assert f.suppressed is False
