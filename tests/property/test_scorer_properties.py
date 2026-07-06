"""L2 Property-Based Scorer Tests (Hypothesis).

Property-based tests for MEWS, NEWS2, SOFA, qSOFA clinical scorers.

Properties tested:
1. Monotonicity — worse vitals → same-or-higher score
2. Bounded range — score stays within [0, max]
3. Missing→0 — None components contribute 0
4. Extreme values don't crash
5. None components handled gracefully
"""

from __future__ import annotations

import sys
import pathlib

import pytest
from hypothesis import given, settings, strategies as st

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from intensicare.services.mews import calculate_mews  # noqa: E402
from intensicare.services.news2 import calculate_news2  # noqa: E402
from intensicare.services.qsofa import calculate_qsofa  # noqa: E402
from intensicare.services.sofa import calculate_sofa  # noqa: E402

# Max score constants (from clinical definitions)
MEWS_MAX = 15       # 5 components × max 3 = 15
NEWS2_MAX = 20      # 7 components: RR(3)+SpO2(3)+O2(2)+SBP(3)+HR(3)+CONS(3)+Temp(2)=19, rounded up
QSOFA_MAX = 3       # 3 binary criteria
SOFA_MAX = 24       # 6 organ systems × max 4 = 24


# ──────────────────────────────────────────────────────────────
# Generators
# ──────────────────────────────────────────────────────────────

# Vital sign ranges for property testing
sbp_range = st.integers(min_value=30, max_value=260)
hr_range = st.integers(min_value=20, max_value=220)
rr_range = st.integers(min_value=2, max_value=60)
temp_range = st.floats(min_value=28.0, max_value=43.0, allow_nan=False, allow_infinity=False)
spo2_range = st.integers(min_value=40, max_value=100)
gcs_range = st.integers(min_value=3, max_value=15)
avpu_values = st.sampled_from(["A", "V", "P", "U", None])
consciousness_values = st.sampled_from(["A", "C", "V", "P", "U", None])
platelets_range = st.integers(min_value=1, max_value=600)
bilirubin_range = st.floats(min_value=0.1, max_value=30.0, allow_nan=False, allow_infinity=False)
creatinine_range = st.floats(min_value=0.1, max_value=15.0, allow_nan=False, allow_infinity=False)
pao2_fio2_range = st.floats(min_value=20.0, max_value=600.0, allow_nan=False, allow_infinity=False)
map_range = st.floats(min_value=20.0, max_value=150.0, allow_nan=False, allow_infinity=False)
urine_range = st.integers(min_value=0, max_value=5000)


# ──────────────────────────────────────────────────────────────
# MEWS Property Tests
# ──────────────────────────────────────────────────────────────


class TestMEWSProperties:
    """Property-based tests for MEWS scorer."""

    @given(sbp_range, hr_range, rr_range, temp_range, avpu_values)
    @settings(max_examples=200)
    def test_mews_bounded_range(
        self,
        systolic_bp: int,
        heart_rate: int,
        respiratory_rate: int,
        temperature: float,
        avpu: str | None,
    ) -> None:
        """MEWS score must be within [0, MEWS_MAX]."""
        score, _ = calculate_mews(
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            temperature=temperature,
            avpu=avpu,
        )
        assert 0 <= score <= MEWS_MAX, f"MEWS out of bounds: {score}"

    @given(sbp_range, st.integers(min_value=51, max_value=210), rr_range, temp_range, avpu_values)
    @settings(max_examples=200)
    def test_mews_monotonic_hr(self, systolic_bp: int, hr: int, rr: int, temp: float, avpu: str | None) -> None:
        """Increasing HR from >=51 should never decrease MEWS (all else equal).

        Note: HR < 51 is excluded because bradycardia scoring is non-monotonic:
        HR≤40=2, 41-50=1 — increasing HR can decrease the score in this range.
        """
        score1, _ = calculate_mews(systolic_bp=systolic_bp, heart_rate=hr, respiratory_rate=rr, temperature=temp, avpu=avpu)
        score2, _ = calculate_mews(systolic_bp=systolic_bp, heart_rate=hr + 10, respiratory_rate=rr, temperature=temp, avpu=avpu)
        # Higher HR → same or higher score (HR sweet spot is 51-100, so
        # going from 90→100 stays 0, which is fine; going from 100→110 adds 1)
        assert score2 >= score1, f"MEWS decreased with higher HR: {score1} -> {score2} (HR {hr} -> {hr+10})"

    def test_mews_missing_components_zero(self) -> None:
        """All-None inputs should produce score 0."""
        score, _ = calculate_mews()
        assert score == 0, f"MEWS with all None should be 0, got {score}"

    @given(st.integers(min_value=0, max_value=300))
    @settings(max_examples=100)
    def test_mews_extreme_sbp_no_crash(self, sbp: int) -> None:
        """Extreme SBP values should not crash MEWS."""
        try:
            score, _ = calculate_mews(systolic_bp=sbp)
            assert 0 <= score <= MEWS_MAX
        except Exception as e:
            pytest.fail(f"MEWS crashed on SBP={sbp}: {e}")

    @given(st.integers(min_value=-100, max_value=500))
    @settings(max_examples=100)
    def test_mews_extreme_hr_no_crash(self, hr: int) -> None:
        """Extreme HR values should not crash MEWS."""
        try:
            score, _ = calculate_mews(heart_rate=hr)
            assert 0 <= score <= MEWS_MAX
        except Exception as e:
            pytest.fail(f"MEWS crashed on HR={hr}: {e}")


# ──────────────────────────────────────────────────────────────
# NEWS2 Property Tests
# ──────────────────────────────────────────────────────────────


class TestNEWS2Properties:
    """Property-based tests for NEWS2 scorer."""

    @given(rr_range, spo2_range, st.booleans(), sbp_range, hr_range, temp_range, consciousness_values)
    @settings(max_examples=200)
    def test_news2_bounded_range(
        self,
        respiratory_rate: int,
        spo2: int,
        supplemental_o2: bool,
        systolic_bp: int,
        heart_rate: int,
        temperature: float,
        consciousness: str | None,
    ) -> None:
        """NEWS2 score must be within [0, NEWS2_MAX]."""
        result = calculate_news2(
            respiratory_rate=respiratory_rate,
            spo2=spo2,
            supplemental_o2=supplemental_o2,
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            temperature=temperature,
            avpu=consciousness,
        )
        assert 0 <= result.total_score <= NEWS2_MAX, f"NEWS2 out of bounds: {result.total_score}"

    @given(rr_range, spo2_range, st.booleans(), sbp_range, hr_range, temp_range, consciousness_values)
    @settings(max_examples=200)
    def test_news2_supplemental_o2_monotonic(
        self,
        respiratory_rate: int,
        spo2: int,
        supplemental_o2: bool,
        systolic_bp: int,
        heart_rate: int,
        temperature: float,
        consciousness: str | None,
    ) -> None:
        """Adding supplemental O2 should never decrease NEWS2."""
        score_without = calculate_news2(
            respiratory_rate=respiratory_rate,
            spo2=spo2,
            supplemental_o2=False,
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            temperature=temperature,
            avpu=consciousness,
        ).total_score
        score_with = calculate_news2(
            respiratory_rate=respiratory_rate,
            spo2=spo2,
            supplemental_o2=True,
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            temperature=temperature,
            avpu=consciousness,
        ).total_score
        assert score_with >= score_without, (
            f"NEWS2 decreased with O2: {score_without} -> {score_with}"
        )

    @given(rr_range, spo2_range, st.booleans(), sbp_range, hr_range, temp_range, consciousness_values)
    @settings(max_examples=200)
    def test_news2_consciousness_monotonic(
        self,
        respiratory_rate: int,
        spo2: int,
        supplemental_o2: bool,
        systolic_bp: int,
        heart_rate: int,
        temperature: float,
        consciousness: str | None,
    ) -> None:
        """Consciousness = 'A' should give lower/equal score vs any non-A."""
        score_alert = calculate_news2(
            respiratory_rate=respiratory_rate,
            spo2=spo2,
            supplemental_o2=supplemental_o2,
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            temperature=temperature,
            avpu="A",
        ).total_score
        score_other = calculate_news2(
            respiratory_rate=respiratory_rate,
            spo2=spo2,
            supplemental_o2=supplemental_o2,
            systolic_bp=systolic_bp,
            heart_rate=heart_rate,
            temperature=temperature,
            avpu=consciousness,
        ).total_score
        assert score_other >= score_alert, (
            f"NEWS2 with avpu='A' ({score_alert}) > avpu='{consciousness}' ({score_other})"
        )

    def test_news2_missing_components_zero(self) -> None:
        """All-None inputs should produce score 0."""
        result = calculate_news2()
        assert result.total_score == 0, f"NEWS2 with all None should be 0, got {result.total_score}"

    @given(st.integers(min_value=-50, max_value=200))
    @settings(max_examples=100)
    def test_news2_extreme_rr_no_crash(self, rr: int) -> None:
        """Extreme RR values should not crash NEWS2."""
        try:
            result = calculate_news2(respiratory_rate=rr)
            assert 0 <= result.total_score <= NEWS2_MAX
        except Exception as e:
            pytest.fail(f"NEWS2 crashed on RR={rr}: {e}")


# ──────────────────────────────────────────────────────────────
# qSOFA Property Tests
# ──────────────────────────────────────────────────────────────


class TestQSOFAProperties:
    """Property-based tests for qSOFA scorer."""

    @given(rr_range, sbp_range, gcs_range)
    @settings(max_examples=200)
    def test_qsofa_bounded_range(
        self,
        respiratory_rate: int,
        systolic_bp: int,
        gcs: int,
    ) -> None:
        """qSOFA score must be within [0, QSOFA_MAX]."""
        result = calculate_qsofa(
            respiratory_rate=respiratory_rate,
            systolic_bp=systolic_bp,
            gcs=gcs,
        )
        assert 0 <= result.total_score <= QSOFA_MAX, f"qSOFA out of bounds: {result.total_score}"

    @given(rr_range, sbp_range, gcs_range)
    @settings(max_examples=200)
    def test_qsofa_monotonic_rr(
        self,
        respiratory_rate: int,
        systolic_bp: int,
        gcs: int,
    ) -> None:
        """Increasing RR from below 22 to above 22 should not decrease qSOFA."""
        score1 = calculate_qsofa(respiratory_rate=respiratory_rate, systolic_bp=systolic_bp, gcs=gcs).total_score
        score2 = calculate_qsofa(respiratory_rate=respiratory_rate + 5, systolic_bp=systolic_bp, gcs=gcs).total_score
        assert score2 >= score1, f"qSOFA decreased with higher RR: {score1} -> {score2}"

    @given(rr_range, sbp_range, gcs_range)
    @settings(max_examples=200)
    def test_qsofa_monotonic_sbp(
        self,
        respiratory_rate: int,
        systolic_bp: int,
        gcs: int,
    ) -> None:
        """Decreasing SBP should not decrease qSOFA."""
        score1 = calculate_qsofa(respiratory_rate=respiratory_rate, systolic_bp=systolic_bp, gcs=gcs).total_score
        score2 = calculate_qsofa(respiratory_rate=respiratory_rate, systolic_bp=systolic_bp - 10, gcs=gcs).total_score
        assert score2 >= score1, f"qSOFA decreased with lower SBP: {score1} -> {score2}"

    @given(rr_range, sbp_range, gcs_range)
    @settings(max_examples=200)
    def test_qsofa_monotonic_gcs(
        self,
        respiratory_rate: int,
        systolic_bp: int,
        gcs: int,
    ) -> None:
        """Decreasing GCS should not decrease qSOFA."""
        score1 = calculate_qsofa(respiratory_rate=respiratory_rate, systolic_bp=systolic_bp, gcs=gcs).total_score
        if gcs > 3:
            score2 = calculate_qsofa(respiratory_rate=respiratory_rate, systolic_bp=systolic_bp, gcs=gcs - 1).total_score
            assert score2 >= score1, f"qSOFA decreased with lower GCS: {score1} -> {score2}"

    def test_qsofa_missing_components_zero(self) -> None:
        """All-None inputs should produce score 0."""
        result = calculate_qsofa()
        assert result.total_score == 0, f"qSOFA with all None should be 0, got {result.total_score}"


# ──────────────────────────────────────────────────────────────
# SOFA Property Tests
# ──────────────────────────────────────────────────────────────


class TestSOFAProperties:
    """Property-based tests for SOFA scorer."""

    @given(
        pao2_fio2_range,
        platelets_range,
        bilirubin_range,
        map_range,
        creatinine_range,
        gcs_range,
    )
    @settings(max_examples=200)
    def test_sofa_bounded_range(
        self,
        pao2_fio2_ratio: float,
        platelets: int,
        bilirubin: float,
        map_value: float,
        creatinine: float,
        gcs: int,
    ) -> None:
        """SOFA score must be within [0, SOFA_MAX]."""
        result = calculate_sofa(
            pao2_fio2=pao2_fio2_ratio,
            platelets=platelets,
            bilirubin=bilirubin,
            map_value=map_value,
            creatinine=creatinine,
            gcs=gcs,
        )
        assert 0 <= result.total_score <= SOFA_MAX, f"SOFA out of bounds: {result.total_score}"

    @given(pao2_fio2_range, platelets_range)
    @settings(max_examples=100)
    def test_sofa_monotonic_platelets(
        self,
        pao2_fio2_ratio: float,
        platelets: int,
    ) -> None:
        """Decreasing platelets should not decrease SOFA."""
        score1 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, platelets=platelets).total_score
        score2 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, platelets=max(1, platelets - 20)).total_score
        assert score2 >= score1, f"SOFA decreased with lower platelets: {score1} -> {score2}"

    @given(pao2_fio2_range, bilirubin_range)
    @settings(max_examples=100)
    def test_sofa_monotonic_bilirubin(
        self,
        pao2_fio2_ratio: float,
        bilirubin: float,
    ) -> None:
        """Increasing bilirubin should not decrease SOFA."""
        score1 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, bilirubin=bilirubin).total_score
        score2 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, bilirubin=bilirubin + 0.5).total_score
        assert score2 >= score1, f"SOFA decreased with higher bilirubin: {score1} -> {score2}"

    @given(pao2_fio2_range, creatinine_range)
    @settings(max_examples=100)
    def test_sofa_monotonic_creatinine(
        self,
        pao2_fio2_ratio: float,
        creatinine: float,
    ) -> None:
        """Increasing creatinine should not decrease SOFA."""
        score1 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, creatinine=creatinine).total_score
        score2 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, creatinine=creatinine + 0.3).total_score
        assert score2 >= score1, f"SOFA decreased with higher creatinine: {score1} -> {score2}"

    @given(pao2_fio2_range, gcs_range)
    @settings(max_examples=100)
    def test_sofa_monotonic_gcs(
        self,
        pao2_fio2_ratio: float,
        gcs: int,
    ) -> None:
        """Decreasing GCS should not decrease SOFA."""
        score1 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, gcs=gcs).total_score
        if gcs > 3:
            score2 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, gcs=gcs - 2).total_score
            assert score2 >= score1, f"SOFA decreased with lower GCS: {score1} -> {score2}"

    @given(pao2_fio2_range, map_range)
    @settings(max_examples=100)
    def test_sofa_monotonic_map(
        self,
        pao2_fio2_ratio: float,
        map_value: float,
    ) -> None:
        """Decreasing MAP should not decrease SOFA."""
        score1 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, map_value=map_value).total_score
        score2 = calculate_sofa(pao2_fio2=pao2_fio2_ratio, map_value=map_value - 10).total_score
        assert score2 >= score1, f"SOFA decreased with lower MAP: {score1} -> {score2}"

    def test_sofa_missing_components_zero(self) -> None:
        """All-None inputs should produce score 0."""
        result = calculate_sofa()
        assert result.total_score == 0, f"SOFA with all None should be 0, got {result.total_score}"

    @given(st.floats(min_value=-100, max_value=1000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_sofa_extreme_pao2_no_crash(self, pf_ratio: float) -> None:
        """Extreme PaO2/FiO2 values should not crash SOFA."""
        try:
            result = calculate_sofa(pao2_fio2=pf_ratio)
            assert 0 <= result.total_score <= SOFA_MAX
        except Exception as e:
            pytest.fail(f"SOFA crashed on PaO2/FiO2={pf_ratio}: {e}")

    @given(st.floats(min_value=-10.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_sofa_extreme_creatinine_no_crash(self, cr: float) -> None:
        """Extreme creatinine values should not crash SOFA."""
        try:
            result = calculate_sofa(creatinine=cr)
            assert 0 <= result.total_score <= SOFA_MAX
        except Exception as e:
            pytest.fail(f"SOFA crashed on creatinine={cr}: {e}")
