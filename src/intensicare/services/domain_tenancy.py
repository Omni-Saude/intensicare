"""Domain service: TENANCY-ORGANIZACAO cluster — UNVERIFIABLE RATIFY rules.

RATIFIED 2026-07-04 per RATIFICATION-DECISIONS.md ASK-2:
  Recommended defaults across groups:
    GRP-TEN-SECTOR-DISPLAY-COUNT: A (keep as-is)
    GRP-TEN-MERGE-PATTERN: A (keep as-is)
    GRP-TEN-INDICATOR-AGG: C (keep as-is)
    GRP-TEN-MESSAGING-COUNTS: C (keep as-is)
    GRP-TEN-CHAT-ORDERING: C (keep as-is)
    GRP-TEN-SCOPING-TODO: C (keep as-is)

Member rules (14 UNVERIFIABLE RATIFY):
  RULE-TENANCY-ORGANIZACAO-005 through 015, 038, 041, 042

All rules confirmed verbatim per drafter recommendations under owner delegation.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.
"""

from __future__ import annotations

from datetime import datetime, timezone
from math import floor


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-005: Establishment macro-indicator aggregate
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/estabelecimento.py @8166c07
# sum/avg of sector-level indicators, rounded to 2 decimal places.
# ═════════════════════════════════════════════════════════════════════════════


def aggregate_establishment_indicators(
    sector_values: list[float],
) -> dict[str, float]:
    """Aggregate macro indicators across sectors (sum + avg, rounded to 2 dp).

    RULE-TENANCY-ORGANIZACAO-005 (RATIFIED, UNVERIFIABLE).

    Args:
        sector_values: List of indicator values from each sector.

    Returns:
        Dict with 'sum' and 'avg' rounded to 2 decimal places.
        If empty list, returns {'sum': 0.0, 'avg': 0.0}.
    """
    if not sector_values:
        return {"sum": 0.0, "avg": 0.0}
    total = sum(sector_values)
    avg = total / len(sector_values)
    return {"sum": round(total, 2), "avg": round(avg, 2)}


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-006: Sector macro-indicator single-record fetch
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Single-record fetch with silent failure (returns None on missing).
# ═════════════════════════════════════════════════════════════════════════════

def fetch_sector_indicator(
    indicators: list[dict[str, object]] | None,
) -> dict[str, object] | None:
    """Fetch a single sector macro indicator, returning None on failure.

    RULE-TENANCY-ORGANIZACAO-006 (RATIFIED, UNVERIFIABLE).
    Single-record fetch with silent failure — returns None if missing/empty.

    Args:
        indicators: List of indicator dicts (expected single-element or None).

    Returns:
        The first indicator dict, or None if empty/missing.
    """
    if not indicators:
        return None
    return indicators[0] if len(indicators) > 0 else None


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-007: Establishment unread message count
# Category: alert-threshold | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/estabelecimento.py @8166c07
# Establishment-level count sums unread messages across ALL sectors.
# ═════════════════════════════════════════════════════════════════════════════

def establishment_unread_count(sector_unread_counts: list[int]) -> int:
    """Sum unread message counts across all sectors.

    RULE-TENANCY-ORGANIZACAO-007 (RATIFIED, UNVERIFIABLE).

    Args:
        sector_unread_counts: List of unread counts per sector.

    Returns:
        Total unread count for the establishment.
    """
    return sum(sector_unread_counts)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-008: Sector unread message count via Firestore
# Category: alert-threshold | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Firestore-backed unread count per sector.
# ═════════════════════════════════════════════════════════════════════════════

def sector_unread_count(firestore_counts: dict[str, int] | None) -> int:
    """Read sector unread message count from Firestore-derived data.

    RULE-TENANCY-ORGANIZACAO-008 (RATIFIED, UNVERIFIABLE).
    Returns 0 if no data available.

    Args:
        firestore_counts: Dict mapping sector_id to count, or None.

    Returns:
        Total unread count (sum of all values), or 0 if input is None.
    """
    if firestore_counts is None:
        return 0
    return sum(firestore_counts.values())


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-009: Combined setor display name
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/setor.py:22-23 @8166c07
# Format: estabelecimento.nome + " - " + setor.nome
# ═════════════════════════════════════════════════════════════════════════════

def combined_setor_display_name(
    estabelecimento_nome: str, setor_nome: str
) -> str:
    """Combine establishment name and sector name for display.

    RULE-TENANCY-ORGANIZACAO-009 (RATIFIED, UNVERIFIABLE).
    Format: "{estabelecimento} - {setor}"

    Args:
        estabelecimento_nome: Name of the parent establishment.
        setor_nome: Name of the sector.

    Returns:
        Combined display name string.
    """
    return f"{estabelecimento_nome} - {setor_nome}"


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-010: 'atualizado_em' timestamp floored to 5-min
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Floor timestamp to 5-minute buckets for display consistency.
# ═════════════════════════════════════════════════════════════════════════════

def floor_to_5min_bucket(ts: datetime) -> datetime:
    """Floor a timestamp to the nearest 5-minute bucket.

    RULE-TENANCY-ORGANIZACAO-010 (RATIFIED, UNVERIFIABLE).

    Args:
        ts: A datetime object (naive or timezone-aware).

    Returns:
        Same datetime with minutes floored to 0, 5, 10, 15, 20, 25, 30, 35,
        40, 45, 50, or 55, and seconds/microseconds zeroed.
    """
    minute_bucket = (ts.minute // 5) * 5
    return ts.replace(minute=minute_bucket, second=0, microsecond=0)


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-011: Sector alert counts merge manual + automatica
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Merges manual-movement alert counts with automatic-pathway records.
# ═════════════════════════════════════════════════════════════════════════════

def merge_sector_alert_counts(
    manual_counts: dict[str, int],
    automatica_counts: dict[str, int],
) -> dict[str, int]:
    """Merge manual and automatica alert counts for a sector.

    RULE-TENANCY-ORGANIZACAO-011 (RATIFIED, UNVERIFIABLE).
    Simple element-wise sum of both count dictionaries.

    Args:
        manual_counts: Alert counts from manual movements.
        automatica_counts: Alert counts from automatic pathways.

    Returns:
        Merged counts by alert type.
    """
    merged: dict[str, int] = {}
    all_keys = set(manual_counts.keys()) | set(automatica_counts.keys())
    for key in all_keys:
        merged[key] = manual_counts.get(key, 0) + automatica_counts.get(key, 0)
    return merged


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-012: Sector bed totals (active beds only)
# Category: physiological-calculation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Only counts beds where ativo=True.
# ═════════════════════════════════════════════════════════════════════════════

def active_bed_count(beds: list[dict[str, object]]) -> int:
    """Count active beds only (ativo=True).

    RULE-TENANCY-ORGANIZACAO-012 (RATIFIED, UNVERIFIABLE).

    Args:
        beds: List of bed dicts with 'ativo' field.

    Returns:
        Count of beds where ativo is truthy.
    """
    return sum(1 for bed in beds if bed.get("ativo"))


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-013: Sector gender counts merge
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Merges gender counts from manual movements + automatic-pathway records.
# ═════════════════════════════════════════════════════════════════════════════

def merge_sector_gender_counts(
    manual_genders: dict[str, int],
    automatica_genders: dict[str, int],
) -> dict[str, int]:
    """Merge manual and automatica gender counts for a sector.

    RULE-TENANCY-ORGANIZACAO-013 (RATIFIED, UNVERIFIABLE).
    Element-wise sum across gender categories (M, F, N, O...).

    Args:
        manual_genders: Gender counts from manual movements.
        automatica_genders: Gender counts from automatic pathways.

    Returns:
        Merged counts by gender.
    """
    merged: dict[str, int] = {}
    all_keys = set(manual_genders.keys()) | set(automatica_genders.keys())
    for key in all_keys:
        merged[key] = manual_genders.get(key, 0) + automatica_genders.get(key, 0)
    return merged


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-014: Sector chat preview
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Picks the first related Observacao without explicit ordering.
# ═════════════════════════════════════════════════════════════════════════════

def sector_chat_preview(
    observacoes: list[dict[str, object]],
) -> dict[str, object] | None:
    """Return the first observation as sector chat preview.

    RULE-TENANCY-ORGANIZACAO-014 (RATIFIED, UNVERIFIABLE).
    Returns the first element (no explicit ordering guarantee).

    Args:
        observacoes: List of observation dicts.

    Returns:
        First observation dict, or None if empty.
    """
    if not observacoes:
        return None
    return observacoes[0]


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-015: Monthly total intervention count
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Total intervention count for current month for sector indicators.
# ═════════════════════════════════════════════════════════════════════════════

def monthly_intervention_count(
    interventions: list[dict[str, object]],
    reference_date: datetime | None = None,
) -> int:
    """Count interventions in the reference month.

    RULE-TENANCY-ORGANIZACAO-015 (RATIFIED, UNVERIFIABLE).

    Args:
        interventions: List of intervention dicts with 'data' field.
        reference_date: Reference date (defaults to now). Used to determine month.

    Returns:
        Count of interventions in the same month as reference_date.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)
    target_month = reference_date.month
    target_year = reference_date.year
    count = 0
    for intervention in interventions:
        data = intervention.get("data")
        if data is not None:
            if isinstance(data, str):
                data = datetime.fromisoformat(data.replace("Z", "+00:00"))
            if (
                isinstance(data, datetime)
                and data.month == target_month
                and data.year == target_year
            ):
                count += 1
    return count


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-038: Sector clinical indicator aggregation
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/setor.py @8166c07
# Aggregates clinical indicators across care pathways within a sector.
# ═════════════════════════════════════════════════════════════════════════════

def sector_clinical_indicator_aggregation(
    pathway_indicators: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Aggregate clinical indicators across care pathways.

    RULE-TENANCY-ORGANIZACAO-038 (RATIFIED, UNVERIFIABLE).

    Args:
        pathway_indicators: Dict mapping pathway_name -> {indicator_name -> value}.

    Returns:
        Aggregated indicators across all pathways (sum per indicator name).
    """
    aggregated: dict[str, float] = {}
    for pathway_name, indicators in pathway_indicators.items():
        for ind_name, value in indicators.items():
            aggregated[ind_name] = aggregated.get(ind_name, 0.0) + value
    return {k: round(v, 2) for k, v in aggregated.items()}


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-041: Company-wide indicadores action scopes
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/empresa.py @8166c07
# Scopes company-wide indicator actions to user's establishments.
# ═════════════════════════════════════════════════════════════════════════════

def company_indicadores_scopes(
    user_establishment_ids: list[int],
    all_establishments: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Filter establishments to those accessible by the user.

    RULE-TENANCY-ORGANIZACAO-041 (RATIFIED, UNVERIFIABLE).

    Args:
        user_establishment_ids: List of establishment IDs the user can access.
        all_establishments: List of all establishment dicts with 'id' field.

    Returns:
        Filtered list of establishments scoped to user access.
    """
    allowed = set(user_establishment_ids)
    return [e for e in all_establishments if e.get("id") in allowed]


# ═════════════════════════════════════════════════════════════════════════════
# RULE-TENANCY-ORGANIZACAO-042: Establishment indicadores action scopes
# Category: clinical-scoring | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/models/estabelecimento.py @8166c07
# Scopes establishment-level indicator actions to movimentacoes and sectors.
# ═════════════════════════════════════════════════════════════════════════════

def establishment_indicadores_scopes(
    establishment_id: int,
    movimentacoes: list[dict[str, object]],
    sectors: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    """Scope indicators to an establishment's movimentacoes and sectors.

    RULE-TENANCY-ORGANIZACAO-042 (RATIFIED, UNVERIFIABLE).

    Args:
        establishment_id: The establishment ID to scope to.
        movimentacoes: List of all movimentacao dicts.
        sectors: List of all sector dicts.

    Returns:
        Dict with 'movimentacoes' and 'setores' keys, each filtered.
    """
    scoped_movs = [
        m for m in movimentacoes
        if m.get("estabelecimento_id") == establishment_id
    ]
    scoped_sectors = [
        s for s in sectors
        if s.get("estabelecimento_id") == establishment_id
    ]
    return {
        "movimentacoes": scoped_movs,
        "setores": scoped_sectors,
    }
