"""NEWS2 (National Early Warning Score 2) scoring engine.

Implements the Royal College of Physicians NEWS2 protocol with all 7 parameters.
"""

from dataclasses import dataclass

# Canonical algorithm version identifier — single source of truth. This is the
# FK target in algorithm_registry.algorithm_version (see migration
# 0021_activate_news2_v3_0_0.py / tests/conftest.py seed) and MUST be imported
# by call sites (e.g. services/vitals.py) instead of duplicating this literal —
# a duplicated literal is how it drifted out of sync and persisted the wrong
# algorithm_version ("NEWS2-v1.0") for every NEWS2 ClinicalScore row.
NEWS2_VERSION = "NEWS2-v3.0.0"

# ─────────────────────────────────────────────────────────────────────────────
# Published NEWS2 thresholds (Royal College of Physicians, NEWS2, 2017). The
# current implementation's values are authoritative and MUST NOT change; these
# named constants only replace inline literals with no behavior change.
# ─────────────────────────────────────────────────────────────────────────────

# Aggregate-score risk thresholds
NEWS2_HIGH_RISK_MIN = 7  # aggregate >= 7 -> high risk
NEWS2_MEDIUM_RISK_MIN = 5  # aggregate >= 5 -> medium risk / urgent response

# A single parameter scoring this value ("red score") triggers urgent assessment
NEWS2_RED_SCORE = 3


@dataclass
class NEWS2Components:
    """Individual component scores for NEWS2."""

    respiratory_rate: int = 0
    spo2: int = 0
    supplemental_o2: int = 0
    systolic_bp: int = 0
    heart_rate: int = 0
    consciousness: int = 0
    temperature: int = 0


@dataclass
class NEWS2Result:
    """Result of a NEWS2 calculation."""

    total_score: int
    components: NEWS2Components
    algorithm_version: str = NEWS2_VERSION

    @property
    def risk_category(self) -> str:
        """Classify the total score into risk category."""
        if self.total_score >= NEWS2_HIGH_RISK_MIN:
            return "high"
        if self.total_score >= NEWS2_MEDIUM_RISK_MIN:
            return "medium"
        return "low"

    @property
    def requires_urgent_assessment(self) -> bool:
        """Whether an urgent clinical assessment is recommended."""
        return self.total_score >= NEWS2_MEDIUM_RISK_MIN or any(
            score == NEWS2_RED_SCORE
            for score in [
                self.components.respiratory_rate,
                self.components.spo2,
                self.components.systolic_bp,
                self.components.heart_rate,
                self.components.consciousness,
                self.components.temperature,
            ]
        )


def _score_numeric(
    value: int | float | None, thresholds: list[tuple[float | None, float | None, int]]
) -> int:
    """Score a numeric value against a list of (min, max, score) thresholds.

    Each threshold is (min_inclusive, max_inclusive, score).
    None means unbounded.
    """
    if value is None:
        return 0

    # Round floats to 1 decimal to prevent boundary edge cases
    # (e.g., 34.9999999999 < 35 causing wrong score).
    if isinstance(value, float):
        value = round(value, 1)

    for lo, hi, score in thresholds:
        lo_ok = lo is None or value >= lo
        hi_ok = hi is None or value <= hi
        if lo_ok and hi_ok:
            return score

    return 0


def score_respiratory_rate(rr: int | None) -> int:
    """Score respiratory rate per NEWS2.

    ≤8 = 3, 9-11 = 1, 12-20 = 0, 21-24 = 2, ≥25 = 3
    """
    return _score_numeric(
        rr,
        [
            (None, 8, 3),
            (9, 11, 1),
            (12, 20, 0),
            (21, 24, 2),
            (25, None, 3),
        ],
    )


# CLINICALLY RATIFIED per RAT-NEWS2-SCALE-2 (AUDIT-002) — CORRECTED per RCP 2017.
# Scale 2 is ONLY for confirmed hypercapnic patients (target SpO₂ 88–92%).
# Being on supplemental O₂ alone does NOT trigger Scale 2 — using Scale 2 on
# non-hypercapnic patients would under-score deterioration (e.g. SpO₂ 93% = score 0
# on Scale 2, but score 2 on Scale 1, masking clinical decline).
def score_spo2(spo2: int | None, hypercapnic: bool = False, on_o2: bool = False) -> int:
    """Score SpO2 per NEWS2 (RCP 2017, corrected Scale-2 bands per AUDIT-002).

    Scale 1 (non-hypercapnic): ≥96=0, 94-95=1, 92-93=2, ≤91=3

    Scale 2 (hypercapnic, ON O2 — targeting 88-92%):
        ≥97=3, 95-96=2, 93-94=1, ≤92=0

    Scale 2 (hypercapnic, OFF O2):
        ≥93=0, 88-92=1, 86-87=2, 84-85=3, ≤83=3
    """
    if spo2 is None:
        return 0

    if hypercapnic:
        if on_o2:
            # Hypercapnic ON O2: aiming for 88-92%, higher SpO2 = overshoot risk
            return _score_numeric(
                spo2,
                [
                    (97, None, 3),
                    (95, 96, 2),
                    (93, 94, 1),
                    (None, 92, 0),
                ],
            )
        # Hypercapnic OFF O2: standard Scale 2 bands
        return _score_numeric(
            spo2,
            [
                (93, None, 0),
                (88, 92, 1),
                (86, 87, 2),
                (84, 85, 3),
                (None, 83, 3),
            ],
        )

    # Scale 1 (non-hypercapnic)
    return _score_numeric(
        spo2,
        [
            (96, None, 0),
            (94, 95, 1),
            (92, 93, 2),
            (None, 91, 3),
        ],
    )


def score_supplemental_o2(on_o2: bool | None) -> int:
    """Score supplemental oxygen: +2 if on O2."""
    return 2 if on_o2 else 0


def score_systolic_bp(sbp: int | None) -> int:
    """Score systolic blood pressure per NEWS2.

    ≤90=3, 91-100=2, 101-110=1, 111-219=0, ≥220=3
    """
    return _score_numeric(
        sbp,
        [
            (None, 90, 3),
            (91, 100, 2),
            (101, 110, 1),
            (111, 219, 0),
            (220, None, 3),
        ],
    )


def score_heart_rate(hr: int | None) -> int:
    """Score heart rate per NEWS2.

    ≤40=3, 41-50=1, 51-90=0, 91-110=1, 111-130=2, ≥131=3
    """
    return _score_numeric(
        hr,
        [
            (None, 40, 3),
            (41, 50, 1),
            (51, 90, 0),
            (91, 110, 1),
            (111, 130, 2),
            (131, None, 3),
        ],
    )


def score_consciousness(avpu: str | None) -> int:
    """Score consciousness per NEWS2.

    Alert (A) = 0
    CVPU (any altered level: C/V/P/U) = 3
    """
    if avpu is None:
        return 0
    avpu_upper = avpu.strip().upper()
    if avpu_upper == "A":
        return 0
    return 3


def score_temperature(temp: float | None) -> int:
    """Score temperature per NEWS2.

    ≤35.0=3, 35.1-36.0=1, 36.1-38.0=0, 38.1-39.0=1, ≥39.1=2
    """
    return _score_numeric(
        temp,
        [
            (None, 35.0, 3),
            (35.1, 36.0, 1),
            (36.1, 38.0, 0),
            (38.1, 39.0, 1),
            (39.1, None, 2),
        ],
    )


def calculate_news2(
    respiratory_rate: int | None = None,
    spo2: int | None = None,
    hypercapnic: bool = False,
    supplemental_o2: bool | None = None,
    systolic_bp: int | None = None,
    heart_rate: int | None = None,
    avpu: str | None = None,
    temperature: float | None = None,
) -> NEWS2Result:
    """Calculate the full NEWS2 score from all 7 parameters.

    Args:
        respiratory_rate: Breaths per minute.
        spo2: Oxygen saturation (%).
        hypercapnic: Whether the patient has confirmed hypercapnic respiratory
                     failure. Scale 2 (target SpO₂ 88–92%) is used ONLY when
                     this is True. Being on supplemental O₂ alone does NOT
                     trigger Scale 2 (CORRECTED per RCP 2017, AUDIT-002).
        supplemental_o2: Whether the patient is on supplemental oxygen.
                         Adds +2 to the score. Also modifies Scale 2 SpO₂
                         bands when the patient is hypercapnic (on_o2=True
                         changes thresholds to target 88-92%).
        systolic_bp: Systolic blood pressure (mmHg).
        heart_rate: Heart rate (bpm).
        avpu: Consciousness level (A=Alert, C/V/P/U=altered).
        temperature: Body temperature (°C).

    Returns:
        NEWS2Result with total score and component breakdown.
    """
    # AUDIT-002 (CORRECTED per RCP 2017): Scale 2 is ONLY for confirmed
    # hypercapnic respiratory failure (target SpO₂ 88–92%). Being on
    # supplemental O₂ alone does NOT trigger Scale 2 — using Scale 2 on
    # non-hypercapnic patients would under-score deterioration (e.g. SpO₂ 93%
    # = score 0 on Scale 2, but score 2 on Scale 1, masking clinical decline).
    use_scale2 = hypercapnic

    components = NEWS2Components(
        respiratory_rate=score_respiratory_rate(respiratory_rate),
        spo2=score_spo2(spo2, hypercapnic=use_scale2, on_o2=bool(supplemental_o2)),
        supplemental_o2=score_supplemental_o2(supplemental_o2),
        systolic_bp=score_systolic_bp(systolic_bp),
        heart_rate=score_heart_rate(heart_rate),
        consciousness=score_consciousness(avpu),
        temperature=score_temperature(temperature),
    )

    total = sum(
        [
            components.respiratory_rate,
            components.spo2,
            components.supplemental_o2,
            components.systolic_bp,
            components.heart_rate,
            components.consciousness,
            components.temperature,
        ]
    )

    return NEWS2Result(
        total_score=total,
        components=components,
        algorithm_version=NEWS2_VERSION,
    )
