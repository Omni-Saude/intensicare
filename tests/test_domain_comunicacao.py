"""Tests for domain_comunicacao — WAVE 2C UNVERIFIABLE RATIFY rules."""

from __future__ import annotations

from intensicare.services.domain_comunicacao import (
    aggregate_reactions_by_emoji_groupby,
    aggregate_reactions_by_emoji_sql,
    aggregate_reactions_with_users,
    find_user_reaction,
    get_user_reaction_id,
    resolve_balanco_hidrico_pk,
    resolve_balanco_hidrico_pk_from_dict,
)


class TestAggregateReactionsByEmoji:
    """RULE-COMUNICACAO-001."""

    def test_sql_correct(self) -> None:
        reactions = [
            {"emoji": "❤️", "usuario_id": 1},
            {"emoji": "❤️", "usuario_id": 2},
            {"emoji": "👍", "usuario_id": 3},
        ]
        result = aggregate_reactions_by_emoji_sql(reactions)
        # Order-independent: should get 2 groups
        emoji_map = {r["emoji"]: r["total"] for r in result}
        assert emoji_map == {"❤️": 2, "👍": 1}

    def test_groupby_sorted(self) -> None:
        reactions = [
            {"emoji": "❤️"},
            {"emoji": "❤️"},
            {"emoji": "👍"},
        ]
        result = aggregate_reactions_by_emoji_groupby(reactions)
        emoji_map = {r["emoji"]: r["total"] for r in result}
        assert emoji_map == {"❤️": 2, "👍": 1}

    def test_groupby_unsorted_split(self) -> None:
        """groupby splits non-consecutive entries — known legacy bug."""
        reactions = [
            {"emoji": "❤️"},
            {"emoji": "👍"},
            {"emoji": "❤️"},
        ]
        result = aggregate_reactions_by_emoji_groupby(reactions)
        # Should produce 3 groups (split)
        assert len(result) == 3

    def test_empty(self) -> None:
        assert aggregate_reactions_by_emoji_sql([]) == []
        assert aggregate_reactions_by_emoji_groupby([]) == []

    def test_with_users(self) -> None:
        reactions = [
            {"emoji": "👍", "usuario_id": 1},
            {"emoji": "👍", "usuario_id": 2},
            {"emoji": "❤️", "usuario_id": 3},
        ]
        result = aggregate_reactions_with_users(reactions)
        emoji_map = {r["emoji"]: r["total"] for r in result}
        assert emoji_map == {"👍": 2, "❤️": 1}


class TestFindUserReaction:
    """RULE-COMUNICACAO-002."""

    def test_finds_reaction(self) -> None:
        reactions = [
            {"usuario_id": 1, "reaction_id": 10},
            {"usuario_id": 2, "reaction_id": 20},
        ]
        result = find_user_reaction(reactions, 2)
        assert result is not None
        assert result["reaction_id"] == 20

    def test_not_found(self) -> None:
        reactions = [{"usuario_id": 1}]
        assert find_user_reaction(reactions, 99) is None

    def test_get_user_reaction_id(self) -> None:
        reactions = [{"usuario_id": 1, "id": 42}]
        assert get_user_reaction_id(reactions, 1) == 42

    def test_get_user_reaction_id_not_found(self) -> None:
        assert get_user_reaction_id([], 1) is None


class FakeRelated:
    """Fake object to simulate AcaoHomecare related record."""

    def __init__(self, bh_id: int | None = None) -> None:
        self.balanco_hidrico_id = bh_id
        self.pk = bh_id

    def get_pk(self) -> int | None:
        return self.pk


class FakeAcaoHomecare:
    """Fake AcaoHomecare-like object."""

    def __init__(self, related: FakeRelated | None = None) -> None:
        self.entrada = related
        self.saida = None
        self.sinal_vital = None


class TestResolveBalancoHidricoPk:
    """RULE-COMUNICACAO-003 — CORRECTED."""

    def test_resolves_via_fk_attr(self) -> None:
        related = FakeRelated(bh_id=42)
        obj = FakeAcaoHomecare(related)
        assert resolve_balanco_hidrico_pk(obj) == 42

    def test_resolves_via_get_pk(self) -> None:
        related = FakeRelated(bh_id=99)
        # Set balanco_hidrico_id to None so it falls through to get_pk
        related.balanco_hidrico_id = None  # type: ignore[attr-defined]
        obj = FakeAcaoHomecare(related)
        assert resolve_balanco_hidrico_pk(obj) == 99

    def test_no_related(self) -> None:
        obj = FakeAcaoHomecare(None)
        assert resolve_balanco_hidrico_pk(obj) is None

    def test_dict_variant(self) -> None:
        data = {"balanco_hidrico_id": 7}
        assert resolve_balanco_hidrico_pk_from_dict(data) == 7

    def test_dict_none(self) -> None:
        assert resolve_balanco_hidrico_pk_from_dict(None) is None

    def test_dict_no_pk(self) -> None:
        assert resolve_balanco_hidrico_pk_from_dict({"other": True}) is None
