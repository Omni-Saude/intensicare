"""
Tests for Clinical Evolution domain service (domain_evolucoes.py).

Covers:
- get_template_catalog: 14 templates, role filtering
- create_evolution: diaria, content hash, amendment chain, validation
- list_evolutions: filter by type, pagination, empty results
- get_evolution: existing, nonexistent
"""

from __future__ import annotations

import hashlib
import json

import pytest

from intensicare.services import domain_evolucoes as mod
from intensicare.services.domain_evolucoes import (
    CLINICAL_ROLES,
    EVOLUTION_TYPES,
    EvolutionRecord,
    EvolutionListResult,
    create_evolution,
    get_evolution,
    get_template_catalog,
    list_evolutions,
    _compute_content_hash,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _reset_store() -> None:
    """Reset in-memory stores to ensure test isolation."""
    mod._evolutions_store.clear()
    mod._next_evolution_id = 1
    # Reset template cache so each test can re-load fresh
    mod._TEMPLATES.clear()


def _valid_sbar_sections() -> list[dict]:
    """Build a minimal valid set of 4 SBAR sections in correct order."""
    return [
        {"section_key": "situation", "content": "Paciente estável", "order": 0},
        {"section_key": "background", "content": "Histórico de HAS", "order": 1},
        {"section_key": "assessment", "content": "Exame físico normal", "order": 2},
        {"section_key": "recommendation", "content": "Manter conduta", "order": 3},
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Test Template Catalog
# ═══════════════════════════════════════════════════════════════════════════════

class TestTemplateCatalog:
    """Tests for get_template_catalog function."""

    def test_14_templates_available(self) -> None:
        """The catalog contains exactly 14 role-specific SBAR templates."""
        catalog = get_template_catalog()
        assert len(catalog) == 14, f"Expected 14 templates, got {len(catalog)}"

    def test_filter_by_role_returns_only_that_role(self) -> None:
        """Filtering by a clinical role returns only templates for that role."""
        catalog = get_template_catalog(role="medico")
        assert len(catalog) >= 1
        for template in catalog:
            assert template.role == "medico"

    def test_filter_by_role_unknown_returns_all(self) -> None:
        """Filtering by an unknown role returns all templates (graceful)."""
        # Store current count to verify the fallback
        all_templates = get_template_catalog()
        result = get_template_catalog(role="astronauta")
        assert len(result) == len(all_templates)

    def test_all_templates_have_active_flag(self) -> None:
        """All 14 templates should be active by default."""
        catalog = get_template_catalog()
        for template in catalog:
            assert template.active is True, f"Template {template.id} is not active"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Create Evolution
# ═══════════════════════════════════════════════════════════════════════════════

class TestCreateEvolution:
    """Tests for create_evolution function."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        _reset_store()

    def test_create_diaria(self) -> None:
        """Creating a daily evolution with valid data succeeds."""
        record = create_evolution(
            mpi_id="MPI-001",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Silva",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert isinstance(record, EvolutionRecord)
        assert record.id == 1
        assert record.mpi_id == "MPI-001"
        assert record.type == "diaria"
        assert record.template_id == "medico_diaria"
        assert record.author == "Dr. Silva"
        assert record.author_role == "medico"
        assert record.status == "final"
        assert record.created_at != ""
        assert record.updated_at != ""
        assert len(record.sections) == 4

    def test_generates_content_hash(self) -> None:
        """Creating an evolution generates a SHA-256 content hash."""
        record = create_evolution(
            mpi_id="MPI-002",
            type="diaria",
            template_id="enfermeiro_diaria",
            author="Enf. Maria",
            author_role="enfermeiro",
            sections=_valid_sbar_sections(),
        )
        assert record.content_hash != ""
        assert len(record.content_hash) == 64  # SHA-256 hex digest
        # Verify hash matches compute function
        expected = _compute_content_hash(_valid_sbar_sections())
        assert record.content_hash == expected

    def test_hash_changes_with_content(self) -> None:
        """Different section content produces a different hash."""
        rec1 = create_evolution(
            mpi_id="MPI-003",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Silva",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )

        # Slightly different sections
        sections2 = [
            {"section_key": "situation", "content": "Paciente instável", "order": 0},
            {"section_key": "background", "content": "Histórico de HAS", "order": 1},
            {"section_key": "assessment", "content": "Exame físico normal", "order": 2},
            {"section_key": "recommendation", "content": "Manter conduta", "order": 3},
        ]
        rec2 = create_evolution(
            mpi_id="MPI-003",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Silva",
            author_role="medico",
            sections=sections2,
        )
        assert rec1.content_hash != rec2.content_hash

    def test_amendment_chain(self) -> None:
        """Creating an amendment via previous_id links records correctly."""
        # Create original
        original = create_evolution(
            mpi_id="MPI-004",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Silva",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert original.status == "final"

        # Create amendment
        amended_sections = [
            {"section_key": "situation", "content": "Piora clínica", "order": 0},
            {"section_key": "background", "content": "HAS + DM", "order": 1},
            {"section_key": "assessment", "content": "Descompensado", "order": 2},
            {"section_key": "recommendation", "content": "Ajustar drogas", "order": 3},
        ]
        amendment = create_evolution(
            mpi_id="MPI-004",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Silva",
            author_role="medico",
            sections=amended_sections,
            previous_id=original.id,
        )
        assert amendment.status == "amended"
        assert amendment.previous_id == original.id
        assert amendment.id == 2
        assert amendment.content_hash != original.content_hash

        # Original should now be marked as amended
        assert original.id is not None
        original_after = get_evolution(original.id)
        assert original_after is not None
        assert original_after.status == "amended"

    def test_amendment_invalid_previous_id(self) -> None:
        """Amending with a nonexistent previous_id raises ValueError."""
        with pytest.raises(ValueError, match="não encontrado"):
            create_evolution(
                mpi_id="MPI-005",
                type="diaria",
                template_id="medico_diaria",
                author="Dr. Silva",
                author_role="medico",
                sections=_valid_sbar_sections(),
                previous_id=9999,
            )

    def test_create_invalid_type_raises(self) -> None:
        """Invalid evolution type raises ValueError."""
        with pytest.raises(ValueError, match="Tipo de evolução inválido"):
            create_evolution(
                mpi_id="MPI-006",
                type="fantasia",
                template_id="medico_diaria",
                author="Dr. Silva",
                author_role="medico",
                sections=_valid_sbar_sections(),
            )

    def test_create_invalid_role_raises(self) -> None:
        """Invalid author_role raises ValueError."""
        with pytest.raises(ValueError, match="Papel clínico inválido"):
            create_evolution(
                mpi_id="MPI-007",
                type="diaria",
                template_id="medico_diaria",
                author="Dr. Silva",
                author_role="astronauta",
                sections=_valid_sbar_sections(),
            )

    def test_create_missing_mpi_id_raises(self) -> None:
        """Missing mpi_id raises ValueError."""
        with pytest.raises(ValueError, match="mpi_id é obrigatório"):
            create_evolution(
                mpi_id="",
                type="diaria",
                template_id="medico_diaria",
                author="Dr. Silva",
                author_role="medico",
                sections=_valid_sbar_sections(),
            )

    def test_create_missing_author_raises(self) -> None:
        """Missing author raises ValueError."""
        with pytest.raises(ValueError, match="author é obrigatório"):
            create_evolution(
                mpi_id="MPI-008",
                type="diaria",
                template_id="medico_diaria",
                author="",
                author_role="medico",
                sections=_valid_sbar_sections(),
            )

    def test_create_invalid_template_raises(self) -> None:
        """Invalid template_id raises ValueError."""
        with pytest.raises(ValueError, match="não encontrado"):
            create_evolution(
                mpi_id="MPI-009",
                type="diaria",
                template_id="template_inexistente",
                author="Dr. Silva",
                author_role="medico",
                sections=_valid_sbar_sections(),
            )

    def test_create_empty_sections_raises(self) -> None:
        """Empty sections list raises ValueError."""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            create_evolution(
                mpi_id="MPI-010",
                type="diaria",
                template_id="medico_diaria",
                author="Dr. Silva",
                author_role="medico",
                sections=[],
            )

    def test_create_admissao_type(self) -> None:
        """Creating an 'admissao' type evolution works with the admissao template."""
        record = create_evolution(
            mpi_id="MPI-011",
            type="admissao",
            template_id="admissao",
            author="Dr. Oliveira",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert record.type == "admissao"
        assert record.template_id == "admissao"
        assert record.status == "final"

    def test_create_alta_type(self) -> None:
        """Creating an 'alta' type evolution works."""
        record = create_evolution(
            mpi_id="MPI-012",
            type="alta",
            template_id="alta",
            author="Dr. Santos",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert record.type == "alta"
        assert record.status == "final"

    def test_create_obito_type(self) -> None:
        """Creating an 'obito' type evolution works."""
        record = create_evolution(
            mpi_id="MPI-013",
            type="obito",
            template_id="medico_diaria",
            author="Dr. Lima",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert record.type == "obito"

    def test_create_intercorrencia_type(self) -> None:
        """Creating an 'intercorrencia' type evolution works."""
        record = create_evolution(
            mpi_id="MPI-014",
            type="intercorrencia",
            template_id="intercorrencia",
            author="Enf. Carla",
            author_role="enfermeiro",
            sections=_valid_sbar_sections(),
        )
        assert record.type == "intercorrencia"

    def test_auto_increment_ids(self) -> None:
        """Multiple creations produce auto-incrementing IDs."""
        rec1 = create_evolution(
            mpi_id="MPI-015",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. A",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        rec2 = create_evolution(
            mpi_id="MPI-015",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. B",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        rec3 = create_evolution(
            mpi_id="MPI-015",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. C",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert rec1.id == 1
        assert rec2.id == 2
        assert rec3.id == 3


# ═══════════════════════════════════════════════════════════════════════════════
# Test List Evolutions
# ═══════════════════════════════════════════════════════════════════════════════

class TestListEvolutions:
    """Tests for list_evolutions function."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        _reset_store()

    def test_list_empty(self) -> None:
        """Listing evolutions for a patient with no records returns empty."""
        result = list_evolutions(mpi_id="NOBODY")
        assert isinstance(result, EvolutionListResult)
        assert len(result.items) == 0
        assert result.total == 0

    def test_list_filter_by_type(self) -> None:
        """Filtering by type returns only records of that type."""
        _seed_evolutions()

        result = list_evolutions(mpi_id="MPI-100", type="diaria")
        assert result.total == 2  # 2 diarias created
        for item in result.items:
            assert item.type == "diaria"

        result_admissao = list_evolutions(mpi_id="MPI-100", type="admissao")
        assert result_admissao.total == 1
        assert result_admissao.items[0].type == "admissao"

    def test_list_pagination(self) -> None:
        """Pagination with limit and offset works correctly."""
        _seed_evolutions()

        # Request 1 item, offset 0
        result = list_evolutions(mpi_id="MPI-100", limit=1, offset=0)
        assert len(result.items) == 1
        assert result.total == 3  # total is pre-pagination count

        # Request 1 item, offset 1
        result2 = list_evolutions(mpi_id="MPI-100", limit=1, offset=1)
        assert len(result2.items) == 1
        assert result2.total == 3
        # Should be different records
        assert result.items[0].id != result2.items[0].id

    def test_list_returns_all_for_patient(self) -> None:
        """Listing without type filter returns all records for the patient."""
        _seed_evolutions()
        result = list_evolutions(mpi_id="MPI-100")
        assert result.total == 3
        assert len(result.items) == 3

    def test_list_unknown_type_no_filter(self) -> None:
        """An unknown type filter logs a warning but does not break."""
        _seed_evolutions()
        result = list_evolutions(mpi_id="MPI-100", type="fantasia")
        # Unknown type should just log warning, still return something
        assert isinstance(result, EvolutionListResult)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Get Evolution
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetEvolution:
    """Tests for get_evolution function."""

    def setup_method(self) -> None:
        """Reset store before each test."""
        _reset_store()

    def test_get_existing(self) -> None:
        """Getting an existing evolution returns the record."""
        created = create_evolution(
            mpi_id="MPI-200",
            type="diaria",
            template_id="medico_diaria",
            author="Dr. Test",
            author_role="medico",
            sections=_valid_sbar_sections(),
        )
        assert created.id is not None
        retrieved = get_evolution(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.mpi_id == "MPI-200"
        assert retrieved.author == "Dr. Test"

    def test_get_nonexistent_returns_none(self) -> None:
        """Getting a nonexistent evolution returns None."""
        result = get_evolution(99999)
        assert result is None


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers for seeding test data
# ═══════════════════════════════════════════════════════════════════════════════

def _seed_evolutions() -> None:
    """Create a few evolutions for MPI-100 to test listing."""
    create_evolution(
        mpi_id="MPI-100",
        type="admissao",
        template_id="admissao",
        author="Dr. Admissao",
        author_role="medico",
        sections=_valid_sbar_sections(),
    )
    create_evolution(
        mpi_id="MPI-100",
        type="diaria",
        template_id="medico_diaria",
        author="Dr. Diaria1",
        author_role="medico",
        sections=_valid_sbar_sections(),
    )
    create_evolution(
        mpi_id="MPI-100",
        type="diaria",
        template_id="medico_diaria",
        author="Dr. Diaria2",
        author_role="medico",
        sections=_valid_sbar_sections(),
    )
