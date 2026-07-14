"""Tests for alert_copy.build_alert_copy — ADR-0039 §6 humanization.

Covers: 1 test per real combination (NEWS2/MEWS × watch/urgent/critical =
6), the unknown-score_type fallback (SOFA/qSOFA not yet on the live alert
path), the "3 parts present" property across all combinations, and the
title length budget (≤60 chars, dense-list scannability).
"""

import pytest

from intensicare.services.alert_copy import build_alert_copy

# Real (score_type, severity, score_value, threshold) combinations observed
# on the live alert path (ALERT_CONSOLIDATION_ANALYSIS.md §1/§5) — matches
# the tenant-global seed thresholds (alembic 0038): MEWS watch=3/urgent=4/
# critical=5; NEWS2 watch=3/urgent=5/critical=7.
NEWS2_CASES = [
    ("NEWS2", "watch", 4, 3),
    ("NEWS2", "urgent", 6, 5),
    ("NEWS2", "critical", 17, 7),
]
MEWS_CASES = [
    ("MEWS", "watch", 3, 3),
    ("MEWS", "urgent", 4, 4),
    ("MEWS", "critical", 9, 5),
]
ALL_REAL_CASES = NEWS2_CASES + MEWS_CASES

_BODY_LABELS = ("O que aconteceu:", "Por que importa:", "O que verificar:")


class TestNEWS2Copy:
    """NEWS2 × watch/urgent/critical — 3 combinations."""

    @pytest.mark.parametrize("score_type,severity,score_value,threshold", NEWS2_CASES)
    def test_news2_copy(self, score_type, severity, score_value, threshold):
        title, body = build_alert_copy(score_type, severity, score_value, threshold)

        # Title: short, scannable, carries score type + PT-BR severity + value.
        assert title == f"NEWS2 {_severity_pt(severity)} — {score_value}"
        assert str(score_value) in title

        # Body: 3 labeled parts present.
        for label in _BODY_LABELS:
            assert label in body

        # "O que aconteceu" carries the raw facts (score, threshold).
        assert str(score_value) in body
        assert str(threshold) in body

        # "Por que importa" is grounded in the same citation the codebase
        # already uses for NEWS2 (services/news2.py, threshold_resolver.py),
        # never a MEWS claim.
        assert "NEWS2" in body
        assert "Subbe" not in body

    def test_news2_critical_cites_rcp_2017_high_risk(self):
        """NEWS2 >= 7 = high risk of deterioration (RCP 2017) — must be the
        exact clinical claim already encoded in services/news2.py
        (NEWS2_HIGH_RISK_MIN=7) and threshold_resolver.GUIDELINE_SOURCES,
        not an invented one."""
        _, body = build_alert_copy("NEWS2", "critical", 17, 7)
        assert "risco alto de deterioração" in body
        assert "Royal College of Physicians" in body
        assert "2017" in body

    def test_news2_urgent_cites_rcp_2017_medium_risk(self):
        """NEWS2 5-6 = medium/moderate risk, urgent response (RCP 2017) —
        matches NEWS2_MEDIUM_RISK_MIN=5 in services/news2.py."""
        _, body = build_alert_copy("NEWS2", "urgent", 6, 5)
        assert "risco clínico moderado" in body
        assert "Royal College of Physicians" in body


class TestMEWSCopy:
    """MEWS × watch/urgent/critical — 3 combinations."""

    @pytest.mark.parametrize("score_type,severity,score_value,threshold", MEWS_CASES)
    def test_mews_copy(self, score_type, severity, score_value, threshold):
        title, body = build_alert_copy(score_type, severity, score_value, threshold)

        assert title == f"MEWS {_severity_pt(severity)} — {score_value}"
        assert str(score_value) in title

        for label in _BODY_LABELS:
            assert label in body

        assert str(score_value) in body
        assert str(threshold) in body

        assert "MEWS" in body
        assert "Royal College" not in body

    def test_mews_critical_cites_subbe_2001_mortality_risk(self):
        """MEWS >= 5 associated with increased mortality/ICU admission
        (Subbe 2001) — matches the seed rationale in alembic migration 0038
        and threshold_resolver.GUIDELINE_SOURCES, not an invented claim."""
        _, body = build_alert_copy("MEWS", "critical", 9, 5)
        assert "mortalidade" in body
        assert "Subbe" in body
        assert "2001" in body

    def test_mews_urgent_cites_subbe_response_trigger(self):
        """MEWS >= 4 = response-trigger threshold (Subbe 2001)."""
        _, body = build_alert_copy("MEWS", "urgent", 4, 4)
        assert "gatilho de resposta" in body
        assert "Subbe" in body


class TestUnknownScoreTypeFallback:
    """SOFA/qSOFA (or any other future score_type) — safe generic fallback,
    no invented clinical claim, per ALERT_CONSOLIDATION_ANALYSIS.md §5.2."""

    @pytest.mark.parametrize("severity", ["watch", "urgent", "critical"])
    @pytest.mark.parametrize("score_type", ["SOFA", "qSOFA", "SOME-FUTURE-SCORE"])
    def test_unknown_score_type_uses_generic_safe_copy(self, score_type, severity):
        title, body = build_alert_copy(score_type, severity, 10, 8)

        assert title == f"{score_type} {_severity_pt(severity)} — 10"
        for label in _BODY_LABELS:
            assert label in body

        # Must not borrow a NEWS2/MEWS-specific clinical claim for a score
        # type it has no evidence mapping for.
        assert "Royal College of Physicians" not in body
        assert "Subbe" not in body
        assert "deterioração" not in body
        assert "mortalidade" not in body

        # Still says something neutral and non-empty for "por que importa".
        assert "Por que importa: O valor" in body


class TestThreePartsProperty:
    """Property: every combination produces a body with all 3 labeled
    parts, in order, each non-empty — real combinations + fallback."""

    @pytest.mark.parametrize(
        "score_type,severity,score_value,threshold",
        [
            *ALL_REAL_CASES,
            ("SOFA", "watch", 5, 4),
            ("SOFA", "urgent", 8, 6),
            ("SOFA", "critical", 12, 10),
            ("qSOFA", "critical", 3, 2),
        ],
    )
    def test_three_parts_present_and_ordered(self, score_type, severity, score_value, threshold):
        _, body = build_alert_copy(score_type, severity, score_value, threshold)

        positions = [body.index(label) for label in _BODY_LABELS]
        assert positions == sorted(positions), "3 parts must appear in order"

        parts = body.split("\n")
        assert len(parts) == 3
        for part, label in zip(parts, _BODY_LABELS, strict=True):
            assert part.startswith(label)
            # Each part has actual content after the label, not just the label.
            assert len(part) > len(label) + 1


class TestTitleLengthBudget:
    """Title must stay short enough for dense list rows (≤60 chars) across
    every real combination — the whole point of keeping title/body
    separate (ADR-0039 §6)."""

    @pytest.mark.parametrize("score_type,severity,score_value,threshold", ALL_REAL_CASES)
    def test_title_is_at_most_60_chars(self, score_type, severity, score_value, threshold):
        title, _ = build_alert_copy(score_type, severity, score_value, threshold)
        assert len(title) <= 60, f"title too long for a dense list row: {title!r}"

    def test_title_stays_short_even_with_large_score_values(self):
        """Guard against a large/unexpected score_value blowing the budget."""
        title, _ = build_alert_copy("NEWS2", "critical", 999, 7)
        assert len(title) <= 60


def _severity_pt(severity: str) -> str:
    """Local mirror of alert_copy._SEVERITY_LABEL, kept intentionally
    independent (not imported) so a regression in that private mapping
    changes visible test output rather than silently passing."""
    return {"watch": "observação", "urgent": "urgente", "critical": "crítico"}[severity]
