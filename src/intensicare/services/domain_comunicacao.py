"""Domain service: COMUNICACAO cluster — UNVERIFIABLE RATIFY rules.

RATIFIED 2026-07-04 per RATIFICATION-DECISIONS.md ASK-2:
  Recommended defaults across groups:
    GRP-COM-B-REACTION-AGGREGATION: B (keep as-is, with corrected path)

Member rules (3 UNVERIFIABLE RATIFY):
  RULE-COMUNICACAO-001: Reaction-count-by-emoji aggregation
  RULE-COMUNICACAO-002: Current user's own reaction id on an observation
  RULE-COMUNICACAO-003: AcaoHomecare balanco_hidrico method-reference bug

All rules confirmed verbatim per drafter recommendations under owner delegation.
Provenance: ahlabs-trilhas @ 8166c07eaef97ad4f9b2a0e51235f3fc3d0feb7f.

NOTE: RULE-COMUNICACAO-003 is a known bug (missing () on get_pk call).
It is RATIFIED to carry the corrected behavior (call get_pk properly),
consistent with the drafter recommendation to fix the bug rather than port it.
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import groupby
from typing import Any


# ═════════════════════════════════════════════════════════════════════════════
# RULE-COMUNICACAO-001: Reaction-count-by-emoji aggregation
# Category: data-validation | Type: formula | Status: DISCREPANCY | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/observacao.py:155-156 @8166c07
# Two backend code paths diverge:
#   (A) ObservacaoSerializer.get_reacoes: SQL GROUP BY — CORRECT
#   (B) ReacaoViewSet.list: itertools.groupby without order_by — BUGGY
#
# The RATIFY disposition confirms the correct behavior (SQL GROUP BY path).
# This service implements the CORRECT aggregation: emoji → count.
# ═════════════════════════════════════════════════════════════════════════════


def aggregate_reactions_by_emoji_sql(
    reactions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Aggregate reaction counts by emoji using dict-based grouping (SQL-equivalent).

    RULE-COMUNICACAO-001 (RATIFIED, UNVERIFIABLE).
    Implements the CORRECT path (equivalent to SQL GROUP BY).
    Order-independent; always produces correct per-emoji totals.

    Args:
        reactions: List of reaction dicts, each with 'emoji' key.

    Returns:
        List of {emoji, total} dicts, one per unique emoji.
    """
    counts: dict[str, int] = {}
    for r in reactions:
        emoji = str(r.get("emoji", ""))
        counts[emoji] = counts.get(emoji, 0) + 1
    return [{"emoji": emoji, "total": total} for emoji, total in counts.items()]


def aggregate_reactions_by_emoji_groupby(
    reactions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Aggregate reactions by emoji using itertools.groupby (order-dependent).

    RULE-COMUNICACAO-001 variant (RATIFIED with warning).
    NOTE: This requires reactions to be pre-sorted by emoji.
    Without .order_by('emoji'), this can silently split/undercount.

    This function is preserved for compatibility but the SQL-equivalent
    version (aggregate_reactions_by_emoji_sql) is preferred.

    Args:
        reactions: List of reaction dicts, PRE-SORTED by 'emoji'.

    Returns:
        List of {emoji, total} dicts, one per consecutive emoji group.
    """
    payload: list[dict[str, object]] = []
    for emoji, group in groupby(reactions, key=lambda r: r.get("emoji")):
        reactions_list = list(group)
        payload.append({"emoji": emoji, "total": len(reactions_list)})
    return payload


def aggregate_reactions_with_users(
    reactions: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Aggregate reactions by emoji including user lists.

    RULE-COMUNICACAO-001 extended (RATIFIED).
    SQL-equivalent grouping with user attribution.

    Args:
        reactions: List of reaction dicts with 'emoji' and 'usuario_id' keys.

    Returns:
        List of {emoji, total, usuario_ids} dicts.
    """
    emoji_map: dict[str, dict[str, object]] = {}
    for r in reactions:
        emoji = str(r.get("emoji", ""))
        usuario_id = r.get("usuario_id")
        if emoji not in emoji_map:
            emoji_map[emoji] = {"emoji": emoji, "total": 0, "usuario_ids": []}
        total_val = emoji_map[emoji]["total"]
        emoji_map[emoji]["total"] = int(total_val) + 1  # type: ignore[arg-type]
        if usuario_id is not None:
            uid_list: list[object] = emoji_map[emoji]["usuario_ids"]  # type: ignore[assignment]
            uid_list.append(usuario_id)
    return list(emoji_map.values())


# ═════════════════════════════════════════════════════════════════════════════
# RULE-COMUNICACAO-002: Current user's own reaction id on an observation
# Category: data-validation | Type: formula | Status: OK | Verdict: UNVERIFIABLE
#
# Legacy source: core/api/v1/serializers/observacao.py @8166c07
# Returns the reaction id (or None) for the current user on a given observation.
# ═════════════════════════════════════════════════════════════════════════════

def find_user_reaction(
    reactions: list[dict[str, object]],
    user_id: int,
) -> dict[str, object] | None:
    """Find the current user's reaction on an observation.

    RULE-COMUNICACAO-002 (RATIFIED, UNVERIFIABLE).

    Args:
        reactions: List of reaction dicts with 'usuario_id' and 'reaction_id' keys.
        user_id: The current user's ID.

    Returns:
        The user's reaction dict if found, or None.
    """
    for reaction in reactions:
        if reaction.get("usuario_id") == user_id:
            return reaction
    return None


def get_user_reaction_id(
    reactions: list[dict[str, object]],
    user_id: int,
) -> int | None:
    """Get the reaction ID for the current user on an observation.

    RULE-COMUNICACAO-002 (RATIFIED, UNVERIFIABLE).
    Convenience wrapper returning just the reaction id.

    Args:
        reactions: List of reaction dicts.
        user_id: The current user's ID.

    Returns:
        The reaction id if the user has reacted, or None.
    """
    reaction = find_user_reaction(reactions, user_id)
    if reaction is not None:
        rid = reaction.get("reaction_id") or reaction.get("id")
        if rid is not None:
            return int(rid)  # type: ignore[arg-type]
    return None


# ═════════════════════════════════════════════════════════════════════════════
# RULE-COMUNICACAO-003: AcaoHomecare balanco_hidrico method-reference bug
# Category: care-pathway | Type: formula | Status: DISCREPANCY | Verdict: UNVERIFIABLE
#
# Legacy source: trilha_homecare/api/v1/serializers/acao_homecare.py:54-58 @8166c07
#
# BUG: The legacy code references `obj.balanco_hidrico.get_pk` without calling
# it (missing parentheses), returning a bound-method object instead of the
# intended integer PK value.
#
# RATIFIED with correction: the intended call is `obj.balanco_hidrico.get_pk()`
# or simply `obj.balanco_hidrico_id` / `obj.balanco_hidrico.pk`.
# ═════════════════════════════════════════════════════════════════════════════


def resolve_balanco_hidrico_pk(
    obj: object,
    *,
    get_pk: Callable[[], int] | None = None,
    pk_attr: str = "balanco_hidrico_id",
) -> int | None:
    """Resolve the fluid-balance PK from an AcaoHomecare instance.

    RULE-COMUNICACAO-003 (RATIFIED, CORRECTED).
    The legacy code had a bug: obj.balanco_hidrico.get_pk (missing () call).
    This corrected version properly calls get_pk() or accesses the FK field.

    Args:
        obj: An AcaoHomecare-like object with entrada/saida/sinal_vital attrs.
        get_pk: Optional callable to use instead of attribute access.
        pk_attr: FK attribute name to try (default: 'balanco_hidrico_id').

    Returns:
        The fluid-balance PK as int, or None if no related record exists.
    """
    # First try to find the related object (entrada, saida, or sinal_vital)
    related = None
    for attr in ("entrada", "saida", "sinal_vital"):
        related = getattr(obj, attr, None)
        if related is not None:
            break

    if related is None:
        return None

    # Try the FK id attribute first (most efficient)
    fk_val = getattr(related, pk_attr, None)
    if fk_val is not None:
        return int(fk_val)

    # Fall back to calling get_pk() if provided
    if get_pk is not None:
        return get_pk()

    # Last resort: try to call get_pk on the related object
    pk_method = getattr(related, "get_pk", None)
    if callable(pk_method):
        result = pk_method()
        if result is not None:
            return int(result)

    # Try direct .pk or .id access
    pk = getattr(related, "pk", None) or getattr(related, "id", None)
    if pk is not None:
        try:
            return int(str(pk))
        except (TypeError, ValueError):
            pass

    return None


def resolve_balanco_hidrico_pk_from_dict(
    related_obj: dict[str, object] | None,
) -> int | None:
    """Resolve fluid-balance PK from a dict-based object.

    RULE-COMUNICACAO-003 dict variant (RATIFIED, CORRECTED).

    Args:
        related_obj: Dict with balanco_hidrico data, or None.

    Returns:
        The PK as int, or None.
    """
    if related_obj is None:
        return None
    pk = related_obj.get("balanco_hidrico_id") or related_obj.get("pk") or related_obj.get("id")
    if pk is not None:
        try:
            return int(str(pk))
        except (TypeError, ValueError):
            pass
    return None
