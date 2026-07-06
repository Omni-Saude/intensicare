"""
FHIR R4 client for HAPI FHIR server integration.

Queries Patient and Observation resources from a configurable FHIR endpoint.
Gracefully degrades when no FHIR server is configured.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import lru_cache
import logging
from typing import Any, cast

import httpx

from intensicare.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FHIRLabResult:
    """Parsed lab result from a FHIR Observation resource."""

    fhir_id: str
    mpi_id: str
    loinc_code: str | None = None
    analyte: str | None = None
    value_num: float | None = None
    value_unit: str | None = None
    reference_low: float | None = None
    reference_high: float | None = None
    abnormal_flag: str | None = None
    collected_at: datetime | None = None
    resulted_at: datetime | None = None

    @classmethod
    def from_observation(cls, mpi_id: str, resource: dict[str, Any]) -> FHIRLabResult:
        """Parse a FHIR Observation resource into a FHIRLabResult."""
        code = resource.get("code", {})
        coding_list = code.get("coding", [])
        loinc_coding = next(
            (c for c in coding_list if c.get("system") == "http://loinc.org"),
            coding_list[0] if coding_list else {},
        )
        loinc_code_val = loinc_coding.get("code")
        analyte_val = loinc_coding.get("display") or code.get("text")

        value_num: float | None = None
        value_unit: str | None = None
        if "valueQuantity" in resource:
            vq = resource["valueQuantity"]
            value_num = vq.get("value")
            value_unit = vq.get("unit")

        reference_low: float | None = None
        reference_high: float | None = None
        ref_ranges = resource.get("referenceRange", [])
        if ref_ranges:
            rr = ref_ranges[0]
            low = rr.get("low", {})
            high = rr.get("high", {})
            reference_low = low.get("value") if low else None
            reference_high = high.get("value") if high else None

        abnormal_flag: str | None = None
        interpretation = resource.get("interpretation", [])
        if interpretation:
            interp_coding = interpretation[0].get("coding", [])
            if interp_coding:
                abnormal_flag = interp_coding[0].get("code")

        collected_at: datetime | None = None
        effective = resource.get("effectiveDateTime")
        if effective:
            with contextlib.suppress(ValueError, TypeError):
                collected_at = datetime.fromisoformat(effective.replace("Z", "+00:00"))

        resulted_at: datetime | None = None
        issued = resource.get("issued")
        if issued:
            with contextlib.suppress(ValueError, TypeError):
                resulted_at = datetime.fromisoformat(issued.replace("Z", "+00:00"))

        return cls(
            fhir_id=resource.get("id", ""),
            mpi_id=mpi_id,
            loinc_code=loinc_code_val,
            analyte=analyte_val,
            value_num=value_num,
            value_unit=value_unit,
            reference_low=reference_low,
            reference_high=reference_high,
            abnormal_flag=abnormal_flag,
            collected_at=collected_at,
            resulted_at=resulted_at,
        )


@dataclass
class FHIRMedicationOrder:
    """Parsed medication order from a FHIR MedicationRequest resource."""

    fhir_id: str
    mpi_id: str
    medication_name: str | None = None
    dose: str | None = None
    route: str | None = None
    frequency: str | None = None
    ordered_at: datetime | None = None

    @classmethod
    def from_medication_request(
        cls, mpi_id: str, resource: dict[str, Any]
    ) -> FHIRMedicationOrder:
        """Parse a FHIR MedicationRequest resource."""
        # Medication name via medicationCodeableConcept
        med_cc = resource.get("medicationCodeableConcept", {})
        med_coding = med_cc.get("coding", [{}])
        med_name = med_coding[0].get("display") or med_cc.get("text")

        # Dose from dosageInstruction
        dose: str | None = None
        route: str | None = None
        frequency: str | None = None
        dosage_instructions = resource.get("dosageInstruction", [])
        if dosage_instructions:
            di = dosage_instructions[0]
            # Dose
            dose_and_rate = di.get("doseAndRate", [])
            if dose_and_rate:
                dq = dose_and_rate[0].get("doseQuantity", {})
                if dq:
                    dose = f"{dq.get('value')} {dq.get('unit')}".strip()
            # Route
            route_cc = di.get("route", {})
            route_coding = route_cc.get("coding", [{}])
            route = route_coding[0].get("display") or route_cc.get("text")
            # Frequency (timing)
            timing = di.get("timing", {})
            timing_code = timing.get("code", {})
            timing_coding = timing_code.get("coding", [{}])
            frequency = timing_coding[0].get("display") or timing_code.get("text")

        ordered_at: datetime | None = None
        authored = resource.get("authoredOn")
        if authored:
            with contextlib.suppress(ValueError, TypeError):
                ordered_at = datetime.fromisoformat(authored.replace("Z", "+00:00"))

        return cls(
            fhir_id=resource.get("id", ""),
            mpi_id=mpi_id,
            medication_name=med_name,
            dose=dose,
            route=route,
            frequency=frequency,
            ordered_at=ordered_at,
        )


@dataclass
class FHIRMedicationAdministration:
    """Parsed medication administration from a FHIR MedicationAdministration resource."""

    fhir_id: str
    mpi_id: str
    order_fhir_id: str | None = None
    administered_at: datetime | None = None
    dose_given: str | None = None
    route: str | None = None

    @classmethod
    def from_administration(
        cls, mpi_id: str, resource: dict[str, Any]
    ) -> FHIRMedicationAdministration:
        """Parse a FHIR MedicationAdministration resource."""
        # Link to MedicationRequest
        order_fhir_id: str | None = None
        request_ref = resource.get("request", {})
        if request_ref:
            ref = request_ref.get("reference", "")
            # e.g. "MedicationRequest/medreq-001"
            order_fhir_id = ref.split("/")[-1] if "/" in ref else ref

        # Dose
        dose_given: str | None = None
        dq = resource.get("dosage", {}).get("dose", {})
        if dq:
            dose_given = f"{dq.get('value')} {dq.get('unit')}".strip()

        # Route
        route: str | None = None
        route_cc = resource.get("dosage", {}).get("route", {})
        route_coding = route_cc.get("coding", [{}])
        route = route_coding[0].get("display") or route_cc.get("text")

        administered_at: datetime | None = None
        effective = resource.get("effectiveDateTime")
        if effective:
            with contextlib.suppress(ValueError, TypeError):
                administered_at = datetime.fromisoformat(effective.replace("Z", "+00:00"))

        return cls(
            fhir_id=resource.get("id", ""),
            mpi_id=mpi_id,
            order_fhir_id=order_fhir_id,
            administered_at=administered_at,
            dose_given=dose_given,
            route=route,
        )


@dataclass
class FHIRPatientContext:
    """Aggregated enrichment context for a patient (labs + medications)."""

    mpi_id: str
    lab_results: list[FHIRLabResult] = field(default_factory=list)
    medication_orders: list[FHIRMedicationOrder] = field(default_factory=list)
    medication_administrations: list[FHIRMedicationAdministration] = field(default_factory=list)


@dataclass
class FHIRPatientData:
    """Enriched patient data fetched from a FHIR server."""

    mpi_id: str
    display_name: str | None = None
    gender: str | None = None
    birth_date: date | None = None
    marital_status: str | None = None
    phone: str | None = None
    address: str | None = None
    primary_condition: str | None = None
    condition_list: list[str] = field(default_factory=list)
    allergy_list: list[str] = field(default_factory=list)
    latest_observations: dict[str, Any] = field(default_factory=dict)
    raw_patient_resource: dict[str, Any] | None = None

    @classmethod
    def from_fhir_bundle(cls, mpi_id: str, bundle: dict[str, Any]) -> FHIRPatientData:
        """Parse a FHIR searchset bundle into structured FHIRPatientData.

        Expects a bundle with Patient, Condition, AllergyIntolerance, and
        Observation entries (typically from a $everything or composite query).
        """
        data: dict[str, Any] = {"mpi_id": mpi_id}

        if bundle.get("resourceType") != "Bundle":
            return cls(mpi_id=mpi_id)

        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource is None:
                continue
            rt = resource.get("resourceType")

            if rt == "Patient":
                data.update(cls._parse_patient(resource))
                if "raw_patient_resource" not in data:
                    data["raw_patient_resource"] = resource
            elif rt == "Condition":
                cls._parse_condition(resource, data)
            elif rt == "AllergyIntolerance":
                cls._parse_allergy(resource, data)
            elif rt == "Observation":
                cls._parse_observation(resource, data)

        return cls(**data)

    @staticmethod
    def _parse_patient(resource: dict[str, Any]) -> dict[str, Any]:
        parsed: dict[str, Any] = {}

        # Name
        names = resource.get("name", [])
        if names:
            official = next((n for n in names if n.get("use") == "official"), names[0])
            parts = []
            for prefix in ("prefix", "given", "family"):
                val = official.get(prefix)
                if val:
                    parts.extend(val if isinstance(val, list) else [val])
            parsed["display_name"] = " ".join(parts) if parts else official.get("text")

        # Gender
        parsed["gender"] = resource.get("gender")

        # Birth date
        bd = resource.get("birthDate")
        if bd:
            with contextlib.suppress(ValueError, TypeError):
                parsed["birth_date"] = date.fromisoformat(bd)

        # Marital status
        ms = resource.get("maritalStatus", {})
        if ms:
            coding = ms.get("coding", [{}])[0] if ms.get("coding") else {}
            parsed["marital_status"] = coding.get("display") or ms.get("text")

        # Phone
        telecoms = resource.get("telecom", [])
        for t in telecoms:
            if t.get("system") == "phone":
                parsed["phone"] = t.get("value")
                break

        # Address
        addresses = resource.get("address", [])
        if addresses:
            addr = addresses[0]
            lines = addr.get("line", [])
            city = addr.get("city", "")
            state = addr.get("state", "")
            postal = addr.get("postalCode", "")
            full = ", ".join([*lines, city, state, postal] if city or state else lines)
            parsed["address"] = full if full else addr.get("text")

        return parsed

    @staticmethod
    def _parse_condition(resource: dict[str, Any], data: dict[str, Any]) -> None:
        code = resource.get("code", {})
        coding_list = code.get("coding", [])
        display = coding_list[0].get("display") if coding_list else code.get("text")
        if display:
            conditions = data.setdefault("condition_list", [])
            conditions.append(display)
            # First active problem is the primary condition
            clinical_status = resource.get("clinicalStatus", {}).get("coding", [{}])
            is_active = any(c.get("code") == "active" for c in clinical_status)
            if is_active and "primary_condition" not in data:
                data["primary_condition"] = display

    @staticmethod
    def _parse_allergy(resource: dict[str, Any], data: dict[str, Any]) -> None:
        code = resource.get("code", {})
        coding_list = code.get("coding", [])
        display = coding_list[0].get("display") if coding_list else code.get("text")
        if display:
            allergies = data.setdefault("allergy_list", [])
            allergies.append(display)

    @staticmethod
    def _parse_observation(resource: dict[str, Any], data: dict[str, Any]) -> None:
        code = resource.get("code", {})
        coding_list = code.get("coding", [])
        obs_name = coding_list[0].get("display") or coding_list[0].get("code") or code.get("text")
        if not obs_name:
            return

        value = None
        if "valueQuantity" in resource:
            vq = resource["valueQuantity"]
            value = {
                "value": vq.get("value"),
                "unit": vq.get("unit"),
                "system": vq.get("system"),
            }
        elif "valueCodeableConcept" in resource:
            vc = resource["valueCodeableConcept"]
            coding = vc.get("coding", [{}])[0] if vc.get("coding") else {}
            value = coding.get("display") or vc.get("text")
        elif "valueString" in resource:
            value = resource["valueString"]

        if value is not None:
            observations = data.setdefault("latest_observations", {})
            observations[obs_name] = value


class FHIRClient:
    """Async client for querying a HAPI FHIR R4 server.

    Requires FHIR_BASE_URL to be configured.  When the base URL is empty or
    None every public method returns None gracefully (no-op mode).
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self._base_url = (base_url or "").rstrip("/")
        self._auth_token = auth_token
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """True when a FHIR base URL has been set."""
        return bool(self._base_url)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers: dict[str, str] = {
                "Accept": "application/fhir+json",
            }
            if self._auth_token:
                headers["Authorization"] = f"Bearer {self._auth_token}"

            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                timeout=httpx.Timeout(self._timeout),
            )
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ── public read API ───────────────────────────────────────────────

    async def get_patient(self, mpi_id: str) -> FHIRPatientData | None:
        """Fetch patient demographics + conditions + allergies + observations.

        Returns None when FHIR is not configured or the patient is not found.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            # Use _include / _revinclude to fetch related resources in one call
            # Only the last "_revinclude" survived dict de-duplication at runtime;
            # behavior preserved as-is (single Observation revinclude).
            params: dict[str, str | int] = {
                "identifier": mpi_id,
                "_include": "Patient:organization",
                "_revinclude": "Observation:patient",
                "_count": 50,
            }
            response = await client.get("/Patient", params=params)
            response.raise_for_status()
            bundle = response.json()

            return FHIRPatientData.from_fhir_bundle(mpi_id, bundle)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == httpx.codes.NOT_FOUND:
                logger.info("FHIR patient not found: %s", mpi_id)
                return FHIRPatientData(mpi_id=mpi_id)
            logger.warning("FHIR HTTP error for patient %s: %s", mpi_id, exc)
            return None
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR request failed for patient %s: %s", mpi_id, exc)
            return None

    async def get_observation(self, mpi_id: str, loinc_code: str) -> dict[str, Any] | None:
        """Fetch the latest Observation for a patient by LOINC code.

        Returns None when FHIR is not configured or no result is found.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            params: dict[str, str | int] = {
                "patient": mpi_id,
                "code": loinc_code,
                "_sort": "-date",
                "_count": 1,
            }
            response = await client.get("/Observation", params=params)
            response.raise_for_status()
            bundle = response.json()

            entries = bundle.get("entry", [])
            if entries:
                return cast("dict[str, Any] | None", entries[0].get("resource"))
            return None
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR observation fetch failed: %s", exc)
            return None

    async def search(self, resource_type: str, **params: str | int) -> dict[str, Any] | None:
        """Generic FHIR search returning the raw bundle.

        Returns None when FHIR is not configured.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get(f"/{resource_type}", params=params)
            response.raise_for_status()
            return cast("dict[str, Any]", response.json())
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR search %s failed: %s", resource_type, exc)
            return None

    # ── Phase-2 enrichment methods ─────────────────────────────────────

    async def enrich_lab_result(self, fhir_id: str) -> FHIRLabResult | None:
        """Fetch a single lab result (Observation) by its FHIR resource ID.

        Returns None when FHIR is not configured or the resource is not found.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get(f"/Observation/{fhir_id}")
            response.raise_for_status()
            resource = response.json()

            # Extract patient reference for mpi_id
            subject = resource.get("subject", {}).get("reference", "")
            mpi_id = subject.split("/")[-1] if "/" in subject else subject

            return FHIRLabResult.from_observation(mpi_id, resource)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == httpx.codes.NOT_FOUND:
                logger.info("FHIR lab result not found: %s", fhir_id)
            else:
                logger.warning("FHIR HTTP error for lab result %s: %s", fhir_id, exc)
            return None
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR request failed for lab result %s: %s", fhir_id, exc)
            return None

    async def enrich_medication(self, fhir_id: str) -> FHIRMedicationOrder | None:
        """Fetch a medication order (MedicationRequest) by its FHIR resource ID.

        Returns None when FHIR is not configured or the resource is not found.
        """
        if not self.is_configured:
            return None

        try:
            client = await self._get_client()
            response = await client.get(f"/MedicationRequest/{fhir_id}")
            response.raise_for_status()
            resource = response.json()

            # Extract patient reference for mpi_id
            subject = resource.get("subject", {}).get("reference", "")
            mpi_id = subject.split("/")[-1] if "/" in subject else subject

            return FHIRMedicationOrder.from_medication_request(mpi_id, resource)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == httpx.codes.NOT_FOUND:
                logger.info("FHIR medication order not found: %s", fhir_id)
            else:
                logger.warning("FHIR HTTP error for medication %s: %s", fhir_id, exc)
            return None
        except (httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR request failed for medication %s: %s", fhir_id, exc)
            return None

    async def enrich_patient_context(self, mpi_id: str) -> FHIRPatientContext | None:
        """Aggregate enrichment for a patient: labs + medication orders + administrations.

        Returns None when FHIR is not configured.
        """
        if not self.is_configured:
            return None

        context = FHIRPatientContext(mpi_id=mpi_id)

        try:
            client = await self._get_client()

            # Fetch lab results (Observations with category 'laboratory')
            obs_params: dict[str, str | int] = {
                "patient": mpi_id,
                "category": "laboratory",
                "_sort": "-date",
                "_count": 50,
            }
            obs_response = await client.get("/Observation", params=obs_params)
            obs_response.raise_for_status()
            obs_bundle = obs_response.json()
            for entry in obs_bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "Observation":
                    lab = FHIRLabResult.from_observation(mpi_id, resource)
                    context.lab_results.append(lab)

            # Fetch medication orders (MedicationRequest)
            med_params: dict[str, str | int] = {
                "patient": mpi_id,
                "_sort": "-authoredon",
                "_count": 50,
            }
            med_response = await client.get("/MedicationRequest", params=med_params)
            med_response.raise_for_status()
            med_bundle = med_response.json()
            for entry in med_bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "MedicationRequest":
                    order = FHIRMedicationOrder.from_medication_request(mpi_id, resource)
                    context.medication_orders.append(order)

            # Fetch medication administrations
            admin_params: dict[str, str | int] = {
                "patient": mpi_id,
                "_sort": "-date",
                "_count": 50,
            }
            admin_response = await client.get("/MedicationAdministration", params=admin_params)
            admin_response.raise_for_status()
            admin_bundle = admin_response.json()
            for entry in admin_bundle.get("entry", []):
                resource = entry.get("resource", {})
                if resource.get("resourceType") == "MedicationAdministration":
                    admin = FHIRMedicationAdministration.from_administration(mpi_id, resource)
                    context.medication_administrations.append(admin)

            return context
        except (httpx.HTTPStatusError, httpx.RequestError, httpx.TimeoutException) as exc:
            logger.warning("FHIR patient context enrichment failed for %s: %s", mpi_id, exc)
            return None


@lru_cache
def get_fhir_client() -> FHIRClient:
    """Return a cached, lazily-initialized FHIR client from app settings."""
    base = settings.fhir_base_url or None
    token = settings.fhir_auth_token.get_secret_value() if settings.fhir_auth_token else None
    return FHIRClient(base_url=base, auth_token=token)
