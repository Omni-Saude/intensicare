"""
Tests for the /api/v1/indicators endpoints — 31 clinical quality indicators.

Covers:
  - GET  /api/v1/indicators          — list catalogue (paginated, filterable)
  - GET  /api/v1/indicators/{id}     — indicator detail
  - GET  /api/v1/indicators/summary  — aggregated dashboard summary
  - Authentication requirement (401 when unauthenticated)
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/indicators — list catalogue
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_indicators_returns_31(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """GET /api/v1/indicators must return the full catalogue of 31 indicators."""
    resp = await client.get("/api/v1/indicators", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 31
    assert data["pagination"]["total_items"] == 31
    assert data["pagination"]["total_pages"] == 1  # 31 items fits in page_size=50


@pytest.mark.asyncio
async def test_list_indicators_filter_by_category(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Filtering by category='TLP' must return only TLP indicators (3 items)."""
    resp = await client.get(
        "/api/v1/indicators", headers=admin_headers, params={"category": "TLP"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 3
    for item in data["data"]:
        assert item["category"] == "TLP"


@pytest.mark.asyncio
async def test_list_indicators_filter_unknown_category(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Filtering by an unknown category must return an empty data list."""
    resp = await client.get(
        "/api/v1/indicators",
        headers=admin_headers,
        params={"category": "NonExistentCategory"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"] == []
    assert data["pagination"]["total_items"] == 0
    assert data["pagination"]["total_pages"] == 0


@pytest.mark.asyncio
async def test_list_indicators_pagination(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Pagination must respect page and page_size parameters."""
    # With page_size=10, 31 items → 4 pages (10, 10, 10, 1)
    resp = await client.get(
        "/api/v1/indicators",
        headers=admin_headers,
        params={"page": 1, "page_size": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 10
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 10
    assert data["pagination"]["total_items"] == 31
    assert data["pagination"]["total_pages"] == 4

    # Page 4 should have 1 item
    resp2 = await client.get(
        "/api/v1/indicators",
        headers=admin_headers,
        params={"page": 4, "page_size": 10},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert len(data2["data"]) == 1
    assert data2["pagination"]["page"] == 4


@pytest.mark.asyncio
async def test_list_indicators_pagination_clamps_overflow(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """A page number beyond total_pages must be clamped to the last page."""
    resp = await client.get(
        "/api/v1/indicators",
        headers=admin_headers,
        params={"page": 999, "page_size": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Should clamp to page 4 (last page)
    assert data["pagination"]["page"] == 4


@pytest.mark.asyncio
async def test_list_indicators_item_structure(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Each item in the list must contain all expected fields."""
    resp = await client.get("/api/v1/indicators", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    first = data["data"][0]
    expected_fields = [
        "id", "name", "category", "description",
        "current_value", "target", "unit", "trend", "updated_at",
    ]
    for field in expected_fields:
        assert field in first, f"Missing field: {field}"
    assert first["trend"] in ("improving", "stable", "declining", "unknown")


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/indicators/{indicator_id} — detail
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_indicator_by_id_exists(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """GET /api/v1/indicators/ind-tlp-001 must return full detail with history."""
    resp = await client.get(
        "/api/v1/indicators/ind-tlp-001", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "ind-tlp-001"
    assert data["category"] == "TLP"
    assert "history" in data
    assert len(data["history"]) == 30
    assert "reference_range" in data


@pytest.mark.asyncio
async def test_get_indicator_by_id_not_found_404(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """A non-existent indicator ID must return 404."""
    resp = await client.get(
        "/api/v1/indicators/ind-nonexistent-999",
        headers=admin_headers,
    )
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert "not found" in detail.lower()


# ═══════════════════════════════════════════════════════════════════════════
# GET /api/v1/indicators/summary — aggregated dashboard
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_get_indicators_summary_structure(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """The summary endpoint must return the correct aggregated structure."""
    resp = await client.get(
        "/api/v1/indicators/summary", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_indicators" in data
    assert "categories" in data
    assert "category_count" in data
    assert "alerts_out_of_range" in data
    assert "last_updated" in data

    assert data["total_indicators"] == 31
    assert data["category_count"] == 10  # 10 categories
    assert len(data["categories"]) == 10
    assert isinstance(data["alerts_out_of_range"], int)
    assert data["alerts_out_of_range"] >= 0


@pytest.mark.asyncio
async def test_summary_categories_are_ordered(
    client: AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Categories in the summary must be returned in the contract order."""
    resp = await client.get(
        "/api/v1/indicators/summary", headers=admin_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    category_names = [c["category"] for c in data["categories"]]
    expected_order = [
        "TLP", "Ocupação", "Sedação", "Ventilação", "Hemodinâmica",
        "Nutrição", "Infecção", "Segurança", "Mobilidade", "Outros",
    ]
    assert category_names == expected_order


# ═══════════════════════════════════════════════════════════════════════════
# Authentication requirement
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_list_indicators_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated requests must return 401."""
    resp = await client.get("/api/v1/indicators")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_indicator_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated detail request must return 401."""
    resp = await client.get("/api/v1/indicators/ind-tlp-001")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_summary_requires_auth(client: AsyncClient) -> None:
    """Unauthenticated summary request must return 401."""
    resp = await client.get("/api/v1/indicators/summary")
    assert resp.status_code == 401
