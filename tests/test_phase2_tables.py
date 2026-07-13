"""
Testes para as tabelas de hot-cache Phase-2 e enriquecimento FHIR.

Cobre:
- Idempotência de lab_result (fhir_id + collected_at)
- Cadeia de FK medication_order → medication_administration
- FHIR enrichment pull (mocked HTTP)
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from intensicare.fhir.client import (
    FHIRClient,
    FHIRLabResult,
    FHIRMedicationOrder,
    FHIRPatientContext,
)
from intensicare.models.lab_result import LabResult
from intensicare.models.medication import MedicationAdministration, MedicationOrder
from intensicare.models.patient_cache import PatientCache

# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

_NOW = datetime(2026, 7, 5, 12, 0, 0, tzinfo=timezone.utc)


async def _ensure_patient(db: AsyncSession, mpi_id: str) -> None:
    """Cria um PatientCache mínimo se não existir (necessário para FK)."""
    existing = await db.get(PatientCache, mpi_id)
    if existing is None:
        patient = PatientCache(
            mpi_id=mpi_id,
            tenant_id="test-tenant",
            display_name=b"encrypted-name",
            is_active=True,
        )
        db.add(patient)
        await db.flush()


# ═══════════════════════════════════════════════════════════════════════════
# Testes de idempotência de lab_result
# ═══════════════════════════════════════════════════════════════════════════


class TestLabResultIdempotency:
    """Garante que (fhir_id, collected_at) seja único — hypertable idempotency."""

    @pytest.mark.anyio
    async def test_same_fhir_id_and_collected_at_twice_one_row(
        self, db_session: AsyncSession
    ) -> None:
        """Mesmo (fhir_id, collected_at) inserido duas vezes → apenas 1 linha."""
        fhir_id = "obs-lab-001"
        collected = _NOW

        lab1 = LabResult(
            mpi_id="MPI-LAB-001",
            fhir_id=fhir_id,
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=14.2,
            value_unit="g/dL",
            collected_at=collected,
            ingested_at=_NOW,
        )
        db_session.add(lab1)
        await db_session.flush()

        # Segunda inserção com mesma chave natural → violação de UNIQUE
        lab2 = LabResult(
            mpi_id="MPI-LAB-001",
            fhir_id=fhir_id,
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=14.5,
            value_unit="g/dL",
            collected_at=collected,
            ingested_at=_NOW,
        )
        db_session.add(lab2)
        with pytest.raises(IntegrityError):
            await db_session.flush()

    @pytest.mark.anyio
    async def test_different_fhir_id_same_collected_at_two_rows(
        self, db_session: AsyncSession
    ) -> None:
        """fhir_id diferente, mesmo collected_at → dois registros permitidos."""
        collected = _NOW

        lab1 = LabResult(
            mpi_id="MPI-LAB-002",
            fhir_id="obs-lab-002a",
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=14.2,
            value_unit="g/dL",
            collected_at=collected,
            ingested_at=_NOW,
        )
        db_session.add(lab1)
        await db_session.flush()

        lab2 = LabResult(
            mpi_id="MPI-LAB-002",
            fhir_id="obs-lab-002b",
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=13.8,
            value_unit="g/dL",
            collected_at=collected,
            ingested_at=_NOW,
        )
        db_session.add(lab2)
        await db_session.flush()

        # Ambos foram inseridos
        result = await db_session.execute(
            select(LabResult).where(LabResult.mpi_id == "MPI-LAB-002")
        )
        rows = result.scalars().all()
        assert len(rows) == 2

    @pytest.mark.anyio
    async def test_same_fhir_id_different_collected_at_two_rows(
        self, db_session: AsyncSession
    ) -> None:
        """Mesmo fhir_id, collected_at diferente → dois registros (série temporal)."""
        fhir_id = "obs-lab-003"

        lab1 = LabResult(
            mpi_id="MPI-LAB-003",
            fhir_id=fhir_id,
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=14.2,
            value_unit="g/dL",
            collected_at=_NOW,
            ingested_at=_NOW,
        )
        db_session.add(lab1)
        await db_session.flush()

        lab2 = LabResult(
            mpi_id="MPI-LAB-003",
            fhir_id=fhir_id,
            loinc_code="718-7",
            analyte="Hemoglobin",
            value_num=13.5,
            value_unit="g/dL",
            collected_at=datetime(2026, 7, 5, 13, 0, 0, tzinfo=timezone.utc),
            ingested_at=_NOW,
        )
        db_session.add(lab2)
        await db_session.flush()

        result = await db_session.execute(select(LabResult).where(LabResult.fhir_id == fhir_id))
        rows = result.scalars().all()
        assert len(rows) == 2


# ═══════════════════════════════════════════════════════════════════════════
# Testes de cadeia FK medication_order → medication_administration
# ═══════════════════════════════════════════════════════════════════════════


class TestMedicationFKChain:
    """Garante que a FK chain entre medication_order e medication_administration funciona."""

    @pytest.mark.anyio
    async def test_order_to_administration_fk_chain(self, db_session: AsyncSession) -> None:
        """Ordem → administração com FK válida."""
        await _ensure_patient(db_session, "MPI-MED-001")

        order = MedicationOrder(
            mpi_id="MPI-MED-001",
            fhir_id="medreq-001",
            medication_name="Metoprolol",
            dose="50 mg",
            route="Oral",
            frequency="BID",
            ordered_at=_NOW,
            ingested_at=_NOW,
        )
        db_session.add(order)
        await db_session.flush()
        order_id = order.id

        admin = MedicationAdministration(
            mpi_id="MPI-MED-001",
            fhir_id="medadmin-001",
            order_id=order_id,
            administered_at=_NOW,
            dose_given="50 mg",
            route="Oral",
            ingested_at=_NOW,
        )
        db_session.add(admin)
        await db_session.flush()

        # Verifica a relação
        result = await db_session.execute(
            select(MedicationAdministration).where(
                MedicationAdministration.fhir_id == "medadmin-001"
            )
        )
        admin_row = result.scalar_one()
        assert admin_row.order_id == order_id
        assert admin_row.mpi_id == "MPI-MED-001"

    @pytest.mark.anyio
    async def test_administration_without_order_allowed(self, db_session: AsyncSession) -> None:
        """Administração sem order_id (NULL) é permitida (FK ondelete SET NULL)."""
        await _ensure_patient(db_session, "MPI-MED-002")

        admin = MedicationAdministration(
            mpi_id="MPI-MED-002",
            fhir_id="medadmin-002",
            order_id=None,
            administered_at=_NOW,
            dose_given="500 mg",
            route="IV",
            ingested_at=_NOW,
        )
        db_session.add(admin)
        await db_session.flush()

        result = await db_session.execute(
            select(MedicationAdministration).where(
                MedicationAdministration.fhir_id == "medadmin-002"
            )
        )
        admin_row = result.scalar_one()
        assert admin_row.order_id is None

    @pytest.mark.anyio
    async def test_order_cascade_on_patient_delete(self, db_session: AsyncSession) -> None:
        """Ao deletar patient_cache, medication_order é removido em cascata."""
        await _ensure_patient(db_session, "MPI-MED-003")

        order = MedicationOrder(
            mpi_id="MPI-MED-003",
            fhir_id="medreq-003",
            medication_name="Paracetamol",
            dose="500 mg",
            route="Oral",
            ordered_at=_NOW,
            ingested_at=_NOW,
        )
        db_session.add(order)
        await db_session.flush()

        # Deleta o paciente
        patient = await db_session.get(PatientCache, "MPI-MED-003")
        await db_session.delete(patient)
        await db_session.flush()

        # A ordem deve ter sido removida em cascata
        result = await db_session.execute(
            select(MedicationOrder).where(MedicationOrder.fhir_id == "medreq-003")
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.anyio
    async def test_multiple_administrations_per_order(self, db_session: AsyncSession) -> None:
        """Múltiplas administrações para a mesma ordem."""
        await _ensure_patient(db_session, "MPI-MED-004")

        order = MedicationOrder(
            mpi_id="MPI-MED-004",
            fhir_id="medreq-004",
            medication_name="Insulin Glargine",
            dose="10 units",
            route="Subcutaneous",
            frequency="QD",
            ordered_at=_NOW,
            ingested_at=_NOW,
        )
        db_session.add(order)
        await db_session.flush()
        order_id = order.id

        for i in range(3):
            admin = MedicationAdministration(
                mpi_id="MPI-MED-004",
                fhir_id=f"medadmin-004-{i}",
                order_id=order_id,
                administered_at=datetime(2026, 7, 5, 8 + i, 0, 0, tzinfo=timezone.utc),
                dose_given="10 units",
                route="Subcutaneous",
                ingested_at=_NOW,
            )
            db_session.add(admin)
        await db_session.flush()

        result = await db_session.execute(
            select(MedicationAdministration).where(MedicationAdministration.order_id == order_id)
        )
        admins = result.scalars().all()
        assert len(admins) == 3


# ═══════════════════════════════════════════════════════════════════════════
# Testes de FHIR enrichment pull (mocked)
# ═══════════════════════════════════════════════════════════════════════════

MOCK_LAB_OBSERVATION = {
    "resourceType": "Observation",
    "id": "obs-lab-100",
    "status": "final",
    "category": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                }
            ]
        }
    ],
    "code": {
        "coding": [
            {
                "system": "http://loinc.org",
                "code": "718-7",
                "display": "Hemoglobin [Mass/volume] in Blood",
            }
        ]
    },
    "subject": {"reference": "Patient/MPI-FHIR-001"},
    "effectiveDateTime": "2026-07-05T10:00:00Z",
    "issued": "2026-07-05T10:30:00Z",
    "valueQuantity": {"value": 14.2, "unit": "g/dL", "system": "http://unitsofmeasure.org"},
    "referenceRange": [
        {"low": {"value": 12.0, "unit": "g/dL"}, "high": {"value": 16.0, "unit": "g/dL"}}
    ],
    "interpretation": [
        {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "N",
                }
            ]
        }
    ],
}

MOCK_MEDICATION_REQUEST = {
    "resourceType": "MedicationRequest",
    "id": "medreq-100",
    "status": "active",
    "intent": "order",
    "medicationCodeableConcept": {
        "coding": [
            {
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": "6918",
                "display": "Metoprolol Tartrate 50 MG Oral Tablet",
            }
        ],
        "text": "Metoprolol 50 mg",
    },
    "subject": {"reference": "Patient/MPI-FHIR-001"},
    "authoredOn": "2026-07-05T08:00:00Z",
    "dosageInstruction": [
        {
            "text": "50 mg oral BID",
            "timing": {
                "code": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-GTSAbbreviation",
                            "code": "BID",
                            "display": "BID",
                        }
                    ]
                }
            },
            "route": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "26643006",
                        "display": "Oral route",
                    }
                ]
            },
            "doseAndRate": [
                {"doseQuantity": {"value": 50, "unit": "mg", "system": "http://unitsofmeasure.org"}}
            ],
        }
    ],
}

MOCK_MEDICATION_ADMINISTRATION = {
    "resourceType": "MedicationAdministration",
    "id": "medadmin-100",
    "status": "completed",
    "medicationCodeableConcept": {
        "coding": [
            {
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": "6918",
                "display": "Metoprolol Tartrate",
            }
        ]
    },
    "subject": {"reference": "Patient/MPI-FHIR-001"},
    "request": {"reference": "MedicationRequest/medreq-100"},
    "effectiveDateTime": "2026-07-05T09:00:00Z",
    "dosage": {
        "dose": {"value": 50, "unit": "mg"},
        "route": {
            "coding": [
                {"system": "http://snomed.info/sct", "code": "26643006", "display": "Oral route"}
            ]
        },
    },
}


class TestFHIREnrichmentPull:
    """Testa os métodos de enrichment do FHIRClient com HTTP mockado."""

    @pytest.mark.anyio
    async def test_enrich_lab_result_success(self) -> None:
        """enrich_lab_result retorna FHIRLabResult com dados parseados."""
        client = FHIRClient(base_url="https://fhir.example.com/fhir")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_LAB_OBSERVATION
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock(spec=httpx.AsyncClient)
        mock_http.get.return_value = mock_response

        with patch.object(client, "_get_client", return_value=mock_http):
            result = await client.enrich_lab_result("obs-lab-100")

        assert result is not None
        assert isinstance(result, FHIRLabResult)
        assert result.fhir_id == "obs-lab-100"
        assert result.mpi_id == "MPI-FHIR-001"
        assert result.loinc_code == "718-7"
        assert result.analyte == "Hemoglobin [Mass/volume] in Blood"
        assert result.value_num == 14.2
        assert result.value_unit == "g/dL"
        assert result.reference_low == 12.0
        assert result.reference_high == 16.0
        assert result.abnormal_flag == "N"
        assert result.collected_at is not None

    @pytest.mark.anyio
    async def test_enrich_lab_result_unconfigured(self) -> None:
        """FHIR não configurado → retorna None."""
        client = FHIRClient(base_url="")
        result = await client.enrich_lab_result("obs-any")
        assert result is None

    @pytest.mark.anyio
    async def test_enrich_lab_result_not_found(self) -> None:
        """404 → retorna None."""
        client = FHIRClient(base_url="https://fhir.example.com/fhir")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
        mock_response.raise_for_status.side_effect = http_error

        mock_http = AsyncMock(spec=httpx.AsyncClient)
        mock_http.get.return_value = mock_response

        with patch.object(client, "_get_client", return_value=mock_http):
            result = await client.enrich_lab_result("obs-nonexistent")

        assert result is None

    @pytest.mark.anyio
    async def test_enrich_medication_success(self) -> None:
        """enrich_medication retorna FHIRMedicationOrder com dados parseados."""
        client = FHIRClient(base_url="https://fhir.example.com/fhir")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_MEDICATION_REQUEST
        mock_response.raise_for_status = MagicMock()

        mock_http = AsyncMock(spec=httpx.AsyncClient)
        mock_http.get.return_value = mock_response

        with patch.object(client, "_get_client", return_value=mock_http):
            result = await client.enrich_medication("medreq-100")

        assert result is not None
        assert isinstance(result, FHIRMedicationOrder)
        assert result.fhir_id == "medreq-100"
        assert result.mpi_id == "MPI-FHIR-001"
        assert result.medication_name == "Metoprolol Tartrate 50 MG Oral Tablet"
        assert result.dose == "50 mg"
        assert result.route == "Oral route"
        assert result.frequency == "BID"
        assert result.ordered_at is not None

    @pytest.mark.anyio
    async def test_enrich_medication_unconfigured(self) -> None:
        """FHIR não configurado → retorna None."""
        client = FHIRClient(base_url="")
        result = await client.enrich_medication("medreq-any")
        assert result is None

    @pytest.mark.anyio
    async def test_enrich_patient_context_aggregates(self) -> None:
        """enrich_patient_context agrega labs + medications + administrations."""
        client = FHIRClient(base_url="https://fhir.example.com/fhir")

        obs_bundle = {
            "resourceType": "Bundle",
            "entry": [{"resource": MOCK_LAB_OBSERVATION}],
        }
        med_bundle = {
            "resourceType": "Bundle",
            "entry": [{"resource": MOCK_MEDICATION_REQUEST}],
        }
        admin_bundle = {
            "resourceType": "Bundle",
            "entry": [{"resource": MOCK_MEDICATION_ADMINISTRATION}],
        }

        mock_http = AsyncMock(spec=httpx.AsyncClient)

        def _make_response(json_body):
            resp = MagicMock(spec=httpx.Response)
            resp.status_code = 200
            resp.json.return_value = json_body
            resp.raise_for_status = MagicMock()
            return resp

        mock_http.get.side_effect = [
            _make_response(obs_bundle),
            _make_response(med_bundle),
            _make_response(admin_bundle),
        ]

        with patch.object(client, "_get_client", return_value=mock_http):
            result = await client.enrich_patient_context("MPI-FHIR-001")

        assert result is not None
        assert isinstance(result, FHIRPatientContext)
        assert result.mpi_id == "MPI-FHIR-001"
        assert len(result.lab_results) == 1
        assert len(result.medication_orders) == 1
        assert len(result.medication_administrations) == 1

        lab = result.lab_results[0]
        assert lab.loinc_code == "718-7"
        assert lab.value_num == 14.2

        med = result.medication_orders[0]
        assert med.medication_name == "Metoprolol Tartrate 50 MG Oral Tablet"

        admin = result.medication_administrations[0]
        assert admin.fhir_id == "medadmin-100"
        assert admin.order_fhir_id == "medreq-100"
        assert admin.dose_given == "50 mg"

    @pytest.mark.anyio
    async def test_enrich_patient_context_unconfigured(self) -> None:
        """FHIR não configurado → retorna None."""
        client = FHIRClient(base_url="")
        result = await client.enrich_patient_context("MPI-ANY")
        assert result is None

    @pytest.mark.anyio
    async def test_enrich_patient_context_connection_error(self) -> None:
        """Erro de conexão → retorna None graciosamente."""
        client = FHIRClient(base_url="https://fhir.example.com/fhir")

        mock_http = AsyncMock(spec=httpx.AsyncClient)
        mock_http.get.side_effect = httpx.ConnectError("Connection refused")

        with patch.object(client, "_get_client", return_value=mock_http):
            result = await client.enrich_patient_context("MPI-ANY")

        assert result is None
