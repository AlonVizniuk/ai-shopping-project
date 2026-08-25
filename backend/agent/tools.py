import json
from typing import Any, Dict, Type

from pydantic import BaseModel

from model.agent import (
    CheckInventoryArguments,
    GetProductDetailsArguments,
    InventoryResult,
    ProductNotFoundResult,
    ProductResult,
    ProductSearchResult,
    SearchProductsArguments,
)
from service import item_service


class UnknownToolError(ValueError):
    pass


def _strict_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    schema = model.schema()
    properties = schema.get("properties", {})
    originally_required = set(schema.get("required", []))

    for property_name, property_schema in properties.items():
        property_schema.pop("default", None)
        if property_name not in originally_required:
            property_type = property_schema.get("type")
            if isinstance(property_type, str):
                property_schema["type"] = [property_type, "null"]
            if "enum" in property_schema and None not in property_schema["enum"]:
                property_schema["enum"].append(None)

    schema["required"] = list(properties.keys())
    schema["additionalProperties"] = False
    return schema


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "search_products",
        "description": "Search and filter the current jersey catalog. Use for product discovery, prices, and availability lists.",
        "parameters": _strict_schema(SearchProductsArguments),
        "strict": True,
    },
    {
        "type": "function",
        "name": "get_product_details",
        "description": "Get authoritative current details for one product by its item ID.",
        "parameters": _strict_schema(GetProductDetailsArguments),
        "strict": True,
    },
    {
        "type": "function",
        "name": "check_inventory",
        "description": "Check current inventory for a product and optionally whether a requested quantity is available.",
        "parameters": _strict_schema(CheckInventoryArguments),
        "strict": True,
    },
]


def _product_result(item) -> ProductResult:
    return ProductResult(
        id=item.id,
        name=item.name,
        price=item.price,
        stock=item.stock,
        available=item.stock > 0,
    )


async def search_products(arguments: SearchProductsArguments) -> ProductSearchResult:
    items = await item_service.search_items(**arguments.dict(exclude_none=True))
    products = [_product_result(item) for item in items]
    return ProductSearchResult(products=products, count=len(products))


async def get_product_details(arguments: GetProductDetailsArguments):
    item = await item_service.get_item_by_id(arguments.item_id)
    if item is None:
        return ProductNotFoundResult(item_id=arguments.item_id)
    return _product_result(item)


async def check_inventory(arguments: CheckInventoryArguments):
    item = await item_service.get_item_by_id(arguments.item_id)
    if item is None:
        return ProductNotFoundResult(item_id=arguments.item_id)

    requested_available = None
    if arguments.requested_quantity is not None:
        requested_available = item.stock >= arguments.requested_quantity

    return InventoryResult(
        item_id=item.id,
        name=item.name,
        stock=item.stock,
        available=item.stock > 0,
        requested_quantity=arguments.requested_quantity,
        requested_quantity_available=requested_available,
    )


async def execute_tool(name: str, raw_arguments: str) -> str:
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("Tool arguments must be valid JSON") from exc

    if name == "search_products":
        result = await search_products(SearchProductsArguments(**arguments))
    elif name == "get_product_details":
        result = await get_product_details(GetProductDetailsArguments(**arguments))
    elif name == "check_inventory":
        result = await check_inventory(CheckInventoryArguments(**arguments))
    else:
        raise UnknownToolError(f"Unknown tool: {name}")

    return result.json()
