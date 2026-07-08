"""Tests for Documentation/Billing domain service — Glosa Zero engine (16 criteria)."""

from __future__ import annotations

import pytest

from intensicare.services.domain_documentacao import (
    GLOSA_CRITERIA,
    GLOSA_MAX_SCORE,
    GLOSA_STATUSES,
    DocumentacaoRecord,
    GlosaEvaluationResult,
    DocumentacaoListResult,
    create_documentacao,
    list_documentacao,
    evaluate_glosa,
    update_glosa_status,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixture — reset the in-memory store before each test
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _reset_store(monkeypatch):
    """Reset the in-memory documentation store before every test."""
    monkeypatch.setattr(
        "intensicare.services.domain_documentacao._documentacao_store", {}
    )
    monkeypatch.setattr(
        "intensicare.services.domain_documentacao._next_documentacao_id", 1
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GLOSA_CRITERIA constants
# ═══════════════════════════════════════════════════════════════════════════════


class TestGlosaCriteria:
    """Tests for GLOSA_CRITERIA, GLOSA_MAX_SCORE, and GLOSA_STATUSES."""

    def test_16_criteria_defined(self):
        """GLOSA_CRITERIA must contain exactly 16 criteria."""
        assert len(GLOSA_CRITERIA) == 16

    def test_max_score_66(self):
        """GLOSA_MAX_SCORE must be 66."""
        assert GLOSA_MAX_SCORE == 66

    def test_weights_sum_is_61(self):
        """Sum of all criteria weights is 61 (GLOSA_MAX_SCORE=66 per spec)."""
        total = sum(c["weight"] for c in GLOSA_CRITERIA)
        assert total == 61
        # The spec defines GLOSA_MAX_SCORE as 66 even though the
        # weights sum to 61 — a known intentional discrepancy.

    def test_all_criteria_have_required_fields(self):
        """Every criterion must have id, name, category, and weight."""
        for c in GLOSA_CRITERIA:
            assert "id" in c
            assert "name" in c
            assert "category" in c
            assert "weight" in c
            assert isinstance(c["id"], str)
            assert isinstance(c["name"], str)
            assert isinstance(c["category"], str)
            assert isinstance(c["weight"], int)
            assert c["weight"] > 0

    def test_all_criteria_ids_unique(self):
        """All criterion IDs must be unique."""
        ids = [c["id"] for c in GLOSA_CRITERIA]
        assert len(ids) == len(set(ids))

    def test_glosa_statuses_defined(self):
        """GLOSA_STATUSES must contain the 5 required statuses."""
        assert len(GLOSA_STATUSES) == 5
        assert "pendente" in GLOSA_STATUSES
        assert "em_analise" in GLOSA_STATUSES
        assert "glosado" in GLOSA_STATUSES
        assert "liberado" in GLOSA_STATUSES
        assert "recorrido" in GLOSA_STATUSES


# ═══════════════════════════════════════════════════════════════════════════════
# create_documentacao
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreateDocumentacao:
    """Tests for create_documentacao()."""

    def test_create_basic(self):
        """Minimal creation: returns a DocumentacaoRecord with 'pendente' status."""
        record = create_documentacao(
            mpi_id="PAT-001",
            type="evolucao",
            description="Evolução clínica do paciente",
        )
        assert record.id == 1
        assert record.mpi_id == "PAT-001"
        assert record.type == "evolucao"
        assert record.description == "Evolução clínica do paciente"
        assert record.glosa_status == "pendente"
        assert record.glosa_motivo is None
        assert record.glosa_valor is None
        assert record.data_registro  # non-empty ISO timestamp
        assert record.data_documento  # defaults to now

    def test_create_with_all_fields(self):
        """Creation with all optional fields populated."""
        record = create_documentacao(
            mpi_id="PAT-002",
            type="prescricao",
            description="Prescrição médica diária",
            data_documento="2025-06-15T10:00:00Z",
            profissional="Dr. Silva",
            observacoes="Paciente estável",
        )
        assert record.mpi_id == "PAT-002"
        assert record.type == "prescricao"
        assert record.profissional == "Dr. Silva"
        assert record.observacoes == "Paciente estável"
        assert record.data_documento == "2025-06-15T10:00:00Z"
        assert record.glosa_status == "pendente"

    def test_create_increments_id(self):
        """Each call to create_documentacao yields a monotonically increasing id."""
        r1 = create_documentacao("PAT-001", "evolucao", "Doc 1")
        r2 = create_documentacao("PAT-001", "prescricao", "Doc 2")
        r3 = create_documentacao("PAT-002", "exame", "Doc 3")
        assert r1.id == 1
        assert r2.id == 2
        assert r3.id == 3


# ═══════════════════════════════════════════════════════════════════════════════
# list_documentacao
# ═══════════════════════════════════════════════════════════════════════════════


class TestListDocumentacao:
    """Tests for list_documentacao()."""

    def test_list_by_mpi_id(self):
        """Listing filters records by mpi_id and returns correct total."""
        create_documentacao("PAT-A", "evolucao", "Doc 1")
        create_documentacao("PAT-A", "prescricao", "Doc 2")
        create_documentacao("PAT-B", "evolucao", "Doc 3")

        result = list_documentacao("PAT-A")
        assert result.total == 2
        assert len(result.items) == 2
        assert all(r.mpi_id == "PAT-A" for r in result.items)

    def test_list_empty(self):
        """Listing a non-existent mpi_id returns empty result."""
        result = list_documentacao("NONEXISTENT")
        assert result.total == 0
        assert result.items == []
        assert isinstance(result, DocumentacaoListResult)

    def test_list_filter_by_glosa_status(self):
        """Optional glosa_status filter narrows results."""
        create_documentacao("PAT-C", "evolucao", "Doc 1")  # pendente
        create_documentacao("PAT-C", "evolucao", "Doc 2")  # pendente

        result = list_documentacao("PAT-C", glosa_status="pendente")
        assert result.total == 2

        result = list_documentacao("PAT-C", glosa_status="liberado")
        assert result.total == 0

    def test_list_pagination(self):
        """Limit and offset pagination controls the returned slice."""
        for i in range(5):
            create_documentacao("PAT-D", "evolucao", f"Doc {i}")

        page1 = list_documentacao("PAT-D", limit=2, offset=0)
        assert len(page1.items) == 2
        assert page1.total == 5  # total is pre-slice count

        page2 = list_documentacao("PAT-D", limit=2, offset=2)
        assert len(page2.items) == 2

        page3 = list_documentacao("PAT-D", limit=10, offset=4)
        assert len(page3.items) == 1
        assert page3.total == 5


# ═══════════════════════════════════════════════════════════════════════════════
# evaluate_glosa
# ═══════════════════════════════════════════════════════════════════════════════


class TestGlosaEvaluation:
    """Tests for evaluate_glosa() — the Glosa Zero scoring engine."""

    def test_evaluate_not_found(self):
        """Evaluating a non-existent ID returns score 0 and all criteria missing."""
        result = evaluate_glosa(999)
        assert result.documentacao_id == 999
        assert result.score == 0
        assert result.max_score == 66
        assert result.glosa_status == "pendente"
        assert len(result.criteria_met) == 0
        assert len(result.criteria_missing) == 16
        assert "não encontrado" in result.recommendation.lower()

    def test_liberado_full_score(self):
        """A fully compliant document scores ≥55 and returns 'liberado'."""
        record = create_documentacao(
            mpi_id="PAT-001",
            type="evolucao",
            description=(
                "Paciente com J18.9 e I10. "
                "Realizado procedimento 03.03.04.015-0. "
                "Paciente internado na UTI. "
                "Gasometria arterial mostra PaO2 90. "
                "Medicamento administrado com justificativa. "
                "Exames laboratoriais solicitados. "
                "Procedimento realizado conforme protocolo. "
                "Evolução clínica e prescrição do dia. "
                "assinatura digital CRM 12345"
            ),
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert result.glosa_status == "liberado"
        assert result.score >= 55
        assert result.score <= GLOSA_MAX_SCORE
        assert len(result.criteria_met) + len(result.criteria_missing) == 16

    def test_liberado_threshold(self):
        """Score of exactly 55 or above must result in 'liberado'."""
        # Build a record that hits at least 55 points
        record = create_documentacao(
            mpi_id="PAT-THR",
            type="evolucao",
            description=(
                "J18.9 I10 CRM 12345 UTI gasometria "
                "medicamento justificativa exame "
                "procedimento 03.03.04.015-0 "
                "evolução clínica prescrição assinatura"
            ),
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert result.glosa_status == "liberado"
        assert result.score >= 55

    def test_em_analise_threshold(self):
        """Score between 35 and 54 (inclusive) returns 'em_analise'."""
        record = create_documentacao(
            mpi_id="PAT-002",
            type="evolucao",
            description=(
                "J18.9 CRM 12345 UTI gasometria "
                "medicamento justificativa"
            ),
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert result.glosa_status == "em_analise"
        assert 35 <= result.score < 55

    def test_glosado_below_threshold(self):
        """Score below 35 returns 'glosado'."""
        record = create_documentacao(
            mpi_id="PAT-003",
            type="outro",
            description="Documento sem informações relevantes",
        )
        result = evaluate_glosa(record.id)
        assert result.glosa_status == "glosado"
        assert result.score < 35

    def test_glosado_minimal(self):
        """Minimal record (only mpi_id + date) scores below 35 → glosado."""
        record = create_documentacao(
            mpi_id="PAT-MIN",
            type="outro",
            description=".",
        )
        result = evaluate_glosa(record.id)
        # GZ-001(3) + GZ-002(3) + GZ-015(3) + GZ-016(3) = 12
        assert result.glosa_status == "glosado"
        assert result.score == 12  # only the auto-pass and basic id/date

    def test_evaluate_returns_complete_result(self):
        """Result includes all expected fields with correct counts."""
        record = create_documentacao(
            mpi_id="PAT-004",
            type="evolucao",
            description="J18.9 CRM 12345 UTI gasometria",
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert result.documentacao_id == record.id
        assert result.max_score == 66
        assert len(result.criteria_met) > 0
        assert len(result.criteria_missing) > 0
        assert len(result.criteria_met) + len(result.criteria_missing) == 16
        assert isinstance(result.recommendation, str)
        assert len(result.recommendation) > 0

    def test_cid_detection_gz005(self):
        """CID-10 pattern (e.g. J18.9) satisfies GZ-005."""
        record = create_documentacao(
            mpi_id="PAT-CID",
            type="evolucao",
            description="Paciente com diagnóstico de J18.9",
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert "GZ-005" in result.criteria_met

    def test_secondary_cid_gz006(self):
        """Two or more CID codes satisfy GZ-006 (secondary diagnoses)."""
        record = create_documentacao(
            mpi_id="PAT-CID2",
            type="evolucao",
            description="CID primário J18.9 e secundário I10, com CRM 12345",
            profissional="Dr. Silva",
        )
        result = evaluate_glosa(record.id)
        assert "GZ-006" in result.criteria_met


# ═══════════════════════════════════════════════════════════════════════════════
# update_glosa_status
# ═══════════════════════════════════════════════════════════════════════════════


class TestUpdateStatus:
    """Tests for update_glosa_status()."""

    def test_update_valid_status(self):
        """Updating to a valid status succeeds and stores motivo."""
        record = create_documentacao("PAT-001", "evolucao", "Teste")
        updated = update_glosa_status(record.id, "liberado", motivo="Auditado e aprovado")
        assert updated.glosa_status == "liberado"
        assert updated.glosa_motivo == "Auditado e aprovado"

    def test_update_lifecycle_transitions(self):
        """Full lifecycle: pendente → em_analise → glosado → recorrido."""
        record = create_documentacao("PAT-002", "evolucao", "Teste")
        assert record.glosa_status == "pendente"

        updated = update_glosa_status(record.id, "em_analise")
        assert updated.glosa_status == "em_analise"

        updated = update_glosa_status(record.id, "glosado", motivo="Falta CID-10")
        assert updated.glosa_status == "glosado"
        assert updated.glosa_motivo == "Falta CID-10"

        updated = update_glosa_status(record.id, "recorrido", motivo="Recurso apresentado")
        assert updated.glosa_status == "recorrido"

    def test_update_invalid_status_raises(self):
        """Passing an unknown status raises ValueError."""
        record = create_documentacao("PAT-003", "evolucao", "Teste")
        with pytest.raises(ValueError, match="Invalid glosa status"):
            update_glosa_status(record.id, "status_invalido")

    def test_update_not_found_raises(self):
        """Passing a non-existent document ID raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            update_glosa_status(999, "liberado")
