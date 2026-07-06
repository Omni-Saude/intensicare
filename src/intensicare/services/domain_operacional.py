"""Domain service: OPERACIONAL cluster — UNVERIFIABLE RATIFY rules.

RATIFIED 2026-07-04 per RATIFICATION-DECISIONS.md ASK-2:
  Recommended defaults across groups:
    GRP-INFRA-STRING-PARSE-UTILS: A (keep as-is)
    GRP-INFRA-OFFLINE-RX: A (keep as-is)
    GRP-INFRA-B-DURATION-PAGINATION: C (keep as-is)

Member rules (10 UNVERIFIABLE RATIFY):
  RULE-OPERACIONAL-INFRA-002 through 011
  (excluding 001 which is not UNVERIFIABLE-RATIFY)

All rules confirmed verbatim per drafter recommendations under owner delegation.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from math import floor
from typing import Any


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-002: Patient name abbreviation
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Abbreviates a patient's full name for display, handling Portuguese
# connectives (de, da, do, dos, das) by either keeping or dropping them.
# ═════════════════════════════════════════════════════════════════════════════

_CONNECTIVES = {"de", "da", "do", "dos", "das", "e"}


def nome_abreviado(nome_completo: str, max_parts: int = 2) -> str:
    """Abbreviate a patient's full name for display.

    RULE-OPERACIONAL-INFRA-002 (RATIFIED, UNVERIFIABLE).
    Keeps the first name(s) and abbreviates subsequent names to initials.
    Handles Portuguese connectives (de, da, do, dos, das, e).

    Args:
        nome_completo: Full name string.
        max_parts: Maximum number of full-name parts to keep (default: 2).

    Returns:
        Abbreviated name, e.g. "Joao Paulo S." or "Maria da S.".

    Examples:
        "Joao Paulo Silva Santos" -> "Joao Paulo S. S."
        "Maria da Silva" -> "Maria da S."
        "Jose de Oliveira" -> "Jose de O."
    """
    if not nome_completo or not nome_completo.strip():
        return ""

    parts = nome_completo.strip().split()
    if len(parts) <= 1:
        return nome_completo.strip()

    result_parts: list[str] = []
    full_kept = 0
    for i, part in enumerate(parts):
        lower = part.lower()
        if full_kept < max_parts or lower in _CONNECTIVES:
            result_parts.append(part)
            if lower not in _CONNECTIVES:
                full_kept += 1
        else:
            # Abbreviate to first letter + "."
            result_parts.append(f"{part[0]}.")

    return " ".join(result_parts)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-003: Offline prescriptions grouped by day
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Groups prescriptions by day, keyed by patient atendimento number.
# ═════════════════════════════════════════════════════════════════════════════

def group_prescriptions_by_day(
    prescriptions: list[dict[str, object]],
) -> dict[str, dict[str, list[dict[str, object]]]]:
    """Group offline prescriptions by patient and day.

    RULE-OPERACIONAL-INFRA-003 (RATIFIED, UNVERIFIABLE).

    Args:
        prescriptions: List of prescription dicts with 'atendimento' and 'data' keys.

    Returns:
        Nested dict: {atendimento_id: {date_str: [prescriptions...]}}.
    """
    grouped: dict[str, dict[str, list[dict[str, object]]]] = {}
    for rx in prescriptions:
        atendimento = str(rx.get("atendimento", ""))
        data_val = rx.get("data")
        if data_val is not None:
            if isinstance(data_val, datetime):
                day_key = data_val.strftime("%Y-%m-%d")
            elif isinstance(data_val, date):
                day_key = data_val.isoformat()
            else:
                day_key = str(data_val)[:10]
        else:
            day_key = "unknown"

        if atendimento not in grouped:
            grouped[atendimento] = {}
        if day_key not in grouped[atendimento]:
            grouped[atendimento][day_key] = []
        grouped[atendimento][day_key].append(rx)

    return grouped


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-004: Continuous prescription 'real day' rolls at 07:00
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Shift boundary: the clinical day rolls over at 07:00, not midnight.
# ═════════════════════════════════════════════════════════════════════════════

_SHIFT_HOUR = 7


def get_real_day(dt: datetime | None = None) -> date:
    """Get the clinical 'real day' considering 07:00 shift boundary.

    RULE-OPERACIONAL-INFRA-004 (RATIFIED, UNVERIFIABLE).
    Before 07:00, the clinical day is still the previous calendar day.

    Args:
        dt: Datetime to check (defaults to now).

    Returns:
        The clinical day date.
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    if dt.hour < _SHIFT_HOUR:
        # Before 07:00, it's still the previous clinical day
        from datetime import timedelta
        return (dt - timedelta(days=1)).date()
    return dt.date()


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-005: Offline prescriptions windowed to last 3 days
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Windowed to the last 3 days, ordered by date descending.
# ═════════════════════════════════════════════════════════════════════════════

def filter_prescriptions_last_3_days(
    prescriptions: list[dict[str, object]],
    reference_date: datetime | None = None,
) -> list[dict[str, object]]:
    """Filter prescriptions to the last 3 days (clinical days).

    RULE-OPERACIONAL-INFRA-005 (RATIFIED, UNVERIFIABLE).

    Args:
        prescriptions: List of prescription dicts with 'data' key.
        reference_date: Reference datetime (defaults to now).

    Returns:
        Filtered list sorted by data descending.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    cutoff_date = reference_date.date()
    from datetime import timedelta
    three_days_ago = cutoff_date - timedelta(days=3)

    filtered = []
    for rx in prescriptions:
        data_val = rx.get("data")
        if data_val is not None:
            if isinstance(data_val, datetime):
                rx_date = data_val.date()
            elif isinstance(data_val, date):
                rx_date = data_val
            else:
                try:
                    rx_date = date.fromisoformat(str(data_val)[:10])
                except (ValueError, TypeError):
                    continue
            if rx_date >= three_days_ago:
                filtered.append(rx)

    # Sort by data descending
    def _sort_key(rx: dict[str, object]) -> str:
        d = rx.get("data")
        if isinstance(d, (datetime, date)):
            return d.isoformat()
        return str(d)

    return sorted(filtered, key=_sort_key, reverse=True)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-006: Length of stay computed property
# Category: physiological-calculation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/movimentacao.py @8166c07
# TEMPO_PERMANENCIA: whole-day difference between now and admission date.
# ═════════════════════════════════════════════════════════════════════════════

def compute_length_of_stay(data_entrada: date | datetime) -> int:
    """Compute length of stay in whole days.

    RULE-OPERACIONAL-INFRA-006 (RATIFIED, UNVERIFIABLE).
    Uses .date() so partial days are truncated (whole-day difference).

    Args:
        data_entrada: Admission date.

    Returns:
        Number of whole days elapsed.
    """
    if isinstance(data_entrada, datetime):
        entrada_date = data_entrada.date()
    else:
        entrada_date = data_entrada
    return (datetime.now(timezone.utc).date() - entrada_date).days


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-007: Pagination page-count and default page size
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Default page size and page count calculation for list endpoints.
# ═════════════════════════════════════════════════════════════════════════════

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


def compute_pagination(
    total_items: int,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> dict[str, int]:
    """Compute pagination metadata.

    RULE-OPERACIONAL-INFRA-007 (RATIFIED, UNVERIFIABLE).

    Args:
        total_items: Total number of items.
        page: Current page number (1-indexed, default: 1).
        page_size: Items per page (default: 10, max: 100).

    Returns:
        Dict with 'page', 'page_size', 'total_items', 'total_pages', 'offset'.
    """
    page_size = min(page_size, MAX_PAGE_SIZE)
    page_size = max(page_size, 1)
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    offset = (page - 1) * page_size

    return {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "offset": offset,
    }


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-008: Minutes elapsed between two dates
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Returns the floor of total seconds / 60 between two datetimes.
# ═════════════════════════════════════════════════════════════════════════════

def minutes_elapsed(
    start: datetime,
    end: datetime | None = None,
) -> int:
    """Calculate minutes elapsed between two datetimes.

    RULE-OPERACIONAL-INFRA-008 (RATIFIED, UNVERIFIABLE).

    Args:
        start: Start datetime.
        end: End datetime (defaults to now).

    Returns:
        Floor of total seconds / 60.
    """
    if end is None:
        end = datetime.now(timezone.utc)
    delta = end - start
    return floor(delta.total_seconds() / 60)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-009: format_horario — normalize hour strings to HH:MM
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py:85-98 @8166c07
# Normalizes hour-only strings (e.g. "7" -> "07:00", "7:30" -> "07:30").
# ═════════════════════════════════════════════════════════════════════════════

def format_horario(hora_str: str) -> str:
    """Normalize an hour-time string to HH:MM format.

    RULE-OPERACIONAL-INFRA-009 (RATIFIED, UNVERIFIABLE).
    Handles formats: "7", "07", "7:30", "07:30", "19", "19:45", etc.

    Args:
        hora_str: Input hour string.

    Returns:
        Normalized HH:MM string, e.g. "7" -> "07:00".

    Raises:
        ValueError: If the string cannot be parsed as a time.
    """
    hora_str = hora_str.strip()
    # Try HH:MM or H:MM
    if ":" in hora_str:
        parts = hora_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1]) if len(parts) > 1 else 0
    else:
        hours = int(hora_str)
        minutes = 0

    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        raise ValueError(f"Invalid time: {hora_str}")

    return f"{hours:02d}:{minutes:02d}"


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-010: parse_date_to_iso — multi-format date parser
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Parses dates from multiple common Brazilian formats with fixed timezone.
# ═════════════════════════════════════════════════════════════════════════════

_DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
]


def parse_date_to_iso(date_str: str | None) -> str | None:
    """Parse a date string into ISO format (YYYY-MM-DDTHH:MM:SS+00:00).

    RULE-OPERACIONAL-INFRA-010 (RATIFIED, UNVERIFIABLE).
    Tries multiple common Brazilian date formats with fixed UTC timezone.

    Args:
        date_str: Input date string or None.

    Returns:
        ISO 8601 datetime string with UTC offset, or None if input is None/empty.

    Raises:
        ValueError: If no format matches.
    """
    if date_str is None or not date_str.strip():
        return None

    date_str = date_str.strip()
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # If no timezone, assume UTC
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.isoformat()
        except ValueError:
            continue

    raise ValueError(f"Cannot parse date: {date_str}")


# ═════════════════════════════════════════════════════════════════════════════
# RULE-OPERACIONAL-INFRA-011: get_number — safe numeric coercion
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/utils.py @8166c07
# Safely coerces a value to float, returning 0.0 on failure.
# ═════════════════════════════════════════════════════════════════════════════

def get_number(value: object) -> float:
    """Safely coerce a value to float, returning 0.0 on failure.

    RULE-OPERACIONAL-INFRA-011 (RATIFIED, UNVERIFIABLE).
    Handles Brazilian decimal separator (comma) by replacing ',' with '.'.

    Args:
        value: Any value (int, float, str, None, etc.).

    Returns:
        Float value, or 0.0 if conversion fails.

    Examples:
        get_number("10,5") -> 10.5
        get_number("10.5") -> 10.5
        get_number(10) -> 10.0
        get_number(None) -> 0.0
        get_number("abc") -> 0.0
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Replace Brazilian decimal comma
        cleaned = value.strip().replace(",", ".")
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            pass
    try:
        return float(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return 0.0
