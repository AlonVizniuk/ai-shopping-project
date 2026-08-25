import pytest
from pydantic import ValidationError

from agent.tools import TOOL_DEFINITIONS
from model.agent import (
    AgentRequest,
    CheckInventoryArguments,
    GetProductDetailsArguments,
    SearchProductsArguments,
)


def test_agent_request_rejects_blank_prompt():
    with pytest.raises(ValidationError):
        AgentRequest(prompt="   ")


@pytest.mark.parametrize("item_id", [0, -1])
def test_product_id_must_be_positive(item_id):
    with pytest.raises(ValidationError):
        GetProductDetailsArguments(item_id=item_id)


def test_requested_quantity_must_be_positive_when_provided():
    with pytest.raises(ValidationError):
        CheckInventoryArguments(item_id=1, requested_quantity=0)


@pytest.mark.parametrize(
    "arguments",
    [
        {"min_price": 100, "max_price": 50},
        {"min_stock": 10, "max_stock": 5},
        {"sort_by": "rating"},
    ],
)
def test_search_arguments_reject_invalid_filters(arguments):
    with pytest.raises(ValidationError):
        SearchProductsArguments(**arguments)


def test_search_arguments_accept_supported_filters():
    arguments = SearchProductsArguments(
        name="Brazil",
        min_price=50,
        max_price=100,
        min_stock=1,
        max_stock=20,
        in_stock_only=True,
        sort_by="price",
    )

    assert arguments.name == "Brazil"
    assert arguments.sort_by == "price"


def test_strict_schemas_require_all_properties_and_make_defaults_nullable():
    definitions = {tool["name"]: tool for tool in TOOL_DEFINITIONS}
    search_schema = definitions["search_products"]["parameters"]
    inventory_schema = definitions["check_inventory"]["parameters"]

    assert search_schema["additionalProperties"] is False
    assert set(search_schema["required"]) == set(search_schema["properties"])
    assert search_schema["properties"]["name"]["type"] == ["string", "null"]
    assert search_schema["properties"]["min_price"]["type"] == ["number", "null"]
    assert search_schema["properties"]["sort_by"]["enum"] == [
        "name",
        "price",
        "stock",
        None,
    ]
    assert "default" not in search_schema["properties"]["min_price"]

    assert inventory_schema["additionalProperties"] is False
    assert inventory_schema["required"] == ["item_id", "requested_quantity"]
    assert inventory_schema["properties"]["item_id"]["type"] == "integer"
    assert inventory_schema["properties"]["requested_quantity"]["type"] == ["integer", "null"]
