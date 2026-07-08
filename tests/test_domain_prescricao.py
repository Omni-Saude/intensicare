"""
Tests for Prescription domain service.

Covers:
- create_prescription: successful creation flow
- _validate_dose: dose safety range checks
- _transition_state: state machine transitions
- _check_interactions: drug interaction detection
- list_prescriptions: filtering by status
- get_prescription: 404 for non-existent
- update_prescription: partial updates and state changes
- Terminal state immutability
"""

from __future__ import annotations

import pytest

from intensicare.services.domain_prescricao import (
    PrescriptionRecord,
    PrescriptionResult,
    PrescriptionListResult,
    InteractionAlert,
    create_prescription,
    get_prescription,
    list_prescriptions,
    update_prescription,
    count_active_prescriptions,
    get_alerts_for_prescription,
    _validate_dose,
    _check_interactions,
    _transition_state,
    DRUG_SAFETY,
    STATE_TRANSITIONS,
    VALID_STATUSES,
    TERMINAL_STATES,
)

# Access in-memory stores for cleanup between tests
import intensicare.services.domain_prescricao as dp


@pytest.fixture(autouse=True)
def _clear_store():
    """Reset in-memory state before each test."""
    dp._prescriptions.clear()
    dp._alerts.clear()
    dp._next_id = 1


# ===========================================================================
# create_prescription — successful creation
# ===========================================================================


class TestCreatePrescription:
    """Successful prescription creation and validation."""

    def test_create_simple_prescription_success(self):
        """Create a basic IV meropenem prescription."""
        result = create_prescription(
            mpi_id="MPI-001",
            drug="meropenem",
            dose=1000,
            unit="mg",
            route="IV",
            frequency="8/8h",
            prescribed_by="dr-test",
        )
        assert isinstance(result, PrescriptionResult)
        assert result.prescription.id == 1
        assert result.prescription.mpi_id == "MPI-001"
        assert result.prescription.drug == "meropenem"
        assert result.prescription.dose == 1000
        assert result.prescription.unit == "mg"
        assert result.prescription.route == "IV"
        assert result.prescription.frequency == "8/8h"
        assert result.prescription.status == "active"
        assert result.prescription.version == 1
        assert result.prescription.prescribed_by == "dr-test"
        assert result.dose_valid is True

    def test_create_prescription_defaults(self):
        """Defaults: prescribed_by='system', start_time auto-populated."""
        result = create_prescription(
            mpi_id="MPI-002",
            drug="omeprazol",
            dose=40,
            unit="mg",
            route="IV",
            frequency="QD",
        )
        assert result.prescription.prescribed_by == "system"
        assert result.prescription.start_time != ""
        assert result.prescription.created_at != ""
        assert result.prescription.updated_at != ""

    def test_create_prescription_generates_unique_ids(self):
        """Each prescription gets a sequentially increasing ID."""
        r1 = create_prescription("MPI-003", "dipirona", 1000, "mg", "IV", "6/6h")
        r2 = create_prescription("MPI-003", "metoclopramida", 10, "mg", "IV", "8/8h")
        assert r1.prescription.id == 1
        assert r2.prescription.id == 2

    def test_create_prescription_rejects_invalid_drug_route(self):
        """R07: route must be compatible with drug's typical routes."""
        with pytest.raises(ValueError, match="R07"):
            create_prescription(
                mpi_id="MPI-004",
                drug="vancomicina",
                dose=1000,
                unit="mg",
                route="PO",  # vancomycin is IV only
                frequency="12/12h",
            )

    def test_create_prescription_rejects_negative_dose(self):
        """R03: dose must be positive."""
        with pytest.raises(ValueError, match="R03"):
            create_prescription(
                mpi_id="MPI-005",
                drug="meropenem",
                dose=0,
                unit="mg",
                route="IV",
                frequency="8/8h",
            )

    def test_create_prescription_rejects_empty_mpi_id(self):
        """R01: mpi_id required."""
        with pytest.raises(ValueError, match="R01"):
            create_prescription(
                mpi_id="",
                drug="meropenem",
                dose=1000,
                unit="mg",
                route="IV",
                frequency="8/8h",
            )

    def test_create_prescription_contraindicated_interaction_rejected(self):
        """Contraindicated interaction raises ValueError before creation."""
        # First create an active enoxaparin prescription
        create_prescription("MPI-006", "enoxaparina", 40, "mg", "SC", "QD")
        # Trying to add heparin should fail (contraindicated)
        with pytest.raises(ValueError, match="CONTRAINDICADA"):
            create_prescription(
                "MPI-006", "heparina_nao_fracionada", 5000, "UI", "SC", "8/8h"
            )


# ===========================================================================
# _validate_dose — dose safety range checks
# ===========================================================================


class TestValidateDose:
    """Dose validation: within range, above max, below min, renal, weight."""

    def test_dose_within_safe_range(self):
        """1000mg meropenem is within 500-2000mg safe range."""
        valid, warnings = _validate_dose(
            drug="meropenem", dose=1000, unit="mg", route="IV", frequency="8/8h"
        )
        assert valid is True
        assert len(warnings) == 0

    def test_dose_exceeds_max_single_dose(self):
        """3000mg meropenem exceeds 2000mg max → R28 warning."""
        valid, warnings = _validate_dose(
            drug="meropenem", dose=3000, unit="mg", route="IV", frequency="8/8h"
        )
        assert valid is True  # still valid, just warned
        assert any("R28" in w for w in warnings)

    def test_dose_below_min_single_dose(self):
        """100mg meropenem below 500mg min → R28 warning."""
        valid, warnings = _validate_dose(
            drug="meropenem", dose=100, unit="mg", route="IV", frequency="8/8h"
        )
        assert any("R28" in w and "abaixo" in w for w in warnings)

    def test_daily_dose_exceeds_max(self):
        """1000mg QID = 4000mg/day > 240mg max daily midazolam → R29."""
        valid, warnings = _validate_dose(
            drug="midazolam", dose=1000, unit="mg", route="IV", frequency="QID"
        )
        assert any("R29" in w for w in warnings)

    def test_renal_adjustment_warning(self):
        """Low GFR triggers R31 renal adjustment warning for meropenem."""
        valid, warnings = _validate_dose(
            drug="meropenem",
            dose=1000,
            unit="mg",
            route="IV",
            frequency="8/8h",
            gfr=15,
        )
        assert any("R31" in w for w in warnings)

    def test_elderly_dose_reduction_warning(self):
        """Age >= 65 with elderly_reduce_pct triggers R32."""
        valid, warnings = _validate_dose(
            drug="midazolam",
            dose=10,
            unit="mg",
            route="IV",
            frequency="QD",
            age_years=70,
        )
        assert any("R32" in w for w in warnings)

    def test_unknown_drug_always_valid(self):
        """Drug not in DRUG_SAFETY returns valid=True, no warnings."""
        valid, warnings = _validate_dose(
            drug="unknown_drug", dose=999, unit="mg", route="IV", frequency="QD"
        )
        assert valid is True
        assert len(warnings) == 0


# ===========================================================================
# _check_interactions — drug interaction detection
# ===========================================================================


class TestCheckInteractions:
    """Drug-drug interaction detection against active prescriptions."""

    def test_no_interactions_when_single_drug(self):
        """Single drug with no other active prescriptions → no alerts."""
        create_prescription("MPI-I01", "meropenem", 1000, "mg", "IV", "8/8h")
        alerts = _check_interactions("omeprazol", "MPI-I01")
        assert len(alerts) == 0

    def test_detects_severe_interaction(self):
        """Midazolam + fentanyl → severe interaction."""
        create_prescription("MPI-I02", "midazolam", 5, "mg", "IV", "8/8h")
        alerts = _check_interactions("fentanil", "MPI-I02")
        assert len(alerts) >= 1
        severities = [a.severity for a in alerts]
        assert "severe" in severities

    def test_detects_contraindicated_pair(self):
        """Heparin + enoxaparin → contraindicated."""
        create_prescription("MPI-I03", "enoxaparina", 40, "mg", "SC", "QD")
        alerts = _check_interactions("heparina_nao_fracionada", "MPI-I03")
        assert any(a.severity == "contraindicated" for a in alerts)

    def test_class_duplication_detected(self):
        """Two beta-lactams → duplicate class alert."""
        create_prescription("MPI-I04", "meropenem", 1000, "mg", "IV", "8/8h")
        alerts = _check_interactions("piperacilina_tazobactam", "MPI-I04")
        assert any(a.interaction_type == "duplicate" for a in alerts)

    def test_opioid_stacking_alert(self):
        """Morphine + fentanyl → R21 opioid stacking."""
        create_prescription("MPI-I05", "morfina", 5, "mg", "IV", "6/6h")
        # Put fentanyl into store so check_interactions picks it up
        create_prescription("MPI-I05", "fentanil", 100, "mcg", "IV", "8/8h")
        # Now check with a third drug to trigger the stacking count
        alerts = _check_interactions("midazolam", "MPI-I05")
        assert any("R21" in a.description for a in alerts)


# ===========================================================================
# _transition_state — state machine
# ===========================================================================


class TestTransitionState:
    """State machine: draft→active→completed/discontinued, terminal immutability."""

    def test_draft_to_active(self):
        """draft → active is valid."""
        rx = PrescriptionRecord(id=1, mpi_id="MPI-T01", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="draft")
        result = _transition_state(rx, "active")
        assert result.status == "active"
        assert result.version == 2

    def test_active_to_completed_sets_end_time(self):
        """active → completed sets end_time automatically."""
        rx = PrescriptionRecord(id=2, mpi_id="MPI-T02", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        result = _transition_state(rx, "completed")
        assert result.status == "completed"
        assert result.end_time is not None
        assert result.end_time != ""

    def test_active_to_discontinued_requires_reason(self):
        """active → discontinued without reason → ValueError."""
        rx = PrescriptionRecord(id=3, mpi_id="MPI-T03", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        with pytest.raises(ValueError, match="R39"):
            _transition_state(rx, "discontinued")

    def test_active_to_discontinued_with_reason_succeeds(self):
        """active → discontinued with reason works."""
        rx = PrescriptionRecord(id=4, mpi_id="MPI-T04", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        result = _transition_state(rx, "discontinued", reason="Reação adversa")
        assert result.status == "discontinued"
        assert result.end_time is not None

    def test_active_to_suspended_requires_reason(self):
        """active → suspended without reason → ValueError."""
        rx = PrescriptionRecord(id=5, mpi_id="MPI-T05", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        with pytest.raises(ValueError, match="R39"):
            _transition_state(rx, "suspended")

    def test_active_to_suspended_with_reason_succeeds(self):
        """active → suspended with reason works."""
        rx = PrescriptionRecord(id=6, mpi_id="MPI-T06", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        result = _transition_state(rx, "suspended", reason="Pausa cirúrgica")
        assert result.status == "suspended"

    def test_suspended_to_active_resume(self):
        """suspended → active (resume) is valid."""
        rx = PrescriptionRecord(id=7, mpi_id="MPI-T07", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="suspended")
        result = _transition_state(rx, "active")
        assert result.status == "active"

    def test_suspended_to_discontinued_requires_reason(self):
        """suspended → discontinued without reason → ValueError."""
        rx = PrescriptionRecord(id=8, mpi_id="MPI-T08", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="suspended")
        with pytest.raises(ValueError, match="R39"):
            _transition_state(rx, "discontinued")

    def test_cannot_modify_completed(self):
        """Completed state is terminal → no transitions allowed."""
        rx = PrescriptionRecord(id=9, mpi_id="MPI-T09", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="completed")
        with pytest.raises(ValueError, match="R37"):
            _transition_state(rx, "active")

    def test_cannot_modify_discontinued(self):
        """Discontinued state is terminal → no transitions allowed."""
        rx = PrescriptionRecord(id=10, mpi_id="MPI-T10", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="discontinued")
        with pytest.raises(ValueError, match="R37"):
            _transition_state(rx, "active")

    def test_invalid_status_rejected(self):
        """Unknown status raises R36."""
        rx = PrescriptionRecord(id=11, mpi_id="MPI-T11", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="draft")
        with pytest.raises(ValueError, match="R36"):
            _transition_state(rx, "nonexistent")

    def test_invalid_transition_rejected(self):
        """active → draft is not allowed."""
        rx = PrescriptionRecord(id=12, mpi_id="MPI-T12", drug="meropenem",
                                dose=1000, unit="mg", route="IV",
                                frequency="8/8h", status="active")
        with pytest.raises(ValueError, match="R38"):
            _transition_state(rx, "draft")


# ===========================================================================
# list_prescriptions — filtering
# ===========================================================================


class TestListPrescriptions:
    """List prescriptions with status filtering and pagination."""

    def test_list_active_by_default(self):
        """Default status filter is 'active'."""
        create_prescription("MPI-L01", "meropenem", 1000, "mg", "IV", "8/8h")
        create_prescription("MPI-L01", "vancomicina", 1000, "mg", "IV", "12/12h")
        result = list_prescriptions("MPI-L01")
        assert result.total == 2
        assert all(rx.status == "active" for rx in result.prescriptions)

    def test_list_with_status_filter_all(self):
        """status='all' returns prescriptions regardless of status."""
        r = create_prescription("MPI-L02", "meropenem", 1000, "mg", "IV", "8/8h")
        # Transition to completed
        assert r.prescription.id is not None
        dp._prescriptions[r.prescription.id].status = "completed"
        result = list_prescriptions("MPI-L02", status="all")
        assert result.total == 1

    def test_list_completed_only(self):
        """Filter by 'completed' returns only completed."""
        r = create_prescription("MPI-L03", "meropenem", 1000, "mg", "IV", "8/8h")
        assert r.prescription.id is not None
        dp._prescriptions[r.prescription.id].status = "completed"
        create_prescription("MPI-L03", "vancomicina", 1000, "mg", "IV", "12/12h")
        result = list_prescriptions("MPI-L03", status="completed")
        assert result.total == 1
        assert result.prescriptions[0].drug == "meropenem"

    def test_list_empty_when_no_match(self):
        """No prescriptions for unknown patient returns empty."""
        result = list_prescriptions("MPI-NONEXISTENT")
        assert result.total == 0
        assert result.prescriptions == []

    def test_list_pagination(self):
        """Offset and limit pagination works."""
        for i in range(5):
            create_prescription(f"MPI-L04", f"drug_{i}" if i > 0 else "meropenem",
                               float(100 + i * 10), "mg", "IV", "8/8h")
        result = list_prescriptions("MPI-L04", limit=2, offset=1)
        assert len(result.prescriptions) <= 2
        assert result.total == 5


# ===========================================================================
# get_prescription — 404 for non-existent
# ===========================================================================


class TestGetPrescription:
    """Single prescription retrieval."""

    def test_get_existing_prescription(self):
        """Retrieve a prescription that exists."""
        create_prescription("MPI-G01", "meropenem", 1000, "mg", "IV", "8/8h")
        rx = get_prescription(1)
        assert rx is not None
        assert rx.id == 1
        assert rx.drug == "meropenem"

    def test_get_nonexistent_returns_none(self):
        """Nonexistent prescription returns None (404 semantic)."""
        rx = get_prescription(9999)
        assert rx is None


# ===========================================================================
# update_prescription — state changes via update
# ===========================================================================


class TestUpdatePrescription:
    """Update prescription fields and state via update_prescription."""

    def test_update_notes_field(self):
        """Update non-critical field like notes."""
        create_prescription("MPI-U01", "meropenem", 1000, "mg", "IV", "8/8h")
        updated = update_prescription(1, {"notes": "Ajustar conforme cultura"})
        assert updated.notes == "Ajustar conforme cultura"
        assert updated.version == 2

    def test_update_status_via_transition(self):
        """Update status field triggers state transition."""
        create_prescription("MPI-U02", "meropenem", 1000, "mg", "IV", "8/8h")
        # First set to draft, then transition
        dp._prescriptions[1].status = "draft"
        updated = update_prescription(1, {"status": "active"})
        assert updated.status == "active"

    def test_update_nonexistent_raises_keyerror(self):
        """Updating non-existent prescription raises KeyError."""
        with pytest.raises(KeyError, match="não encontrada"):
            update_prescription(9999, {"notes": "test"})

    def test_cannot_update_completed_prescription(self):
        """Terminal state blocks update."""
        create_prescription("MPI-U03", "meropenem", 1000, "mg", "IV", "8/8h")
        dp._prescriptions[1].status = "completed"
        with pytest.raises(ValueError, match="R37"):
            update_prescription(1, {"status": "active"})


# ===========================================================================
# Constants
# ===========================================================================


class TestConstants:
    """Verify module-level constants."""

    def test_drug_safety_has_known_drugs(self):
        """DRUG_SAFETY contains expected ICU drugs."""
        expected = {"meropenem", "vancomicina", "noradrenalina", "midazolam",
                    "fentanil", "propofol", "morfina", "enoxaparina"}
        assert expected.issubset(set(DRUG_SAFETY.keys()))

    def test_terminal_states_correct(self):
        """TERMINAL_STATES are completed and discontinued."""
        assert TERMINAL_STATES == {"completed", "discontinued"}

    def test_state_transitions_map_known_states(self):
        """STATE_TRANSITIONS covers all valid statuses."""
        for status in VALID_STATUSES:
            assert status in STATE_TRANSITIONS
