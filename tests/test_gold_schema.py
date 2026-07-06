"""Testes para o módulo gold_schema — schemas e templates SQL da camada Gold."""

from __future__ import annotations

import pytest

from intensicare.services.gold_schema import (
    DOMAIN_CADENCE,
    DOMAIN_WATERMARK_COLUMN,
    FactAlert,
    FactPatientScore,
    GoldColumn,
    GoldTableSchema,
    LAB_RESULT_SCHEMA,
    MEDICATION_SCHEMA,
    VITAL_SIGN_SCHEMA,
    build_domain_query,
    build_incremental_query,
    _domain_to_table,
    _domain_columns,
)


# ---------------------------------------------------------------------------
# Constantes de domínio
# ---------------------------------------------------------------------------


class TestDomainCadence:
    """Testa as cadências padrão por domínio clínico."""

    def test_sepsis_cadence(self):
        assert DOMAIN_CADENCE["sepsis"] == 300

    def test_aki_cadence(self):
        assert DOMAIN_CADENCE["aki"] == 3600

    def test_electrolytes_cadence(self):
        assert DOMAIN_CADENCE["electrolytes"] == 120

    def test_all_domains_have_positive_cadence(self):
        for domain, cadence in DOMAIN_CADENCE.items():
            assert cadence > 0, f"{domain} cadence must be positive"


class TestDomainWatermark:
    """Testa as colunas de watermark por domínio."""

    def test_most_domains_use_ingested_at(self):
        for domain in ["sepsis", "electrolytes", "aki", "ventilation", "hemodynamics"]:
            assert DOMAIN_WATERMARK_COLUMN[domain] == "ingested_at"

    def test_medication_uses_administered_at(self):
        assert DOMAIN_WATERMARK_COLUMN["medication"] == "administered_at"


# ---------------------------------------------------------------------------
# GoldColumn / GoldTableSchema
# ---------------------------------------------------------------------------


class TestGoldColumn:
    def test_create_column(self):
        col = GoldColumn("test_col", "VARCHAR", nullable=False, description="Test")
        assert col.name == "test_col"
        assert col.data_type == "VARCHAR"
        assert col.nullable is False
        assert col.description == "Test"

    def test_column_default_nullable(self):
        col = GoldColumn("col", "INTEGER")
        assert col.nullable is True
        assert col.description == ""


class TestGoldTableSchema:
    def test_schema_has_columns(self):
        assert len(VITAL_SIGN_SCHEMA.columns) > 0
        assert VITAL_SIGN_SCHEMA.table_name == "gold_vital_sign"

    def test_lab_schema_has_columns(self):
        assert len(LAB_RESULT_SCHEMA.columns) > 0
        assert LAB_RESULT_SCHEMA.table_name == "gold_lab_result"

    def test_medication_schema_has_columns(self):
        assert len(MEDICATION_SCHEMA.columns) > 0
        assert MEDICATION_SCHEMA.table_name == "gold_medication"


# ---------------------------------------------------------------------------
# _domain_to_table
# ---------------------------------------------------------------------------


class TestDomainToTable:
    def test_sepsis_maps_to_lab(self):
        assert _domain_to_table("sepsis") == "gold_lab_result"

    def test_aki_maps_to_lab(self):
        assert _domain_to_table("aki") == "gold_lab_result"

    def test_hemodynamics_maps_to_vital_sign(self):
        assert _domain_to_table("hemodynamics") == "gold_vital_sign"

    def test_medication_maps_correctly(self):
        assert _domain_to_table("medication") == "gold_medication"

    def test_unknown_domain_defaults_to_vital_sign(self):
        assert _domain_to_table("unknown_domain") == "gold_vital_sign"


# ---------------------------------------------------------------------------
# _domain_columns
# ---------------------------------------------------------------------------


class TestDomainColumns:
    def test_sepsis_columns_include_common(self):
        cols = _domain_columns("sepsis")
        assert "patient_id" in cols
        assert "parameter" in cols
        assert "value" in cols

    def test_medication_columns_exclude_value(self):
        cols = _domain_columns("medication")
        assert "drug_name" in cols
        assert "dose" in cols
        # medication uses drug-oriented columns, not parameter/value
        assert "parameter" not in cols


# ---------------------------------------------------------------------------
# build_incremental_query
# ---------------------------------------------------------------------------


class TestBuildIncrementalQuery:
    def test_full_load_when_no_watermark(self):
        query = build_incremental_query("sepsis", "tenant-1", None)
        assert "WHERE tenant_id = 'tenant-1'" in query
        assert "LIMIT 10000" in query
        # No watermark filter on full load
        assert ">" not in query.split("WHERE")[-1] if ">" in query.split("WHERE")[-1] else True

    def test_incremental_with_watermark(self):
        query = build_incremental_query(
            "sepsis", "tenant-1", "2026-01-01T00:00:00",
        )
        assert "ingested_at > TIMESTAMP '2026-01-01T00:00:00'" in query
        assert "tenant_id = 'tenant-1'" in query

    def test_custom_limit(self):
        query = build_incremental_query("aki", "t1", None, limit=500)
        assert "LIMIT 500" in query


# ---------------------------------------------------------------------------
# build_domain_query
# ---------------------------------------------------------------------------


class TestBuildDomainQuery:
    def test_selects_domain_columns(self):
        query = build_domain_query("sepsis", "tenant-1", None)
        assert "SELECT" in query
        assert "patient_id" in query

    def test_includes_watermark_filter(self):
        query = build_domain_query(
            "hemodynamics", "t1", "2026-06-01T00:00:00",
        )
        assert "ingested_at > TIMESTAMP" in query


# ---------------------------------------------------------------------------
# FactPatientScore / FactAlert models
# ---------------------------------------------------------------------------


class TestFactModels:
    def test_fact_patient_score_tablename(self):
        assert FactPatientScore.__tablename__ == "fact_patient_score"

    def test_fact_patient_score_has_unique_constraint(self):
        args = FactPatientScore.__table_args__
        assert args is not None
        # Should have a UniqueConstraint on source_score_id
        assert any("source_score_id" in str(c) for c in (args if isinstance(args, tuple) else [args]))

    def test_fact_alert_tablename(self):
        assert FactAlert.__tablename__ == "fact_alert"

    def test_fact_alert_has_unique_constraint(self):
        args = FactAlert.__table_args__
        assert args is not None
        assert any("source_alert_id" in str(c) for c in (args if isinstance(args, tuple) else [args]))
