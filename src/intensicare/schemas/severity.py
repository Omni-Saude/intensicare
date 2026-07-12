"""
Canonical Severity Model — normal < watch < urgent < critical.
Triple-encoded: color + icon + shape.
P0-10: highest-severity-wins aggregation (never last-writer-wins).

Resolves AUDIT-008: Severity enum mismatch between backend and frontend.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar


class SeverityLevel(str, Enum):
    """Canonical severity levels for clinical alerts.

    Ordered: normal < watch < urgent < critical (P0-10 highest-severity-wins).
    Resolves AUDIT-008: backend watch/urgent/critical vs frontend info/warning/critical.
    """

    NORMAL = "normal"
    WATCH = "watch"
    URGENT = "urgent"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        """Numeric rank for comparison (P0-10: higher = more severe)."""
        return _SEVERITY_RANK[self]

    @property
    def p10_score(self) -> int:
        """P0-10 score mapping:
        normal → 0, watch → 3, urgent → 7, critical → 10.
        """
        return _P10_SCORE[self]

    def is_more_severe_than(self, other: SeverityLevel | str) -> bool:
        """Check if this severity is strictly higher than another."""
        other_sev = SeverityLevel(other) if isinstance(other, str) else other
        return self.rank > other_sev.rank

    def is_at_least(self, other: SeverityLevel | str) -> bool:
        """Check if this severity is >= another."""
        other_sev = SeverityLevel(other) if isinstance(other, str) else other
        return self.rank >= other_sev.rank


# Severity ranking (P0-10: highest-severity-wins)
_SEVERITY_RANK: dict[SeverityLevel, int] = {
    SeverityLevel.NORMAL: 0,
    SeverityLevel.WATCH: 1,
    SeverityLevel.URGENT: 2,
    SeverityLevel.CRITICAL: 3,
}

# P0-10 clinical severity scores
_P10_SCORE: dict[SeverityLevel, int] = {
    SeverityLevel.NORMAL: 0,
    SeverityLevel.WATCH: 3,
    SeverityLevel.URGENT: 7,
    SeverityLevel.CRITICAL: 10,
}

# Canonical severity ordering for DB CHECK and validation
CANONICAL_SEVERITIES: tuple[str, ...] = ("normal", "watch", "urgent", "critical")


class TripleEncoder:
    """Triple-encoding: color + icon + shape for each severity level.

    Designed for GUI rendering: color codes for visual urgency,
    icon names for semantic meaning, and shape modifiers for
    accessibility (WCAG 2.1 AA compliant).
    """

    _ENCODING: ClassVar[dict[SeverityLevel, dict[str, str]]] = {
        SeverityLevel.NORMAL: {
            "color": "#2DD269",  # spec green
            "icon": "check-circle",
            "shape": "circle",
            "label": "Normal",
            "description": "Sem alerta ativo",
        },
        SeverityLevel.WATCH: {
            "color": "#F2B90D",  # spec yellow
            "icon": "eye",
            "shape": "rounded-square",
            "label": "Observação",
            "description": "Monitoramento recomendado",
        },
        SeverityLevel.URGENT: {
            "color": "#F96F06",  # spec orange
            "icon": "alert-triangle",
            "shape": "triangle",
            "label": "Urgente",
            "description": "Ação em até 2h",
        },
        SeverityLevel.CRITICAL: {
            "color": "#F5828F",  # spec red/pink
            "icon": "alert-octagon",
            "shape": "octagon",
            "label": "Crítico",
            "description": "Ação imediata",
        },
    }

    @classmethod
    def encode(cls, severity: SeverityLevel | str) -> dict[str, str]:
        """Return triple-encoding dict for a severity level."""
        if isinstance(severity, str):
            severity = SeverityLevel(severity)
        return dict(cls._ENCODING[severity])

    @classmethod
    def color(cls, severity: SeverityLevel | str) -> str:
        """Return hex color for a severity level."""
        if isinstance(severity, str):
            severity = SeverityLevel(severity)
        return cls._ENCODING[severity]["color"]

    @classmethod
    def icon(cls, severity: SeverityLevel | str) -> str:
        """Return icon name for a severity level."""
        if isinstance(severity, str):
            severity = SeverityLevel(severity)
        return cls._ENCODING[severity]["icon"]

    @classmethod
    def shape(cls, severity: SeverityLevel | str) -> str:
        """Return shape modifier for a severity level."""
        if isinstance(severity, str):
            severity = SeverityLevel(severity)
        return cls._ENCODING[severity]["shape"]

    @classmethod
    def label(cls, severity: SeverityLevel | str) -> str:
        """Return human-readable label for a severity level."""
        if isinstance(severity, str):
            severity = SeverityLevel(severity)
        return cls._ENCODING[severity]["label"]

    @classmethod
    def all_severities(cls) -> list[dict[str, Any]]:
        """Return encoding for all severity levels (for API discovery)."""
        return [{"severity": sev.value, **cls._ENCODING[sev]} for sev in SeverityLevel]


def highest_severity(*severities: str | None) -> SeverityLevel | None:
    """P0-10: return the highest severity from a collection.

    Never last-writer-wins — always picks the MAX severity.
    Returns None for empty input or all-None input.

    Examples:
        >>> highest_severity("watch", "critical", "urgent")
        <SeverityLevel.CRITICAL: 'critical'>
        >>> highest_severity("normal", None, "watch")
        <SeverityLevel.WATCH: 'watch'>
        >>> highest_severity(None, None)
        None
    """
    best: SeverityLevel | None = None
    best_rank = -1
    for s in severities:
        if s is None:
            continue
        sev = SeverityLevel(s) if isinstance(s, str) else s
        if sev.rank > best_rank:
            best = sev
            best_rank = sev.rank
    return best


def max_severity(*severities: str | None) -> str | None:
    """P0-10: return the highest severity string from a collection.

    Alias for highest_severity() that returns str or None.
    """
    result = highest_severity(*severities)
    return result.value if result else None
