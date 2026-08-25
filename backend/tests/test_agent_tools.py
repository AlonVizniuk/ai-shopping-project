import json
from unittest.mock import AsyncMock

import pytest

from agent import tools
from model.item import Item


@pytest.mark.asyncio
async def test_search_products_maps_arguments_to_item_service(monkeypatch):
    search_items = AsyncMock(
        return_value=[Item(id=1, name="Brazil Jersey", price=92, stock=12)]
    )
    monkeypatch.setattr(tools.item_service, "search_items", search_items)

    result = json.loads(await tools.execute_tool(
        "search_products",
        json.dumps({
            "name": "Brazil",
            "min_price": 50,
            "max_price": 100,
            "min_stock": 1,
            "max_stock": 20,
            "in_stock_only": True,
            "sort_by": "price",
        }),
    ))

    search_items.assert_awaited_once_with(
        name="Brazil",
        min_price=50,
        max_price=100,
        min_stock=1,
        max_stock=20,
        in_stock_only=True,
        sort_by="price",
    )
    assert result == {
        "products": [{
            "id": 1,
            "name": "Brazil Jersey",
            "price": 92.0,
            "stock": 12,
            "available": True,
        }],
        "count": 1,
    }


@pytest.mark.asyncio
async def test_search_products_excludes_null_arguments(monkeypatch):
    search_items = AsyncMock(return_value=[])
    monkeypatch.setattr(tools.item_service, "search_items", search_items)

    await tools.execute_tool(
        "search_products",
        json.dumps({
            "name": None,
            "min_price": None,
            "max_price": 100,
            "min_stock": None,
            "max_stock": None,
            "in_stock_only": True,
            "sort_by": None,
        }),
    )

    search_items.assert_awaited_once_with(max_price=100, in_stock_only=True)


@pytest.mark.asyncio
async def test_get_product_details_serializes_authoritative_item(monkeypatch):
    get_item = AsyncMock(
        return_value=Item(id=2, name="France Jersey", price=94, stock=0)
    )
    monkeypatch.setattr(tools.item_service, "get_item_by_id", get_item)

    result = json.loads(
        await tools.execute_tool("get_product_details", '{"item_id": 2}')
    )

    get_item.assert_awaited_once_with(2)
    assert result["id"] == 2
    assert result["available"] is False
    assert result["stock"] == 0


@pytest.mark.asyncio
async def test_check_inventory_reports_requested_quantity(monkeypatch):
    get_item = AsyncMock(
        return_value=Item(id=3, name="Japan Jersey", price=79, stock=4)
    )
    monkeypatch.setattr(tools.item_service, "get_item_by_id", get_item)

    result = json.loads(await tools.execute_tool(
        "check_inventory",
        '{"item_id": 3, "requested_quantity": 5}',
    ))

    get_item.assert_awaited_once_with(3)
    assert result["available"] is True
    assert result["requested_quantity"] == 5
    assert result["requested_quantity_available"] is False


@pytest.mark.asyncio
async def test_missing_product_is_serialized(monkeypatch):
    monkeypatch.setattr(
        tools.item_service,
        "get_item_by_id",
        AsyncMock(return_value=None),
    )

    result = json.loads(
        await tools.execute_tool("get_product_details", '{"item_id": 999}')
    )

    assert result == {"item_id": 999, "found": False}


@pytest.mark.asyncio
async def test_unknown_tool_is_rejected():
    with pytest.raises(tools.UnknownToolError, match="Unknown tool"):
        await tools.execute_tool("delete_product", "{}")
